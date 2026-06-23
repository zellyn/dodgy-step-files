"""Me223 — eulerUpdate_triangle_adjacency_e3: BFS enqueues t3 (e3 neighbor) (Branch 4).

MeshFix `Basic_TMesh.eulerUpdate` Branch 4 (*triangle_adjacency_e3*) @ line 1758:
  't3 != NULL && !IS_BIT(s, 5)' — t3 (edge e3 neighbor) unvisited; add to queue.

In eulerUpdate's BFS, each visited triangle checks its three edge-neighbors.
Branch 4 fires when the e3 neighbor exists and hasn't been visited yet. The seed
triangle (t0) is adjacent to t3 via its third edge slot. BFS enqueues t3 and
marks it as belonging to the same shell as t0.

Geometry: two adjacent triangles sharing edge (v0, v1). The BFS step from t0
enqueues t1 via the e3 slot — confirming the e3-adjacency branch fires.

  t0 = (v0, v1, v2)  seed; e3 = edge (v0,v1) shared with t1
  t1 = (v1, v0, v3)  e3 neighbor; shares (v0,v1) with t0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me223",
             title="eulerUpdate_triangle_adjacency_e3: BFS enqueues unvisited e3 neighbor",
             defect_class="euler_update_bfs_adjacency")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(0.5, -1.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)   # 0 — seed; e3 = (v0,v1)
t1 = m.triangle(v1, v0, v3)   # 1 — shares edge (v0,v1) with t0 (note reversed for opposite normal)

# The shared edge (v0,v1) is interior — incident on 2 triangles.
m.assert_edge_shared(v0, v1, 2)

# Boundary edges each appear on exactly 1 triangle.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
