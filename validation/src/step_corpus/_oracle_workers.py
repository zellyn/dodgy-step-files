"""Per-oracle worker scripts. Each is invoked as `python -m step_corpus._oracle_workers <oracle> <file.stp>`
and emits a single JSON object on stdout. stderr is reserved for diagnostics
which the parent process captures via subprocess pipes.

Subprocess isolation buys us:
  - OCCT segfaults / aborts don't kill the parent runner.
  - Complete stdout/stderr capture without fd-juggling tricks.
  - Each oracle runs with a fresh process (no global-state pollution between fixtures).
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from pathlib import Path


def _emit(d: dict):
    json.dump(d, sys.stdout, default=str)
    sys.stdout.write("\n")
    sys.stdout.flush()


def _capture_stderr_text() -> str:
    # The parent process pipes stderr; this is just a placeholder if we want to
    # also peek before writing. We rely on subprocess to capture it externally.
    return ""


def oracle_ifcopenshell(path: str):
    try:
        import ifcopenshell  # type: ignore
    except ImportError as e:
        _emit({"status": "tool_missing", "error": str(e)})
        return
    try:
        f = ifcopenshell.open(path)
        _emit({
            "status": "accept",
            "schema": f.schema,
            "n_entities": len(list(f)),
        })
    except Exception as e:
        msg = str(e)
        low = msg.lower()
        if any(s in low for s in ["unsupported schema", "no schema", "schema not", "unknown schema"]):
            _emit({"status": "schema_class_reject", "error": msg[:300]})
        else:
            _emit({"status": "reject", "error": msg[:500]})


def oracle_occt(path: str, healing: bool):
    try:
        from OCP.STEPControl import STEPControl_Reader  # type: ignore
        from OCP.IFSelect import IFSelect_RetDone  # type: ignore
        from OCP.Interface import Interface_Static  # type: ignore
    except ImportError as e:
        _emit({"status": "tool_missing", "error": str(e)})
        return

    if not healing:
        Interface_Static.SetIVal_s("read.precision.mode", 0)
        Interface_Static.SetRVal_s("read.precision.val", 1.0e-7)
        Interface_Static.SetRVal_s("read.maxprecision.val", 1.0e-7)
        Interface_Static.SetIVal_s("read.maxprecision.mode", 1)
        Interface_Static.SetIVal_s("read.stdsameparameter.mode", 1)
        Interface_Static.SetIVal_s("read.surfacecurve.mode", 0)
    else:
        Interface_Static.SetIVal_s("read.precision.mode", 0)
        Interface_Static.SetIVal_s("read.surfacecurve.mode", 3)

    try:
        reader = STEPControl_Reader()
        status = reader.ReadFile(path)
        read_status = str(status)
        if status != IFSelect_RetDone:
            _emit({"status": "reject_at_read", "ret_status": read_status})
            return
        n_roots = reader.TransferRoots()
        shape = reader.OneShape()
        shape_null = shape.IsNull()
        from OCP.TopExp import TopExp_Explorer  # type: ignore
        from OCP.TopAbs import (  # type: ignore
            TopAbs_VERTEX, TopAbs_EDGE, TopAbs_WIRE,
            TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_COMPOUND,
        )
        counts = {}
        for label, t in [
            ("vertex", TopAbs_VERTEX), ("edge", TopAbs_EDGE),
            ("wire", TopAbs_WIRE), ("face", TopAbs_FACE),
            ("shell", TopAbs_SHELL), ("solid", TopAbs_SOLID),
            ("compound", TopAbs_COMPOUND),
        ]:
            if shape_null:
                counts[label] = 0
            else:
                exp = TopExp_Explorer(shape, t)
                c = 0
                while exp.More():
                    c += 1
                    exp.Next()
                counts[label] = c

        if shape_null or n_roots == 0:
            _emit({
                "status": "accept_silent",
                "n_roots": n_roots,
                "shape_null": shape_null,
                "shape_counts": counts,
                "note": "parser accepted but transfer produced no shape",
            })
        else:
            _emit({
                "status": "accept",
                "n_roots": n_roots,
                "shape_null": shape_null,
                "shape_counts": counts,
            })
    except Exception as e:
        _emit({
            "status": "exception",
            "error": str(e)[:400],
            "traceback": traceback.format_exc()[-500:],
        })


def oracle_gmsh(path: str, autofix: bool):
    try:
        import gmsh  # type: ignore
    except ImportError as e:
        _emit({"status": "tool_missing", "error": str(e)})
        return
    try:
        gmsh.initialize([], False)
        try:
            gmsh.option.setNumber("Geometry.OCCAutoFix", 1 if autofix else 0)
            gmsh.option.setNumber("General.Terminal", 0)
            try:
                gmsh.model.occ.importShapes(path)
                gmsh.model.occ.synchronize()
                ents = gmsh.model.getEntities()
                by_dim = {0: 0, 1: 0, 2: 0, 3: 0}
                for d, _ in ents:
                    by_dim[d] = by_dim.get(d, 0) + 1
                _emit({
                    "status": "accept" if ents else "accept_silent",
                    "by_dim": by_dim,
                    "total_entities": len(ents),
                })
            except Exception as e:
                _emit({"status": "reject", "error": str(e)[:400]})
        finally:
            try:
                gmsh.clear()
            except Exception:
                pass
            gmsh.finalize()
    except Exception as e:
        _emit({"status": "exception", "error": str(e)[:400]})


def oracle_manifold(path: str):
    """Tessellate the STEP file via OCC, validate via manifold3d.

    Auxiliary oracle: only meaningful for fixtures that load shapes.
    Adds an *independent* topology check (every edge shared by exactly
    2 triangles, no T-vertices). Independence is partial: tessellation
    is OCC's, so OCC-internal healing during meshing may erase defects
    before manifold sees them.

    Returns:
    - status: ``manifold_ok`` / ``not_manifold`` / ``empty_mesh`` /
      ``no_shapes_loaded`` / ``step_read_failed`` / ``mesh_failed``
    - aux: n_verts, n_tris, volume, genus when applicable
    """
    try:
        from OCP.STEPControl import STEPControl_Reader  # type: ignore
        from OCP.IFSelect import IFSelect_RetDone  # type: ignore
        from OCP.BRepMesh import BRepMesh_IncrementalMesh  # type: ignore
        from OCP.TopExp import TopExp_Explorer  # type: ignore
        from OCP.TopAbs import TopAbs_FACE  # type: ignore
        from OCP.BRep import BRep_Tool  # type: ignore
        from OCP.TopLoc import TopLoc_Location  # type: ignore
        from OCP.TopoDS import TopoDS  # type: ignore
        import manifold3d  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as e:
        _emit({"status": "tool_missing", "error": str(e)})
        return

    try:
        reader = STEPControl_Reader()
        if reader.ReadFile(path) != IFSelect_RetDone:
            _emit({"status": "step_read_failed"})
            return
        reader.TransferRoots()
        n_shapes = reader.NbShapes()
        if n_shapes == 0:
            _emit({"status": "no_shapes_loaded"})
            return

        all_verts: list[list[float]] = []
        all_tris: list[list[int]] = []
        n_faces_total = 0
        for i in range(1, n_shapes + 1):
            shape = reader.Shape(i)
            try:
                BRepMesh_IncrementalMesh(shape, 0.1)
            except Exception as e:
                _emit({"status": "mesh_failed", "error": str(e)[:200]})
                return
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
            _emit({"status": "empty_mesh", "n_faces_brep": n_faces_total})
            return

        verts = np.array(all_verts, dtype=np.float32)
        tris = np.array(all_tris, dtype=np.uint32)
        try:
            mesh = manifold3d.Mesh(vert_properties=verts, tri_verts=tris)
            m = manifold3d.Manifold(mesh)
            err = m.status()
        except Exception as e:
            _emit({"status": "construct_failed", "error": str(e)[:200]})
            return

        err_name = str(err).rsplit(".", 1)[-1]
        is_empty = bool(m.is_empty())
        _emit({
            "status": "manifold_ok" if err_name == "NoError" and not is_empty else
                      ("not_manifold" if err_name == "NotManifold" else err_name.lower()),
            "n_verts": int(len(verts)),
            "n_tris": int(len(tris)),
            "n_faces_brep": int(n_faces_total),
            "is_empty": is_empty,
            "volume": float(m.volume()) if not is_empty else 0.0,
            "genus": int(m.genus()) if not is_empty else None,
        })
    except Exception as e:
        _emit({"status": "exception", "error": str(e)[:400]})


def oracle_ocaf(path: str):
    """OCAF / XCAF document-layer oracle.

    Loads the fixture into a ``TDocStd_Document`` via
    ``STEPCAFControl_Reader`` and walks the OCAF tree using the
    ``XCAFDoc_*`` accessors. Reports root-label / colored-label /
    assembly-component / transform counts. See ``_ocaf_oracle`` for
    the full field documentation.
    """
    try:
        from step_corpus._ocaf_oracle import analyze
    except ImportError as e:
        _emit({"status": "tool_missing", "error": str(e)})
        return
    try:
        rec = analyze(path)
    except Exception as e:
        _emit({
            "status": "exception",
            "error": str(e)[:400],
            "traceback": traceback.format_exc()[-400:],
        })
        return
    # Map analyze() -> oracle-worker JSON contract
    load_status = rec.get("load_status", "unknown")
    out = {
        "status": (
            "accept" if load_status == "ok"
            else ("reject" if load_status == "failed"
                  else load_status)
        ),
        "load_status": load_status,
        "root_labels": rec.get("root_labels", 0),
        "free_shapes": rec.get("free_shapes", 0),
        "named_labels": rec.get("named_labels", 0),
        "named_label_examples": rec.get("named_label_examples", []),
        "colored_labels": rec.get("colored_labels", 0),
        "colored_label_count_with_alpha": rec.get("colored_label_count_with_alpha", 0),
        "assembly_count": rec.get("assembly_count", 0),
        "assembly_components": rec.get("assembly_components", 0),
        "max_depth": rec.get("max_depth", 0),
        "transforms_at_leaf": rec.get("transforms_at_leaf", 0),
        "non_identity_transforms": rec.get("non_identity_transforms", 0),
        "sub_shape_labels": rec.get("sub_shape_labels", 0),
        "layer_count": rec.get("layer_count", 0),
    }
    if rec.get("diagnostics"):
        out["ocaf_diagnostics"] = rec["diagnostics"][:8]
    _emit(out)


def oracle_part21_strict(path: str):
    """Pure-Python Part-21 syntactic validator (independent of OCCT).

    Implements ISO 10303-21 Edition 3 lexical / framing rules. Used as
    a cross-validation oracle: where this and OCCT disagree, OCCT is
    silently healing (or imposing) something the spec doesn't.
    """
    try:
        from step_corpus._part21_validator import validate_file
        from pathlib import Path as _P
        v = validate_file(_P(path))
        _emit({
            "status": v.status,
            "n_entities": v.n_entities,
            "n_unresolved_refs": v.n_unresolved_refs,
            "first_error": v.errors[0]["code"] if v.errors else None,
            "first_warning": v.warnings[0]["code"] if v.warnings else None,
        })
    except Exception as e:
        _emit({"status": "exception", "error": str(e)[:400]})


def oracle_solvespace(path: str) -> None:
    """Solvespace cross-kernel oracle: STEP via independent (non-OCCT) parser.

    Install-optional: when solvespace isn't in PATH, emits
    ``{status: "not_installed"}`` quickly.
    """
    try:
        from pathlib import Path as _P
        from step_corpus._solvespace_oracle import run_solvespace
        result = run_solvespace(_P(path), timeout_s=30)
        _emit({
            "status": result["status"],
            "n_solids": result["n_solids"],
            "stderr_tail": result["stderr_tail"],
            "duration_ms": result["duration_ms"],
        })
    except Exception as e:
        _emit({"status": "exception", "error": str(e)[:400]})


def oracle_brlcad(path: str) -> None:
    """BRL-CAD cross-kernel oracle: STEP via STEPcode parser (NIST PDES,
    fully independent of OpenCASCADE).

    Install-optional: when step-g isn't in PATH, emits
    ``{status: "not_installed"}`` quickly.
    """
    try:
        from pathlib import Path as _P
        from step_corpus._brlcad_oracle import run_brlcad
        result = run_brlcad(_P(path), timeout_s=30)
        _emit({
            "status": result["status"],
            "n_regions": result["n_regions"],
            "stderr_tail": result["stderr_tail"],
            "duration_ms": result["duration_ms"],
        })
    except Exception as e:
        _emit({"status": "exception", "error": str(e)[:400]})


def oracle_structural(path: str) -> None:
    """Non-kernel STEP structural linter (units-consistency, degenerate axes,
    dangling refs, duplicate ids). Asserts on spec conformance / model integrity
    — a dimension the geometry kernels are blind to. See _structural_oracle.
    """
    try:
        from step_corpus._structural_oracle import lint_file
        _emit({"status": "ok_scan", "code": lint_file(path)})
    except Exception as e:
        _emit({"status": "exception", "error": str(e)[:400]})


ORACLES = {
    "ifcopenshell": oracle_ifcopenshell,
    "occt_heal_on": lambda p: oracle_occt(p, healing=True),
    "occt_heal_off": lambda p: oracle_occt(p, healing=False),
    "gmsh_autofix_on": lambda p: oracle_gmsh(p, autofix=True),
    "gmsh_autofix_off": lambda p: oracle_gmsh(p, autofix=False),
    "part21_strict": oracle_part21_strict,
    "manifold": oracle_manifold,
    "ocaf": oracle_ocaf,
    "solvespace": oracle_solvespace,
    "brlcad": oracle_brlcad,
    "structural": oracle_structural,
}


def main():
    if len(sys.argv) != 3:
        print("usage: python -m step_corpus._oracle_workers <oracle> <file.stp>", file=sys.stderr)
        sys.exit(2)
    oracle = sys.argv[1]
    path = sys.argv[2]
    if oracle not in ORACLES:
        print(f"unknown oracle: {oracle}; valid: {list(ORACLES)}", file=sys.stderr)
        sys.exit(2)
    ORACLES[oracle](path)


if __name__ == "__main__":
    main()
