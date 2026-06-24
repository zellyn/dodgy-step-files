"""Me585 — createSubMeshFromSelection empty_selection: no triangles visited; delete sub-mesh and return NULL (Branch 6).

Basic_TMesh.createSubMeshFromSelection branch 6: empty_selection

Source method: `Basic_TMesh.createSubMeshFromSelection` @ line 877
Branch condition: `!sT.numels()` — after the BFS or global scan, the collected
triangle list sT is empty (no triangles were IS_VISITED). The algorithm deletes
the partially constructed sub-mesh object and returns NULL.

Defect pattern: a valid triangle mesh of 3 triangles in a fan, with NO triangles
marked IS_VISITED (empty selection). The caller passes NULL as the seed. The
global scan (Branch 3 path) finds zero visited triangles. sT.numels() == 0, so
Branch 6 fires: the empty sub-mesh is discarded and the return value is NULL.

This is the complement of Branch 3 (no_seed + all visited) — here no_seed but
with zero visited triangles.

Geometric signature:
  v0=(0,0,0) — hub
  v1=(2,0,0), v2=(1,2,0), v3=(−1,2,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v1) — ALL unvisited

  Standard closed fan. All triangles unvisited → empty selection →
  extraction returns NULL after deleting the sub-mesh object.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me585",
    title="createSubMeshFromSelection empty_selection: zero triangles IS_VISITED; sT.numels()==0; sub-mesh deleted, returns NULL (Branch 6)",
    defect_class="mesh_selection",
)

# Hub vertex and 3 rim vertices forming a closed fan.
v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — hub
v1 = m.vertex(2.0,  0.0, 0.0)  # 1 — rim right
v2 = m.vertex(1.0,  2.0, 0.0)  # 2 — rim top
v3 = m.vertex(-1.0, 2.0, 0.0)  # 3 — rim left

# Three fan triangles around hub v0, ALL unvisited — empty selection.
t0 = m.triangle(v0, v1, v2)  # 0: unvisited
t1 = m.triangle(v0, v2, v3)  # 1: unvisited
t2 = m.triangle(v0, v3, v1)  # 2: unvisited

# Spoke edges — each shared by exactly 2 fan triangles.
m.assert_edge_shared(v0, v1, 2)  # t0 and t2
m.assert_edge_shared(v0, v2, 2)  # t0 and t1
m.assert_edge_shared(v0, v3, 2)  # t1 and t2

# Outer rim edges — boundary (each in exactly 1 triangle).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v1, 1)

# Euler: V=4, E=6, F=3, chi=1 (open disk).
m.assert_euler_characteristic(4, 6, 3, 1)
