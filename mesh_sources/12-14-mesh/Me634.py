"""Me634 — Basic_TMesh.growSelection branch 5: vertex_unmark_cleanup.

MeshFix `Basic_TMesh.growSelection` Branch 5 (*vertex_unmark_cleanup*)
@ line 708:
  'FOREACHVERTEX(v, n) UNMARK_VISIT(v);'
  — after the two-pass selection grow (mark vertices of selected triangles,
  then select unselected triangles touching any marked vertex), a cleanup
  pass iterates ALL vertices in the mesh and clears the temporary VISITED
  flag that was set during the grow. Branch 5 fires once per vertex in the
  mesh during this cleanup. A mesh with N vertices exercises Branch 5 N times.

Defect pattern: a 6-triangle mesh (fan of 6 around a central vertex v0) where:
  - t0 is pre-selected; the first pass marks v0, v1, v2.
  - The second pass selects t1 and t5 (adjacent to t0, sharing marked vertices).
  - The cleanup pass then UNMARKS all 7 vertices (v0–v6) exactly once each
    (Branch 5 fires 7 times).
  The relatively large vertex count (7) makes the cleanup pass count meaningful
  and distinguishable from the marking and selection counts.

Geometry (6-triangle fan):
  v0=(0,0,0) central vertex (in all 6 triangles)
  v1=(2,0,0), v2=(1,1,0), v3=(0,2,0), v4=(-1,1,0), v5=(-2,0,0), v6=(0,-1,0)
  t0=(v0,v1,v2) pre-selected
  t1=(v0,v2,v3) unselected; shares edge (v0,v2) — v0 and v2 marked → selected
  t2=(v0,v3,v4) unselected; v3 not marked after t0 first pass
  t3=(v0,v4,v5) unselected; no marked vertex
  t4=(v0,v5,v6) unselected; no marked vertex
  t5=(v0,v6,v1) unselected; shares edge (v0,v1) — v0 and v1 marked → selected
  After grow: t0,t1,t5 selected. Cleanup UNMARKS v0–v6 (7 iterations of Branch 5).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me634",
    title="growSelection vertex_unmark_cleanup: FOREACHVERTEX UNMARK_VISIT fires 7 times after grow; 6-triangle fan around central v0 (Branch 5)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — central vertex; MARKED in pass 1 (via t0)
v1 = m.vertex(2.0,  0.0, 0.0)  # 1 — t0 corner; MARKED in pass 1
v2 = m.vertex(1.0,  1.0, 0.0)  # 2 — t0 apex; MARKED in pass 1
v3 = m.vertex(0.0,  2.0, 0.0)  # 3 — t1 outer; not marked in pass 1
v4 = m.vertex(-1.0, 1.0, 0.0)  # 4 — t2 outer; not marked in pass 1
v5 = m.vertex(-2.0, 0.0, 0.0)  # 5 — t3 outer; not marked in pass 1
v6 = m.vertex(0.0, -1.0, 0.0)  # 6 — t4 outer; not marked in pass 1

# Pre-selected triangle (marks v0, v1, v2 in first pass).
t0 = m.triangle(v0, v1, v2)  # 0: selected seed

# Adjacent neighbors — selected by Branch 4 during second pass.
t1 = m.triangle(v0, v2, v3)  # 1: shares (v0,v2) — both marked → Branch 4 selects
t5 = m.triangle(v0, v6, v1)  # 5: shares (v0,v1) — both marked → Branch 4 selects

# Remaining neighbors — not selected (no marked vertex).
t2 = m.triangle(v0, v3, v4)  # 2: v0 marked but this is after 1st pass only marks t0's verts
t3 = m.triangle(v0, v4, v5)  # 3: v0 marked similarly
t4 = m.triangle(v0, v5, v6)  # 4: v0 marked similarly

# Interior fan edges (each shared by 2 triangles).
m.assert_edge_shared(v0, v1, 2)  # t0 and t5
m.assert_edge_shared(v0, v2, 2)  # t0 and t1
m.assert_edge_shared(v0, v3, 2)  # t1 and t2
m.assert_edge_shared(v0, v4, 2)  # t2 and t3
m.assert_edge_shared(v0, v5, 2)  # t3 and t4
m.assert_edge_shared(v0, v6, 2)  # t4 and t5

# Outer rim edges (boundary, n=1 each).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v6, v1, 1)

# Euler: V=7, E=12, F=6, chi=1 (open disk).
m.assert_euler_characteristic(7, 12, 6, 1)
