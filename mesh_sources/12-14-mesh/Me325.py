"""Me325 — with_third_points_cost_function_strategy: Weight_min_max_dihedral_and_area selects best triangulation (Branch 6).

CGAL PMP `triangulate_hole_polyline.with_third_points` Branch 6 (*cost_function_strategy*) @ line 751:
  'Weight_calculator<…, Weight_min_max_dihedral_and_area> weight_calculator(is_valid);'
  The cost metric Weight_min_max_dihedral_and_area minimises the maximum dihedral
  angle while also weighting by area; Weight_calculator wraps the validity check
  to score candidate triangulations.  A high-aspect-ratio triangle has a poor
  (high) cost under this metric.

Defect pattern: a needle/sliver triangle with extreme aspect ratio.  The high
  aspect ratio produces a large Weight_min_max_dihedral_and_area cost — this
  is exactly the pattern the cost function is designed to avoid when choosing
  among candidate triangulations.

Geometry: needle triangle.
  v0=(0,0,0), v1=(100,0,0), v2=(50,0.01,0) — very long, almost flat triangle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me325",
             title="with_third_points_cost_function_strategy: Weight_min_max_dihedral_and_area scores needle triangle poorly (Branch 6)",
             defect_class="degenerate_triangle")

# Needle / sliver triangle: very long base, tiny height.
v0 = m.vertex(  0.0, 0.0,  0.0)   # 0
v1 = m.vertex(100.0, 0.0,  0.0)   # 1
v2 = m.vertex( 50.0, 0.01, 0.0)   # 2 — apex barely above baseline

t0 = m.triangle(v0, v1, v2)   # 0

# All edges on boundary (open triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# High aspect ratio: longest edge=100, height=0.01.
# aspect = longest * perimeter / (4 * area)
# area = 0.5 * 100 * 0.01 = 0.5
# perimeter ≈ 100 + 50.000001 + 50.000001 ≈ 200
# aspect ≈ 100 * 200 / (4 * 0.5) = 10000
m.assert_triangle_aspect_ratio_gt(t0, 100.0)

# Euler: V=3, E=3, F=1, chi=1.
m.assert_euler_characteristic(3, 3, 1, 1)
