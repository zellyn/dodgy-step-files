"""Me115 — intersects_bbox_z_reject_min: t2 entirely below t1's z-min — fast reject.

MeshFix `Triangle.intersects` Branch 11 (*BBOX_Z_REJECT_MIN*):
'if (v21->z < mx && v22->z < mx && v23->z < mx) return false' — all
three vertices of t2 have z-coordinate strictly less than the minimum
z-coordinate of t1. Bounding boxes are z-separated.

Geometric signature: t0 is an elevated triangle (z ∈ [5, 7]) and t1 is
a ground-level triangle (z ∈ [0, 2]). All t1 vertices have z < 5 = t0's
z-min.

Geometry:
  t0 (high): (0,0,5), (1,0,5), (0.5,1,7)  — z_min = 5
  t1 (low):  (0,0,0), (1,0,0), (0.5,1,2)  — z_max = 2  (all < 5)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me115",
             title="intersects_bbox_z_reject_min: t2 entirely below t1's z-min bounding-box fast-reject",
             defect_class="mesh_spatially_separated_z")

# t0 — elevated (z ∈ [5,7])
v0 = m.vertex(0.0, 0.0, 5.0)
v1 = m.vertex(1.0, 0.0, 5.0)
v2 = m.vertex(0.5, 1.0, 7.0)

# t1 — ground level (z ∈ [0,2]); all z < 5 = t0's z-min
v3 = m.vertex(0.0, 0.0, 0.0)
v4 = m.vertex(1.0, 0.0, 0.0)
v5 = m.vertex(0.5, 1.0, 2.0)

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v3, v4, v5)

# Triangles are spatially separated; bounding boxes disjoint in Z.
m.assert_triangles_do_not_intersect(t0, t1)
