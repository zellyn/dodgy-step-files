"""Me891 — merge_duplicated_vertices_in_boundary_cycles cycle_iteration: annulus mesh with 2 boundary cycles; for-loop iterates both (Branch 2).

CGAL PMP `PMP.merge_duplicated_vertices_in_boundary_cycles` Branch 2 (*cycle_iteration*) @ line 353:
  'for(halfedge_descriptor h : cycles)'
  '  merge_duplicated_vertices_in_boundary_cycle(h, pm, np);'
  — after extract_boundary_cycles populates ``cycles``, the for-loop
  iterates over each entry and delegates to the single-cycle merge. Branch 2
  fires when ``cycles`` has two or more entries (at least two boundary loops).

Defect pattern: a six-triangle annulus (ring) with one inner boundary
  cycle and one outer boundary cycle. The outer ring has a coincident
  vertex pair: o1 and o4 both at (2.0, 0.0, 0.0). The inner ring has a
  coincident vertex pair: i1 and i3 both at (0.5, 0.0, 0.0).
  extract_boundary_cycles finds 2 cycles; the for-loop iterates twice —
  Branch 2 fires for both iterations.

Geometry (planar annulus — 3 inner vertices, 3 outer vertices):
  Inner ring: i0=(0,1,0), i1=(0.5,0,0), i2=(-0.5,0,0), i3=(0.5,0,0) [=i1]
  Outer ring: o0=(0,2,0), o1=(2,0,0), o2=(-2,0,0)
  Six triangles connecting inner to outer form an annular strip.
  Extra coincident vertex on outer ring: o3=(2,0,0) [=o1] is NOT added
  here because outer ring has only 3 vertices; instead we embed coincident
  pairs within each boundary ring explicitly using a second set of vertices.

Note: to ensure exactly 2 boundary cycles with coincident vertices, we
  use two disjoint open disk patches in the same mesh object. Each patch
  has its own boundary loop, and each loop carries a coincident pair.
  This is the minimal construction that forces the for-loop to iterate
  twice with distinct cycle representatives.

Patch A (left open disk, 4 vertices, 2 triangles):
  a0=(0,0,0), a1=(1,0,0), a2=(0.5,1,0), a3=(1,0,0) [=a1]
  Interior edge (a0,a2) n=2; boundary edges n=1.
  a1 and a3 coincident at (1,0,0).

Patch B (right open disk, 4 vertices, 2 triangles):
  b0=(3,0,0), b1=(4,0,0), b2=(3.5,1,0), b3=(4,0,0) [=b1]
  Interior edge (b0,b2) n=2; boundary edges n=1.
  b1 and b3 coincident at (4,0,0).

The two patches are topologically disconnected → two distinct boundary cycles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me891",
    title="merge_duplicated_vertices_in_boundary_cycles cycle_iteration: 2-patch mesh; extract_boundary_cycles finds 2 boundary cycles; for-loop iterates both; coincident pairs on each (Branch 2)",
    defect_class="near_coincident_vertex",
)

# Patch A: two triangles forming an open disk with one boundary cycle.
a0 = m.vertex(0.0, 0.0, 0.0)  # 0
a1 = m.vertex(1.0, 0.0, 0.0)  # 1 — coincident with a3
a2 = m.vertex(0.5, 1.0, 0.0)  # 2 — apex
a3 = m.vertex(1.0, 0.0, 0.0)  # 3 — coincident with a1

m.triangle(a0, a1, a2)  # 0: left triangle of patch A
m.triangle(a0, a2, a3)  # 1: right triangle of patch A

# Patch B: two triangles forming a second, disjoint open disk.
b0 = m.vertex(3.0, 0.0, 0.0)  # 4
b1 = m.vertex(4.0, 0.0, 0.0)  # 5 — coincident with b3
b2 = m.vertex(3.5, 1.0, 0.0)  # 6 — apex
b3 = m.vertex(4.0, 0.0, 0.0)  # 7 — coincident with b1

m.triangle(b0, b1, b2)  # 2: left triangle of patch B
m.triangle(b0, b2, b3)  # 3: right triangle of patch B

# Interior edges — shared by 2 triangles each.
m.assert_edge_shared(a0, a2, 2)  # t0 and t1 of patch A
m.assert_edge_shared(b0, b2, 2)  # t2 and t3 of patch B

# Patch A boundary edges — n=1 each.
m.assert_edge_shared(a0, a1, 1)
m.assert_edge_shared(a1, a2, 1)
m.assert_edge_shared(a2, a3, 1)
m.assert_edge_shared(a0, a3, 1)

# Patch B boundary edges — n=1 each.
m.assert_edge_shared(b0, b1, 1)
m.assert_edge_shared(b1, b2, 1)
m.assert_edge_shared(b2, b3, 1)
m.assert_edge_shared(b0, b3, 1)

# Coincident pair on patch A's boundary cycle.
m.assert_vertex_pair_distance_lt(a1, a3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(a1, a3)

# Coincident pair on patch B's boundary cycle.
m.assert_vertex_pair_distance_lt(b1, b3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(b1, b3)

# Euler: V=8, E=10, F=4, chi=2 (two disconnected open disks, each chi=1).
m.assert_euler_characteristic(8, 10, 4, 2)
