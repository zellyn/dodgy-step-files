"""Me1179 — triangulate_hole.main planarity_check_needed: hole boundary bbox
  triggers max_squared_distance computation for CDT2 planarity test (Branch 3).

CGAL PMP `triangulate_hole.main` Branch 3 (*planarity_check_needed*)
  @ line 200:
  'double max_squared_distance = 0; ... max_squared_distance = ...' —
  When use_cdt is true (CDT2 path available), triangulate_hole.main computes
  the bounding box of the hole boundary and measures the maximum squared
  distance from each boundary vertex to the best-fit plane. If this distance
  is within the threshold, the hole qualifies for the faster CDT2 algorithm.
  Branch 3 fires as the planarity computation is performed on the hole boundary.

Defect pattern: a planar pentagon hole — five hat triangles surrounding a
  regular pentagonal hole in the z=0 plane. The hole boundary vertices all
  lie exactly on the z=0 plane, so max_squared_distance = 0.0, which is below
  any positive threshold. Branch 3 fires as the bbox+distance computation is
  performed; the planarity check passes and CDT2 is eligible to run.

Geometry: regular pentagon hole with five hat triangles.
  p0=(0,0,0), p1=(2,0,0), p2=(2.6,1.9,0), p3=(1,3.1,0), p4=(-0.6,1.9,0)
  o0..o4: outer hat vertices; five hat triangles.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(
    catalog_id="Me1179",
    title="triangulate_hole.main planarity_check_needed: bbox+max_squared_distance computed for CDT2 planarity test; planar pentagon hole (Branch 3)",
    defect_class="boundary_hole",
)

# Regular pentagon hole corners (in z=0 plane, CCW)
p0 = m.vertex(0.0,   0.0,   0.0)   # 0
p1 = m.vertex(2.0,   0.0,   0.0)   # 1
p2 = m.vertex(2.6,   1.9,   0.0)   # 2
p3 = m.vertex(1.0,   3.1,   0.0)   # 3
p4 = m.vertex(-0.6,  1.9,   0.0)   # 4

# Hat outer vertices (pointing away from hole)
o0 = m.vertex(1.0,  -1.2,   0.0)   # 5 — south
o1 = m.vertex(3.6,   0.8,   0.0)   # 6 — SE
o2 = m.vertex(3.0,   3.0,   0.0)   # 7 — NE
o3 = m.vertex(1.0,   4.3,   0.0)   # 8 — N
o4 = m.vertex(-1.6,  3.0,   0.0)   # 9 — NW

# Five hat triangles
t0 = m.triangle(p0, o0, p1)   # 0
t1 = m.triangle(p1, o1, p2)   # 1
t2 = m.triangle(p2, o2, p3)   # 2
t3 = m.triangle(p3, o3, p4)   # 3
t4 = m.triangle(p4, o4, p0)   # 4

# Pentagon hole boundary (n=1)
m.assert_edge_shared(p0, p1, 1)
m.assert_edge_shared(p1, p2, 1)
m.assert_edge_shared(p2, p3, 1)
m.assert_edge_shared(p3, p4, 1)
m.assert_edge_shared(p0, p4, 1)

m.assert_hole_boundary([p0, p1, p2, p3, p4])

# Hat outer edges (n=1 each)
m.assert_edge_shared(p0, o0, 1)
m.assert_edge_shared(p1, o0, 1)
m.assert_edge_shared(p1, o1, 1)
m.assert_edge_shared(p2, o1, 1)
m.assert_edge_shared(p2, o2, 1)
m.assert_edge_shared(p3, o2, 1)
m.assert_edge_shared(p3, o3, 1)
m.assert_edge_shared(p4, o3, 1)
m.assert_edge_shared(p4, o4, 1)
m.assert_edge_shared(p0, o4, 1)

# Open mesh with pentagon hole: V=10, E=15, F=5, chi=0
m.assert_euler_characteristic(10, 15, 5, 0)
