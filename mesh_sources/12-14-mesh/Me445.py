"""Me445 — removeSmallestComponents_non_largest: non-biggest components marked for removal.

Catalog claim: checkAndRepair::removeSmallestComponents@L780 Branch 6
(*NON_LARGEST_COMPONENT*) fires when iterating over all components after
identifying `biggest`. For each component that is not the largest
(`((List *)n->data) != biggest`), the triangles in that component are marked
for unlinking and its edges/vertices are nullified. This fixture uses two clearly
different-sized components so Branch 6 fires for the smaller one.

Geometric design: Two disconnected components:
  - Component A: 1 small triangle (will be marked non-largest → Branch 6 fires)
  - Component B: 5-triangle patch (is the `biggest`; is NOT marked)

The size differential (1 vs 5 triangles) makes it unambiguous which is biggest.

Source: MeshFix checkAndRepair::removeSmallestComponents@L780 Branch 6
(*NON_LARGEST_COMPONENT*): `if (((List *)n->data) != biggest) { ... unlink ... }`
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me445",
             title="removeSmallestComponents non_largest: 2-component mesh (1 vs 5 triangles); smaller component marked for removal",
             defect_class="disconnected_components")

# Component A: 1 small isolated triangle (the non-largest; Branch 6 fires for this).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(0.5, 0.0, 0.0)
v2 = m.vertex(0.0, 0.5, 0.0)
t0 = m.triangle(v0, v1, v2)   # face 0: the small/non-largest component

# Component B: 5-triangle fan (the `biggest` component).
v3 = m.vertex(10.0, 0.0, 0.0)   # apex
v4 = m.vertex(12.0, 0.0, 0.0)
v5 = m.vertex(11.5, 1.5, 0.0)
v6 = m.vertex(10.5, 2.0, 0.0)
v7 = m.vertex(9.5, 1.5, 0.0)
v8 = m.vertex(8.5, 0.5, 0.0)
t1 = m.triangle(v3, v4, v5)   # face 1: fan petal 1
t2 = m.triangle(v3, v5, v6)   # face 2: fan petal 2; shares (v3,v5) with t1
t3 = m.triangle(v3, v6, v7)   # face 3: fan petal 3; shares (v3,v6) with t2
t4 = m.triangle(v3, v7, v8)   # face 4: fan petal 4; shares (v3,v7) with t3
t5 = m.triangle(v3, v8, v4)   # face 5: fan petal 5; shares (v3,v8) with t4; closes fan

# Assert: components are disconnected.
m.assert_triangle_not_reachable_from(t1, t0)   # B disconnected from A

# Assert: the small component A has a single boundary edge set.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Assert: interior fan edges of B are each shared by 2 triangles.
m.assert_edge_shared(v3, v5, 2)   # between t1 and t2
m.assert_edge_shared(v3, v6, 2)   # between t2 and t3
m.assert_edge_shared(v3, v7, 2)   # between t3 and t4
m.assert_edge_shared(v3, v8, 2)   # between t4 and t5

# Assert: cross-component vertices share no triangle (confirms disjoint topology).
m.assert_vertex_pair_no_shared_triangle(v0, v3)
