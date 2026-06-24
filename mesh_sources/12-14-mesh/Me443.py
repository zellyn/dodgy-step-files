"""Me443 — removeSmallestComponents_adjacent_t3: BFS expands across t->t3() neighbor.

Catalog claim: checkAndRepair::removeSmallestComponents@L780 Branch 4
(*ADJACENT_TRIANGLE_T3*) fires during BFS flood-fill when the t3 neighbor of the
current triangle is non-null and not yet visited (IS_BIT(t3,5) == 0). The BFS
appends t3 to the todo list. In MeshFix, t1/t2/t3 are the three adjacency slots
of a triangle; all three are exercised when a triangle has three shared-edge
neighbors that are unvisited.

Geometric design: Component A is a central triangle fully surrounded by three
adjacent triangles (all three adjacency slots t1, t2, t3 occupied and initially
unvisited). The BFS starts from the center and expands outward to all three
neighbors, exercising the t3 branch for the third adjacency. Component B is
an isolated triangle.

Source: MeshFix checkAndRepair::removeSmallestComponents@L780 Branch 4
(*ADJACENT_TRIANGLE_T3*): `if (t3 != NULL && !IS_BIT(t3, 5)) { l.appendHead(t3); SET_BIT(t3,5); }`
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me443",
             title="removeSmallestComponents adjacent_t3: BFS visits t3 neighbor; central triangle with all 3 neighbors unvisited",
             defect_class="disconnected_components")

# Component A: central triangle (v0,v1,v2) surrounded by 3 outer triangles.
# This gives the BFS seed all three adjacency slots filled (t1, t2, t3 non-null).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(2.0, 0.0, 0.0)
v2 = m.vertex(1.0, 2.0, 0.0)
# Outer triangle A: shares edge (v0,v1)
v3 = m.vertex(1.0, -2.0, 0.0)
# Outer triangle B: shares edge (v1,v2)
v4 = m.vertex(3.0, 1.5, 0.0)
# Outer triangle C: shares edge (v0,v2)
v5 = m.vertex(-1.0, 1.5, 0.0)

t_center = m.triangle(v0, v1, v2)   # face 0: the BFS seed
t_n1 = m.triangle(v1, v0, v3)       # face 1: outer neighbor across (v0,v1) — t1 slot
t_n2 = m.triangle(v2, v1, v4)       # face 2: outer neighbor across (v1,v2) — t2 slot
t_n3 = m.triangle(v0, v2, v5)       # face 3: outer neighbor across (v0,v2) — t3 slot

# Component B: isolated triangle far from component A.
v6 = m.vertex(10.0, 0.0, 0.0)
v7 = m.vertex(11.0, 0.0, 0.0)
v8 = m.vertex(10.5, 1.0, 0.0)
t4 = m.triangle(v6, v7, v8)   # face 4: isolated

# Assert: all three center edges are shared by exactly 2 triangles (BFS t1/t2/t3 evidence).
m.assert_edge_shared(v0, v1, 2)   # center shared with outer neighbor t_n1
m.assert_edge_shared(v1, v2, 2)   # center shared with outer neighbor t_n2
m.assert_edge_shared(v0, v2, 2)   # center shared with outer neighbor t_n3

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t_center)

# Assert: outer boundary edges of component A are non-shared (n=1).
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
