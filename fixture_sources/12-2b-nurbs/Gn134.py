"""Gn134 — NURBS weight array uniform propagation.

Catalog claim: rational NURBS surface with uniform weights; ConvertSurfaceToBezierBasis
may fail to preserve weight consistency across Bezier patch decomposition, causing
rational-surface metadata loss.

Previous fixture used non-rational B_SPLINE_SURFACE_WITH_KNOTS — no weights
to lose. This regen uses the rational complex-instance form with weights=1.0
in a 3×2 grid, degree 2×1. ConvertSurfaceToBezierBasis splits this into
multiple Bezier patches; the defect is in whether each patch retains the
rational flag.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gn134",
             defect="rational NURBS weight propagation across Bezier conversion")

# 3 U × 2 V grid, uniform weight 1.0.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
    [(1.0, 0.0, 0.5), (1.0, 1.0, 0.5)],
    [(2.0, 0.0, 0.0), (2.0, 1.0, 0.0)],
]]
weights = [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]

# Use rational_b_spline_surface_with_knots from builder.
surf = f.rational_b_spline_surface_with_knots(
    u_degree=2, v_degree=1,
    control_points_grid=pts,
    weights_grid=weights,
    u_multiplicities=[3, 3],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
)

# Minimal face boundary so the fixture is consumable.
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
