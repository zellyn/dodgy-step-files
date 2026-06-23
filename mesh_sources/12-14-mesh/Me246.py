"""Me246 — negligible_size_open_component: border edges mark component as non-closed.

Catalog claim: one connected component has border edges (open boundary), so CGAL
PMP.remove_connected_components_of_negligible_size Branch 7 @ line 265
(*volume-computation-closedness*) detects `is_border(h, tmesh)` for at least one
halfedge in the component and marks it cc_closeness=false. This prevents volume
computation for that component (volume is undefined for open surfaces).

Geometric signature: component A is a closed tetrahedron (no border edges);
component B is an open triangle strip with exposed boundary edges (hole_boundary).
Branch 7 fires for component B, marking it as non-closed.

Defect carrier: triangles 0-3 form a closed tetrahedron (component A). Triangles
4-5 form an open two-triangle strip at (10,10,10) with four boundary edges
(component B, open).

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 7 @
line 265 — *volume-computation-closedness*: `if (is_border(h, tmesh))` →
`cc_closeness[cc_id] = false` for the component.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me246",
             title="negligible_size open_component: border edges detected; cc_closeness=false skips volume",
             defect_class="disconnected_components")

# Component A: closed tetrahedron (no border edges, volume ≈ 0.118).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, 0.333, 0.816)
t0 = m.triangle(v0, v2, v1)   # face 0
t1 = m.triangle(v0, v1, v3)   # face 1
t2 = m.triangle(v1, v2, v3)   # face 2
t3 = m.triangle(v0, v3, v2)   # face 3

# Component B: open two-triangle strip at (10,10,10) with four boundary edges.
# This is an open surface; is_border will fire → cc_closeness[B] = false.
v4 = m.vertex(10.0, 10.0, 10.0)
v5 = m.vertex(11.0, 10.0, 10.0)
v6 = m.vertex(10.5, 11.0, 10.0)
v7 = m.vertex(11.5, 11.0, 10.0)
t4 = m.triangle(v4, v5, v6)   # face 4: open, 3 boundary edges
t5 = m.triangle(v5, v7, v6)   # face 5: open, shares edge (v5,v6) with t4

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: the shared edge in the open strip is incident on exactly 2 triangles.
m.assert_edge_shared(v5, v6, 2)

# Assert: all four boundary edges of the open strip are incident on exactly 1 triangle.
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v4, v6, 1)
m.assert_edge_shared(v5, v7, 1)
m.assert_edge_shared(v6, v7, 1)

# Assert the open boundary loop of component B.
m.assert_hole_boundary([v4, v5, v7, v6])
