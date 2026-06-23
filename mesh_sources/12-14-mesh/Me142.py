"""Me142 — isInnerPoint_degenerate_triangle: collinear vertices, all orientations zero.

MeshFix `Basic_TMesh.isInnerPoint` Branch 4 (*degenerate_triangle*) @ line 2003:
  'if (o1 == 0 && o2 == 0 && o3 == 0) continue'
  After the Y-Z bounding box test, isInnerPoint computes three 2D
  orientation values (o1, o2, o3) for the triangle's projected edges
  relative to the query point. If all three are exactly zero, the
  triangle is degenerate (collinear in the projected plane) and is
  skipped.

Geometric signature: three collinear vertices forming a zero-area
"triangle". All three 2D cross-products in isInnerPoint's orientation
test return 0. The fixture demonstrates this with three collinear points
along the X-axis.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)  — all on x-axis, y=z=0
  t0=(v0,v1,v2)  — degenerate, zero area
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me142",
             title="isInnerPoint_degenerate_triangle: collinear vertices give o1=o2=o3=0, skip branch fires",
             defect_class="degenerate_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2

t0 = m.triangle(v0, v1, v2)    # 0 — degenerate: collinear

# Zero area confirms the degenerate branch input.
m.assert_triangle_area_lt(t0, 1e-9)

# v1 lies exactly on the segment v0→v2 (collinearity evidence).
m.assert_vertex_on_edge(v1, v0, v2)
