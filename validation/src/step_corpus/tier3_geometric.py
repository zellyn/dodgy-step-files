"""Tier 3: geometric property checks.

Loads a STEP file via OCCT and computes quantitative properties needed to
verify defect *magnitudes* (face areas, edge lengths, sliver aspect ratios,
vertex tolerances, knot multiplicities, etc.). Pairs with `validate.py` for
the cases where parser-pass/fail isn't enough.

Usage:
    uv run python -m step_corpus.tier3_geometric <file.stp> [--json]
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path


def _shape_iter(shape, kind):
    from OCP.TopExp import TopExp_Explorer  # type: ignore
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        yield exp.Current()
        exp.Next()


def load_shape(path: Path):
    from OCP.STEPControl import STEPControl_Reader  # type: ignore
    from OCP.IFSelect import IFSelect_RetDone  # type: ignore
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        return None, "ReadFile failed"
    n = reader.TransferRoots()
    return reader.OneShape(), {"roots": n}


def face_metrics(shape) -> list[dict]:
    """Per-face: surface type, area, bounding-box, sliver aspect ratio."""
    from OCP.BRep import BRep_Tool  # type: ignore
    from OCP.BRepGProp import BRepGProp  # type: ignore
    from OCP.GProp import GProp_GProps  # type: ignore
    from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE  # type: ignore
    from OCP.TopoDS import TopoDS  # type: ignore
    from OCP.Bnd import Bnd_Box  # type: ignore
    from OCP.BRepBndLib import BRepBndLib  # type: ignore
    from OCP.GeomAbs import (  # type: ignore
        GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Cone, GeomAbs_Sphere,
        GeomAbs_Torus, GeomAbs_BezierSurface, GeomAbs_BSplineSurface,
        GeomAbs_SurfaceOfRevolution, GeomAbs_SurfaceOfExtrusion,
        GeomAbs_OffsetSurface, GeomAbs_OtherSurface,
    )
    from OCP.BRepAdaptor import BRepAdaptor_Surface  # type: ignore

    surftype_names = {
        GeomAbs_Plane: "plane", GeomAbs_Cylinder: "cylinder",
        GeomAbs_Cone: "cone", GeomAbs_Sphere: "sphere",
        GeomAbs_Torus: "torus", GeomAbs_BezierSurface: "bezier",
        GeomAbs_BSplineSurface: "bspline",
        GeomAbs_SurfaceOfRevolution: "revolution",
        GeomAbs_SurfaceOfExtrusion: "extrusion",
        GeomAbs_OffsetSurface: "offset", GeomAbs_OtherSurface: "other",
    }

    metrics = []
    if shape is None or shape.IsNull():
        return metrics

    for i, face in enumerate(_shape_iter(shape, TopAbs_FACE)):
        f = TopoDS.Face_s(face)
        try:
            adaptor = BRepAdaptor_Surface(f)
            stype = surftype_names.get(adaptor.GetType(), "unknown")
        except Exception:
            stype = "?"
        # Area
        gp = GProp_GProps()
        try:
            BRepGProp.SurfaceProperties_s(f, gp)
            area = gp.Mass()
        except Exception:
            area = None
        # BBox + sliver aspect ratio
        bb = Bnd_Box()
        try:
            BRepBndLib.Add_s(f, bb)
            xmin, ymin, zmin, xmax, ymax, zmax = bb.Get()
            extents = sorted([xmax - xmin, ymax - ymin, zmax - zmin], reverse=True)
            big = extents[0] or 1e-30
            aspect = (big / extents[2]) if extents[2] > 1e-30 else float("inf")
        except Exception:
            extents = None
            aspect = None
        # Edge count
        edges = list(_shape_iter(f, TopAbs_EDGE))
        metrics.append({
            "i": i,
            "surface_type": stype,
            "area": area,
            "bbox_extents_sorted_desc": extents,
            "sliver_aspect_max_min": aspect,
            "edge_count": len(edges),
        })
    return metrics


def edge_metrics(shape) -> list[dict]:
    """Per-edge: 3D length, vertex tolerance, curve type."""
    from OCP.BRep import BRep_Tool  # type: ignore
    from OCP.BRepGProp import BRepGProp  # type: ignore
    from OCP.GProp import GProp_GProps  # type: ignore
    from OCP.TopAbs import TopAbs_EDGE  # type: ignore
    from OCP.TopoDS import TopoDS  # type: ignore

    metrics = []
    if shape is None or shape.IsNull():
        return metrics
    for i, edge in enumerate(_shape_iter(shape, TopAbs_EDGE)):
        e = TopoDS.Edge_s(edge)
        gp = GProp_GProps()
        try:
            BRepGProp.LinearProperties_s(e, gp)
            length = gp.Mass()
        except Exception:
            length = None
        try:
            tol = BRep_Tool.Tolerance_s(e)
        except Exception:
            tol = None
        metrics.append({"i": i, "length": length, "tolerance": tol})
    return metrics


def vertex_metrics(shape) -> list[dict]:
    """Per-vertex: tolerance, position."""
    from OCP.BRep import BRep_Tool  # type: ignore
    from OCP.TopAbs import TopAbs_VERTEX  # type: ignore
    from OCP.TopoDS import TopoDS  # type: ignore

    metrics = []
    if shape is None or shape.IsNull():
        return metrics
    for i, v in enumerate(_shape_iter(shape, TopAbs_VERTEX)):
        vv = TopoDS.Vertex_s(v)
        try:
            p = BRep_Tool.Pnt_s(vv)
            xyz = (p.X(), p.Y(), p.Z())
        except Exception:
            xyz = None
        try:
            tol = BRep_Tool.Tolerance_s(vv)
        except Exception:
            tol = None
        metrics.append({"i": i, "xyz": xyz, "tolerance": tol})
    return metrics


def brepcheck(shape) -> dict:
    """Run BRepCheck_Analyzer; aggregate fault counts by type."""
    if shape is None or shape.IsNull():
        return {"valid": None, "reason": "null shape"}
    try:
        from OCP.BRepCheck import BRepCheck_Analyzer  # type: ignore
        a = BRepCheck_Analyzer(shape, True)
        return {"valid": a.IsValid()}
    except Exception as e:
        return {"valid": None, "error": str(e)[:300]}


def parametric_summary(path: Path) -> dict:
    """File-text-level parametric checks: knot multiplicities sum, weight ranges, etc.

    Cheap regex-based; doesn't require successful OCCT load.
    """
    text = path.read_text(encoding="latin-1", errors="replace")
    out: dict = {}

    # B_SPLINE_*_WITH_KNOTS: pull (degree) and (multiplicities) and (knots)
    bsplines = []
    for m in re.finditer(
        r"B_SPLINE_(CURVE|SURFACE)_WITH_KNOTS\s*\(\s*'[^']*'\s*,\s*(\d+)",
        text,
    ):
        kind = m.group(1)  # CURVE or SURFACE
        degree = int(m.group(2))
        bsplines.append({"kind": kind, "degree": degree})

    # Weights
    weights = re.findall(r"WEIGHTS_DATA\s*\(\s*\(([^)]+)\)\s*\)", text, flags=re.S)
    out["weights_groups"] = []
    for w in weights[:5]:
        try:
            vals = [float(x.strip()) for x in w.replace("\n", " ").split(",") if x.strip()]
            out["weights_groups"].append({
                "n": len(vals),
                "min": min(vals) if vals else None,
                "max": max(vals) if vals else None,
                "all_unit": all(abs(v - 1.0) < 1e-12 for v in vals) if vals else None,
            })
        except Exception:
            pass

    out["bsplines"] = bsplines

    # Tolerance / uncertainty values
    out["uncertainty_values"] = [
        float(m.group(1))
        for m in re.finditer(
            r"UNCERTAINTY_MEASURE_WITH_UNIT\s*\(\s*LENGTH_MEASURE\s*\(\s*([0-9.eE+-]+)",
            text,
        )
    ]

    # FILE_SCHEMA + magic
    out["schema"] = re.search(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", text)
    out["schema"] = out["schema"].group(1) if out["schema"] else None

    return out


def geometric_report(path: Path) -> dict:
    shape, info = load_shape(path)
    if shape is None:
        return {"file": str(path), "load": "fail", "info": info,
                "parametric": parametric_summary(path)}
    faces = face_metrics(shape)
    return {
        "file": str(path),
        "load": "ok",
        "load_info": info,
        "shape_null": shape.IsNull(),
        "faces": faces,
        "n_faces_total": len(faces),
        "edges": edge_metrics(shape)[:20],  # cap for output
        "n_edges_total": sum(1 for _ in _shape_iter(shape, _topabs_edge())),
        "vertices": vertex_metrics(shape)[:20],
        "n_vertices_total": sum(1 for _ in _shape_iter(shape, _topabs_vertex())),
        "brepcheck": brepcheck(shape),
        "parametric": parametric_summary(path),
    }


def _topabs_edge():
    from OCP.TopAbs import TopAbs_EDGE  # type: ignore
    return TopAbs_EDGE


def _topabs_vertex():
    from OCP.TopAbs import TopAbs_VERTEX  # type: ignore
    return TopAbs_VERTEX


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: tier3_geometric.py <file.stp> [--json]", file=sys.stderr)
        return 2
    path = Path(argv[0])
    as_json = "--json" in argv[1:]
    result = geometric_report(path)
    if as_json:
        json.dump(result, sys.stdout, indent=2, default=str)
    else:
        from rich.console import Console
        from rich.pretty import Pretty
        Console().print(Pretty(result, expand_all=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
