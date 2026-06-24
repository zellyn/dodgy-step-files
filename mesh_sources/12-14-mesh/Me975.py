"""Me975 — deselectConnectedComponent_unmark_and_count: UNMARK_VISIT(t) + ns++ deselects each reached triangle (Branch 6).

MeshFix `Basic_TMesh.deselectConnectedComponent` Branch 6 (*unmark_and_count*) @ line 1110:
  'UNMARK_VISIT(t); ns++;'
  — after the neighbor checks (Branches 3-5), the current BFS triangle t
  is deselected (IS_VISITED bit cleared) and the counter ns is incremented.
  This fires once for every triangle that was selected and reached by the BFS.
  The return value of deselectConnectedComponent is ns — the number of
  triangles deselected.

Defect pattern: a 4-triangle connected patch, all selected. BFS from seed
  t0 visits all 4 triangles; for each one UNMARK_VISIT fires and ns
  increments. The return value is 4. The mesh uses a 2×2 quad split to
  ensure all four BFS visits trigger Branch 6.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(0,1,0), v4=(1,1,0), v5=(2,1,0)
  t0=(v0,v1,v4): seed — UNMARK_VISIT fires first
  t1=(v0,v4,v3): selected; UNMARK_VISIT fires second
  t2=(v1,v2,v4): selected; UNMARK_VISIT fires third
  t3=(v2,v5,v4): selected; UNMARK_VISIT fires fourth
  All four trigger Branch 6; ns returns 4.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me975",
    title="deselectConnectedComponent_unmark_and_count: UNMARK_VISIT(t); ns++ fires 4 times across all-selected 4-triangle patch (Branch 6)",
    defect_class="selection_connected",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(2.0, 0.0, 0.0)  # 2
v3 = m.vertex(0.0, 1.0, 0.0)  # 3
v4 = m.vertex(1.0, 1.0, 0.0)  # 4 — central hub
v5 = m.vertex(2.0, 1.0, 0.0)  # 5

t0 = m.triangle(v0, v1, v4)  # 0: seed — UNMARK_VISIT + ns++ (Branch 6, count=1)
t1 = m.triangle(v0, v4, v3)  # 1: selected — UNMARK_VISIT + ns++ (Branch 6, count=2)
t2 = m.triangle(v1, v2, v4)  # 2: selected — UNMARK_VISIT + ns++ (Branch 6, count=3)
t3 = m.triangle(v2, v5, v4)  # 3: selected — UNMARK_VISIT + ns++ (Branch 6, count=4)

# Interior shared edges (hub v4 connects all four triangles).
m.assert_edge_shared(v0, v4, 2)  # t0 and t1
m.assert_edge_shared(v1, v4, 2)  # t0 and t2
m.assert_edge_shared(v2, v4, 2)  # t2 and t3

# Boundary edges (n=1 each).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v5, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v3, 1)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
