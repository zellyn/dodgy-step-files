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


def _bspline_surface_props(face) -> dict | None:
    """Extract B-spline / Bezier surface introspection: rationality,
    periodicity, degree, knot summaries. Returns None if the face isn't a
    parametric (Bezier or B-spline) surface, or a partial dict if some
    properties aren't applicable.

    Keys (any may be None on Bezier or extraction failure):
        is_rational, is_u_periodic, is_v_periodic,
        u_degree, v_degree,
        n_u_knots, n_v_knots,
        u_knot_mult_max, v_knot_mult_max
    """
    from OCP.BRep import BRep_Tool  # type: ignore
    from OCP.GeomAbs import GeomAbs_BSplineSurface, GeomAbs_BezierSurface  # type: ignore
    from OCP.BRepAdaptor import BRepAdaptor_Surface  # type: ignore

    try:
        adaptor = BRepAdaptor_Surface(face)
        gtype = adaptor.GetType()
    except Exception:
        return None
    if gtype not in (GeomAbs_BSplineSurface, GeomAbs_BezierSurface):
        return None

    out: dict = {
        "is_rational": None, "is_u_periodic": None, "is_v_periodic": None,
        "u_degree": None, "v_degree": None,
        "n_u_knots": None, "n_v_knots": None,
        "u_knot_mult_max": None, "v_knot_mult_max": None,
    }
    if gtype == GeomAbs_BSplineSurface:
        try:
            bs = adaptor.BSpline()
        except Exception:
            return out
        try:
            out["u_degree"] = int(bs.UDegree())
            out["v_degree"] = int(bs.VDegree())
        except Exception:
            pass
        try:
            out["is_u_periodic"] = bool(bs.IsUPeriodic())
            out["is_v_periodic"] = bool(bs.IsVPeriodic())
        except Exception:
            pass
        try:
            out["is_rational"] = bool(bs.IsURational() or bs.IsVRational())
        except Exception:
            pass
        try:
            out["n_u_knots"] = int(bs.NbUKnots())
            out["n_v_knots"] = int(bs.NbVKnots())
        except Exception:
            pass
        try:
            um = list(bs.UMultiplicities())
            vm = list(bs.VMultiplicities())
            out["u_knot_mult_max"] = max(um) if um else None
            out["v_knot_mult_max"] = max(vm) if vm else None
        except Exception:
            pass
    else:  # GeomAbs_BezierSurface
        try:
            bz = adaptor.Bezier()
        except Exception:
            return out
        try:
            out["u_degree"] = int(bz.UDegree())
            out["v_degree"] = int(bz.VDegree())
        except Exception:
            pass
        try:
            out["is_rational"] = bool(bz.IsURational() or bz.IsVRational())
        except Exception:
            pass
        # Bezier has no knot vector / periodicity in OCCT's model
    return out


def _bspline_curve_props(edge) -> dict | None:
    """Per-edge B-spline / Bezier curve introspection. Returns None if the
    edge curve isn't parametric, partial dict otherwise.

    Keys: is_rational, is_periodic, degree, n_knots, knot_mult_max
    """
    from OCP.GeomAbs import GeomAbs_BSplineCurve, GeomAbs_BezierCurve  # type: ignore
    from OCP.BRepAdaptor import BRepAdaptor_Curve  # type: ignore

    try:
        adaptor = BRepAdaptor_Curve(edge)
        gtype = adaptor.GetType()
    except Exception:
        return None
    if gtype not in (GeomAbs_BSplineCurve, GeomAbs_BezierCurve):
        return None

    out: dict = {
        "is_rational": None, "is_periodic": None,
        "degree": None, "n_knots": None, "knot_mult_max": None,
    }
    if gtype == GeomAbs_BSplineCurve:
        try:
            bs = adaptor.BSpline()
        except Exception:
            return out
        try:
            out["degree"] = int(bs.Degree())
        except Exception:
            pass
        try:
            out["is_periodic"] = bool(bs.IsPeriodic())
        except Exception:
            pass
        try:
            out["is_rational"] = bool(bs.IsRational())
        except Exception:
            pass
        try:
            out["n_knots"] = int(bs.NbKnots())
        except Exception:
            pass
        try:
            mm = list(bs.Multiplicities())
            out["knot_mult_max"] = max(mm) if mm else None
        except Exception:
            pass
    else:  # GeomAbs_BezierCurve
        try:
            bz = adaptor.Bezier()
        except Exception:
            return out
        try:
            out["degree"] = int(bz.Degree())
        except Exception:
            pass
        try:
            out["is_rational"] = bool(bz.IsRational())
        except Exception:
            pass
    return out


def face_metrics(shape) -> list[dict]:
    """Per-face: surface type, area, bounding-box, sliver aspect ratio,
    and (for B-spline/Bezier surfaces) rationality, periodicity, degree,
    knot-vector summaries."""
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
        # Edge-loop orientation counts within this face
        ori_counts = {"forward": 0, "reversed": 0, "internal": 0, "external": 0}
        try:
            from OCP.TopAbs import (  # type: ignore
                TopAbs_FORWARD, TopAbs_REVERSED,
                TopAbs_INTERNAL, TopAbs_EXTERNAL,
            )
            ori_map = {
                TopAbs_FORWARD: "forward", TopAbs_REVERSED: "reversed",
                TopAbs_INTERNAL: "internal", TopAbs_EXTERNAL: "external",
            }
            for e in edges:
                try:
                    ori_counts[ori_map[e.Orientation()]] += 1
                except Exception:
                    pass
        except Exception:
            pass
        entry = {
            "i": i,
            "surface_type": stype,
            "area": area,
            "bbox_extents_sorted_desc": extents,
            "sliver_aspect_max_min": aspect,
            "edge_count": len(edges),
            "edge_orientations": ori_counts,
        }
        bs_props = _bspline_surface_props(f)
        if bs_props is not None:
            entry["bspline"] = bs_props
        metrics.append(entry)
    return metrics


def edge_metrics(shape) -> list[dict]:
    """Per-edge: 3D length, vertex tolerance, curve type, orientation, and
    (for B-spline/Bezier curves) rationality, periodicity, degree, knots."""
    from OCP.BRep import BRep_Tool  # type: ignore
    from OCP.BRepGProp import BRepGProp  # type: ignore
    from OCP.GProp import GProp_GProps  # type: ignore
    from OCP.TopAbs import (  # type: ignore
        TopAbs_EDGE, TopAbs_FORWARD, TopAbs_REVERSED,
        TopAbs_INTERNAL, TopAbs_EXTERNAL,
    )
    from OCP.TopoDS import TopoDS  # type: ignore
    from OCP.BRepAdaptor import BRepAdaptor_Curve  # type: ignore
    from OCP.GeomAbs import (  # type: ignore
        GeomAbs_Line, GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_Hyperbola,
        GeomAbs_Parabola, GeomAbs_BezierCurve, GeomAbs_BSplineCurve,
        GeomAbs_OffsetCurve, GeomAbs_OtherCurve,
    )

    curvetype_names = {
        GeomAbs_Line: "line", GeomAbs_Circle: "circle",
        GeomAbs_Ellipse: "ellipse", GeomAbs_Hyperbola: "hyperbola",
        GeomAbs_Parabola: "parabola", GeomAbs_BezierCurve: "bezier",
        GeomAbs_BSplineCurve: "bspline", GeomAbs_OffsetCurve: "offset",
        GeomAbs_OtherCurve: "other",
    }
    ori_map = {
        TopAbs_FORWARD: "forward", TopAbs_REVERSED: "reversed",
        TopAbs_INTERNAL: "internal", TopAbs_EXTERNAL: "external",
    }

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
        try:
            ctype = curvetype_names.get(BRepAdaptor_Curve(e).GetType(), "unknown")
        except Exception:
            ctype = "?"
        try:
            ori = ori_map.get(e.Orientation(), "?")
        except Exception:
            ori = "?"
        entry = {
            "i": i, "length": length, "tolerance": tol,
            "curve_type": ctype, "orientation": ori,
        }
        bs_props = _bspline_curve_props(e)
        if bs_props is not None:
            entry["bspline"] = bs_props
        metrics.append(entry)
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
