"""Me450 — removeSmallestComponents_area_empty_mesh: empty mesh triggers early return.

checkAndRepair::removeSmallestComponents@L861 branch 1: EMPTY_MESH

Catalog claim: when the mesh contains zero triangles (T.numels() == 0), the
area-based removeSmallestComponents returns 0 immediately at line 869 without
entering the BFS traversal or area accumulation loop. This is the guard branch
that avoids operating on an empty mesh.

Geometric signature: a single isolated vertex with no triangles. T.numels() == 0
so Branch 1 fires and the function returns 0.

Defect carrier: vertex v0 at origin with no triangles attached — an isolated
vertex fixture. No area can be computed; no component BFS is initiated.

Source: checkAndRepair::removeSmallestComponents@L861 Branch 1 — EMPTY_MESH:
T.numels() == 0 → return 0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me450",
             title="removeSmallestComponents area EMPTY_MESH: T.numels()==0 → return 0; no triangles to area-filter",
             defect_class="disconnected_components")

# An isolated vertex — produces a mesh with zero triangles.
v0 = m.vertex(0.0, 0.0, 0.0)

# Confirm the vertex is isolated (no shared edges with any other vertex).
m.assert_isolated_vertex(v0)
