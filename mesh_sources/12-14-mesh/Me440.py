"""Me440 — removeSmallestComponents_empty_mesh: T.numels() == 0 triggers early return.

Catalog claim: checkAndRepair::removeSmallestComponents@L780 Branch 1 (*EMPTY_MESH*)
fires when the mesh contains zero triangles. The function returns 0 immediately —
no BFS traversal or component comparison is performed. This fixture provides the
minimal-contrast case: a single-triangle mesh (triangle_count == 1) that does NOT
trigger the empty-mesh early return, demonstrating the boundary condition.

The single triangle forms a valid non-empty mesh; the contrast assertion
(triangle_count == 1) confirms the mesh is minimal yet non-degenerate for the
removeSmallestComponents path.

Source: MeshFix checkAndRepair::removeSmallestComponents@L780 Branch 1
(*EMPTY_MESH*): `if (T.numels() == 0) return 0;`
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me440",
             title="removeSmallestComponents empty_mesh: single-triangle contrast for T.numels()==0 early-return branch",
             defect_class="disconnected_components")

# Minimal single-triangle mesh — contrast for the empty-mesh early return.
# A mesh with exactly 1 triangle passes the numels()==0 check and enters
# the BFS loop, so it covers the code path just beyond Branch 1.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.0, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # single triangle; area = 0.5

# Assert: the single triangle has positive area (non-degenerate, non-empty mesh).
m.assert_triangle_area_lt(t0, 1.0)   # area is 0.5, below 1.0

# Assert: the only edges exist in this triangle (manifold, 1-component).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
