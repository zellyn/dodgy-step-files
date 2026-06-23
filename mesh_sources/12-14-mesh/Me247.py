"""Me247 — negligible_size_volume_skip_open: non-closed component skips volume computation.

Catalog claim: CGAL PMP.remove_connected_components_of_negligible_size Branch 8
@ line 279 (*closed-component-volume-skip*) checks `if (!cc_closeness[i])` and
skips the volume computation loop for components already known to be open. This
is the second guard after Branch 7 sets cc_closeness=false — Branch 8 is the
actual skip decision.

Geometric signature: two disconnected components: a closed tetrahedron (component A,
cc_closeness=true → volume computed) and a small open triangle patch at (8,8,8)
(component B, cc_closeness=false → volume computation skipped by Branch 8).
Component B is removed by area criterion instead.

Defect carrier: triangles 0-3 form a closed tetrahedron; triangles 4-5 form
an open two-triangle patch at (8,8,8) with boundary edges.

Source: CGAL PMP.remove_connected_components_of_negligible_size Branch 8 @
line 279 — *closed-component-volume-skip*: `if (!cc_closeness[i]) continue;`
skips volume computation for the open component.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me247",
             title="negligible_size volume_skip_open: non-closed component skips volume via !cc_closeness[i]",
             defect_class="disconnected_components")

# Component A: unit tetrahedron (closed, volume ≈ 0.118).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, 0.333, 0.816)
t0 = m.triangle(v0, v2, v1)   # face 0
t1 = m.triangle(v0, v1, v3)   # face 1
t2 = m.triangle(v1, v2, v3)   # face 2
t3 = m.triangle(v0, v3, v2)   # face 3

# Component B: small open patch at (8,8,8) — two triangles with a shared edge
# and boundary edges around the perimeter.
v4 = m.vertex(8.0,  8.0,  8.0)
v5 = m.vertex(8.02, 8.0,  8.0)
v6 = m.vertex(8.01, 8.02, 8.0)
v7 = m.vertex(8.03, 8.02, 8.0)
t4 = m.triangle(v4, v5, v6)   # face 4: open (3 boundary edges)
t5 = m.triangle(v5, v7, v6)   # face 5: open (shares edge v5-v6 with t4)

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: the internal shared edge of the open patch (incident on 2 triangles).
m.assert_edge_shared(v5, v6, 2)

# Assert the open boundary loop of component B.
m.assert_hole_boundary([v4, v5, v7, v6])

# Assert: boundary edges of component B are incident on only 1 triangle each.
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v4, v6, 1)
