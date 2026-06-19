"""Gn157 — Rational B-spline with extreme weight ratio (1e4).

Catalog claim: weight ratio 10000:1 spans 4 orders of magnitude, escalating
condition number in rational basis-function evaluation and creating numerical
instability in homogeneous-coordinate normalization.

Previous fixture had a structurally invalid RATIONAL_B_SPLINE_SURFACE(...)
followed by an attempted B_SPLINE_SURFACE_WITH_KNOTS(#100, ...) referencing
the rational entity as its first arg — which is malformed. This regen uses
the proper rational_b_spline_surface_with_knots complex-instance form with
weights (1.0, 10000.0, 1.0, 1.0, 1.0, 1.0).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn157",
             defect="rational B-spline surface with extreme weight ratio")

# 3 U × 2 V grid.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.5), (1.0, 1.0, 1.0)],
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0)],
]]

# Weight at (U=0, V=1) = 10000.0; all others = 1.0.
# Ratio max:min = 10000:1 → ill-conditioned rational evaluation.
weights = [
    [1.0, 10000.0],
    [1.0, 1.0],
    [1.0, 1.0],
]

surf = f.rational_b_spline_surface_with_knots(
    u_degree=2, v_degree=1,
    control_points_grid=pts,
    weights_grid=weights,
    u_multiplicities=[3, 3],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
)

# Minimal face boundary for consumability.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((2.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 2.0)
ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
