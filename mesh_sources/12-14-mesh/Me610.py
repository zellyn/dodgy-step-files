"""Me610 — is_cap_triangle_face degenerate_edge: first edge has zero squared length.

CGAL PMP `PMP.is_cap_triangle_face` Branch 1 (*degenerate_edge*) @ line 460:
  'if(is_zero(sq_lengths[0]))'
  — before cap detection the function computes squared edge lengths for all
  three edges. If the first edge (p, q) has zero squared length (coincident
  endpoints), the triangle is degenerate and the early-exit branch fires.
  No cap classification is performed.

Defect pattern: a single triangle (v0, v1, v2) where v0 and v1 occupy the
  same coordinate (0,0,0). The squared length of edge (v0, v1) is exactly
  zero, triggering Branch 1. A second valid triangle is included as context
  to make the mesh non-trivial.

Geometry:
  v0=(0,0,0), v1=(0,0,0) [coincident with v0], v2=(1,0,0), v3=(0,1,0), v4=(1,1,0)
  t0 = (v0, v1, v2) — degenerate; edge (v0,v1) has zero length
  t1 = (v2, v3, v4) — valid triangle (context)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me610",
    title="is_cap_triangle_face degenerate_edge: first edge (v0,v1) has zero squared length; coincident endpoints trigger early-exit Branch 1",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — coincident with v1
v1 = m.vertex(0.0, 0.0, 0.0)  # 1 — coincident with v0 (zero-length first edge)
v2 = m.vertex(1.0, 0.0, 0.0)  # 2
v3 = m.vertex(0.0, 1.0, 0.0)  # 3 — context triangle vertex
v4 = m.vertex(1.0, 1.0, 0.0)  # 4 — context triangle vertex

# t0: degenerate triangle — edge (v0, v1) has zero length.
t0 = m.triangle(v0, v1, v2)  # 0 — degenerate; sq_lengths[0] = dist(v0,v1)^2 = 0
# t1: valid context triangle.
t1 = m.triangle(v2, v3, v4)  # 1 — valid triangle

# v0 and v1 are coincident: zero-length first edge → Branch 1 fires.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-12)

# Degenerate triangle t0 has zero area (two vertices coincide).
m.assert_triangle_area_lt(t0, 1e-12)
