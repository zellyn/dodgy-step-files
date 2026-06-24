"""Me1177 — triangulate_hole.main compile_time_feature_disable DT3:
  CGAL_HOLE_FILLING_DO_NOT_USE_DT3 macro controls use_dt3 flag; hole
  boundary mesh demonstrates triangulation path (Branch 1).

CGAL PMP `triangulate_hole.main` Branch 1 (*compile_time_feature_disable*)
  @ line 184:
  '#ifdef CGAL_HOLE_FILLING_DO_NOT_USE_DT3 use_dt3 = false; #endif' —
  The first branch in triangulate_hole.main is the compile-time guard that
  disables the 3D Delaunay Triangulation path. When the macro is defined,
  use_dt3 is forced to false, routing the algorithm to the CDT2/cubic fallback.
  Branch 1 fires at compile time but the runtime fixture must carry the hole
  geometry that triangulate_hole.main would process.

Defect pattern: a triangular hole in a planar mesh — three hat triangles
  surrounding a triangular hole. This is the minimal case that triangulate_hole
  processes. The compile-time flag does not change the input geometry; it
  changes which internal algorithm is dispatched. Branch 1 represents the
  code path where DT3 is unavailable and the function must fall back to CDT2
  or the cubic algorithm for triangulation.

Geometry: equilateral triangular hole with three hat triangles.
  h0=(0,0,0), h1=(2,0,0), h2=(1,1.73,0): hole corners
  o0=(1,-1,0), o1=(3,1,0), o2=(-1,1,0): outer hat vertices
  t0=(h0,o0,h1), t1=(h1,o1,h2), t2=(h2,o2,h0): hat triangles
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1177",
    title="triangulate_hole.main compile_time_feature_disable DT3: CGAL_HOLE_FILLING_DO_NOT_USE_DT3 sets use_dt3=false; triangular hole boundary (Branch 1)",
    defect_class="boundary_hole",
)

# Hole corner vertices
h0 = m.vertex(0.0,   0.0,   0.0)   # 0 — left corner
h1 = m.vertex(2.0,   0.0,   0.0)   # 1 — right corner
h2 = m.vertex(1.0,   1.73,  0.0)   # 2 — top corner

# Hat outer vertices
o0 = m.vertex(1.0,  -1.0,   0.0)   # 3 — south hat
o1 = m.vertex(3.0,   1.0,   0.0)   # 4 — SE hat
o2 = m.vertex(-1.0,  1.0,   0.0)   # 5 — SW hat

# Three hat triangles surrounding the hole
t0 = m.triangle(h0, o0, h1)   # 0: south hat
t1 = m.triangle(h1, o1, h2)   # 1: SE hat
t2 = m.triangle(h2, o2, h0)   # 2: SW hat

# Hole boundary edges (n=1 — one side of hole)
m.assert_edge_shared(h0, h1, 1)
m.assert_edge_shared(h1, h2, 1)
m.assert_edge_shared(h0, h2, 1)

# Hole boundary loop
m.assert_hole_boundary([h0, h1, h2])

# Hat outer boundary edges (n=1)
m.assert_edge_shared(h0, o0, 1)
m.assert_edge_shared(h1, o0, 1)
m.assert_edge_shared(h1, o1, 1)
m.assert_edge_shared(h2, o1, 1)
m.assert_edge_shared(h2, o2, 1)
m.assert_edge_shared(h0, o2, 1)

# Open mesh with triangular hole: V=6, E=9, F=3, chi=0
m.assert_euler_characteristic(6, 9, 3, 0)
