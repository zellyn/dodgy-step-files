"""Gs182 — ShapeUpgrade_Surface.SplitContinuity periodic-knot discontinuity mask.

Catalog claim: "PERIODIC B_SPLINE_SURFACE_WITH_KNOTS (pole_list has repeated
first/last pole) with interior C1 discontinuity. SplitContinuity fails to
detect discontinuity across periodic seam (u=0≡u=1)."

Demonstration: A degree-2 periodic B-spline in U with intentional C1 gap at the
seam. The periodic topology (first pole=last pole by construction) bypasses the
seam-detection guard in SplitContinuity, causing the discontinuity to remain
undetected and unsplit.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs182",
             defect="PERIODIC B_SPLINE_SURFACE_WITH_KNOTS with seam C1 discontinuity; SplitContinuity skips seam detection")

# -----------------------------------------------------------------------
# Base: Periodic B_SPLINE_SURFACE_WITH_KNOTS in U (repeating poles at seam)
# -----------------------------------------------------------------------
# Create pole grid where cp00 == cp20 (periodic closure) but with C1 gap
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp10_a = f.cartesian_point((1.0, 0.0, 0.3))  # First version at u=0
cp10_b = f.cartesian_point((1.0, 0.0, 0.5))  # Different Z at u=1 (C1 gap)
cp20 = f.cartesian_point((0.0, 0.0, 0.0))   # Repeating pole

cp01 = f.cartesian_point((0.0, 1.0, 0.0))
cp11_a = f.cartesian_point((1.0, 1.0, 0.3))
cp11_b = f.cartesian_point((1.0, 1.0, 0.5))
cp21 = f.cartesian_point((0.0, 1.0, 0.0))

# Build periodic control points (first=last in U)
control_points = [
    [cp00, cp01],
    [cp10_a, cp11_a],
    [cp10_b, cp11_b],
    [cp20, cp21]
]

# Degree 2, 4 poles: need mult sum = 4 + 2 + 1 = 7
# Use (2,2,2,1) for 4 knots and 4 poles
# V: degree 1, 2 poles: need mult sum = 2 + 1 + 1 = 4, so (2,2)
u_multiplicities = [2, 2, 2, 1]
v_multiplicities = [2, 2]
u_knots = [0.0, 0.33, 0.67, 1.0]
v_knots = [0.0, 1.0]

bspline = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=1,
    control_points_grid=control_points,
    u_multiplicities=u_multiplicities,
    v_multiplicities=v_multiplicities,
    u_knots=u_knots,
    v_knots=v_knots,
    surface_form="B_SPLINE_SURFACE"
)

rts = f.rectangular_trimmed_surface(bspline, 0.0, 1.0, 0.0, 1.0)

# Face boundary
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.3))
p2 = f.cartesian_point((1.0, 1.0, 0.3))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d_u = f.direction((1.0, 0.0, 0.0))
d_v = f.direction((0.0, 1.0, 0.0))

line1 = f.line(p0, f.vector(d_u, 1.0))
line2 = f.line(p1, f.vector(d_v, 1.0))
line3 = f.line(p2, f.vector(d_u, -1.0))
line4 = f.line(p3, f.vector(d_v, -1.0))

e1 = f.edge_curve(v0, v1, line1)
e2 = f.edge_curve(v1, v2, line2)
e3 = f.edge_curve(v2, v3, line3)
e4 = f.edge_curve(v3, v0, line4)

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e4, True)
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], rts)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
