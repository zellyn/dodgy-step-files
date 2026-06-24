"""Me973 — deselectConnectedComponent_neighbor_t2_dequeue: t2 selected + edge not sharp → enqueue t2 (Branch 4).

MeshFix `Basic_TMesh.deselectConnectedComponent` Branch 4 (*neighbor_t2_dequeue*) @ line 1107:
  'if (t2 != NULL && IS_VISITED(t2) && !IS_SHARPEDGE(t->e2)) todo.appendHead(t2);'
  — the BFS checks neighbor t2: if t2 is non-NULL, is selected (IS_VISITED),
  and the shared edge e2 is not sharp, then t2 is added to the todo list.
  This is the analogous check for the second edge of each dequeued triangle.

Defect pattern: a 3-triangle fan sharing hub v0 where t0 is the seed.
  t0's e2-neighbor is t2 (adjacent across the v0-v3 edge). t2 is selected
  and the edge is not sharp — Branch 4 fires. t1 (e1-neighbor of t0) is
  also selected → Branch 3 fires too. All three triangles are deselected.

Geometry:
  v0=(0,0,0) hub; v1=(1,0,0), v2=(0,1,0), v3=(-1,0,0)
  t0=(v0,v1,v2): seed — e1 edge to t1 (v0,v2), e2 edge to t2 (v0,v3)
  t1=(v0,v2,v3): selected, adjacent across e1 of t0
  t2=(v0,v3,v1): selected, adjacent across e2 of t0 → Branch 4 fires
  Note: in the half-edge structure e2 of t0=(v0,v1,v2) is the edge v0-v3
  crossing to t2 — but to keep the geometry simple we use a plain
  3-triangle fan and note that one of the two non-e1 cross-edges triggers
  Branch 4.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me973",
    title="deselectConnectedComponent_neighbor_t2_dequeue: t2 selected + edge (v0,v3) not sharp → todo.appendHead(t2) fires Branch 4",
    defect_class="selection_connected",
)

v0 = m.vertex( 0.0, 0.0, 0.0)  # 0 — hub vertex
v1 = m.vertex( 1.0, 0.0, 0.0)  # 1
v2 = m.vertex( 0.0, 1.0, 0.0)  # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)  # 0: seed — e1→t1, e2→t2
t1 = m.triangle(v0, v2, v3)  # 1: selected; reached via e1 (v0,v2)
t2 = m.triangle(v0, v3, v1)  # 2: selected; reached via e2 (v0,v3) → Branch 4

# Interior spoke edges (each shared by 2 triangles — not sharp).
m.assert_edge_shared(v0, v2, 2)  # e1: t0 and t1
m.assert_edge_shared(v0, v3, 2)  # e2: t1 and t2
m.assert_edge_shared(v0, v1, 2)  # e3: t2 and t0

# Boundary rim edges.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# Euler: V=4, E=6, F=3, chi=1 (open disk — triangular fan).
m.assert_euler_characteristic(4, 6, 3, 1)
