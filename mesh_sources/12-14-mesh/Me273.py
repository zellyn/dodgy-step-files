"""Me273 — autorefine_triangle_soup: single-point-containment-branch (Branch 4).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 4 @ line 1130:
  'case 1:' — when nbi == 1 the intersection is a single point; the repair adds
  this point to both triangles via add_point<1> and add_point<2> so each can be
  refined to include the intersection vertex.

The classic input pattern: a vertex of one triangle lies exactly on the edge of
another triangle (vertex-on-edge touch). The intersection of the two triangles is
exactly one point, so nbi == 1. Branch 4 adds this point to both triangle's
point-insertion lists.

Geometry: triangle 0 is a base triangle. Triangle 1 has one vertex (v3) that lies
exactly on the boundary edge (v0, v1) of triangle 0, midway along it. The other
two vertices of t1 are in a different plane. The intersection is the single point v3.

The mesh is technically a T-junction (T-vertex): t1's vertex touches t0's edge
mid-span, forcing autorefine to insert v3 into t0's edge as an insertion point.

Keywords: case 1:, add_point<1>, add_point<2>, single point containment.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me273",
             title="autorefine_triangle_soup single-point containment: T-vertex on edge → case 1",
             defect_class="autorefine_vertex_on_edge_touch")

# Triangle 0: base triangle.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2

# Triangle 1: v3 lies exactly at midpoint of edge (v0, v1) = (1, 0, 0).
# v4 and v5 are on the other side (below z=0) so the triangles touch at v3 only.
v3 = m.vertex(1.0, 0.0, 0.0)   # 3 — midpoint of v0-v1 edge
v4 = m.vertex(0.5, -1.0, 0.0)  # 4
v5 = m.vertex(1.5, -1.0, 0.0)  # 5

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v3, v4, v5)   # 1

# v3 lies exactly on edge (v0, v1): a T-junction.
m.assert_vertex_on_edge(v3, v0, v1)

# t0's edges do not share any edge with t1 (open soup).
m.assert_edge_shared(v0, v1, 1)  # boundary of t0
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)  # boundary of t1
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)
