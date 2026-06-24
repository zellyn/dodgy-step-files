"""Me392 — do_faces_intersect branch 3: shared-edge-coplanarity-orientation.

PMP.do_faces_intersect Branch 3 (*shared-edge-coplanarity-orientation*) @ line 247:
  After detecting that two faces share a full edge, tests whether the faces are
  coplanar AND have the same orientation (CGAL::POSITIVE). When coplanar faces
  share an edge and their normals point the same direction, they overlap —
  classified as an overlapping self-intersection.

The fixture models two coplanar triangles sharing edge (v0,v1) where the second
triangle's apex lies strictly inside the first triangle's interior. Both
triangles lie in the XY plane (z=0) and have normals pointing in the +Z
direction (same orientation). The coplanar 2D projection overlap test detects
their interiors overlap — Branch 3 fires to classify this as an overlapping SI.

Geometry:
  v0=(0,0,0), v1=(3,0,0) — shared edge
  v2=(1.5,3,0) — apex of large triangle (t0)
  v3=(1.5,1,0) — apex of small triangle (t1); inside t0's interior
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me392",
    title="do_faces_intersect shared-edge coplanar same-orientation: overlapping coplanar faces → overlapping SI (Branch 3)",
    defect_class="self_intersection_face_pair",
)

# Shared edge.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
# Large triangle apex.
v2 = m.vertex(1.5, 3.0, 0.0)   # 2: apex of t0 (large, XY plane)
# Small triangle apex — lies inside t0's area (coplanar, same normal dir).
v3 = m.vertex(1.5, 1.0, 0.0)   # 3: apex of t1 (small, inside t0)

t0 = m.triangle(v0, v1, v2)    # 0: large coplanar triangle
t1 = m.triangle(v0, v1, v3)    # 1: small coplanar triangle sharing edge (v0,v1)

# Shared edge incident on both.
m.assert_edge_shared(v0, v1, 2)
# Coplanar, same orientation, interiors overlap → self-intersection.
m.assert_triangles_self_intersect(t0, t1)
