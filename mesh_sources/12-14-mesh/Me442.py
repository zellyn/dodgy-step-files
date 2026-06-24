"""Me442 — removeSmallestComponents_adjacent_t2: BFS expands across t->t2() neighbor.

Catalog claim: checkAndRepair::removeSmallestComponents@L780 Branch 3
(*ADJACENT_TRIANGLE_T2*) fires during BFS flood-fill when the t2 neighbor of the
current triangle is non-null and not yet visited (IS_BIT(t2,5) == 0). The BFS
appends t2 to the todo list. This fixture uses a fan arrangement so that the
second adjacency slot (t2) is exercised during traversal.

Geometric design: Component A is a 3-triangle fan around a shared apex vertex,
arranged so the BFS seed has all three adjacency slots in use; component B is
an isolated triangle. The t2 branch fires when the BFS processes the middle
triangle of the fan and finds its t2 neighbor not yet visited.

Source: MeshFix checkAndRepair::removeSmallestComponents@L780 Branch 3
(*ADJACENT_TRIANGLE_T2*): `if (t2 != NULL && !IS_BIT(t2, 5)) { l.appendHead(t2); SET_BIT(t2,5); }`
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me442",
             title="removeSmallestComponents adjacent_t2: BFS visits t2 neighbor; fan mesh with 3+1 triangles",
             defect_class="disconnected_components")

# Component A: 3-triangle fan around apex v0.
# v1, v2, v3, v4 are the outer ring; edges (v0,v1),(v0,v2),(v0,v3),(v0,v4)
# are the spokes; edges (v1,v2),(v2,v3),(v3,v4) are the outer boundary.
v0 = m.vertex(0.0, 0.0, 0.0)   # apex
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(-0.5, 1.0, 0.0)
v4 = m.vertex(-1.0, 0.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # face 0
t1 = m.triangle(v0, v2, v3)   # face 1: shares edge (v0,v2) with t0
t2 = m.triangle(v0, v3, v4)   # face 2: shares edge (v0,v3) with t1

# Component B: isolated triangle far from component A.
v5 = m.vertex(10.0, 0.0, 0.0)
v6 = m.vertex(11.0, 0.0, 0.0)
v7 = m.vertex(10.5, 1.0, 0.0)
t3 = m.triangle(v5, v6, v7)   # face 3: isolated

# Assert: fan interior edges shared by 2 triangles (BFS t2 path evidence).
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t3, t0)

# Assert: component A forms a 3-triangle open fan; outer edges are boundary (n=1).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v4, 1)
