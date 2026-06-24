"""Me541 — checkAndRepair::removeDegenerateTriangles branch 2: CAP_GEOMETRY_OV2

MeshFix `checkAndRepair::removeDegenerateTriangles` Branch 2 (*CAP_GEOMETRY_OV2*) @ line 482:
  'if (pointInInnerSegment(ov2, e->v1, e->v2))'
  After checking ov1, MeshFix also checks ov2 (the second cap's opposite vertex).
  When ov2 also lies strictly inside the cap-edge segment, both cap vertices trigger
  T-junction splits.  This fixture has two adjacent degenerate cap triangles, each
  contributing an opposite vertex that lies on the inner segment of the shared cap edge.

Geometry (z = 0):
  v0=(0,0,0), v1=(6,0,0) — endpoints of the shared cap edge
  v2=(3,1,0)             — apex of outer triangle; area stays positive
  v3=(2,0,0)             — ov1: first inner-segment cap vertex (t1 opposite vertex)
  v4=(4,0,0)             — ov2: second inner-segment cap vertex (t2 opposite vertex)

  t0 = (v0, v1, v2)  — outer triangle; edge (v0,v1) is the cap edge
  t1 = (v0, v3, v2)  — left cap triangle; ov1=v3 strictly inside (v0,v1)
  t2 = (v3, v4, v2)  — middle cap triangle; ov2=v4 strictly inside (v0,v1)
  t3 = (v4, v1, v2)  — right cap triangle completing the fan
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me541",
    title="checkAndRepair::removeDegenerateTriangles CAP_GEOMETRY_OV2: second cap vertex ov2 also on inner segment (two adjacent T-junction caps both trigger splitEdge)",
    defect_class="degenerate_triangle_cap_geometry_ov2",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left endpoint of cap edge
v1 = m.vertex(6.0, 0.0, 0.0)   # 1 — right endpoint of cap edge
v2 = m.vertex(3.0, 1.0, 0.0)   # 2 — apex of outer triangle
v3 = m.vertex(2.0, 0.0, 0.0)   # 3 — ov1: strictly inside (v0, v1)
v4 = m.vertex(4.0, 0.0, 0.0)   # 4 — ov2: strictly inside (v0, v1)

# Outer triangle whose cap edge (v0, v1) has two T-junction vertices.
t0 = m.triangle(v0, v1, v2)    # 0 — outer triangle
# Four sub-triangles produced by the two inner cap vertices v3 and v4.
t1 = m.triangle(v0, v3, v2)    # 1 — leftmost segment; ov1=v3
t2 = m.triangle(v3, v4, v2)    # 2 — middle segment; ov2=v4
t3 = m.triangle(v4, v1, v2)    # 3 — rightmost segment

# Branch 1: v3 (ov1) lies strictly inside segment v0-v1.
m.assert_vertex_on_edge(v3, v0, v1)
# Branch 2: v4 (ov2) also lies strictly inside segment v0-v1.
m.assert_vertex_on_edge(v4, v0, v1)

# Area assertions (all positive; defect is topology, not zero-area).
m.assert_triangle_area_lt(0, 4.0)   # t0: area=3 < 4
m.assert_triangle_area_lt(1, 2.0)   # t1: area=1 < 2
m.assert_triangle_area_lt(2, 2.0)   # t2: area=1 < 2
m.assert_triangle_area_lt(3, 2.0)   # t3: area=1 < 2

# Interior shared edges between sub-triangles.
m.assert_edge_shared(v2, v3, 2)    # shared between t1 and t2
m.assert_edge_shared(v2, v4, 2)    # shared between t2 and t3
