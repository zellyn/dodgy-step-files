"""Me460 — selectConnectedComponent seed_enqueue: todo.appendHead(t0) initializes BFS.

Catalog claim: Basic_TMesh.selectConnectedComponent Branch 1 @ line 1070
(*seed_enqueue*): the seed triangle t0 is pushed onto the `todo` list to start BFS.
This fires unconditionally for any non-NULL seed. The fixture provides a 3-triangle
connected mesh so the seed enqueue is the first step of a productive traversal.

Basic_TMesh.selectConnectedComponent (MeshFix, lines 1064–1087) performs a
BFS flood-fill starting from a seed triangle t0, marking all reachable triangles
as VISITED and counting them. The first statement inside the function is:
  `todo.appendHead(t0);`
which enqueues the seed. This branch fires for any valid call with t0 != NULL.

Geometric signature: three triangles sharing a common edge hub (v0,v1) so all
three are reachable in one BFS hop. The seed is t0; t1 and t2 are immediately
enqueued when t0's neighbors are processed.

  t0 = (v0, v1, v2)  — seed triangle (BFS root)
  t1 = (v1, v0, v3)  — neighbor sharing edge (v0,v1)
  t2 = (v0, v2, v3)  — neighbor sharing edge (v0,v2) via t0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me460",
             title="selectConnectedComponent seed_enqueue: todo.appendHead(t0) initializes BFS from seed triangle",
             defect_class="disconnected_components")

# Four vertices forming a compact connected triangle fan.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, -1.0, 0.0)

# Three triangles — seed t0 and two BFS-reachable neighbors.
t0 = m.triangle(v0, v1, v2)    # 0: seed triangle — todo.appendHead(t0)
t1 = m.triangle(v1, v0, v3)    # 1: shares edge (v0,v1) with t0
t2 = m.triangle(v0, v2, v3)    # 2: shares edge (v0,v2) with t0; also reachable via t1

# The hub edge (v0,v1) is interior: shared by t0 and t1.
m.assert_edge_shared(v0, v1, 2)

# Edge (v0,v2) is interior: shared by t0 and t2.
m.assert_edge_shared(v0, v2, 2)

# Edge (v1,v3) is boundary: only t1.
m.assert_edge_shared(v1, v3, 1)

# All three triangles form a single connected component — the BFS from t0 reaches t1 and t2.
# Euler: V=4, E=6 (3 interior + 3 boundary), F=3, chi = 4 - 6 + 3 = 1 (open disk).
m.assert_euler_characteristic(v=4, e=6, f=3, chi=1)
