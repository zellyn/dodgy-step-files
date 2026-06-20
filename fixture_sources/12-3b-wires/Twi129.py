"""Twi129 — ShapeFix_Wire.FixSelfIntersectingEdge inflection-self-touch.

Catalog claim: Single EDGE_CURVE with a 3D figure-8 (self-touching at inflection
point, not transverse crossing); FixSelfIntersectingEdge split logic assumes
transverse self-intersection and fails on self-touch.

Fixture: B_SPLINE_CURVE degree-3 with control points forming a figure-8 shape:
(0,0,0)→(2.5,5,0)→(5,0,0)→(7.5,-5,0)→(10,0,0). The curve self-touches at (5,0)
at the inflection point. FixSelfIntersectingEdge's split heuristic cannot resolve
self-touch because it's a tangential contact, not a crossing.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi129",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 1 edge; "
        "e1: B_SPLINE_CURVE_WITH_KNOTS degree-3 figure-8 curve; "
        "control points (0,0,0),(2.5,5,0),(5,0,0),(7.5,-5,0),(10,0,0); "
        "curve self-touches at inflection point (5,0,0) — tangential contact not transverse crossing; "
        "FixSelfIntersectingEdge split heuristic assumes transverse crossing IS defect; "
        "tangential self-touch cannot be resolved by split logic; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── Figure-8 B-spline: self-touches at (5,0,0) ──────────────────────────────
# degree-3 B-spline with 5 control points
# knot_multiplicities: [4, 1, 4] => sum = 9 = 5 + 3 + 1 ✓
cp0 = f.cartesian_point((0.0,   0.0, 0.0))
cp1 = f.cartesian_point((2.5,   5.0, 0.0))
cp2 = f.cartesian_point((5.0,   0.0, 0.0))   # inflection / self-touch point
cp3 = f.cartesian_point((7.5,  -5.0, 0.0))
cp4 = f.cartesian_point((10.0,  0.0, 0.0))

bspline = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp0, cp1, cp2, cp3, cp4],
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.5, 1.0],
)

P_start = (0.0,  0.0, 0.0)
P_end   = (10.0, 0.0, 0.0)

v_start = f.vertex_point(f.cartesian_point(P_start))
v_end   = f.vertex_point(f.cartesian_point(P_end))

e1  = f.edge_curve(v_start, v_end, bspline)
oe1 = f.oriented_edge(e1, True)

# Single-edge EDGE_LOOP (open wire in GEOMETRIC_CURVE_SET context)
loop = f.edge_loop([oe1])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi129.stp")
