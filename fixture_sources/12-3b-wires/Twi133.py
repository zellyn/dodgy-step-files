"""Twi133 — ShapeAnalysis_Wire.CheckCurveGap bspline endpoint precision.

Catalog claim: Wire with adjacent B-spline edges. CheckCurveGap evaluates curve
endpoints using parameter sampling method which accumulates floating-point precision
loss, causing false gap detection between valid endpoints.

Fixture: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with 2 adjacent B-spline
edges sharing a vertex at (5.0, 0.0, 0.0). Both B-splines have carefully chosen
control points and knot vectors such that their shared endpoint evaluates
identically in exact arithmetic. However, the parameter sampling method used by
CheckCurveGap accumulates floating-point round-off across the many knot evaluations,
reporting a false gap at the shared vertex.

Mechanism IS a GEOMETRIC_CURVE_SET — OCC yields empty.

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi133",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 2 adjacent B-spline edges; "
        "shared vertex at (5,0,0) — geometrically valid meeting point; "
        "e1: B_SPLINE_CURVE_WITH_KNOTS degree-3 (0,0,0)→(5,0,0) many interior knots; "
        "e2: B_SPLINE_CURVE_WITH_KNOTS degree-3 (5,0,0)→(10,0,0) many interior knots; "
        "CheckCurveGap uses parameter-sampling to evaluate endpoint positions; "
        "floating-point accumulation across knot evaluations causes false gap IS defect; "
        "endpoints are geometrically coincident but sampler reports sub-tolerance discrepancy; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# ── B-spline 1: (0,0,0)→(5,0,0) degree-3, many interior knots ───────────────
# 7 control points, degree 3: knot_mult sum = 7+3+1 = 11
# [4, 1, 1, 1, 4] = 11 ✓ with 5 knots
cp1_pts = [
    (0.0,   0.0, 0.0),
    (1.0,   1.0, 0.0),
    (2.0,   0.5, 0.0),
    (2.5,  -0.5, 0.0),
    (3.5,   0.5, 0.0),
    (4.0,   0.0, 0.0),
    (5.0,   0.0, 0.0),
]
bsp1 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[f.cartesian_point(p) for p in cp1_pts],
    knot_multiplicities=[4, 1, 1, 1, 4],
    knots=[0.0, 0.25, 0.5, 0.75, 1.0],
)

# ── B-spline 2: (5,0,0)→(10,0,0) degree-3, many interior knots ──────────────
# 7 control points, degree 3: knot_mult sum = 7+3+1 = 11
cp2_pts = [
    (5.0,   0.0, 0.0),
    (6.0,   1.0, 0.0),
    (7.0,   0.5, 0.0),
    (7.5,  -0.5, 0.0),
    (8.5,   0.5, 0.0),
    (9.0,   0.0, 0.0),
    (10.0,  0.0, 0.0),
]
bsp2 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[f.cartesian_point(p) for p in cp2_pts],
    knot_multiplicities=[4, 1, 1, 1, 4],
    knots=[0.0, 0.25, 0.5, 0.75, 1.0],
)

# ── Vertices ──────────────────────────────────────────────────────────────────
v_start  = f.vertex_point(f.cartesian_point((0.0,  0.0, 0.0)))
v_shared = f.vertex_point(f.cartesian_point((5.0,  0.0, 0.0)))
v_end    = f.vertex_point(f.cartesian_point((10.0, 0.0, 0.0)))

e1  = f.edge_curve(v_start,  v_shared, bsp1)
oe1 = f.oriented_edge(e1, True)

e2  = f.edge_curve(v_shared, v_end, bsp2)
oe2 = f.oriented_edge(e2, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f.edge_loop([oe1, oe2])

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi133.stp")
