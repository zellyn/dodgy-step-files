"""Me252 — openToDisk_boundary_traversal_edge3: BFS queues neighbor via e3 (Branch 3).

MeshFix `Basic_TMesh.openToDisk` Branch 3 (*boundary_traversal_edge3*) @ line 1805:
  't->t3() != NULL && !IS_BIT(s,3)' — neighbor triangle via e3 is unvisited; add to queue.

During the BFS traversal in openToDisk, if a triangle's e3-neighbor exists and is
not yet visited, Branch 3 adds it to the queue. This is the third edge slot
(the closing edge from v2 back to v0 in triangle (v0,v1,v2)).

Geometry: a 4-triangle fan around center vertex v0. The third edge (e3 = v2→v0)
of each triangle links to the next triangle in the fan. BFS from t0 adds t1 via
e3 (Branch 3), t1 adds t2 via e3 (Branch 3), t2 adds t3 via e3 (Branch 3).

Fan layout (CCW from +X axis):
  v0 = center
  v1..v5 = rim vertices at angles 0, 72, 144, 216, 288 degrees

For simplicity use 4 triangles in a fan (not a closed ring — so there's a boundary).
"""
from step_corpus.mesh_builder import MeshFile

import math

m = MeshFile(catalog_id="Me252",
             title="openToDisk_boundary_traversal_edge3: BFS discovers neighbor via e3 shared edge",
             defect_class="open_to_disk_traversal")

# 4-triangle open fan around v0.
v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — center
v1 = m.vertex(1.0,  0.0, 0.0)   # 1 — rim at 0°
v2 = m.vertex(0.0,  1.0, 0.0)   # 2 — rim at 90°
v3 = m.vertex(-1.0, 0.0, 0.0)   # 3 — rim at 180°
v4 = m.vertex(0.0, -1.0, 0.0)   # 4 — rim at 270°
v5 = m.vertex(1.0, -0.5, 0.0)   # 5 — rim extra for open fan

# t0=(v0,v1,v2): e1=(v0,v1), e2=(v1,v2), e3=(v2,v0)
# t1=(v0,v2,v3): e1=(v0,v2) [shares e3 of t0=(v2,v0) reversed], e2=(v2,v3), e3=(v3,v0)
# t2=(v0,v3,v4): shares (v0,v3) with t1's e3
# t3=(v0,v4,v5): shares (v0,v4) with t2's e3

t0 = m.triangle(v0, v1, v2)   # 0 — e3=(v2,v0)=(v0,v2) canonical
t1 = m.triangle(v0, v2, v3)   # 1 — e3=(v3,v0)=(v0,v3) canonical; e1=(v0,v2) [e3 of t0]
t2 = m.triangle(v0, v3, v4)   # 2 — e1=(v0,v3) [e3 of t1]
t3 = m.triangle(v0, v4, v5)   # 3 — e1=(v0,v4) [e3 of t2]

# Interior edges: the shared (v0,rim) edges are each shared by 2 triangles.
m.assert_edge_shared(v0, v2, 2)   # e3 of t0 / e1 of t1
m.assert_edge_shared(v0, v3, 2)   # e3 of t1 / e1 of t2
m.assert_edge_shared(v0, v4, 2)   # e3 of t2 / e1 of t3

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v0, v5, 1)

# Boundary loop: v0 → v1 → v2 → v3 → v4 → v5 → v0
m.assert_hole_boundary([v0, v1, v2, v3, v4, v5])
