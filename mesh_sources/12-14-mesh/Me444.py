"""Me444 — removeSmallestComponents_multiple_components: biggest reference updated.

Catalog claim: checkAndRepair::removeSmallestComponents@L780 Branch 5
(*MULTIPLE_COMPONENTS_FOUND*) fires when a newly counted component has more
triangles (gnt > current max nt). The variable `biggest` is updated to point
to this component's List entry (`gnt=nt; biggest=n;`). Three components of
different sizes force the branch to fire twice as progressively larger
components are encountered. The 5-triangle component C becomes the final
`biggest`.

Geometric design: Three disconnected components:
  - Component A: 1 triangle (smallest)
  - Component B: 3-triangle connected strip
  - Component C: 5-triangle connected patch (largest — becomes `biggest`)

Source: MeshFix checkAndRepair::removeSmallestComponents@L780 Branch 5
(*MULTIPLE_COMPONENTS_FOUND*): `if (gnt > nt) { gnt = nt; biggest = n; }`
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me444",
             title="removeSmallestComponents multiple_components: 3-component mesh (1+3+5 triangles); biggest updated twice",
             defect_class="disconnected_components")

# Component A: 1 isolated triangle.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.0, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # face 0: component A (1 triangle)

# Component B: 3-triangle connected strip.
v3 = m.vertex(5.0, 0.0, 0.0)
v4 = m.vertex(6.0, 0.0, 0.0)
v5 = m.vertex(5.5, 1.0, 0.0)
v6 = m.vertex(7.0, 0.0, 0.0)
v7 = m.vertex(6.5, 1.0, 0.0)
t1 = m.triangle(v3, v4, v5)   # face 1: component B triangle 1
t2 = m.triangle(v4, v6, v5)   # face 2: shares edge (v4,v5) with t1
t3 = m.triangle(v5, v6, v7)   # face 3: shares edge (v5,v6) with t2

# Component C: 5-triangle connected patch (2x2 grid with 5 triangles).
v8  = m.vertex(15.0, 0.0, 0.0)
v9  = m.vertex(16.0, 0.0, 0.0)
v10 = m.vertex(17.0, 0.0, 0.0)
v11 = m.vertex(15.5, 1.0, 0.0)
v12 = m.vertex(16.5, 1.0, 0.0)
t4 = m.triangle(v8,  v9,  v11)   # face 4: component C
t5 = m.triangle(v9,  v12, v11)   # face 5: shares edge (v9,v11) with t4
t6 = m.triangle(v9,  v10, v12)   # face 6: shares edge (v9,v12) with t5
t7 = m.triangle(v8,  v11, v10)   # face 7: shares edge (v8,v11)... actually connect via v11
# Use a fifth triangle anchored at v11/v12 to stay in the component.
v13 = m.vertex(16.0, 2.0, 0.0)
t8 = m.triangle(v11, v12, v13)   # face 8: shares edge (v11,v12) — note t5 uses v9,v12,v11

# Assert: components are mutually disconnected.
m.assert_triangle_not_reachable_from(t1, t0)   # B disconnected from A
m.assert_triangle_not_reachable_from(t4, t0)   # C disconnected from A
m.assert_triangle_not_reachable_from(t4, t1)   # C disconnected from B

# Assert: shared interior edges within each component confirm intra-connectivity.
m.assert_edge_shared(v4, v5, 2)    # B: edge between t1 and t2
m.assert_edge_shared(v5, v6, 2)    # B: edge between t2 and t3
m.assert_edge_shared(v9, v11, 2)   # C: edge between t4 and t5
m.assert_edge_shared(v9, v12, 2)   # C: edge between t5 and t6
m.assert_edge_shared(v11, v12, 2)  # C: edge between t5 and t8
