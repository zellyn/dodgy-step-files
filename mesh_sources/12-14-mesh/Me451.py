"""Me451 — removeSmallestComponents_area_adjacent_t1: BFS expands via t1 neighbor.

checkAndRepair::removeSmallestComponents@L861 branch 2: ADJACENT_TRIANGLE_T1_AREA

Catalog claim: during BFS traversal over triangles in the larger component, the
code checks s = t->t1() (the triangle adjacent via edge 1). If s is non-null and
IS_BIT(s, 5) is false (not yet visited), s is appended to the BFS todo list and
marked visited. Branch 2 fires when the first unvisited neighbor is reached via t1.

Geometric signature: a strip of four triangles sharing edges in a fan pattern so
that adjacent triangle lookup via t1 propagates the BFS. A tiny isolated triangle
forms the small component whose area is below eps_area.

Defect carrier: triangles 0-3 form a connected strip (component A, total area > 1.0);
triangle 4 is a micro-triangle (component B, area ≈ 5e-5), unreachable from t0 by
edge-walk. BFS over component A traverses t1-neighbors.

Source: checkAndRepair::removeSmallestComponents@L861 Branch 2 — ADJACENT_TRIANGLE_T1_AREA:
s = t->t1(); if (s != NULL && !IS_BIT(s, 5)) push s to todo
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me451",
             title="removeSmallestComponents area ADJACENT_TRIANGLE_T1_AREA: BFS expands via t->t1() neighbor; micro-component has area below eps_area",
             defect_class="disconnected_components")

# Component A: four-triangle strip so BFS must traverse t1 adjacency.
# Two quads each split diagonally.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(2.0, 0.0, 0.0)
v5 = m.vertex(2.0, 1.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # area = 0.5
t1 = m.triangle(v0, v2, v3)   # area = 0.5, shares edge (v0,v2) with t0
t2 = m.triangle(v1, v4, v5)   # area = 0.5
t3 = m.triangle(v1, v5, v2)   # area = 0.5, shares edge (v1,v5)? — shares (v1,v2) with t0

# Component B: micro-triangle (area ≈ 5e-5) well below any eps_area.
v6 = m.vertex(10.0, 10.0, 0.0)
v7 = m.vertex(10.01, 10.0, 0.0)
v8 = m.vertex(10.0, 10.01, 0.0)
t4 = m.triangle(v6, v7, v8)   # area ≈ 5e-5

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: micro-triangle has negligible area.
m.assert_triangle_area_lt(t4, 1e-3)

# Assert: shared interior edge in component A exists (t0 and t1 share edge v0-v2).
m.assert_edge_shared(v0, v2, 2)
