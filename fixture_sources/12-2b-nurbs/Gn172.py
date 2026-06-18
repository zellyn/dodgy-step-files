"""Gn172 — B-spline with interior knot multiplicity equal to degree (C0 discontinuity).

Catalog claim: "Interior knot with multiplicity == degree creates C0 (positional)
discontinuity. ShapeAnalysis_Surface recognizes this as closure-blocking, but
ShapeUpgrade_SplitSurfaceContinuity may fail to properly subdivide or detect
the defect, leaving C0 junctions unhealed in multi-pass tolerance escalation."

Demonstration: A degree-3 B-spline curve with 5 control points and an interior
knot whose multiplicity equals 3 (the degree). By Bezier continuity theory,
this creates a sharp corner (C0 only, not C1).

Knot vector [0,0,0,0, 0.5, 1,1,1,1] with multiplicities (4,1,4) = 9
Degree 3, 5 poles → 5 + 3 + 1 = 9. The knot at 0.5 has multiplicity 1.
Revised: [0,0,0,0, 0.5, 0.5, 0.5, 1,1,1,1] with mults (4,3,4) = 11
But 5 + 3 + 1 = 9, not 11. Fix: 4 poles, degree 3 → 4 + 3 + 1 = 8
Knot [0,0,0,0, 0.5,0.5,0.5, 1,1,1,1] has 8 multiplicities. But that's (4,3,4) = 11.
Simpler: 5 poles, degree 2 → 5 + 2 + 1 = 8
[0,0,0, 0.5,0.5, 1,1,1] mults (3,2,3) = 8. Multiplicity 2 at interior is less than degree 2.

Use degree 2, interior knot with mult 2: [0,0,0, 0.5,0.5, 1,1,1]
With 5 poles, sum = 3 + 2 + 3 = 8 = 5 + 2 + 1 ✓
Multiplicity 2 == degree 2 at interior → C0 discontinuity.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn172",
             defect="B-spline with interior knot multiplicity == degree: C0 discontinuity trigger")

# 5 control points arranged to show the corner
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((2.0, 1.0, 0.0))  # Middle pole pulls toward y=1
p3 = f.cartesian_point((3.0, 0.0, 0.0))
p4 = f.cartesian_point((4.0, 0.0, 0.0))

# Degree 2: 5 poles + 2 + 1 = 8 knot-mult sum
# Interior knot at 0.5 with multiplicity 2 (== degree): creates C0
u_knots = [0.0, 0.5, 1.0]
u_mults = [3, 2, 3]  # 3 + 2 + 3 = 8 ✓

bspl_curve = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[p0, p1, p2, p3, p4],
    knot_multiplicities=u_mults,
    knots=u_knots,
    curve_form="UNSPECIFIED",
    closed=False
)

# Create a simple face to contextualize the curve
loop = f.closed_polyline_loop([
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.cartesian_point((4.0, 0.0, 0.0)),
    f.cartesian_point((4.0, 1.0, 0.0)),
    f.cartesian_point((0.0, 1.0, 0.0))
])
fob = f.face_outer_bound(loop)
plane = f.plane((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
