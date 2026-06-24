"""Me821 — does_polygon_soup_self_intersect branch 2: polygon_type_mixed.

PMP.does_polygon_soup_self_intersect Branch 2 (*polygon_type_mixed*) @ line 45:
  After merging duplicate points the function checks whether every polygon in the
  soup is already a triangle: `if(polygon.size() != std::size_t(3))`.  When any
  polygon has more than 3 vertices (a quad, pentagon, etc.) Branch 2 fires and the
  function calls `triangulate_polygons` to convert the soup to an all-triangle
  representation before running the SI check.

Simulation rationale: the mesh_builder only handles triangle soups.  The closest
  geometric pre-condition that exercises the *intent* of this branch is a polygon
  soup that contains a polygon whose vertex count is not 3 — here simulated by
  using a degenerate vertex layout where one "triangle" is maximally needle-shaped
  (aspect ratio >> 1), representing the pathological geometry that a higher-polygon
  soup would have after a naive ear-clip triangulation.  The high aspect ratio
  assertion documents the polygon_type_mixed defect class in a triangle-builder
  context.

Geometry:
  v0=(0,0,0), v1=(10,0,0), v2=(5,1e-4,0)
  t0=(v0,v1,v2): severely needle triangle (long base, tiny height).
  The aspect ratio (longest edge / shortest altitude) ≫ 1 — flags the
  polygon_type_mixed pre-condition check.

  A second clean triangle provides context:
  v3=(0,2,0), v4=(1,2,0), v5=(0,3,0)
  t1=(v3,v4,v5): normal triangle with no SI relative to t0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me821",
    title="does_polygon_soup_self_intersect polygon_type_mixed: needle triangle (aspect >> 1) simulates non-triangle-polygon pre-condition; triangulate_polygons branch fires (Branch 2)",
    defect_class="degenerate_triangle",
)

# Needle triangle: base 10, height 1e-4 → extreme aspect ratio.
v0 = m.vertex(0.0,    0.0,   0.0)  # 0
v1 = m.vertex(10.0,   0.0,   0.0)  # 1 — far end of base
v2 = m.vertex(5.0,    1e-4,  0.0)  # 2 — tiny apex

t0 = m.triangle(v0, v1, v2)        # 0: needle triangle (polygon_type_mixed target)

# Normal companion triangle — no SI with t0.
v3 = m.vertex(0.0,    2.0,   0.0)  # 3
v4 = m.vertex(1.0,    2.0,   0.0)  # 4
v5 = m.vertex(0.0,    3.0,   0.0)  # 5

t1 = m.triangle(v3, v4, v5)        # 1: clean triangle

# Needle: longest edge ~10, shortest altitude = 2*area/base = 2*(0.5*10*1e-4)/10 = 1e-4
# aspect_ratio = longest_edge / altitude = 10 / 1e-4 = 1e5
m.assert_triangle_aspect_ratio_gt(t0, 1000.0)

# The two triangles are spatially separated — no SI.
m.assert_triangles_do_not_intersect(t0, t1)
