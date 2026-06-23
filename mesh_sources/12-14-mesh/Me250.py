"""Me250 — openToDisk_boundary_traversal_edge1: BFS queues neighbor via e1 (Branch 1).

MeshFix `Basic_TMesh.openToDisk` Branch 1 (*boundary_traversal_edge1*) @ line 1801:
  't->t1() != NULL && !IS_BIT(s,3)' — neighbor triangle via e1 is unvisited; add to queue.

openToDisk performs a BFS over all triangles to label boundary edges. In each BFS
step, if a triangle's e1-neighbor exists and is not yet visited (BIT 3 not set), it
is appended to the traversal list. Branch 1 fires for every triangle that has a
valid e1-adjacent triangle not yet seen.

Geometry: a fan of three triangles sharing a central vertex. The BFS starts from t0
and discovers t1 via e1 (shared edge v0-v1), then t2 via t1's neighbor.

  v0 = (0,0,0)  v1 = (1,0,0)  v2 = (0.5,1,0)
  v3 = (1.5,1,0)  v4 = (2,0,0)
  t0 = (v0,v1,v2)  t1 = (v1,v4,v3) [shares nothing with t0 yet — separate piece
  for clarity; connected via v1 only for adjacency through shared edge v1-v3]

Simpler: strip of 3 triangles where each triangle has a t1-neighbor:
  t0=(v0,v1,v2), t1=(v1,v3,v2) — share edge (v1,v2) = e1 of t0
  t2=(v1,v4,v3) — share edge (v1,v3) = e1 of t1
BFS from t0 → pushes t1 via e1 (Branch 1). From t1 → pushes t2 via e1 (Branch 1 again).
All interior edges shared by exactly 2 triangles; boundary edges by 1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me250",
             title="openToDisk_boundary_traversal_edge1: BFS discovers neighbor via e1 shared edge",
             defect_class="open_to_disk_traversal")

# Three-triangle strip: each pair shares an interior edge.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3
v4 = m.vertex(2.0, 0.0, 0.0)   # 4

# t0: triangle with e1-neighbor t1 via shared interior edge (v1,v2).
t0 = m.triangle(v0, v1, v2)   # 0
# t1: adjacent to t0 via (v1,v2); also has e1-neighbor t2 via (v1,v3).
t1 = m.triangle(v1, v3, v2)   # 1
# t2: adjacent to t1 via (v1,v3); outermost triangle.
t2 = m.triangle(v1, v4, v3)   # 2

# Interior edges (shared by exactly 2 triangles — not boundary).
m.assert_edge_shared(v1, v2, 2)   # between t0 and t1 — e1 of t0
m.assert_edge_shared(v1, v3, 2)   # between t1 and t2 — e1 of t1

# Boundary edges (shared by exactly 1 triangle — the open boundary).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# Boundary loop: v0-v1-v4-v3-v2-v0
m.assert_hole_boundary([v0, v1, v4, v3, v2])
