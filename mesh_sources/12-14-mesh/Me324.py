"""Me324 — with_third_points_triangle_validity_check: Is_not_degenerate_triangle rejects zero-area candidate (Branch 5).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 5 (*triangle_validity_check*) @ line 748:
  'Is_not_degenerate_triangle is_not_degenerate;'
  'Is_valid_compose<Is_not_degenerate_triangle, visitor_type> is_valid(is_not_degenerate, visitor);'
  The degenerate-triangle predicate is combined with the visitor into a single
  Is_valid_compose functor.  A candidate triangulation that would produce a
  zero-area triangle is rejected by this combined check.

Defect pattern: a collinear boundary (3 co-linear points). Any triangle
  formed by 3 collinear points is degenerate (zero area), so Is_not_degenerate
  fires on the only candidate and the triangulation fails to fill it.

Geometry: three collinear vertices along the x-axis.
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — strictly collinear.
  One triangle t0=(v0,v1,v2) with zero area.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me324",
             title="with_third_points_triangle_validity_check: Is_not_degenerate_triangle rejects zero-area candidate (Branch 5)",
             defect_class="degenerate_triangle")

# Three collinear vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2

# Degenerate triangle (zero area — collinear points).
t0 = m.triangle(v0, v1, v2)   # 0

# All edges incident on exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Triangle has zero area — is rejected by Is_not_degenerate_triangle.
m.assert_triangle_area_lt(t0, 1e-12)

# Euler: V=3, E=3, F=1, chi=1.
m.assert_euler_characteristic(3, 3, 1, 1)
