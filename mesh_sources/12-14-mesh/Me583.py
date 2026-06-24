"""Me583 — createSubMeshFromSelection keep_reference: keep_ref flag preserves info pointers in extracted sub-mesh (Branch 4).

Basic_TMesh.createSubMeshFromSelection branch 4: keep_reference

Source method: `Basic_TMesh.createSubMeshFromSelection` @ line 842
Branch condition: `keep_ref` — when the caller passes keep_ref=true, the
algorithm copies each vertex's and triangle's `info` pointer from the original
mesh into the extracted sub-mesh, preserving references to external data. When
keep_ref=false, info pointers are cleared (set to NULL) after extraction.

Defect pattern: a minimal connected mesh of 3 triangles sharing a central vertex,
all marked IS_VISITED. A seed triangle is provided. The keep_ref=true path causes
the sub-mesh's elements to retain their info pointer values from the original.
The resulting sub-mesh contains all 3 triangles and 4 vertices with their info
slots intact.

This is a structural variation of Branch 2: the BFS flood fill is the same, but
the info-pointer preservation flag changes what happens to each vertex's `info`
field during the copy. A mesh where ALL triangles are visited and a seed is given
naturally exercises keep_ref with a clean sub-mesh.

Geometric signature:
  v0=(0,0,0) — hub
  v1=(2,0,0), v2=(1,2,0), v3=(−1,2,0)
  t0=(v0,v1,v2) — visited
  t1=(v0,v2,v3) — visited
  t2=(v0,v3,v1) — visited (closes a closed fan around the hub)

  Three triangles form a closed fan: every spoke edge (v0,vN) is shared by
  two visited triangles (n=2), outer edges are boundary (n=1). Seed = t0.
  keep_ref=true means info pointers on each vertex and triangle are copied
  through to the sub-mesh rather than zeroed.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me583",
    title="createSubMeshFromSelection keep_reference: all triangles visited; seed t0; keep_ref=true preserves info pointers in extracted sub-mesh (Branch 4)",
    defect_class="mesh_selection",
)

# Hub vertex and 3 rim vertices forming a closed fan.
v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — hub
v1 = m.vertex(2.0,  0.0, 0.0)  # 1 — rim right
v2 = m.vertex(1.0,  2.0, 0.0)  # 2 — rim top
v3 = m.vertex(-1.0, 2.0, 0.0)  # 3 — rim left

# Three triangles in a fan around hub v0, all visited.
t0 = m.triangle(v0, v1, v2)  # 0: visited (BFS seed)
t1 = m.triangle(v0, v2, v3)  # 1: visited (reachable from t0 via edge v0,v2)
t2 = m.triangle(v0, v3, v1)  # 2: visited (reachable from t0 via edge v0,v1 or from t1 via v0,v3)

# Spoke edges — each shared by exactly 2 fan triangles (interior in full mesh).
m.assert_edge_shared(v0, v1, 2)  # t0 and t2
m.assert_edge_shared(v0, v2, 2)  # t0 and t1
m.assert_edge_shared(v0, v3, 2)  # t1 and t2

# Outer rim edges — boundary (each in exactly 1 triangle).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v1, 1)

# Euler: V=4, E=6, F=3, chi=1 (open disk — open boundary from rim edges).
m.assert_euler_characteristic(4, 6, 3, 1)
