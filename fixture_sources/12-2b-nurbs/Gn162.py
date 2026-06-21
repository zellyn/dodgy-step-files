"""Gn162 — B-spline curve with interior knot over-multiplicity.

Catalog claim: 6-pole curve (degree 3); interior knot at 0.5 has multiplicity
4 (degree+1). Creates geometric discontinuity at interior point. Falsifiable:
knot removal must repair interior clamping that violates smoothness.

Fixture: degree-3 B_SPLINE_CURVE_WITH_KNOTS with 6 control points.
Knot vector: (0, 0.5, 1.0) with multiplicities (4, 4, 4). The interior
knot at 0.5 has multiplicity 4 = degree+1, which is only valid at
boundaries; at an interior knot this creates a C(-1) discontinuity
(the curve breaks at 0.5). OCC loads but may not heal.

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn162",
    defect=(
        "degree-3 B_SPLINE_CURVE_WITH_KNOTS with 6 poles; "
        "interior knot at 0.5 has multiplicity 4 = degree+1 (overclamped); "
        "creates C(-1) geometric discontinuity at t=0.5 (breakpoint); "
        "knot removal must repair; curve splits into two independent cubic segments; "
        "EDGE_CURVE on this curve — loads as shape(1)"
    ),
)

# 6 control points: two cubic Bezier segments meeting at a discontinuity
# Segment 1: pts 0-3 for t in [0, 0.5]
# Segment 2: pts 2-5 for t in [0.5, 1.0] (shared endpoints at break)
cp0 = f.cartesian_point(( 0.0, 0.0, 0.0))
cp1 = f.cartesian_point(( 2.0, 4.0, 0.0))
cp2 = f.cartesian_point(( 4.0, 4.0, 0.0))
cp3 = f.cartesian_point(( 5.0, 0.0, 0.0))  # at break: segment 1 end
cp4 = f.cartesian_point(( 6.0, 4.0, 0.0))  # at break: segment 2 start (discontinuous)
cp5 = f.cartesian_point((10.0, 0.0, 0.0))

# Degree 3, 6 poles: knot sum = 6 + 3 + 1 = 10
# Multiplicities: (4, 4, 4) at knots (0, 0.5, 1.0) → sum = 12 ≠ 10? No.
# Actually for n poles and degree p: num_knots = n + p + 1
# 6 poles, degree 3: num_knots = 10
# Mults (4, 2, 4) would give 10: but we want interior mult=4 (over-multiplicity).
# Mults (4, 4, 4) = 12: that's too many for 6 poles, degree 3.
# For interior over-multiplicity defect with 8 poles, degree 3:
# n=8: num_knots = 12 → (4, 4, 4) works (4+4+4=12). So use 8 poles.

cp0b = f.cartesian_point(( 0.0, 0.0, 0.0))
cp1b = f.cartesian_point(( 1.5, 4.0, 0.0))
cp2b = f.cartesian_point(( 3.0, 4.0, 0.0))
cp3b = f.cartesian_point(( 4.5, 0.0, 0.0))  # segment 1 end (at t=0.5)
cp4b = f.cartesian_point(( 5.5, 4.0, 0.0))  # segment 2 start (at t=0.5, DISCONTINUOUS)
cp5b = f.cartesian_point(( 7.0, 4.0, 0.0))
cp6b = f.cartesian_point(( 8.5, 0.0, 0.0))
cp7b = f.cartesian_point((10.0, 0.0, 0.0))

# 8 poles, degree 3: num_knots = 12 → mults (4,4,4) at (0, 0.5, 1.0) ✓
curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('interior_overclamp',3,"
    f"(#{cp0b.eid},#{cp1b.eid},#{cp2b.eid},#{cp3b.eid},"
    f"#{cp4b.eid},#{cp5b.eid},#{cp6b.eid},#{cp7b.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

v_start = f.vertex_point(cp0b)
v_end   = f.vertex_point(cp7b)
edge = f.edge_curve(v_start, v_end, curve, name="overclamp_edge")
loop = f.edge_loop([f.oriented_edge(edge, True)])

# Host plane
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
