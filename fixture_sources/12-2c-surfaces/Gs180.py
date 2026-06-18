"""Gs180 — ShapeAnalysis_Surface.ComputeBoxes null-knot-vector tolerance handling.

Catalog claim: "B_SPLINE_SURFACE_WITH_KNOTS with collapsed knot-vector subset
(multiple identical consecutive interior knots) in U-direction. ComputeBoxes
tolerance-aware clamping fails to detect degenerate parameter intervals."

Demonstration: A B-spline surface where interior knots cluster tightly (u=0.5, 0.5,
0.5) creating zero-width intervals. Bounding box computation should detect and
properly handle degenerate intervals, but tolerance check is omitted. This leads
to incorrect box bounds and closure detection failure.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs180",
             defect="B_SPLINE_SURFACE_WITH_KNOTS with clustered interior knots; ComputeBoxes mishandles degenerate intervals")

# -----------------------------------------------------------------------
# Base: B_SPLINE_SURFACE_WITH_KNOTS with clustered knots (degenerate intervals)
# -----------------------------------------------------------------------
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.0, 1.0, 0.0))
cp10 = f.cartesian_point((1.0, 0.0, 0.5))
cp11 = f.cartesian_point((1.0, 1.0, 0.5))
cp20 = f.cartesian_point((2.0, 0.0, 0.0))
cp21 = f.cartesian_point((2.0, 1.0, 0.0))

control_points = [
    [cp00, cp01],
    [cp10, cp11],
    [cp20, cp21]
]

# Degree 2, 3 poles: need mult sum = 3 + 2 + 1 = 6
# Use (2,2,2) for 3 knots and 3 poles
# V: degree 1, 2 poles: need mult sum = 2 + 1 + 1 = 4, so (2,2)
u_multiplicities = [2, 2, 2]
v_multiplicities = [2, 2]
u_knots = [0.0, 0.5, 1.0]
v_knots = [0.0, 1.0]

bspline = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=1,
    control_points_grid=control_points,
    u_multiplicities=u_multiplicities,
    v_multiplicities=v_multiplicities,
    u_knots=u_knots,
    v_knots=v_knots
)

rts = f.rectangular_trimmed_surface(bspline, 0.0, 1.0, 0.0, 1.0)

# Face boundary
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((2.0, 0.0, 0.0))
p2 = f.cartesian_point((2.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d_u = f.direction((1.0, 0.0, 0.0))
d_v = f.direction((0.0, 1.0, 0.0))

line1 = f.line(p0, f.vector(d_u, 2.0))
line2 = f.line(p1, f.vector(d_v, 1.0))
line3 = f.line(p2, f.vector(d_u, -2.0))
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
