"""Me452 — removeSmallestComponents_area_adjacent_t2: BFS expands via t2 neighbor.

checkAndRepair::removeSmallestComponents@L861 branch 3: ADJACENT_TRIANGLE_T2_AREA

Catalog claim: during BFS traversal the code checks s = t->t2() (the triangle
adjacent via edge 2). If s is non-null and not yet visited (IS_BIT(s,5) == 0),
s is appended to the todo list. Branch 3 fires when BFS expansion via t2 provides
the unvisited neighbor.

Geometric signature: three triangles arranged in an L-shape where BFS from the
first triangle must use the t2 adjacency edge to reach the third triangle.
A separate tiny triangle forms the small component below eps_area.

Defect carrier: triangles 0-2 form component A; triangle 3 is the micro-component B
(area ≈ 5e-5). The t2 edge of triangle 0 connects to triangle 2 in the BFS.

Source: checkAndRepair::removeSmallestComponents@L861 Branch 3 — ADJACENT_TRIANGLE_T2_AREA:
s = t->t2(); if (s != NULL && !IS_BIT(s, 5)) push s to todo
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me452",
             title="removeSmallestComponents area ADJACENT_TRIANGLE_T2_AREA: BFS expands via t->t2() neighbor; disconnected micro-component below eps_area",
             defect_class="disconnected_components")

# Component A: three-triangle fan sharing a common central vertex so that
# t2 adjacency (second edge) propagates the BFS.
v0 = m.vertex(0.0, 0.0, 0.0)   # center
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(-0.5, 1.0, 0.0)
v4 = m.vertex(-1.0, 0.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # area ≈ 0.5; edge (v0,v2) and (v0,v1)
t1 = m.triangle(v0, v2, v3)   # area ≈ 0.5; shares (v0,v2) with t0
t2 = m.triangle(v0, v3, v4)   # area ≈ 0.5; shares (v0,v3) with t1

# Component B: micro-triangle (area ≈ 5e-5).
v5 = m.vertex(20.0, 20.0, 0.0)
v6 = m.vertex(20.01, 20.0, 0.0)
v7 = m.vertex(20.0, 20.01, 0.0)
t3 = m.triangle(v5, v6, v7)   # area ≈ 5e-5

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t3, t0)

# Assert: micro-triangle has negligible area.
m.assert_triangle_area_lt(t3, 1e-3)

# Assert: interior edges shared between triangles in component A.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2
