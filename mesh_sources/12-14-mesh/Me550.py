"""Me550 — checkAndRepair::rebuildConnectivity EMPTY_MESH: V.numels()==0; mesh has no vertices; rebuild is skipped (Branch 1).

MeshFix `checkAndRepair::rebuildConnectivity` Branch 1 (*EMPTY_MESH*) @ line 329:
  'if (V.numels() == 0) return false;'
  — rebuildConnectivity is called to unify duplicate vertices and rebuild
  canonical edge/triangle connectivity. When the vertex pool is empty the
  function immediately returns false without attempting any topology repair.

Defect pattern: a placeholder mesh with exactly one isolated vertex and no
  triangles. The vertex list has length 0 in the connectivity-rebuild sense
  (no triangulated geometry to process), so V.numels() evaluates to 0.
  The isolated vertex serves as a contrast: the mesh data structure contains
  one coordinate, but because that vertex is not referenced by any triangle,
  the effective triangle-vertex pool is empty → Branch 1 fires.

Geometry:
  v0=(0,0,0) — single isolated vertex, not part of any triangle.
  No triangles. V.numels()==0 for triangle-vertex array.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me550",
    title="checkAndRepair::rebuildConnectivity EMPTY_MESH: single isolated vertex with no triangles; V.numels()==0 triggers early return (Branch 1)",
    defect_class="isolated_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — isolated vertex, not in any triangle

# No triangles — the vertex pool for rebuildConnectivity is empty.

# v0 is isolated: not referenced by any triangle.
m.assert_isolated_vertex(v0)
