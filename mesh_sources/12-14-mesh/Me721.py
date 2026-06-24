"""Me721 — Basic_TMesh.safeCoordBackApproximation branch 2: Opposite-vertex selection.

Basic_TMesh.safeCoordBackApproximation Branch 2 (*opposite-vertex selection*) @ line 284:
  'a1 = ov1->squaredTriangleArea3D(e); a2 = ov2->squaredTriangleArea3D(e);
   ov = (a1 < a2) ? ov1 : ov2;'
  — for each overlapping edge the algorithm identifies the two opposite vertices (one
  per adjacent triangle) and jitters the one whose incident triangle has the smaller
  squared area, because the smaller triangle is geometrically more sensitive to
  coordinate quantization.

Defect pattern: a shared edge (v0,v1) is incident on two coplanar triangles. The first
  triangle t0 is large; the second triangle t1 is clearly smaller (ov2 side). Both are
  coplanar in the XY plane and their interiors overlap (t1's apex lies inside t0's area).
  Branch 2 fires because a1 > a2 → ov = ov2 (apex of t1 is jittered).

Geometry:
  v0=(0,0,0), v1=(4,0,0)  — shared edge
  v2=(2,4,0)              — apex of large triangle t0; opposite vertex ov1 (large area)
  v3=(2,1,0)              — apex of small triangle t1; opposite vertex ov2 (small area), inside t0
  t0=(v0,v1,v2): area = 8.0 (large)
  t1=(v0,v1,v3): area = 2.0 (small) — ov2 is jittered; Branch 2 selects t1's apex
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me721",
    title="safeCoordBackApproximation opposite-vertex selection: small-area triangle apex jittered; ov2 chosen because squaredArea(t1) < squaredArea(t0) (Branch 2)",
    defect_class="self_intersection_coplanar_overlap",
)

# Shared edge between t0 and t1.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — shared edge endpoint
v1 = m.vertex(4.0, 0.0, 0.0)  # 1 — shared edge endpoint
# Large triangle: apex far from shared edge.
v2 = m.vertex(2.0, 4.0, 0.0)  # 2 — ov1: large area side (area=8)
# Small triangle: apex close to shared edge and inside t0's area.
v3 = m.vertex(2.0, 1.0, 0.0)  # 3 — ov2: small area side (area=2); inside t0

t0 = m.triangle(v0, v1, v2)   # 0: large triangle — ov1 side
t1 = m.triangle(v0, v1, v3)   # 1: small triangle — ov2 side; overlapping interiors

# Shared edge (v0,v1) incident on both triangles.
m.assert_edge_shared(v0, v1, 2)
# Non-shared boundary edges.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Both triangles coplanar; t1's apex inside t0 → overlapping interiors.
m.assert_triangles_self_intersect(t0, t1)

# t1 has smaller area (2.0 < 8.0) — Branch 2 selects this vertex for jitter.
m.assert_triangle_area_lt(t1, 3.0)
