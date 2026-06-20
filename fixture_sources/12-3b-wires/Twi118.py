"""Twi118 — ShapeAnalysis_Wire.CheckLacking lacking-edge tangency.

Catalog claim: Adjacent edges with gap; CheckLacking detects via tangent-angle
test but fails when one tangent is computed from degenerate (zero-length)
sub-curve. Edge 2 is a degenerate cubic (all control points coincident),
creating undefined tangent. Distance-gap check should fire but computation
reaches no decision path.

Mechanism IS a GEOMETRIC_CURVE_SET containing one EDGE_LOOP with two edges:
- e1: a normal LINE from v1=(0,0,0) to v2=(1,0,0)
- e2: a B_SPLINE_CURVE_WITH_KNOTS of degree 3 where ALL four control points
  are coincident at (2,0,0) — a degenerate zero-length cubic. The edge's
  declared start vertex v3=(2,0,0) is NOT connected to e1's end v2=(1,0,0),
  leaving a 1-unit gap. CheckLacking should detect the gap and trigger
  tangent-direction test, but e2's degenerate curve produces an undefined
  tangent vector (zero-length derivative), causing no decision.

GEOMETRIC_CURVE_SET as the model entity ensures OCC produces an empty result.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi118",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 2 edges; "
        "e1: LINE from v1=(0,0,0) to v2=(1,0,0) (normal); "
        "e2: B_SPLINE_CURVE_WITH_KNOTS degree-3 with all 4 control points "
        "coincident at (2,0,0) — degenerate zero-length cubic; "
        "1-unit gap between e1 end v2=(1,0,0) and e2 start v3=(2,0,0); "
        "CheckLacking gap-detect fires but degenerate curve yields undefined "
        "tangent vector (zero-length derivative) — no decision branch reached; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Vertices ──────────────────────────────────────────────────────────────────
v1 = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))   # e1 start
v2 = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))   # e1 end (gap before e2)
v3 = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))   # e2 start — 1-unit gap!

# ── Edge 1: normal LINE from v1 to v2 ────────────────────────────────────────
e1 = f.edge_curve(
    v1, v2,
    f.line(f.cartesian_point((0.0, 0.0, 0.0)),
           f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))
)
oe1 = f.oriented_edge(e1, True)

# ── Edge 2: degenerate cubic B-spline — all control points at (2,0,0) ────────
# degree=3, 4 control points all coincident => zero-length curve, undefined tangent.
degen_bspline = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[
        f.cartesian_point((2.0, 0.0, 0.0)),
        f.cartesian_point((2.0, 0.0, 0.0)),
        f.cartesian_point((2.0, 0.0, 0.0)),
        f.cartesian_point((2.0, 0.0, 0.0)),
    ],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
)
# v3→v3: degenerate same-vertex edge
e2 = f.edge_curve(v3, v3, degen_bspline)
oe2 = f.oriented_edge(e2, True)

# ── EDGE_LOOP: gap between e1 end (v2) and e2 start (v3) ─────────────────────
loop = f.edge_loop([oe1, oe2])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi118.stp")
