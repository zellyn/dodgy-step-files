"""Me972 — deselectConnectedComponent_neighbor_t1_dequeue: t1 selected + edge not sharp → enqueue t1 (Branch 3).

MeshFix `Basic_TMesh.deselectConnectedComponent` Branch 3 (*neighbor_t1_dequeue*) @ line 1106:
  'if (t1 != NULL && IS_VISITED(t1) && !IS_SHARPEDGE(t->e1)) todo.appendHead(t1);'
  — while processing a dequeued triangle, the BFS checks neighbor t1:
  if t1 is non-NULL, is selected (IS_VISITED), and the shared edge e1 is not
  sharp, then t1 is added to the todo list. This branch controls BFS expansion
  across the first edge.

Defect pattern: two adjacent triangles both selected. The seed t0 is
  dequeued; its e1-neighbor t1 is non-NULL, selected, and the shared edge
  (v0,v2) is not sharp — Branch 3 fires, t1 is enqueued. Both triangles
  are ultimately deselected (ns=2).

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(-0.5,1,0)
  t0=(v0,v1,v2): selected seed
  t1=(v0,v2,v3): selected, reachable via e1 (edge v0,v2) — Branch 3 fires
  Shared edge (v0,v2): n=2 (interior, not sharp).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me972",
    title="deselectConnectedComponent_neighbor_t1_dequeue: t1 selected + edge (v0,v2) not sharp → todo.appendHead(t1) fires Branch 3",
    defect_class="selection_connected",
)

v0 = m.vertex(0.0,  0.0, 0.0)  # 0
v1 = m.vertex(1.0,  0.0, 0.0)  # 1
v2 = m.vertex(0.5,  1.0, 0.0)  # 2
v3 = m.vertex(-0.5, 1.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)  # 0: selected seed; e1 is the edge leading to t1
t1 = m.triangle(v0, v2, v3)  # 1: selected neighbor; reached via e1 edge (v0,v2)

# Interior edge (v0,v2) shared by both triangles — not sharp, so Branch 3 fires.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
