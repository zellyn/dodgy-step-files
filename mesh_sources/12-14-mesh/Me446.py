"""Me446 — removeSmallestComponents_components_removed: topology dirty after removal.

Catalog claim: checkAndRepair::removeSmallestComponents@L780 Branch 7
(*COMPONENTS_REMOVED*) fires after the removal loop when at least one non-largest
component was unlinked (nt > 0). The function sets topology-dirty flags
(`d_boundaries = d_handles = d_shells = 1`) and calls `removeUnlinkedElements()`.
This fixture is the canonical multi-component mesh demonstrating that removal
actually occurred — two components of different sizes where the smaller one is
removed, triggering the post-removal dirty-flag branch.

Geometric design: Two disconnected components:
  - Component A: 2-triangle pair (smaller — gets removed; triggers Branch 7 on exit)
  - Component B: 6-triangle hexagonal patch (largest — survives)

Source: MeshFix checkAndRepair::removeSmallestComponents@L780 Branch 7
(*COMPONENTS_REMOVED*): `if (nt > 0) { d_boundaries = d_handles = d_shells = 1; removeUnlinkedElements(); }`
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me446",
             title="removeSmallestComponents components_removed: 2-component mesh (2 vs 6 triangles); removal triggers dirty-flag branch",
             defect_class="disconnected_components")

# Component A: 2-triangle pair (small component — will be removed).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(1.5, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # face 0: component A triangle 1
t1 = m.triangle(v1, v3, v2)   # face 1: shares edge (v1,v2); component A triangle 2

# Component B: 6-triangle hexagonal fan (largest component — survives).
v4 = m.vertex(10.0, 1.0, 0.0)   # center apex
v5 = m.vertex(12.0, 1.0, 0.0)
v6 = m.vertex(11.5, 2.5, 0.0)
v7 = m.vertex(10.0, 3.0, 0.0)
v8 = m.vertex(8.5,  2.5, 0.0)
v9 = m.vertex(8.0,  1.0, 0.0)
v10 = m.vertex(9.0, -0.5, 0.0)
t2 = m.triangle(v4, v5, v6)    # face 2: fan petal 1
t3 = m.triangle(v4, v6, v7)    # face 3: shares (v4,v6); petal 2
t4 = m.triangle(v4, v7, v8)    # face 4: shares (v4,v7); petal 3
t5 = m.triangle(v4, v8, v9)    # face 5: shares (v4,v8); petal 4
t6 = m.triangle(v4, v9, v10)   # face 6: shares (v4,v9); petal 5
t7 = m.triangle(v4, v10, v5)   # face 7: shares (v4,v10); petal 6 closes fan

# Assert: components are disconnected.
m.assert_triangle_not_reachable_from(t2, t0)   # B disconnected from A

# Assert: shared interior edge within component A.
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1

# Assert: fan interior edges of component B (all shared by 2 triangles).
m.assert_edge_shared(v4, v6, 2)    # between t2 and t3
m.assert_edge_shared(v4, v7, 2)    # between t3 and t4
m.assert_edge_shared(v4, v8, 2)    # between t4 and t5
m.assert_edge_shared(v4, v9, 2)    # between t5 and t6
m.assert_edge_shared(v4, v10, 2)   # between t6 and t7

# Assert: cross-component vertices share no triangle (confirms distinct components).
m.assert_vertex_pair_no_shared_triangle(v0, v4)

# Assert: component A outer edges are single-triangle boundary.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v2, v3, 1)
