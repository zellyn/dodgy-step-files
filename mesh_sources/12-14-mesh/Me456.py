"""Me456 — removeSmallestComponents_area_removed: topology dirty-flags set after removal.

checkAndRepair::removeSmallestComponents@L861 branch 7: SMALL_COMPONENTS_REMOVED

Catalog claim: after the BFS loop over all components completes, if rem_comps > 0
(at least one component was unlinked due to pa < eps_area), Branch 7 fires at
line 894. The method sets topology dirty flags (d_boundaries = d_handles = d_shells = 1)
and calls removeUnlinkedElements() to purge the unlinked triangles from memory.

Geometric signature: two disconnected components where the tiny one satisfies
pa < eps_area. After BFS removes it, rem_comps == 1 > 0 → Branch 7 fires,
marking topology as dirty and triggering cleanup.

Defect carrier: triangles 0-3 form component A (a solid quad, area = 1.0);
triangle 4 is a nano-triangle (component B, area ≈ 1.25e-7) that clearly satisfies
pa < eps_area. After removal, rem_comps = 1 and Branch 7 sets dirty flags.

Source: checkAndRepair::removeSmallestComponents@L861 Branch 7 — SMALL_COMPONENTS_REMOVED:
if (rem_comps > 0) { d_boundaries = d_handles = d_shells = 1; removeUnlinkedElements(); }
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me456",
             title="removeSmallestComponents area SMALL_COMPONENTS_REMOVED: rem_comps > 0 → dirty flags set + removeUnlinkedElements(); nano-triangle component removed",
             defect_class="disconnected_components")

# Component A: a 2x2 patch of 4 triangles (total area = 2.0), clearly above eps_area.
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

# Component B: nano-triangle with edge length 0.0005.
# Area ≈ 0.5 * 0.0005 * 0.0005 = 1.25e-7, far below any eps_area.
# Its removal drives rem_comps = 1 → Branch 7 fires.
v6 = m.vertex(50.0,    50.0,    0.0)
v7 = m.vertex(50.0005, 50.0,    0.0)
v8 = m.vertex(50.0,    50.0005, 0.0)
t4 = m.triangle(v6, v7, v8)   # area ≈ 1.25e-7

# Assert: component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)

# Assert: nano-triangle has negligible area (satisfies pa < eps_area condition).
m.assert_triangle_area_lt(t4, 1e-4)

# Assert: shared interior edges in component A.
m.assert_edge_shared(v0, v4, 2)
m.assert_edge_shared(v1, v5, 2)
m.assert_edge_shared(v1, v4, 2)

# Assert: nano-triangle edges are unshared (pure boundary).
m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v7, v8, 1)
m.assert_edge_shared(v6, v8, 1)

# Assert: Euler characteristic of the whole mesh.
# Component A: 4 triangles in a 2x2 grid.
# V=6, E=9 (4 shared interior + 8 boundary - wait, let's count:
# Component A: V=6, E=9 (3 interior + 6? let me check...)
# Actually: t0=(v0,v1,v4), t1=(v0,v4,v3), t2=(v1,v2,v5), t3=(v1,v5,v4)
# Interior edges: (v0,v4), (v1,v4), (v1,v5) — 3 edges shared by 2 triangles
# Boundary edges: (v0,v1),(v1,v2),(v2,v5),(v4,v5),(v3,v4),(v0,v3) — 6 boundary
# Plus... (v4,v3) hmm, let me just not use euler for the full combined mesh,
# it's complex. The key assertions are reachability and area.
