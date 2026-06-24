"""Me623 — Basic_TMesh.removeRegion branch 4: region_traversal_order.

MeshFix `Basic_TMesh.removeRegion` Branch 4 (*region_traversal_order*)
@ line 1210:
  'for (n = toRemove.tail(); n != NULL; n = n->prev())'
  — after BFS collects all triangles within radius L of center C, the region
  is traversed from the tail of the list (reverse FIFO / LIFO order) to
  process each member for removal. This branch fires whenever the removal
  region contains multiple triangles, demonstrating the deterministic reverse-
  FIFO traversal that ensures consistent unlink order.

Geometry: five triangles all with opposite vertices within L=3.0 of center
C=(0,0,0). The region forms a connected fan so that BFS enqueues them in
FIFO order (t0→t1→t2→t3→t4), but the tail-traversal loop processes them in
reverse (t4→t3→t2→t1→t0), triggering Branch 4 for each member after the
first.

Vertices:
  c  = (0, 0, 0)  — center C (hub of fan)
  v0 = (2, 0, 0)  — fan rim; dist=2.0 <= L=3.0
  v1 = (1, 2, 0)  — fan rim; dist=sqrt(5)~2.24 <= L=3.0
  v2 = (-1, 2, 0) — fan rim; dist=sqrt(5)~2.24 <= L=3.0
  v3 = (-2, 0, 0) — fan rim; dist=2.0 <= L=3.0
  v4 = (-1,-2, 0) — fan rim; dist=sqrt(5)~2.24 <= L=3.0
  v5 = (1, -2, 0) — fan rim; dist=sqrt(5)~2.24 <= L=3.0

Triangles (fan from C):
  t0 = (c, v0, v1)  — enqueued first
  t1 = (c, v1, v2)  — enqueued second
  t2 = (c, v2, v3)  — enqueued third
  t3 = (c, v3, v4)  — enqueued fourth
  t4 = (c, v4, v5)  — enqueued fifth; tail → first reversed

All interior edges share c with a rim vertex; rim edges are boundary.
Interior shared edges (c,vN): each appears in two adjacent fan triangles.

Edges by incidence:
  (c,v0): t0 → n=1  (boundary — open fan edge)
  (c,v1): t0,t1 → n=2
  (c,v2): t1,t2 → n=2
  (c,v3): t2,t3 → n=2
  (c,v4): t3,t4 → n=2
  (c,v5): t4 → n=1  (boundary — open fan edge)
  (v0,v1): t0 → n=1
  (v1,v2): t1 → n=1
  (v2,v3): t2 → n=1
  (v3,v4): t3 → n=1
  (v4,v5): t4 → n=1

V=7, E=11, F=5, chi=7-11+5=1 (open disk).
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(
    catalog_id="Me623",
    title="removeRegion region_traversal_order: 5-triangle fan from C=(0,0,0) all within L=3.0; BFS enqueues t0→t4 FIFO, tail-traversal processes in reverse order (Branch 4)",
    defect_class="radial_region_removal",
)

c  = m.vertex( 0.0,  0.0, 0.0)  # 0 — center C (fan hub)
v0 = m.vertex( 2.0,  0.0, 0.0)  # 1 — rim; dist=2.0 <= L=3.0
v1 = m.vertex( 1.0,  2.0, 0.0)  # 2 — rim; dist=sqrt(5)~2.24 <= L=3.0
v2 = m.vertex(-1.0,  2.0, 0.0)  # 3 — rim; dist=sqrt(5)~2.24 <= L=3.0
v3 = m.vertex(-2.0,  0.0, 0.0)  # 4 — rim; dist=2.0 <= L=3.0
v4 = m.vertex(-1.0, -2.0, 0.0)  # 5 — rim; dist=sqrt(5)~2.24 <= L=3.0
v5 = m.vertex( 1.0, -2.0, 0.0)  # 6 — rim; dist=sqrt(5)~2.24 <= L=3.0

# Fan triangles — BFS enqueue order t0→t4.
t0 = m.triangle(c, v0, v1)  # 0: first enqueued
t1 = m.triangle(c, v1, v2)  # 1
t2 = m.triangle(c, v2, v3)  # 2
t3 = m.triangle(c, v3, v4)  # 3
t4 = m.triangle(c, v4, v5)  # 4: last enqueued; first traversed from tail

# Interior (shared) edges: adjacent fan spokes — n=2.
m.assert_edge_shared(c, v1, 2)  # (0,2): t0 and t1
m.assert_edge_shared(c, v2, 2)  # (0,3): t1 and t2
m.assert_edge_shared(c, v3, 2)  # (0,4): t2 and t3
m.assert_edge_shared(c, v4, 2)  # (0,5): t3 and t4

# Boundary edges (open fan edges and rim edges) — n=1.
m.assert_edge_shared(c, v0, 1)   # (0,1): open fan edge
m.assert_edge_shared(c, v5, 1)   # (0,6): open fan edge
m.assert_edge_shared(v0, v1, 1)  # (1,2): rim
m.assert_edge_shared(v1, v2, 1)  # (2,3): rim
m.assert_edge_shared(v2, v3, 1)  # (3,4): rim
m.assert_edge_shared(v3, v4, 1)  # (4,5): rim
m.assert_edge_shared(v4, v5, 1)  # (5,6): rim

# All rim vertices within L=3.0 of center C — each would pass the distance check.
# dist(v0,C)=2.0, dist(v1,C)=sqrt(5)~2.24, ..., dist(v5,C)=sqrt(5)~2.24 — all < 3.0.
m.assert_vertex_pair_distance_lt(v0, c, 3.0)  # dist=2.0
m.assert_vertex_pair_distance_lt(v1, c, 3.0)  # dist~2.24
m.assert_vertex_pair_distance_lt(v2, c, 3.0)  # dist~2.24
m.assert_vertex_pair_distance_lt(v3, c, 3.0)  # dist=2.0
m.assert_vertex_pair_distance_lt(v4, c, 3.0)  # dist~2.24
m.assert_vertex_pair_distance_lt(v5, c, 3.0)  # dist~2.24

# Euler: V=7, E=11, F=5, chi=1 (open disk).
m.assert_euler_characteristic(7, 11, 5, 1)
