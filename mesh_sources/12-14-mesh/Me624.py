"""Me624 — Basic_TMesh.removeRegion branch 5: triangle_unlink_removal.

MeshFix `Basic_TMesh.removeRegion` Branch 5 (*triangle_unlink_removal*)
@ line 1213:
  'unlinkTriangle(s);'
  — after traversing the removal region from the tail, each collected triangle
  is detached (unlinked) from the mesh data structure. This branch fires for
  every triangle in the removal region; with a multi-triangle region all members
  are unlinked. A mesh with three connected triangles forming a complete radial
  region demonstrates the full unlink pass.

Geometry: six triangles — three central triangles forming a hexagonal region
(all within L=2.0 of center C=(0,0,0)) plus three outer triangles for
structural context. All three inner triangles are removed via unlinkTriangle.

Vertices:
  c  = (0, 0, 0)   — center C
  a0 = (1, 0, 0)   — inner rim; dist=1.0 <= L=2.0
  a1 = (0, 1, 0)   — inner rim; dist=1.0 <= L=2.0
  a2 = (-1, 0, 0)  — inner rim; dist=1.0 <= L=2.0
  b0 = (2, 1, 0)   — outer rim (context); dist=sqrt(5)~2.24 > L=2.0 (boundary)
  b1 = (-1, 2, 0)  — outer rim (context); dist=sqrt(5)~2.24 > L=2.0
  b2 = (-2,-1, 0)  — outer rim (context); dist=sqrt(5)~2.24 > L=2.0

Triangles:
  t0 = (c, a0, a1)   — inner region member 1; all verts within L
  t1 = (c, a1, a2)   — inner region member 2
  t2 = (c, a2, a0)   — inner region member 3 (closes inner fan)
  t3 = (a0, b0, a1)  — outer context triangle
  t4 = (a1, b1, a2)  — outer context triangle
  t5 = (a2, b2, a0)  — outer context triangle

All three inner triangles are within L=2.0 (all vertices dist <= 1.0 from C)
and are collected into the removal region. unlinkTriangle fires three times.

Edges by incidence:
  (c,a0): t0,t2 → n=2  (interior hub)
  (c,a1): t0,t1 → n=2  (interior hub)
  (c,a2): t1,t2 → n=2  (interior hub)
  (a0,a1): t0,t3 → n=2
  (a1,a2): t1,t4 → n=2
  (a0,a2): t2,t5 → n=2
  (a0,b0): t3 → n=1
  (b0,a1): t3 → n=1
  (a1,b1): t4 → n=1
  (b1,a2): t4 → n=1
  (a2,b2): t5 → n=1
  (b2,a0): t5 → n=1

V=7, E=12, F=6, chi=7-12+6=1 (open disk).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me624",
    title="removeRegion triangle_unlink_removal: 3-triangle inner fan from C=(0,0,0) all within L=2.0 collected into removal region; unlinkTriangle fires for each member (Branch 5)",
    defect_class="radial_region_removal",
)

c  = m.vertex( 0.0,  0.0, 0.0)  # 0 — center C (hub)
a0 = m.vertex( 1.0,  0.0, 0.0)  # 1 — inner rim; dist=1.0 <= L=2.0
a1 = m.vertex( 0.0,  1.0, 0.0)  # 2 — inner rim; dist=1.0 <= L=2.0
a2 = m.vertex(-1.0,  0.0, 0.0)  # 3 — inner rim; dist=1.0 <= L=2.0
b0 = m.vertex( 2.0,  1.0, 0.0)  # 4 — outer rim context; dist~2.24
b1 = m.vertex(-1.0,  2.0, 0.0)  # 5 — outer rim context; dist~2.24
b2 = m.vertex(-2.0, -1.0, 0.0)  # 6 — outer rim context; dist~2.24

# Inner region triangles (all within L=2.0 of C; all get unlinked).
t0 = m.triangle(c, a0, a1)   # 0: inner member 1
t1 = m.triangle(c, a1, a2)   # 1: inner member 2
t2 = m.triangle(c, a2, a0)   # 2: inner member 3
# Outer context triangles (vertices outside L; not in removal region).
t3 = m.triangle(a0, b0, a1)  # 3: outer context
t4 = m.triangle(a1, b1, a2)  # 4: outer context
t5 = m.triangle(a2, b2, a0)  # 5: outer context

# Interior (shared) edges — n=2.
m.assert_edge_shared(c, a0, 2)   # (0,1): t0 and t2
m.assert_edge_shared(c, a1, 2)   # (0,2): t0 and t1
m.assert_edge_shared(c, a2, 2)   # (0,3): t1 and t2
m.assert_edge_shared(a0, a1, 2)  # (1,2): t0 and t3
m.assert_edge_shared(a1, a2, 2)  # (2,3): t1 and t4
m.assert_edge_shared(a0, a2, 2)  # (1,3): t2 and t5

# Boundary edges — n=1.
m.assert_edge_shared(a0, b0, 1)  # (1,4): t3 outer
m.assert_edge_shared(b0, a1, 1)  # (2,4): t3 outer
m.assert_edge_shared(a1, b1, 1)  # (2,5): t4 outer
m.assert_edge_shared(b1, a2, 1)  # (3,5): t4 outer
m.assert_edge_shared(a2, b2, 1)  # (3,6): t5 outer
m.assert_edge_shared(b2, a0, 1)  # (1,6): t5 outer

# All inner vertices within L=2.0 of C — the unlink condition is met for all.
m.assert_vertex_pair_distance_lt(a0, c, 2.0)  # dist=1.0 < 2.0
m.assert_vertex_pair_distance_lt(a1, c, 2.0)  # dist=1.0 < 2.0
m.assert_vertex_pair_distance_lt(a2, c, 2.0)  # dist=1.0 < 2.0

# Euler: V=7, E=12, F=6, chi=1 (open disk).
m.assert_euler_characteristic(7, 12, 6, 1)
