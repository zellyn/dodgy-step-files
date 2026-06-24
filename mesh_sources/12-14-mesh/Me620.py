"""Me620 — Basic_TMesh.removeRegion branch 1: neighbor_t1_distance_check.

MeshFix `Basic_TMesh.removeRegion` Branch 1 (*neighbor_t1_distance_check*)
@ line 1202:
  'if (!VISITED(t->t1) && s->oppositeVertex(t->e1)->distance(center) <= L)'
  — while BFS-expanding the removal region, the algorithm checks the neighbor
  reachable through edge e1 of the current seed triangle. If that neighbor is
  not yet visited AND its opposite vertex is within radius L of the center
  point, it is added to the removal list.

Geometry: four triangles where seed t0 shares its e1 edge with neighbor t1,
and the opposite vertex of t1 across that edge lies within radius L=2.5 of
center C=(0,0,0).

Vertices:
  c  = (0, 0, 0)  — center C (also a corner of the seed triangle)
  v0 = (1, 0, 0)  — seed base
  v1 = (0, 1, 0)  — seed base
  n1 = (1, 1, 0)  — t1 opposite vertex; dist(n1,C)=sqrt(2)~1.414 <= L=2.5
  v2 = (2, 0, 0)  — context vertex
  v3 = (0, 2, 0)  — context vertex

Triangles:
  t0 = (c, v0, v1)   — seed; e1 edge = (c,v0) shared with t1
  t1 = (c, n1, v0)   — e1-neighbor; opposite vertex n1 within L of C
  t2 = (c, v1, v2)   — context
  t3 = (v1, v3, v2)  — context

Edges by incidence:
  (c,v0): t0,t1 → n=2  (shared/interior)
  (c,v1): t0,t2 → n=2  (shared/interior)
  (v1,v2): t2,t3 → n=2  (shared/interior)
  (v0,v1): t0 → n=1  (boundary)
  (c,n1): t1 → n=1  (boundary)
  (n1,v0): t1 → n=1  (boundary)
  (c,v2): t2 → n=1  (boundary)
  (v1,v3): t3 → n=1  (boundary)
  (v3,v2): t3 → n=1  (boundary)

V=6, E=9, F=4, chi=6-9+4=1 (open disk).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me620",
    title="removeRegion neighbor_t1_distance_check: seed t0 e1-neighbor t1 has opposite vertex n1 at distance sqrt(2)~1.41 from center C=(0,0,0) <= L=2.5 (Branch 1)",
    defect_class="radial_region_removal",
)

c  = m.vertex(0.0, 0.0, 0.0)  # 0 — center C
v0 = m.vertex(1.0, 0.0, 0.0)  # 1 — seed base
v1 = m.vertex(0.0, 1.0, 0.0)  # 2 — seed base
n1 = m.vertex(1.0, 1.0, 0.0)  # 3 — t1 opposite vertex; dist=sqrt(2)~1.41
v2 = m.vertex(2.0, 0.0, 0.0)  # 4 — context vertex
v3 = m.vertex(0.0, 2.0, 0.0)  # 5 — context vertex

# Triangles.
t0 = m.triangle(c, v0, v1)    # 0: seed; e1=(c,v0) shared with t1
t1 = m.triangle(c, n1, v0)    # 1: e1-neighbor; n1 opposite to shared edge (c,v0)
t2 = m.triangle(c, v1, v2)    # 2: context
t3 = m.triangle(v1, v3, v2)   # 3: context

# Interior (shared) edges — n=2.
m.assert_edge_shared(c, v0, 2)   # (0,1): t0 and t1
m.assert_edge_shared(c, v1, 2)   # (0,2): t0 and t2
m.assert_edge_shared(v1, v2, 2)  # (2,4): t2 and t3

# Boundary edges — n=1.
m.assert_edge_shared(v0, v1, 1)  # (1,2): t0 outer
m.assert_edge_shared(c, n1, 1)   # (0,3): t1 outer
m.assert_edge_shared(n1, v0, 1)  # (1,3): t1 outer
m.assert_edge_shared(c, v2, 1)   # (0,4): t2 outer
m.assert_edge_shared(v1, v3, 1)  # (2,5): t3 outer
m.assert_edge_shared(v3, v2, 1)  # (4,5): t3 outer

# Key assertion: n1 opposite vertex within radius L=2.5 of center C — Branch 1.
# dist(n1, C) = sqrt(1^2 + 1^2 + 0^2) = sqrt(2) ~ 1.414 < 2.5
m.assert_vertex_pair_distance_lt(n1, c, 2.5)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
