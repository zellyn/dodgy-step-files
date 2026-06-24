"""Me455 — removeSmallestComponents_area_below_threshold: tiny-area component unlinked.

checkAndRepair::removeSmallestComponents@L861 branch 6: COMPONENT_AREA_BELOW_THRESHOLD

Catalog claim: after BFS accumulates the total area pa for a component, the code
checks if pa < eps_area. If so, all triangles in that component are unlinked from
the mesh and rem_comps is incremented. Branch 6 fires for each component whose
accumulated area falls below the area threshold eps_area.

Geometric signature: two disconnected components with a large area disparity.
Component A is a large quad patch (area = 1.0); component B is a micro-triangle
(area ≈ 5e-5 << eps_area). When eps_area is set at any reasonable threshold
(e.g., 0.001), pa for component B triggers pa < eps_area and the triangles are
unlinked.

Defect carrier: triangles 0-1 form component A (area = 1.0); triangle 2 is
component B (area ≈ 5e-5), unreachable from t0 by edge-walk. The pa < eps_area
condition fires for component B.

Source: checkAndRepair::removeSmallestComponents@L861 Branch 6 — COMPONENT_AREA_BELOW_THRESHOLD:
if (pa < eps_area) { /* unlink all component triangles */ rem_comps++; }
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me455",
             title="removeSmallestComponents area COMPONENT_AREA_BELOW_THRESHOLD: pa < eps_area → component unlinked; micro-triangle area 5e-5 vs large patch area 1.0",
             defect_class="disconnected_components")

# Component A: unit-square patch (two triangles, total area = 1.0).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # area = 0.5
t1 = m.triangle(v0, v2, v3)   # area = 0.5

# Component B: micro-triangle — area ≈ 0.5 * 0.01 * 0.01 = 5e-5 << eps_area.
v4 = m.vertex(5.0, 5.0, 0.0)
v5 = m.vertex(5.01, 5.0, 0.0)
v6 = m.vertex(5.0, 5.01, 0.0)
t2 = m.triangle(v4, v5, v6)   # area ≈ 5e-5; triggers pa < eps_area

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t2, t0)

# Assert: micro-triangle has area far below typical eps_area.
m.assert_triangle_area_lt(t2, 1e-3)

# Assert: shared interior edge in component A.
m.assert_edge_shared(v0, v2, 2)

# Assert: component A triangles have much larger area than the threshold.
# (Each triangle in A has area 0.5 — about 10,000x larger than t2's area.)
# Verify component B boundary edges are unshared.
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v4, v6, 1)
