"""Me029 — degenerate_edge_in_face: triangle with a zero-length edge (Branch 6).

Catalog claim: triangle 1 has a zero-length edge — vertices 3 and 4 occupy
the exact same position (0.5, 1.0, 0.0). The degenerate edge is the pair
(v3, v4). CGAL PMP.remove_degenerate_faces detects faces containing
is_degenerate_edge and invokes remove_degenerate_edges before attempting
the face-removal Euler operators.

Source: CGAL PMP.remove_degenerate_faces Branch 6 @ line 2170 —
*degenerate-edge-in-degenerate-face*: face has a zero-length edge;
remove_degenerate_edges is called first before face removal.

Defect carrier: triangle 1 = (v3, v4, v5) where v3 == v4 geometrically
(same coordinates, distinct vertex indices). The edge (v3, v4) has length
exactly 0. The triangle collapses to a line segment from v3/v4 to v5.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me029",
             title="degenerate edge in face: triangle with a zero-length edge (v3==v4 coordinates)",
             defect_class="degenerate_triangle")

# Clean control triangle.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # face 0: clean

# Triangle with a zero-length edge: v3 and v4 are at the same coordinates.
v3 = m.vertex(0.5, 1.0, 0.0)   # index 3
v4 = m.vertex(0.5, 1.0, 0.0)   # index 4 — same coords as v3 → zero-length edge
v5 = m.vertex(2.0, 0.0, 0.0)   # index 5
t1 = m.triangle(v3, v4, v5)   # face 1: zero-length edge (v3,v4), collapses to segment

# Assert zero area (collapsed triangle).
m.assert_triangle_area_lt(t1, 1e-12)

# Assert the degenerate edge (v3, v4) has distance 0.
m.assert_vertex_pair_distance_lt(v3, v4, 1e-12)
