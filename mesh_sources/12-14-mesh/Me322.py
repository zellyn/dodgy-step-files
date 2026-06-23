"""Me322 — with_third_points_dt3_compile_disabled: use_dt3 forced false when CGAL_HOLE_FILLING_DO_NOT_USE_DT3 set (Branch 3).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 3 (*compile_time_feature_disable*) @ line 738:
  '#ifdef CGAL_HOLE_FILLING_DO_NOT_USE_DT3'
  '  use_dt3 = false;'
  When this compile-time macro is defined, use_dt3 is unconditionally set
  to false regardless of the caller's parameter, forcing the cubic-algorithm
  fallback path.

Defect pattern: a quadrilateral hole boundary (4 vertices).  The DT3 path
  would normally be preferred for 3D hole filling; disabling it forces the
  cubic algorithm branch.

Geometry: quadrilateral open boundary.
  v0=(0,0,0), v1=(3,0,0), v2=(3,2,0), v3=(0,2,0) — boundary quad of the hole.
  No fill triangles — the quad represents the unfilled opening.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me322",
             title="with_third_points_dt3_compile_disabled: CGAL_HOLE_FILLING_DO_NOT_USE_DT3 forces use_dt3=false (Branch 3)",
             defect_class="hole_in_hull")

# Boundary quad vertices of the unfilled hole.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(3.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3

# Two surrounding triangles that form the rim context (one on each diagonal).
# They provide the "existing mesh" into which the hole would be filled.
t0 = m.triangle(v0, v1, v3)   # 0 — lower-left half; shares edges with hole
t1 = m.triangle(v1, v2, v3)   # 1 — upper-right half; shares edges with hole

# Interior diagonal (v1,v3) is shared by 2 triangles.
m.assert_edge_shared(v1, v3, 2)

# Outer rim edges are each incident on 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v2, 1)

# Hole boundary: the outer quad loop.
m.assert_hole_boundary([v0, v1, v2, v3])

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
