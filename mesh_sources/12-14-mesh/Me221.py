"""Me221 — eulerUpdate_triangle_adjacency_e1: BFS enqueues t1 (e1 neighbor) (Branch 2).

MeshFix `Basic_TMesh.eulerUpdate` Branch 2 (*triangle_adjacency_e1*) @ line 1756:
  't1 != NULL && !IS_BIT(s, 5)' — t1 (edge e1 neighbor) unvisited; add to queue.

In eulerUpdate's BFS, each visited triangle checks its three edge-neighbors
(t1, t2, t3). Branch 2 fires when the e1 neighbor exists and hasn't been
visited yet. The seed triangle (t0) is adjacent to t1 via its first edge slot.
BFS then marks t1 as visited, keeping it in the same shell as t0.

Geometry: two adjacent triangles sharing edge (v1, v2). The first BFS step
from t0 enqueues t1 via the e1 slot — confirming the e1-adjacency branch fires.
Both triangles end up in the same shell.

  t0 = (v0, v1, v2)  seed triangle; e1 = edge (v1,v2) shared with t1
  t1 = (v1, v3, v2)  e1 neighbor; reachable from t0 via BFS
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me221",
             title="eulerUpdate_triangle_adjacency_e1: BFS enqueues unvisited e1 neighbor",
             defect_class="euler_update_bfs_adjacency")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)   # 0 — seed; e1 = (v1,v2)
t1 = m.triangle(v1, v3, v2)   # 1 — shares edge (v1,v2) with t0

# The shared edge (v1,v2) is interior — incident on 2 triangles (t0 and t1).
m.assert_edge_shared(v1, v2, 2)

# t1 IS reachable from t0 through edge (v1,v2) — both in same shell.
# Boundary edges each appear on exactly 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
