"""Manifold-validity oracle: tessellate STEP geometry, check via manifold3d.

Adds an *independent* signal for shape-loading fixtures: does the
tessellated triangle mesh form a manifold per ``manifold3d``'s
definition (every edge shared by exactly 2 triangles, no T-vertices,
no self-intersection at the triangle level)?

Only meaningful for fixtures that load with shapes; silent-empty,
parser-reject, segfault fixtures get ``n/a``.

The independence is partial: tessellation is OCC's, so OCC-internal
healing during meshing may erase defects before manifold sees them.
But the signal is genuinely cross-checking: manifold uses different
manifold-validity rules than OCC's ``BRepCheck_Analyzer``.

Usage::

    cd validation
    uv run python -m step_corpus._manifold_oracle --shape-loading
    uv run python -m step_corpus._manifold_oracle ../step-examples/12-3a-shells/Tsh007.stp
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


def step_to_manifold(step_path: str, deflection: float = 0.1) -> dict[str, Any]:
    """Tessellate the STEP file via OCC, build manifold3d.Manifold, return validity info."""
    from OCP.STEPControl import STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS
    import manifold3d

    reader = STEPControl_Reader()
    if reader.ReadFile(step_path) != IFSelect_RetDone:
        return {"manifold_status": "step_read_failed"}
    reader.TransferRoots()
    n_shapes = reader.NbShapes()
    if n_shapes == 0:
        return {"manifold_status": "no_shapes_loaded"}

    all_verts: list[list[float]] = []
    all_tris: list[list[int]] = []
    n_faces_total = 0
    for i in range(1, n_shapes + 1):
        shape = reader.Shape(i)
        try:
            BRepMesh_IncrementalMesh(shape, deflection)
        except Exception as e:
            return {"manifold_status": "mesh_failed", "error": str(e)[:200]}
        explorer = TopExp_Explorer(shape, TopAbs_FACE)
        while explorer.More():
            face = TopoDS.Face_s(explorer.Current())
            loc = TopLoc_Location()
            tri = BRep_Tool.Triangulation_s(face, loc)
            if tri is not None:
                trsf = loc.Transformation()
                vert_offset = len(all_verts)
                for j in range(1, tri.NbNodes() + 1):
                    pnt = tri.Node(j).Transformed(trsf)
                    all_verts.append([pnt.X(), pnt.Y(), pnt.Z()])
                for j in range(1, tri.NbTriangles() + 1):
                    t = tri.Triangle(j)
                    a, b, c = t.Get()
                    all_tris.append([vert_offset + a - 1,
                                     vert_offset + b - 1,
                                     vert_offset + c - 1])
                n_faces_total += 1
            explorer.Next()

    if not all_verts or not all_tris:
        return {"manifold_status": "empty_mesh", "n_faces_brep": n_faces_total}

    verts = np.array(all_verts, dtype=np.float32)
    tris = np.array(all_tris, dtype=np.uint32)

    try:
        mesh = manifold3d.Mesh(vert_properties=verts, tri_verts=tris)
        m = manifold3d.Manifold(mesh)
        err = m.status()
    except Exception as e:
        return {
            "manifold_status": "construct_failed",
            "error": str(e)[:200],
            "n_verts": len(verts),
            "n_tris": len(tris),
        }

    return {
        "manifold_status": str(err).rsplit(".", 1)[-1],
        "n_verts": int(len(verts)),
        "n_tris": int(len(tris)),
        "n_faces_brep": int(n_faces_total),
        "is_empty": bool(m.is_empty()),
        "volume": float(m.volume()) if not m.is_empty() else 0.0,
        "genus": int(m.genus()) if not m.is_empty() else None,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="step_corpus._manifold_oracle")
    p.add_argument("paths", nargs="*", type=Path)
    p.add_argument("--shape-loading", action="store_true",
                   help="run on every shape-loading fixture (uses /tmp/cad-shape-loading.json)")
    p.add_argument("--deflection", type=float, default=0.1)
    p.add_argument("--out", type=Path, default=Path("/tmp/cad-manifold-results.json"))
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    if args.shape_loading:
        from step_corpus._build_catalog_json import RESEARCH_ROOT
        EXAMPLES = RESEARCH_ROOT / "step-examples"
        fixtures = json.load(open("/tmp/cad-shape-loading.json"))
        results = []
        for sec, eid in fixtures:
            path = EXAMPLES / sec / f"{eid}.stp"
            try:
                r = step_to_manifold(str(path), args.deflection)
            except Exception as e:
                r = {"manifold_status": "exception", "error": str(e)[:200]}
            r["id"] = eid
            r["section"] = sec
            results.append(r)
        args.out.write_text(json.dumps(results, indent=2))

        from collections import Counter
        bucket = Counter(r["manifold_status"] for r in results)
        print(f"Manifold-oracle results across {len(results)} shape-loading fixtures:")
        for k, n in sorted(bucket.items(), key=lambda kv: -kv[1]):
            print(f"  {k:<22} {n:>4}")
        return 0

    for path in args.paths:
        try:
            r = step_to_manifold(str(path), args.deflection)
        except Exception as e:
            r = {"manifold_status": "exception", "error": str(e)[:200]}
        if args.json:
            json.dump({"file": str(path), **r}, sys.stdout)
            sys.stdout.write("\n")
        else:
            print(f"{path.stem}: {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
