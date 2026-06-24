"""Me453 — removeSmallestComponents_area_adjacent_t3: BFS expands via t3 neighbor.

checkAndRepair::removeSmallestComponents@L861 branch 4: ADJACENT_TRIANGLE_T3_AREA

Catalog claim: during BFS traversal the code checks s = t->t3() (the triangle
adjacent via edge 3). If s is non-null and not yet visited, it is appended to the
BFS todo list. Branch 4 fires when t3-adjacency provides the unvisited neighbor
that expands the component.

Geometric signature: four triangles forming a closed tetrahedral fan so that BFS
must use t3 (third edge adjacency) to traverse the component. A separate tiny
triangle forms component B with area below eps_area.

Defect carrier: triangles 0-3 form a tetrahedral surface patch (component A);
triangle 4 is the micro-component B (area ≈ 5e-5). In the BFS, expanding via
t3 connects a pair of triangles in component A.

Source: checkAndRepair::removeSmallestComponents@L861 Branch 4 — ADJACENT_TRIANGLE_T3_AREA:
s = t->t3(); if (s != NULL && !IS_BIT(s, 5)) push s to todo
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me453",
             title="removeSmallestComponents area ADJACENT_TRIANGLE_T3_AREA: BFS expands via t->t3() neighbor; disconnected micro-component below eps_area",
             defect_class="disconnected_components")

# Component A: a 4-triangle patch (like a tent) where each triangle shares one
# edge with its neighbor — requires all three t1/t2/t3 adjacency directions.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(2.0, 0.0, 0.0)
v2 = m.vertex(1.0, 2.0, 0.0)
v3 = m.vertex(1.0, 1.0, 1.0)   # apex above

t0 = m.triangle(v0, v1, v3)   # front face
t1 = m.triangle(v1, v2, v3)   # right face; shares (v1,v3) with t0
t2 = m.triangle(v2, v0, v3)   # left face; shares (v2,v3) with t1
t3 = m.triangle(v0, v2, v1)   # base face; closes the component

# Component B: micro-triangle (area ≈ 5e-5).
v4 = m.vertex(30.0, 30.0, 0.0)
v5 = m.vertex(30.01, 30.0, 0.0)
v6 = m.vertex(30.0, 30.01, 0.0)
t4 = m.triangle(v4, v5, v6)   # area ≈ 5e-5

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: micro-triangle has negligible area.
m.assert_triangle_area_lt(t4, 1e-3)

# Assert: interior shared edges in component A (closed tetrahedron).
m.assert_edge_shared(v1, v3, 2)   # t0 and t1
m.assert_edge_shared(v2, v3, 2)   # t1 and t2
m.assert_edge_shared(v0, v3, 2)   # t0 and t2
