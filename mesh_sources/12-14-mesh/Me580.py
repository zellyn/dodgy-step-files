"""Me580 — createSubMeshFromSelection invalid_triangle_seed: seed triangle not visited; return NULL (Branch 1).

Basic_TMesh.createSubMeshFromSelection branch 1: invalid_triangle_seed

Source method: `Basic_TMesh.createSubMeshFromSelection` @ line 794
Branch condition: `t0 != NULL && !IS_VISITED(t0)` — the caller provided a seed
triangle t0 but that triangle is NOT in the IS_VISITED selection. The function
immediately returns NULL without extracting any sub-mesh.

Defect pattern: a connected strip of 4 triangles where only the middle two have
been marked IS_VISITED. The caller passes t0 (the leftmost, unvisited triangle)
as the seed. Since t0 is non-NULL but not visited, Branch 1 fires immediately
and the extraction returns NULL.

The presence of selected triangles (t1, t2) that ARE visited, combined with an
unvisited seed (t0), is the defining invariant for Branch 1.

Geometric signature:
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(3,2,0), v4=(4,0,0)
  t0=(v0,v1,v2) — unvisited — this is the invalid seed
  t1=(v1,v3,v2) — visited (in selection)
  t2=(v1,v4,v3) — visited (in selection)
  t3=(v2,v3,v4) — unvisited

  Interior edges (v1,v2) between t0/t1, (v1,v3) between t1/t2, (v3,v4) between
  t2/t3 are each shared by exactly 2 triangles, confirming a single connected
  component — but the seed is not in the selection, so extraction aborts.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me580",
    title="createSubMeshFromSelection invalid_triangle_seed: seed t0 not IS_VISITED; extraction aborts, returns NULL (Branch 1)",
    defect_class="mesh_selection",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left
v1 = m.vertex(2.0, 0.0, 0.0)  # 1 — bottom-center
v2 = m.vertex(1.0, 2.0, 0.0)  # 2 — top-left
v3 = m.vertex(3.0, 2.0, 0.0)  # 3 — top-right
v4 = m.vertex(4.0, 0.0, 0.0)  # 4 — right

# Four triangles in a strip.
t0 = m.triangle(v0, v1, v2)  # 0: unvisited (seed — NOT in IS_VISITED selection)
t1 = m.triangle(v1, v3, v2)  # 1: visited (in selection)
t2 = m.triangle(v1, v4, v3)  # 2: visited (in selection)
t3 = m.triangle(v2, v3, v4)  # 3: unvisited

# Interior shared edges — each shared by exactly 2 triangles.
m.assert_edge_shared(v1, v2, 2)  # t0 and t1
m.assert_edge_shared(v1, v3, 2)  # t1 and t2
m.assert_edge_shared(v3, v4, 2)  # t2 and t3
m.assert_edge_shared(v2, v3, 2)  # t1 and t3

# Outer boundary edges — each shared by exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v2, v4, 1)

# Euler: V=5, E=8, F=4, chi=1 (open disk, genus 0).
m.assert_euler_characteristic(5, 8, 4, 1)
