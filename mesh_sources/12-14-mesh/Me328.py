"""Me328 — with_third_points_fallback_dt3_or_cubic: CDT failed; fallback to DT3 or cubic algorithm (Branch 9).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 9 (*fallback_to_dt3_or_cubic*) @ line 793:
  'triangulate_hole_polyline(points, third_points, out, weight_calculator,'
  '    use_dt3, do_not_use_cubic_algorithm, …);'
  When CDT fails (or is skipped), the code falls through to a call of
  `triangulate_hole_polyline` with the use_dt3 and do_not_use_cubic_algorithm
  flags.  If use_dt3 is true the 3D Delaunay triangulation is attempted first;
  if do_not_use_cubic_algorithm is false the cubic algorithm is the final
  fallback.

Defect pattern: a non-planar quadrilateral hole boundary (3D saddle shape).
  CDT requires planarity — this non-planar hole causes CDT to fail.
  The fallback (DT3 or cubic) handles non-planar holes.

Geometry: saddle-shaped 4-vertex hole.
  v0=(0,0,0), v1=(2,0,1), v2=(2,2,0), v3=(0,2,1) — vertices at alternating
  heights, producing a non-planar quadrilateral boundary.
  Two surrounding triangles provide mesh context.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me328",
             title="with_third_points_fallback_dt3_or_cubic: CDT fails on non-planar hole; DT3/cubic fallback fires (Branch 9)",
             defect_class="hole_in_hull")

# Non-planar saddle hole boundary.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — z=0
v1 = m.vertex(2.0, 0.0, 1.0)   # 1 — z=1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2 — z=0
v3 = m.vertex(0.0, 2.0, 1.0)   # 3 — z=1

# Two surrounding triangles (one on each diagonal), giving context to the hole.
t0 = m.triangle(v0, v1, v3)   # 0 — left triangle
t1 = m.triangle(v1, v2, v3)   # 1 — right triangle (shares edge v1-v3)

# Shared diagonal between the two surrounding triangles.
m.assert_edge_shared(v1, v3, 2)

# Outer boundary edges incident on 1 triangle each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)

# Hole boundary: the non-planar quad — CDT would fail here; DT3/cubic fills it.
m.assert_hole_boundary([v0, v1, v2, v3])

# Euler: V=4, E=5, F=2, chi=1 (open disk, two triangles sharing a diagonal).
m.assert_euler_characteristic(4, 5, 2, 1)
