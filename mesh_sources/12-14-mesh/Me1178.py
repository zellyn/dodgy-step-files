"""Me1178 — triangulate_hole.main compile_time_feature_disable CDT2:
  CGAL_HOLE_FILLING_DO_NOT_USE_CDT2 macro forces use_cdt=false; quad hole
  demonstrates triangulation dispatch (Branch 2).

CGAL PMP `triangulate_hole.main` Branch 2 (*compile_time_feature_disable*)
  @ line 192:
  '#ifdef CGAL_HOLE_FILLING_DO_NOT_USE_CDT2 use_cdt = false; #endif' —
  The second branch in triangulate_hole.main is the compile-time guard that
  disables the 2D Constrained Delaunay Triangulation path. When the macro is
  defined, use_cdt is forced to false, bypassing the planarity-check+CDT2
  shortcut and routing directly to the DT3 or cubic algorithm.
  Branch 2 fires at compile time; the runtime geometry still has a hole.

Defect pattern: a quadrilateral hole surrounded by four hat triangles. With
  CDT2 disabled, the planarity check (Branch 3) is bypassed and the function
  falls straight through to the 3D-DT or cubic triangulation. This is the
  "CDT2 not available" path that exercises the DT3 fallback for planar holes.

Geometry: quadrilateral hole with four hat triangles.
  q0=(0,0,0), q1=(2,0,0), q2=(2,2,0), q3=(0,2,0): hole corners (CCW)
  o0=(1,-1,0), o1=(3,1,0), o2=(1,3,0), o3=(-1,1,0): outer hat vertices
  t0=(q0,o0,q1), t1=(q1,o1,q2), t2=(q2,o2,q3), t3=(q3,o3,q0): hat tris
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1178",
    title="triangulate_hole.main compile_time_feature_disable CDT2: CGAL_HOLE_FILLING_DO_NOT_USE_CDT2 sets use_cdt=false; quad hole boundary (Branch 2)",
    defect_class="boundary_hole",
)

# Quadrilateral hole corners
q0 = m.vertex(0.0,  0.0,  0.0)   # 0
q1 = m.vertex(2.0,  0.0,  0.0)   # 1
q2 = m.vertex(2.0,  2.0,  0.0)   # 2
q3 = m.vertex(0.0,  2.0,  0.0)   # 3

# Hat outer vertices
o0 = m.vertex(1.0,  -1.0,  0.0)   # 4 — south
o1 = m.vertex(3.0,   1.0,  0.0)   # 5 — east
o2 = m.vertex(1.0,   3.0,  0.0)   # 6 — north
o3 = m.vertex(-1.0,  1.0,  0.0)   # 7 — west

# Four hat triangles
t0 = m.triangle(q0, o0, q1)   # 0: south
t1 = m.triangle(q1, o1, q2)   # 1: east
t2 = m.triangle(q2, o2, q3)   # 2: north
t3 = m.triangle(q3, o3, q0)   # 3: west

# Hole boundary edges (n=1)
m.assert_edge_shared(q0, q1, 1)
m.assert_edge_shared(q1, q2, 1)
m.assert_edge_shared(q2, q3, 1)
m.assert_edge_shared(q0, q3, 1)

# Hole boundary loop
m.assert_hole_boundary([q0, q1, q2, q3])

# Hat outer boundary edges (n=1 each)
m.assert_edge_shared(q0, o0, 1)
m.assert_edge_shared(q1, o0, 1)
m.assert_edge_shared(q1, o1, 1)
m.assert_edge_shared(q2, o1, 1)
m.assert_edge_shared(q2, o2, 1)
m.assert_edge_shared(q3, o2, 1)
m.assert_edge_shared(q3, o3, 1)
m.assert_edge_shared(q0, o3, 1)

# Open mesh with quad hole: V=8, E=12, F=4, chi=0
m.assert_euler_characteristic(8, 12, 4, 0)
