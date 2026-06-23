"""Me327 — with_third_points_threshold_override: user threshold_distance overrides bbox-based default (Branch 8).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 8 (*threshold_override*) @ line 776:
  'const FT squared_dist = (threshold_distance < 0) ?'
  '    default_squared_distance : CGAL::to_double(threshold_distance * threshold_distance);'
  If threshold_distance >= 0 the user value is squared and used directly;
  otherwise the default (bbox height / 4)^2 is computed.  A too-small
  threshold rejects all CDT candidates when max_squared_distance < hole span.
  The user supplies a threshold large enough to cover the elongated hole.

Defect pattern: a wide elongated triangular hole (width=10, height=0.2) in a
  minimal mesh context.  The bbox default_squared_distance would be (0.2/4)^2
  = 0.0025 — far too small for a hole of diameter ~10.  The user must pass
  threshold_distance >= 10 for CDT to succeed.

  We represent this as a long-and-flat triangle (the single mesh face whose
  three edges bound the hole), plus assertions demonstrating the extreme
  aspect ratio that defeats the default threshold.

Geometry: elongated triangle.
  v0=(0,0,0), v1=(10,0,0), v2=(5,0.2,0) — width 10, height 0.2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me327",
             title="with_third_points_threshold_override: auto bbox threshold too small for wide flat hole; user override needed (Branch 8)",
             defect_class="hole_in_hull")

# Wide flat triangle represents the boundary of the elongated hole.
v0 = m.vertex( 0.0, 0.0, 0.0)   # 0
v1 = m.vertex(10.0, 0.0, 0.0)   # 1
v2 = m.vertex( 5.0, 0.2, 0.0)   # 2 — apex barely above baseline

t0 = m.triangle(v0, v1, v2)   # 0

# All edges boundary (open triangle — hole on the other side).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Hole boundary is the triangle loop itself.
m.assert_hole_boundary([v0, v1, v2])

# Extreme aspect ratio: longest_edge=10, perimeter≈20.4, area=0.5*10*0.2=1.
# aspect = 10 * 20.4 / (4 * 1) = 51 >> 1.
# The bbox height = 0.2; default_squared_distance = (0.2/4)^2 = 0.0025.
# The hole span^2 ≈ 100, so default threshold is 40000× too small.
m.assert_triangle_aspect_ratio_gt(t0, 10.0)

# Euler: V=3, E=3, F=1, chi=1.
m.assert_euler_characteristic(3, 3, 1, 1)
