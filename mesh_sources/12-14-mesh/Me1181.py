"""Me1181 — triangulate_hole.main algorithm_fallback_strategy: delegation to
  internal::triangulate_hole_polygon_mesh with use_dt3/use_cdt/cubic flags
  controlling the fallback chain (Branch 5).

CGAL PMP `triangulate_hole.main` Branch 5 (*algorithm_fallback_strategy*)
  @ line 225:
  'internal::triangulate_hole_polygon_mesh(pm, h, out, use_dt3, use_cdt,
    do_not_use_cubic_algorithm, ...)' —
  After resolving compile-time flags (Branches 1-2), checking planarity
  (Branch 3), and optionally applying a threshold (Branch 4), triangulate_hole
  delegates to the internal implementation with the resolved use_dt3, use_cdt,
  and do_not_use_cubic flags. Branch 5 is the actual algorithm dispatch — it
  fires for every call to triangulate_hole after all flag resolution is complete.

Defect pattern: a non-planar 4-edge hole — the four boundary vertices are NOT
  co-planar. A non-planar hole cannot use the CDT2 flat-projection path;
  triangulate_hole must fall back to 3D-DT or cubic. Branch 5 fires when
  the delegation to internal::triangulate_hole_polygon_mesh occurs, passing
  the resolved algorithm flags. The non-planar geometry ensures the CDT2
  planarity check fails (max_squared_distance > threshold), demonstrating
  the DT3 fallback path.

Geometry: a non-planar quadrilateral hole — three corners in z=0, one at z=1.
  q0=(0,0,0), q1=(2,0,0), q2=(2,2,0), q3=(1,1,1): hole corners (non-planar)
  Four hat triangles surround the hole.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1181",
    title="triangulate_hole.main algorithm_fallback_strategy: non-planar hole triggers DT3 fallback; delegation to internal with use_dt3/use_cdt flags (Branch 5)",
    defect_class="boundary_hole",
)

# Non-planar quadrilateral hole: q3 lifted to z=1
q0 = m.vertex(0.0,  0.0,  0.0)   # 0 — flat
q1 = m.vertex(2.0,  0.0,  0.0)   # 1 — flat
q2 = m.vertex(2.0,  2.0,  0.0)   # 2 — flat
q3 = m.vertex(1.0,  1.0,  1.0)   # 3 — lifted! non-planar

# Hat outer vertices (around the hole boundary)
o0 = m.vertex(1.0,  -1.0,  0.0)   # 4 — south
o1 = m.vertex(3.0,   1.0,  0.0)   # 5 — east
o2 = m.vertex(1.5,   3.0,  0.0)   # 6 — north
o3 = m.vertex(-1.0,  0.5,  0.5)   # 7 — west-lifted

# Four hat triangles
t0 = m.triangle(q0, o0, q1)   # 0: south
t1 = m.triangle(q1, o1, q2)   # 1: east
t2 = m.triangle(q2, o2, q3)   # 2: north
t3 = m.triangle(q3, o3, q0)   # 3: west

# Non-planar hole boundary (n=1)
m.assert_edge_shared(q0, q1, 1)
m.assert_edge_shared(q1, q2, 1)
m.assert_edge_shared(q2, q3, 1)
m.assert_edge_shared(q0, q3, 1)

m.assert_hole_boundary([q0, q1, q2, q3])

# Hat outer edges (n=1)
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
