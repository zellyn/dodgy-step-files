"""Me222 — eulerUpdate_triangle_adjacency_e2: BFS enqueues t2 (e2 neighbor) (Branch 3).

MeshFix `Basic_TMesh.eulerUpdate` Branch 3 (*triangle_adjacency_e2*) @ line 1757:
  't2 != NULL && !IS_BIT(s, 5)' — t2 (edge e2 neighbor) unvisited; add to queue.

In eulerUpdate's BFS, each visited triangle checks its three edge-neighbors.
Branch 3 fires when the e2 neighbor exists and hasn't been visited yet. The seed
triangle (t0) is adjacent to t2 via its second edge slot. BFS enqueues t2 and
marks it as belonging to the same shell as t0.

Geometry: two adjacent triangles sharing edge (v0, v2). The BFS step from t0
enqueues t1 via the e2 slot — confirming the e2-adjacency branch fires.

  t0 = (v0, v1, v2)  seed; e2 = edge (v2,v0) shared with t1
  t1 = (v2, v3, v0)  e2 neighbor; shares (v2,v0) with t0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me222",
             title="eulerUpdate_triangle_adjacency_e2: BFS enqueues unvisited e2 neighbor",
             defect_class="euler_update_bfs_adjacency")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.5, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)   # 0 — seed; e2 = (v2,v0)
t1 = m.triangle(v2, v3, v0)   # 1 — shares edge (v2,v0) with t0

# The shared edge (v0,v2) is interior — incident on 2 triangles.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges each appear on exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
