"""Me621 — Basic_TMesh.removeRegion branch 2: neighbor_t2_distance_check.

MeshFix `Basic_TMesh.removeRegion` Branch 2 (*neighbor_t2_distance_check*)
@ line 1204:
  'if (!VISITED(t->t2) && s->oppositeVertex(t->e2)->distance(center) <= L)'
  — during BFS region expansion, the algorithm checks the neighbor reachable
  through edge e2 of the current seed triangle. If unvisited AND its opposite
  vertex is within radius L of the center, it is added to the removal list.
  This branch fires for the e2 (second) adjacency of the seed triangle.

Geometry: four triangles where seed t0 shares its e2 edge with neighbor t2,
and the opposite vertex of t2 across that edge is within L=2.5 of center
C=(0,0,0). The e1 neighbor is absent (boundary), isolating Branch 2.

Vertices:
  c  = (0, 0, 0)  — center C (corner of seed)
  v0 = (1, 0, 0)  — seed vertex
  v1 = (0, 1, 0)  — seed vertex; e2 edge is (c,v1) shared with t2
  n2 = (-1, 1, 0) — t2 opposite vertex; dist(n2,C)=sqrt(2)~1.414 <= L=2.5
  v2 = (2, 1, 0)  — context vertex
  v3 = (1, 2, 0)  — context vertex

Triangles:
  t0 = (c, v0, v1)   — seed; e2 edge = (c,v1) shared with t2
  t2 = (c, v1, n2)   — e2-neighbor; n2 opposite to shared edge (c,v1)
  t3 = (v0, v2, v1)  — context (fills e1 side)
  t4 = (v0, v3, v2)  — context

Edges by incidence:
  (c,v1): t0,t2 → n=2  (shared)
  (v0,v1): t0,t3 → n=2  (shared)
  (v0,v2): t3,t4 → n=2  (shared)
  (c,v0): t0 → n=1  (boundary)
  (c,n2): t2 → n=1  (boundary)
  (n2,v1): t2 → n=1  (boundary)
  (v1,v2): t3 → n=1  (boundary)
  (v0,v3): t4 → n=1  (boundary)
  (v3,v2): t4 → n=1  (boundary)

V=6, E=9, F=4, chi=6-9+4=1 (open disk).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me621",
    title="removeRegion neighbor_t2_distance_check: seed t0 e2-neighbor t2 has opposite vertex n2 at distance sqrt(2)~1.41 from center C=(0,0,0) <= L=2.5 (Branch 2)",
    defect_class="radial_region_removal",
)

c  = m.vertex( 0.0, 0.0, 0.0)  # 0 — center C
v0 = m.vertex( 1.0, 0.0, 0.0)  # 1 — seed vertex
v1 = m.vertex( 0.0, 1.0, 0.0)  # 2 — seed vertex; e2 edge is (c,v1)
n2 = m.vertex(-1.0, 1.0, 0.0)  # 3 — t2 opposite vertex; dist=sqrt(2)~1.41
v2 = m.vertex( 2.0, 1.0, 0.0)  # 4 — context vertex
v3 = m.vertex( 1.0, 2.0, 0.0)  # 5 — context vertex

# Triangles.
t0 = m.triangle(c, v0, v1)    # 0: seed; e2 edge = (c,v1) shared with t2
t2 = m.triangle(c, v1, n2)    # 1: e2-neighbor; n2 opposite to shared edge (c,v1)
t3 = m.triangle(v0, v2, v1)   # 2: context (fills e1-side neighbor slot)
t4 = m.triangle(v0, v3, v2)   # 3: context

# Interior (shared) edges — n=2.
m.assert_edge_shared(c, v1, 2)   # (0,2): t0 and t2 — the e2 shared edge
m.assert_edge_shared(v0, v1, 2)  # (1,2): t0 and t3
m.assert_edge_shared(v0, v2, 2)  # (1,4): t3 and t4

# Boundary edges — n=1.
m.assert_edge_shared(c, v0, 1)   # (0,1): t0 outer
m.assert_edge_shared(c, n2, 1)   # (0,3): t2 outer
m.assert_edge_shared(n2, v1, 1)  # (2,3): t2 outer
m.assert_edge_shared(v1, v2, 1)  # (2,4): t3 outer
m.assert_edge_shared(v0, v3, 1)  # (1,5): t4 outer
m.assert_edge_shared(v3, v2, 1)  # (4,5): t4 outer

# Key assertion: n2 opposite vertex within radius L=2.5 of center C — Branch 2.
# dist(n2, C) = sqrt((-1)^2 + 1^2 + 0^2) = sqrt(2) ~ 1.414 < 2.5
m.assert_vertex_pair_distance_lt(n2, c, 2.5)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
