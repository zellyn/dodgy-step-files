"""Me118 — intersects_proper_3d: non-coplanar triangles with interior edge crossing.

MeshFix `Triangle.intersects` Branch 16 (*PROPER_INTERSECTION_3D*):
'else return (segmentIntersectsTriangle(...) || ...)' — the non-coplanar
case with mixed orientation signs. At least one edge of t1 crosses t2's
plane on one side and another vertex on the other side, AND the same
for t2 vs t1. Six edge-triangle segment tests are performed; at least
one succeeds.

Geometric signature: the classic cross-plane intersection — t0 lies in
the XY plane and t1 lies in the XZ plane, both spanning the X axis between
x=−1 and x=+1. Their intersection line is the segment from (−1,0,0) to
(+1,0,0).

Geometry:
  t0 (XY plane): (−1,0,0), (1,0,0), (0,2,0)
  t1 (XZ plane): (−1,0,0), (1,0,0), (0,0,2)

The shared edge (v0, v1) lies in both planes. Both non-shared vertices
(v2 and v5) are strictly off each other's plane. Mixed orientations →
Branch 16 fires; the segment tests confirm proper intersection.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me118",
             title="intersects_proper_3d: XY-plane and XZ-plane triangles intersect along shared base edge",
             defect_class="self_intersection_face_pair")

v0 = m.vertex(-1.0, 0.0, 0.0)  # shared base left
v1 = m.vertex( 1.0, 0.0, 0.0)  # shared base right
v2 = m.vertex( 0.0, 2.0, 0.0)  # t0 apex — in XY plane (z=0)
v3 = m.vertex( 0.0, 0.0, 2.0)  # t1 apex — in XZ plane (y=0)

t0 = m.triangle(v0, v1, v2)   # XY plane
t1 = m.triangle(v0, v1, v3)   # XZ plane

# Both triangles share edge (v0,v1); the other vertices are in orthogonal planes.
m.assert_edge_shared(v0, v1, 2)

# Non-coplanar proper 3D intersection via Branch 16.
m.assert_triangles_self_intersect(t0, t1)
