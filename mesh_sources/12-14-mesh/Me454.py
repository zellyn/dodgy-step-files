"""Me454 — removeSmallestComponents_area_accumulation: BFS accumulates triangle areas.

checkAndRepair::removeSmallestComponents@L861 branch 5: AREA_ACCUMULATION

Catalog claim: for each triangle t visited during BFS, its area is added to the
component's running total: pa += t->area(). Branch 5 fires each time a triangle's
area contribution is added. After the BFS finishes, pa holds the total geometric
area of the component.

Geometric signature: two disconnected components with measurably different areas.
Component A has total area = 2.0 (four triangles of area 0.5 each); component B
is a small triangle with area 0.5. The area accumulation during BFS over component
A sums to 2.0; for component B it sums to 0.5. Neither falls below eps_area in
this scenario — the fixture demonstrates the accumulation mechanism.

Defect carrier: triangles 0-3 form component A (total area = 2.0); triangle 4
forms component B (area = 0.5, small but above typical eps_area). Each triangle
visit increments pa with t->area().

Source: checkAndRepair::removeSmallestComponents@L861 Branch 5 — AREA_ACCUMULATION:
pa += t->area(); accumulate each triangle's geometric area into running component total
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me454",
             title="removeSmallestComponents area AREA_ACCUMULATION: pa += t->area() accumulates component geometric area during BFS; two-component mesh with area disparity",
             defect_class="disconnected_components")

# Component A: four triangles, each area = 0.5, total = 2.0.
# A 2x1 rectangle split into 4 triangles.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(2.0, 0.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(1.0, 1.0, 0.0)
v5 = m.vertex(2.0, 1.0, 0.0)

t0 = m.triangle(v0, v1, v4)   # area = 0.5
t1 = m.triangle(v0, v4, v3)   # area = 0.5
t2 = m.triangle(v1, v2, v5)   # area = 0.5
t3 = m.triangle(v1, v5, v4)   # area = 0.5

# Component B: single triangle with area = 0.5 (well above any eps_area,
# but still distinctly smaller than component A's total of 2.0).
v6 = m.vertex(10.0, 0.0, 0.0)
v7 = m.vertex(11.0, 0.0, 0.0)
v8 = m.vertex(10.0, 1.0, 0.0)
t4 = m.triangle(v6, v7, v8)   # area = 0.5

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: shared interior edges in component A.
m.assert_edge_shared(v0, v4, 2)   # t0 and t1
m.assert_edge_shared(v1, v5, 2)   # t2 and t3
m.assert_edge_shared(v1, v4, 2)   # t0 and t3

# Assert: component B triangles are boundary-only (no shared edges within B).
m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v7, v8, 1)
m.assert_edge_shared(v6, v8, 1)
