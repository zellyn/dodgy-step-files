"""Me394 — do_faces_intersect branch 5: opposite-segment-vs-triangle-containment.

PMP.do_faces_intersect Branch 5 (*opposite-segment-vs-triangle-containment*) @ line 292:
  After detecting a shared vertex between two faces, tests whether the segment
  OPPOSITE to the shared vertex in the first triangle pierces the second
  triangle's interior (do_intersect(t1, s2)), or vice versa. When the opposite
  segment of one triangle passes through the interior of the other, that is a
  genuine self-intersection even though the triangles share a vertex.

The fixture models two triangles sharing vertex v0=(0,0,0):
  t0 lies in the XY plane (z=0): (v0, v1=(2,0,0), v2=(0,2,0)).
  t1 is a near-vertical triangle sharing v0, with its other two vertices above
  and below the XY plane so that the edge v3-v4 (the segment OPPOSITE to v0
  in t1) passes through t0's interior at point (1,1,0).

Branch 5 fires: `do_intersect(t0, segment(v3,v4))` is true → return true (SI).

Geometry:
  v0=(0,0,0): shared vertex
  v1=(2,0,0), v2=(0,2,0): t0 in XY plane
  v3=(1,1,-1), v4=(1,1,1): t1's non-shared edge pierces t0 at (1,1,0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me394",
    title="do_faces_intersect shared-vertex opposite-segment-pierces: segment opposite shared vertex crosses other triangle's interior (Branch 5)",
    defect_class="self_intersection_face_pair",
)

# Shared vertex.
v0 = m.vertex(0.0, 0.0,  0.0)   # 0: shared vertex

# t0: in XY plane (z=0).
v1 = m.vertex(2.0, 0.0,  0.0)   # 1
v2 = m.vertex(0.0, 2.0,  0.0)   # 2

# t1: shares v0; its opposite edge pierces t0 at (1,1,0).
v3 = m.vertex(1.0, 1.0, -1.0)   # 3: below XY plane
v4 = m.vertex(1.0, 1.0,  1.0)   # 4: above XY plane

t0 = m.triangle(v0, v1, v2)     # 0: XY-plane triangle
t1 = m.triangle(v0, v3, v4)     # 1: near-vertical, shares v0; edge v3-v4 pierces t0

# The segment from v3 to v4 passes through (1,1,0) which is inside t0's interior.
# Branch 5 in do_faces_intersect detects this via do_intersect(t0, segment(v3,v4)).
m.assert_triangles_self_intersect(t0, t1)
