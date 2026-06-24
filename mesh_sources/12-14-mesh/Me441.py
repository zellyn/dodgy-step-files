"""Me441 — removeSmallestComponents_adjacent_t1: BFS expands across t->t1() neighbor.

Catalog claim: checkAndRepair::removeSmallestComponents@L780 Branch 2
(*ADJACENT_TRIANGLE_T1*) fires during BFS flood-fill when the t1 neighbor of the
current triangle is non-null and not yet visited (IS_BIT(t1,5) == 0). The BFS
appends t1 to the todo list. This fixture provides a two-component mesh where
the t1 adjacency path is exercised within the larger component.

Geometric design: Component A is a 4-triangle strip where interior edges are
each shared by exactly 2 triangles (t1 adjacency BFS path). Component B is a
single isolated triangle far away. The BFS over component A must cross at least
one t1 adjacency to enumerate all 4 triangles; component B remains unreachable.

Source: MeshFix checkAndRepair::removeSmallestComponents@L780 Branch 2
(*ADJACENT_TRIANGLE_T1*): `if (t1 != NULL && !IS_BIT(t1, 5)) { l.appendHead(t1); SET_BIT(t1,5); }`
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me441",
             title="removeSmallestComponents adjacent_t1: BFS visits t1 neighbor; 2-component mesh with 4+1 triangles",
             defect_class="disconnected_components")

# Component A: 4-triangle strip sharing interior edges (exercises t1 BFS path).
# v0-v1-v2-v3-v4 form a strip of 4 triangles.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(1.5, 1.0, 0.0)
v4 = m.vertex(2.0, 0.0, 0.0)
v5 = m.vertex(2.5, 1.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # face 0
t1 = m.triangle(v1, v3, v2)   # face 1: shares edge (v1,v2) with t0
t2 = m.triangle(v1, v4, v3)   # face 2: shares edge (v1,v3) with t1
t3 = m.triangle(v3, v4, v5)   # face 3: shares edge (v3,v4) with t2

# Component B: single isolated triangle far from component A.
v6 = m.vertex(10.0, 10.0, 0.0)
v7 = m.vertex(11.0, 10.0, 0.0)
v8 = m.vertex(10.0, 11.0, 0.0)
t4 = m.triangle(v6, v7, v8)   # face 4: isolated

# Assert: interior shared edges of component A (BFS t1 path evidence).
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(v3, v4, 2)   # shared by t2 and t3

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: boundary edges of component B are single-triangle.
m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v7, v8, 1)
m.assert_edge_shared(v6, v8, 1)
