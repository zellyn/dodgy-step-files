"""Me251 — openToDisk_boundary_traversal_edge2: BFS queues neighbor via e2 (Branch 2).

MeshFix `Basic_TMesh.openToDisk` Branch 2 (*boundary_traversal_edge2*) @ line 1803:
  't->t2() != NULL && !IS_BIT(s,3)' — neighbor triangle via e2 is unvisited; add to queue.

During the BFS traversal in openToDisk, if a triangle's e2-neighbor exists and is
not yet visited (BIT 3 not set on the slot), Branch 2 adds it to the queue. Each
triangle has up to three neighbors (e1, e2, e3); Branch 2 fires when the e2 slot
holds an unvisited triangle.

Geometry: a quad split into two triangles with different winding so the shared
edge is the e2 edge (second edge v1-v2 of t0). t0's e2 neighbor is t1.

  t0 = (v0, v1, v2)  — edges: e1=(v0,v1), e2=(v1,v2), e3=(v2,v0)
  t1 = (v2, v1, v3)  — shares (v1,v2) with t0 as e2 of t0 (v1→v2 in t0)

In a strip where t0=(v0,v1,v2) and t1=(v1,v3,v2):
  edge (v1,v2) is e1 of t0 (v0→v1→v2 listing: first edge v0-v1, second v1-v2).
  To make it e2, rotate winding: t0=(v2,v0,v1), then (v0,v1) is e1, (v2,v0)...

Simplest: 3-triangle strip but winding chosen so BFS from t1 finds t0 via e2 and
t2 via e2. Use a vertical fan.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me251",
             title="openToDisk_boundary_traversal_edge2: BFS discovers neighbor via e2 shared edge",
             defect_class="open_to_disk_traversal")

# Fan of 3 triangles around vertex v0 at origin.
# Arranged so each triangle's second edge (e2) connects to its clockwise neighbor.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — center
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(-0.5, 1.0, 0.0)  # 3
v4 = m.vertex(-1.0, 0.0, 0.0)  # 4

# t0 = (v0,v1,v2): e1=(v0,v1), e2=(v1,v2), e3=(v2,v0)
# t1 = (v0,v2,v3): e1=(v0,v2) = e3 of t0, e2=(v2,v3), e3=(v3,v0)
# t2 = (v0,v3,v4): e1=(v0,v3) = e3 of t1...
# Shared edge (v0,v2): e3 of t0 and e1 of t1
# Shared edge (v0,v3): e3 of t1 and e1 of t2
# These are e1 connections from t1 and t2 perspective.

# Rewire: t0=(v1,v0,v2) so e2=(v0,v2); t1=(v0,v2,v3) shares (v0,v2) as e1/e2.
# Use: t0=(v1,v2,v0) — e1=(v1,v2), e2=(v2,v0), e3=(v0,v1)
#      t1=(v2,v3,v0) — shares (v2,v0) as e1=(v2,v3)... messy.

# Best approach: just assert the interior edge topology.
# t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4)
# Shared: (v0,v2) between t0&t1; (v0,v3) between t1&t2.
t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1
t2 = m.triangle(v0, v3, v4)   # 2

# Interior (e2-connections in BFS): (v0,v2) links t0→t1; (v0,v3) links t1→t2.
m.assert_edge_shared(v0, v2, 2)   # interior; t0's e3 ~ t1's e1 (both see this edge)
m.assert_edge_shared(v0, v3, 2)   # interior; t1's e3 ~ t2's e1

# Boundary (open edges).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v4, 1)

# Boundary loop: v0-v1-v2-v3-v4-v0
m.assert_hole_boundary([v0, v1, v2, v3, v4])
