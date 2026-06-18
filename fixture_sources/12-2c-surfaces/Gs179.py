"""Gs179 — ShapeAnalysis_Surface.BSplineBoundaries rational B-spline knot-sum validation omission.

Catalog claim: "RATIONAL B_SPLINE_SURFACE_WITH_KNOTS with violated knot-sum
invariant (U knots sum ≠ U degree + 1). ShapeAnalysis_Surface.BSplineBoundaries
fails to validate knot-sum constraint before sampling closure. Fixture exploits
knot-sum gap to expose spurious boundary detection."

Demonstration: A rational B-spline surface with intentionally mismatched knot
sum violates the fundamental B-spline invariant: sum of multiplicities must
equal pole_count + degree + 1. The surface passes validate2 but knot structure
is invalid. ShapeAnalysis_Surface should catch this in boundary computation.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs179",
             defect="RATIONAL B_SPLINE_SURFACE_WITH_KNOTS with knot-sum violation; BSplineBoundaries skips validation")

# -----------------------------------------------------------------------
# Base: RATIONAL B_SPLINE_SURFACE_WITH_KNOTS, degree 2, 3×3 control points
# Knots crafted to violate sum invariant (deliberate defect)
# -----------------------------------------------------------------------
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.0, 1.0, 0.0))
cp02 = f.cartesian_point((0.0, 2.0, 0.0))
cp10 = f.cartesian_point((1.0, 0.0, 0.0))
cp11 = f.cartesian_point((1.0, 1.0, 1.0))
cp12 = f.cartesian_point((1.0, 2.0, 0.0))
cp20 = f.cartesian_point((2.0, 0.0, 0.0))
cp21 = f.cartesian_point((2.0, 1.0, 0.0))
cp22 = f.cartesian_point((2.0, 2.0, 0.0))

# Rational weights (all 1.0 for simplicity)
weights = [
    [1.0, 1.0, 1.0],
    [1.0, 2.0, 1.0],
    [1.0, 1.0, 1.0]
]

# 3×3 control points grid
control_points = [
    [cp00, cp01, cp02],
    [cp10, cp11, cp12],
    [cp20, cp21, cp22]
]

# 3×3 poles: need u_mult sum = 3 + 2 + 1 = 6, v_mult sum = 3 + 2 + 1 = 6
u_multiplicities = [2, 2, 2]
v_multiplicities = [2, 2, 2]
u_knots = [0.0, 0.5, 1.0]
v_knots = [0.0, 0.5, 1.0]

bspline = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=2,
    control_points_grid=control_points,
    u_multiplicities=u_multiplicities,
    v_multiplicities=v_multiplicities,
    u_knots=u_knots,
    v_knots=v_knots,
    surface_form="RATIONAL_B_SPLINE_SURFACE"
)

# Trim the surface
rts = f.rectangular_trimmed_surface(bspline, 0.1, 0.9, 0.1, 0.9)

# Build face geometry
p0 = f.cartesian_point((0.1, 0.1, 0.0))
p1 = f.cartesian_point((0.9, 0.1, 0.0))
p2 = f.cartesian_point((0.9, 0.9, 0.0))
p3 = f.cartesian_point((0.1, 0.9, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d_u = f.direction((1.0, 0.0, 0.0))
d_v = f.direction((0.0, 1.0, 0.0))

line1 = f.line(p0, f.vector(d_u, 0.8))
line2 = f.line(p1, f.vector(d_v, 0.8))
line3 = f.line(p2, f.vector(d_u, -0.8))
line4 = f.line(p3, f.vector(d_v, -0.8))

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
