"""Me321 — with_third_points_cdt2_compile_disabled: CDT2 path skipped when CGAL_HOLE_FILLING_DO_NOT_USE_CDT2 set (Branch 2).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 2 (*compile_time_feature_disable*) @ line 735:
  '#ifndef CGAL_HOLE_FILLING_DO_NOT_USE_CDT2'
  When this macro is defined at compile-time, the CDT2 hole-filling code path
  is entirely omitted; only the DT3 / cubic fallback is available.

Defect pattern: a triangular hole bounded by 3 boundary edges; the CDT2 path
  would normally attempt to fill it first.  With the macro set, CDT2 is
  skipped and the fallback fires instead.

Geometry: a triangular hole in an L-shaped mesh.
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0) — boundary triangle of the hole.
  Surrounding context: one closed triangle t0 well away from the hole, and
  the boundary loop [v0,v1,v2] pointing to the unfilled region.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me321",
             title="with_third_points_cdt2_compile_disabled: CGAL_HOLE_FILLING_DO_NOT_USE_CDT2 skips CDT2 path (Branch 2)",
             defect_class="hole_in_hull")

# Boundary triangle of the unfilled hole.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2

# Three boundary-edge-only triangles that form the rim of the hole
# (each boundary edge incident on exactly 1 triangle from the rim side).
# Use a single partial-ring: two half-disks sharing the boundary.
t0 = m.triangle(v0, v1, v2)    # 0 — the single triangle (hole is on its other side)

# The boundary edges of t0 are each incident on 1 triangle only —
# the opposite side is the unfilled hole.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Hole boundary loop — the triangular opening CDT2 would fill.
m.assert_hole_boundary([v0, v1, v2])

# Euler: V=3, E=3, F=1, chi=1 (open disk / single triangle).
m.assert_euler_characteristic(3, 3, 1, 1)
