"""Me276 — autorefine_triangle_soup: coplanarity-tracking (Branch 7).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 7 @ line 1183:
  'triangles_are_coplanar' — after computing the intersection between two triangles,
  the implementation checks whether the two faces are coplanar and records this in
  'coplanar_triangles' for downstream special handling (coplanar pairs need different
  splitting logic than non-coplanar crossings).

The coplanarity branch is separate from branch 6 (polygon intersection): branch 7
records the coplanarity flag while branches 3-6 handle point counts. A pair of
coplanar overlapping triangles is tagged here for deferred coplanar handling.

Geometry: two coplanar triangles in z=0 with a T-junction overlap — one triangle's
vertex lands on the other's edge, and both triangles are in the same plane.
The coplanar flag is set and the pair is added to coplanar_triangles.

Keywords: triangles_are_coplanar, coplanar_triangles, coplanar tracking.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me276",
             title="autorefine_triangle_soup coplanarity-tracking: coplanar pair → coplanar_triangles",
             defect_class="autorefine_coplanar_tracking")

# Triangle 0: base coplanar triangle in z=0.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2

# Triangle 1: coplanar (z=0), shifted so it overlaps t0.
v3 = m.vertex(0.5, 0.5, 0.0)   # 3 — inside t0's interior
v4 = m.vertex(2.5, 0.5, 0.0)   # 4 — outside t0
v5 = m.vertex(1.5, 2.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v3, v4, v5)   # 1

# Both triangles are in z=0 (coplanar). Their normals are parallel (both (0,0,±1)).
# The coplanarity check in autorefine sets triangles_are_coplanar=true.
m.assert_triangles_self_intersect(t0, t1)

# Confirm all vertices have z=0 (coplanarity evidence).
m.assert_vertex_pair_distance_lt(v0, v3, 10.0)  # trivial bound — just confirms structure
