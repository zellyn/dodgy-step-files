"""Me622 — Basic_TMesh.removeRegion branch 3: neighbor_t3_distance_check.

MeshFix `Basic_TMesh.removeRegion` Branch 3 (*neighbor_t3_distance_check*)
@ line 1206:
  'if (!VISITED(t->t3) && s->oppositeVertex(t->e3)->distance(center) <= L)'
  — during BFS region expansion, the algorithm checks the neighbor reachable
  through edge e3 of the current seed triangle. If unvisited AND its opposite
  vertex is within radius L of center, it is added to the removal list.
  This branch fires specifically for the e3 (third) adjacency of the seed.

Geometry: four triangles where seed t0 shares its e3 edge (v0,v1) with
neighbor t3, and t3's opposite vertex n3 lies within L=2.5 of center C.
The e1 and e2 sides of t0 are on the mesh boundary, isolating Branch 3.

Vertices:
  v0 = (1, 0, 0)  — seed base; e3 edge is (v0,v1) shared with t3
  v1 = (0, 1, 0)  — seed base; e3 edge
  c  = (0, 0, 0)  — seed apex (also center C of the removal region)
  n3 = (1, 1, 0)  — t3 opposite vertex; dist(n3,C)=sqrt(2)~1.414 <= L=2.5
  v2 = (2, 1, 0)  — context vertex
  v3 = (-1, 2, 0) — context vertex

Triangles:
  t0 = (c, v0, v1)   — seed; e3 edge = (v0,v1) shared with t3
  t3 = (v0, n3, v1)  — e3-neighbor; n3 opposite to shared edge (v0,v1)
  t4 = (v0, v2, n3)  — context
  t5 = (v1, n3, v3)  — context

Edges by incidence:
  (v0,v1): t0,t3 → n=2  (shared/e3)
  (v0,n3): t3,t4 → n=2  (shared)
  (n3,v1): t3,t5 → n=2  (shared)
  (c,v0): t0 → n=1  (boundary)
  (c,v1): t0 → n=1  (boundary)
  (v0,v2): t4 → n=1  (boundary)
  (v2,n3): t4 → n=1  (boundary)
  (v1,v3): t5 → n=1  (boundary)
  (n3,v3): t5 → n=1  (boundary)

V=6, E=9, F=4, chi=6-9+4=1 (open disk).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me622",
    title="removeRegion neighbor_t3_distance_check: seed t0 e3-neighbor t3 has opposite vertex n3 at distance sqrt(2)~1.41 from center C=(0,0,0) <= L=2.5 (Branch 3)",
    defect_class="radial_region_removal",
)

v0 = m.vertex(1.0,  0.0, 0.0)  # 0 — seed base; e3 edge is (v0,v1)
v1 = m.vertex(0.0,  1.0, 0.0)  # 1 — seed base; e3 edge
c  = m.vertex(0.0,  0.0, 0.0)  # 2 — seed apex = center C
n3 = m.vertex(1.0,  1.0, 0.0)  # 3 — t3 opposite vertex; dist=sqrt(2)~1.41
v2 = m.vertex(2.0,  1.0, 0.0)  # 4 — context vertex
v3 = m.vertex(-1.0, 2.0, 0.0)  # 5 — context vertex

# Triangles.
t0 = m.triangle(c, v0, v1)    # 0: seed; e3=(v0,v1) shared with t3
t3 = m.triangle(v0, n3, v1)   # 1: e3-neighbor; n3 opposite to (v0,v1)
t4 = m.triangle(v0, v2, n3)   # 2: context
t5 = m.triangle(v1, n3, v3)   # 3: context

# Interior (shared) edges — n=2.
m.assert_edge_shared(v0, v1, 2)  # (0,1): t0 and t3 — the e3 shared edge
m.assert_edge_shared(v0, n3, 2)  # (0,3): t3 and t4
m.assert_edge_shared(n3, v1, 2)  # (1,3): t3 and t5

# Boundary edges — n=1.
m.assert_edge_shared(c, v0, 1)   # (0,2): t0 outer (e1 side — boundary)
m.assert_edge_shared(c, v1, 1)   # (1,2): t0 outer (e2 side — boundary)
m.assert_edge_shared(v0, v2, 1)  # (0,4): t4 outer
m.assert_edge_shared(v2, n3, 1)  # (3,4): t4 outer
m.assert_edge_shared(v1, v3, 1)  # (1,5): t5 outer
m.assert_edge_shared(n3, v3, 1)  # (3,5): t5 outer

# Key assertion: n3 opposite vertex within radius L=2.5 of center C — Branch 3.
# dist(n3, C) = sqrt((1-0)^2 + (1-0)^2) = sqrt(2) ~ 1.414 < 2.5
m.assert_vertex_pair_distance_lt(n3, c, 2.5)

# Euler: V=6, E=9, F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
