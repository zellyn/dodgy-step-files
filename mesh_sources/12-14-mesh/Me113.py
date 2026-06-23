"""Me113 — intersects_bbox_x_reject_min: t2 entirely left of t1's x-min — fast reject.

MeshFix `Triangle.intersects` Branch 7 (*BBOX_X_REJECT_MIN*):
'if (v21->x < mx && v22->x < mx && v23->x < mx) return false' — all
three vertices of t2 have x-coordinate strictly less than the minimum
x-coordinate of t1. Bounding boxes are x-separated; no intersection is
possible.

Geometric signature: t1 occupies x ∈ [3, 5] and t2 occupies x ∈ [0, 1].
All t2 vertices fail the mx test immediately (mx = 3.0, all t2.x < 3.0).

Geometry:
  t0 (right): (3,0,0), (5,0,0), (4,2,0)  — x_min = 3
  t1 (left):  (0,0,0), (1,0,0), (0.5,2,0) — x_max = 1  (all < 3)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me113",
             title="intersects_bbox_x_reject_min: t2 entirely left of t1's x-min bounding-box fast-reject",
             defect_class="mesh_spatially_separated_x")

# t0 — right slab (x ∈ [3,5])
v0 = m.vertex(3.0, 0.0, 0.0)
v1 = m.vertex(5.0, 0.0, 0.0)
v2 = m.vertex(4.0, 2.0, 0.0)

# t1 — left slab (x ∈ [0,1]); all x < 3 = t0's x-min
v3 = m.vertex(0.0, 0.0, 0.0)
v4 = m.vertex(1.0, 0.0, 0.0)
v5 = m.vertex(0.5, 2.0, 0.0)

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v3, v4, v5)

# Triangles are spatially separated; bounding boxes disjoint in X.
m.assert_triangles_do_not_intersect(t0, t1)
