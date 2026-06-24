"""Me923 — keep_largest_output_iterator_presence: output_iterator records removed component faces.

Catalog claim: CGAL PMP.keep_largest_connected_components Branch 4 @
line 421 (*output_iterator_presence*) fires when the caller provides a
non-emptyset output iterator. In that case the function populates the
iterator with the face descriptors of all removed components before (or
while) removing them, enabling the caller to inspect what was discarded.
When an emptyset_iterator is used instead, this branch is skipped.

Geometric signature: two disconnected components — a large 4-triangle closed
tetrahedron (component A) and a small 2-triangle open strip (component B).
With desired_num=1 and a live output_iterator, Branch 4 writes component B's
2 face descriptors into the iterator and then removes them from the mesh.

Defect carrier: triangles 0-3 form a tetrahedron (component A, 4 faces,
closed); triangles 4-5 form a 2-triangle strip at (15,15,0) (component B,
2 faces, open). Branch 4 detects the non-emptyset output iterator and
routes through the iterator-population path before calling
remove_connected_components.

Source: CGAL PMP.keep_largest_connected_components Branch 4 @ line 421 —
*output_iterator_presence*: `if (out != emptyset_iterator) {
  *out++ = f; } remove_connected_components(...)`.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me923",
             title="keep_largest output_iterator_presence: removed component faces recorded via output_iterator",
             defect_class="disconnected_components")

# Component A: tetrahedron (closed, 4 triangles, large component).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, 0.333, 0.816)

t0 = m.triangle(v0, v2, v1)   # face 0 (outward CCW)
t1 = m.triangle(v0, v1, v3)   # face 1
t2 = m.triangle(v1, v2, v3)   # face 2
t3 = m.triangle(v0, v3, v2)   # face 3

# Component B: 2-triangle open strip at (15,15,0) (small component, 2 faces).
# t4 and t5 share edge (v5,v6); 4 boundary edges remain open.
v4 = m.vertex(15.0, 15.0, 0.0)
v5 = m.vertex(16.0, 15.0, 0.0)
v6 = m.vertex(15.5, 16.0, 0.0)
v7 = m.vertex(16.5, 16.0, 0.0)

t4 = m.triangle(v4, v5, v6)   # face 4; shares edge (v5,v6) with t5
t5 = m.triangle(v5, v7, v6)   # face 5

# Assert: component B (t4) is disconnected from component A (t0).
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: tetrahedron (component A) is closed — all interior edges shared by 2 triangles.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Assert: component B has the shared interior edge (v5,v6) shared by exactly 2 triangles.
m.assert_edge_shared(v5, v6, 2)
