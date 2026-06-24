"""Me575 — Basic_TMesh.invertSelection branch 6: global_invert — t0 == NULL; invert all triangles globally via FOREACHTRIANGLE.

MeshFix `Basic_TMesh.invertSelection` Branch 6 (*global_invert*) @ line 760:
  'else { FOREACHTRIANGLE(t, i) MARK_VISIT(t); }'  (or UNMARK_VISIT variant)
  — when no seed triangle is provided (t0 == NULL), the algorithm iterates ALL
  triangles in the mesh and flips their VISITED bit globally. Branch 6 fires
  whenever invertSelection is called with a NULL seed.

Defect pattern: a simple closed-disk mesh with no particular structural defect.
  The caller passes t0=NULL, so the algorithm skips the BFS logic entirely and
  uses FOREACHTRIANGLE to toggle all triangles at once. The fixture demonstrates
  that the global-invert path operates on every triangle regardless of connectivity.

Geometry (closed tetrahedron — 4 triangles, fully manifold):
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(1,1,2)
  t0=(v0,v1,v2): base
  t1=(v0,v1,v3): front face
  t2=(v1,v2,v3): right face
  t3=(v0,v2,v3): left face
  All edges shared by exactly 2 triangles → closed manifold.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me575",
    title="Basic_TMesh.invertSelection global_invert: t0==NULL; FOREACHTRIANGLE flips VISITED bit on all 4 triangles (Branch 6)",
    defect_class="mesh_selection_toggle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 2.0, 0.0)  # 2
v3 = m.vertex(1.0, 1.0, 2.0)  # 3 — apex

# Tetrahedron: 4 fully-connected triangles.
t0 = m.triangle(v0, v1, v2)  # 0: base
t1 = m.triangle(v0, v1, v3)  # 1: front
t2 = m.triangle(v1, v2, v3)  # 2: right
t3 = m.triangle(v0, v2, v3)  # 3: left

# Every edge is shared by exactly 2 triangles (closed manifold).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler: V=4, E=6, F=4, chi=2 (sphere — genus 0 closed manifold).
m.assert_euler_characteristic(4, 6, 4, 2)
