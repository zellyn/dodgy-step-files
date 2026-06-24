"""Me1083 — remove_degenerate_faces null_edge_face_detection: cascading degeneracy after edge removal triggers is_degenerate_triangle_face check on adjacent faces (Branch 4).

CGAL PMP `PMP.remove_degenerate_faces` Branch 4 (*null_edge_face_detection*) @ line 2078:
  'if (is_degenerate_triangle_face(adj_fd, tmesh, vpm, gt)) faces_to_visit.push(adj_fd);'
  — during the repair pass, after collapsing a degenerate edge, the faces adjacent to
  the removed edge are checked for induced degeneracy. If an adjacent face is now also
  degenerate (because its three vertices became collinear after the edge operation), it
  is pushed onto faces_to_visit to be processed in a subsequent iteration.

Defect pattern: a near-degenerate fan of triangles where one initially-degenerate
  triangle shares an edge with a second triangle that becomes degenerate after the
  first is repaired. The adjacent face gains collinearity because two of its three
  vertices are brought to the same position by the edge-removal operation.

Geometry (cascading degeneracy via shared edge):
  v0=(0,0,0), v1=(1,0,0), v2=(1,0,0) — v1 and v2 at same position (zero-length edge)
  v3=(2,0,0) — extends the collinear chain
  t0=(v0,v1,v2): zero-length edge (v1,v2) → immediately degenerate
  t1=(v0,v2,v3): shares edge (v0,v2) with t0; after v1==v2 collapse, t1 vertices
                 become (v0,v1/v2,v3) all collinear on x-axis → induced degenerate
  t2=(v4,v5,v6): clean control triangle; area > 0 (non-degenerate)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1083",
    title="remove_degenerate_faces null_edge_face_detection: zero-length edge in t0 induces collinear degeneracy in adjacent t1 after edge collapse; is_degenerate_triangle_face(adj_fd) fires (Branch 4)",
    defect_class="degenerate_triangle",
)

# Primary degenerate triangle: v1 and v2 are at identical coordinates.
# The zero-length edge (v1,v2) makes t0 immediately degenerate.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — coincides with v2
v2 = m.vertex(1.0, 0.0, 0.0)  # 2 — coincides with v1 (zero-length edge)
v3 = m.vertex(2.0, 0.0, 0.0)  # 3 — right end

t0 = m.triangle(v0, v1, v2)   # 0: zero-length edge (v1,v2); area=0 — primary degenerate face
t1 = m.triangle(v0, v2, v3)   # 1: shares (v0,v2) with t0; after v1==v2 collapse, t1
                                #    becomes (v0, v1≡v2, v3) all on x-axis → cascading degeneracy

# Clean control triangle at a separate location.
v4 = m.vertex(5.0, 0.0, 0.0)  # 4
v5 = m.vertex(6.0, 0.0, 0.0)  # 5
v6 = m.vertex(5.5, 1.0, 0.0)  # 6 — apex ensures positive area
t2 = m.triangle(v4, v5, v6)   # 2: clean, non-degenerate control

# t0 has a zero-length edge (v1, v2) → area = 0.
m.assert_triangle_area_lt(t0, 1e-12)

# v1 and v2 are coincident → zero-length degenerate edge.
m.assert_vertex_pair_distance_lt(v1, v2, 1e-12)

# t1 is collinear after collapse: v0=(0,0,0), v2=(1,0,0), v3=(2,0,0) → area = 0.
m.assert_triangle_area_lt(t1, 1e-12)

# The shared edge (v0,v2) between t0 and t1 is the cascade path.
m.assert_edge_shared(v0, v2, 2)
