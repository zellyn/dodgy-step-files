"""Me114 — intersects_bbox_y_reject_min: t2 entirely below t1's y-min — fast reject.

MeshFix `Triangle.intersects` Branch 9 (*BBOX_Y_REJECT_MIN*):
'if (v21->y < mx && v22->y < mx && v23->y < mx) return false' — all
three vertices of t2 have y-coordinate strictly less than the minimum
y-coordinate of t1. Bounding boxes are y-separated.

Geometric signature: t0 sits in the upper half (y ∈ [4, 6]) and t1 sits
in the lower half (y ∈ [0, 2]). All t1 vertices have y < 4 = t0's y-min.

Geometry:
  t0 (upper): (0,4,0), (2,4,0), (1,6,0)  — y_min = 4
  t1 (lower): (0,0,0), (2,0,0), (1,2,0)  — y_max = 2  (all < 4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me114",
             title="intersects_bbox_y_reject_min: t2 entirely below t1's y-min bounding-box fast-reject",
             defect_class="mesh_spatially_separated_y")

# t0 — upper (y ∈ [4,6])
v0 = m.vertex(0.0, 4.0, 0.0)
v1 = m.vertex(2.0, 4.0, 0.0)
v2 = m.vertex(1.0, 6.0, 0.0)

# t1 — lower (y ∈ [0,2]); all y < 4 = t0's y-min
v3 = m.vertex(0.0, 0.0, 0.0)
v4 = m.vertex(2.0, 0.0, 0.0)
v5 = m.vertex(1.0, 2.0, 0.0)

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v3, v4, v5)

# Triangles are spatially separated; bounding boxes disjoint in Y.
m.assert_triangles_do_not_intersect(t0, t1)
