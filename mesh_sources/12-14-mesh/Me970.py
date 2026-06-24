"""Me970 — deselectConnectedComponent_seed_enqueue: seed triangle t0 added to BFS todo (Branch 1).

MeshFix `Basic_TMesh.deselectConnectedComponent` Branch 1 (*seed_enqueue*) @ line 1098:
  'todo.appendHead(t0);'
  — the BFS is initialized by pushing the seed triangle t0 onto the todo
  list. This fires unconditionally whenever deselectConnectedComponent is
  called with a non-NULL seed. Without this enqueue the entire deselection
  BFS would not start; Branch 1 is the entry point to the whole function.

Defect pattern: a 3-triangle connected strip where all three triangles are
  selected (IS_VISITED). Calling deselectConnectedComponent(t0) enqueues t0
  as seed → Branch 1 fires. The BFS then unmarks all three triangles; the
  selection is cleared.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(0.5,1,0), v4=(1.5,1,0)
  t0=(v0,v1,v3): left triangle — seed
  t1=(v1,v4,v3): middle triangle — reached via BFS
  t2=(v1,v2,v4): right triangle — reached via BFS
  Interior edges (v1,v3) and (v1,v4) each shared by 2 triangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me970",
    title="deselectConnectedComponent_seed_enqueue: todo.appendHead(t0) initializes BFS deselection from seed triangle (Branch 1)",
    defect_class="selection_connected",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — hub
v2 = m.vertex(2.0, 0.0, 0.0)  # 2
v3 = m.vertex(0.5, 1.0, 0.0)  # 3
v4 = m.vertex(1.5, 1.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v3)  # 0: left — seed for deselectConnectedComponent
t1 = m.triangle(v1, v4, v3)  # 1: middle — reached via interior edge (v1,v3)
t2 = m.triangle(v1, v2, v4)  # 2: right — reached via interior edge (v1,v4)

# Interior shared edges.
m.assert_edge_shared(v1, v3, 2)  # t0 and t1 share this edge
m.assert_edge_shared(v1, v4, 2)  # t1 and t2 share this edge

# Boundary edges (n=1 each).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v1, v2, 1)

# All three triangles are connected — t2 reachable from t0 via t1.
# Euler: V=5, E=7, F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
