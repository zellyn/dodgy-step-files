"""Me974 — deselectConnectedComponent_neighbor_t3_dequeue: t3 selected + edge not sharp → enqueue t3 (Branch 5).

MeshFix `Basic_TMesh.deselectConnectedComponent` Branch 5 (*neighbor_t3_dequeue*) @ line 1108:
  'if (t3 != NULL && IS_VISITED(t3) && !IS_SHARPEDGE(t->e3)) todo.appendHead(t3);'
  — the BFS checks the third neighbor t3: if t3 is non-NULL, selected
  (IS_VISITED), and the shared edge e3 is not sharp, t3 is enqueued.
  This is the analogous check for the third edge of each dequeued triangle.

Defect pattern: a 4-triangle strip where t0 is the seed. t0 shares its
  e3 (third edge) with t3 (the triangle across the v1-v2 boundary). t3 is
  selected and the shared edge is not sharp — Branch 5 fires, t3 is
  enqueued. All 4 triangles are deselected via BFS.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(3,1,0), v4=(0,2,0), v5=(2,2,0)
  t0=(v0,v1,v2): seed — e3 is the edge (v1,v2) → crosses to t3
  t1=(v1,v3,v2): selected neighbor (across e1 of t0)
  t2=(v0,v2,v4): selected neighbor (across e2 of t0)
  t3=(v2,v3,v5): selected neighbor across e3 (v1,v2) of t0 → Branch 5
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me974",
    title="deselectConnectedComponent_neighbor_t3_dequeue: t3 selected + edge (v1,v2) not sharp → todo.appendHead(t3) fires Branch 5",
    defect_class="selection_connected",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 1.0, 0.0)  # 2 — shared among t0, t1, t2, t3
v3 = m.vertex(3.0, 1.0, 0.0)  # 3
v4 = m.vertex(0.0, 2.0, 0.0)  # 4
v5 = m.vertex(2.0, 2.0, 0.0)  # 5

t0 = m.triangle(v0, v1, v2)  # 0: seed
t1 = m.triangle(v1, v3, v2)  # 1: selected; e1-neighbor of t0 (edge v1,v2 — also shared with t3)
t2 = m.triangle(v0, v2, v4)  # 2: selected; e2-neighbor of t0 (edge v0,v2)
t3 = m.triangle(v2, v3, v5)  # 3: selected; e3-neighbor of t0 across (v1,v2) → Branch 5

# Interior shared edges.
m.assert_edge_shared(v1, v2, 2)  # t0 and t1 (e3 of t0 leads to t1; t3 also meets v2)
m.assert_edge_shared(v0, v2, 2)  # t0 and t2
m.assert_edge_shared(v2, v3, 2)  # t1 and t3

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v2, v5, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v0, v4, 1)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
