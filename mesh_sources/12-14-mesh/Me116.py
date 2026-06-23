"""Me116 — intersects_orientation_t1_above_plane: t1 entirely above t2's plane.

MeshFix `Triangle.intersects` Branch 13 (*ORIENTATION_T1_ABOVE_OR_BELOW*):
'if ((o11>0 && o12>0 && o13>0) || (o11<0 && o12<0 && o13<0)) return false' —
all three vertices of t1 have the same orientation (sign) w.r.t. the plane
of t2, meaning t1 lies entirely on one side of t2's plane with no edge
crossing the plane.

Geometric signature: t2 lies in z=0 and t1 is a triangle whose all vertices
have z > 0. Since o11, o12, o13 are all positive, the predicate exits early.

Geometry:
  t0 (in z=0 plane): (0,0,0), (2,0,0), (1,2,0)
  t1 (above z=0):    (0,1,2), (2,1,2), (1,3,4)   — all z > 0, well above

Bounding boxes overlap in X and Y so they pass the BBOX tests, but the
orientation test catches t1 being strictly above t0's plane.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me116",
             title="intersects_orientation_t1_above_plane: t1 all vertices above t0 plane — orientation fast-reject",
             defect_class="mesh_plane_separated_triangles")

# t0 — base triangle in z=0
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(2.0, 0.0, 0.0)
v2 = m.vertex(1.0, 2.0, 0.0)

# t1 — floating above; all z > 0 → all same sign w.r.t. t0's plane (z=0)
v3 = m.vertex(0.0, 1.0, 2.0)
v4 = m.vertex(2.0, 1.0, 2.0)
v5 = m.vertex(1.0, 3.0, 4.0)

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v3, v4, v5)

# t1 is on one strict side of t0's plane → no crossing → no intersection.
m.assert_triangles_do_not_intersect(t0, t1)
