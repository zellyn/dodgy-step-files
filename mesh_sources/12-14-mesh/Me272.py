"""Me272 — autorefine_triangle_soup: intersection-point-count-cases switch (Branch 3).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 3 @ line 1127:
  'switch(nbi)' — after computing the intersection between two triangles, the
  code switches on the count nbi of intersection points to dispatch the correct
  sub-triangle insertion strategy.

The switch statement is the central dispatch point: case 1 (single point touch),
case 2 (segment intersection), and default (polygon/coplanar intersection with 3+
points) all branch here. This fixture establishes the count-dispatch pattern using
a single-point vertex touch (nbi == 1), which takes the minimal branch.

Geometry: triangle 0 and triangle 1 share exactly one vertex (v2 == v3), so their
intersection is a single point. The autorefine pass sees nbi = 1 and takes case 1.

Keywords: nbi, switch(nbi), case 1:, add_point<1>, add_point<2>.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me272",
             title="autorefine_triangle_soup intersection-point-count switch: nbi=1 vertex touch",
             defect_class="autorefine_single_point_touch")

# Triangle 0: left triangle.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — shared touch point

# Triangle 1: right triangle touching t0 at v2 only.
# v3 is distinct from all t0 vertices, but v2 == "touch point".
# We place t1 so its vertex v3 coincides with v2 (index 2 = same position).
v3 = m.vertex(0.5, 1.0, 0.0)   # 3 — same position as v2: single-point intersection
v4 = m.vertex(1.5, 1.0, 0.0)   # 4
v5 = m.vertex(1.0, 2.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v3, v4, v5)   # 1

# v2 and v3 are at the same position: a near-coincident vertex pair (distance = 0).
m.assert_vertex_pair_distance_lt(v2, v3, 1e-12)

# The triangles are non-intersecting in the interior (touch at single point only).
# The Möller test does not count a shared vertex as a crossing with positive length.
m.assert_triangles_do_not_intersect(t0, t1)
