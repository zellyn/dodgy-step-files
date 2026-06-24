"""Me540 — checkAndRepair::removeDegenerateTriangles branch 1: CAP_GEOMETRY_OV1

MeshFix `checkAndRepair::removeDegenerateTriangles` Branch 1 (*CAP_GEOMETRY_OV1*) @ line 481:
  'if (pointInInnerSegment(ov1, e->v1, e->v2))'
  A triangle has a cap edge (v0, v1).  The first cap triangle's opposite vertex ov1
  lies strictly inside the segment v0–v1 (T-junction).  MeshFix detects this and
  queues the cap edge for a splitEdge subdivision.

Geometry (z = 0):
  v0=(0,0,0), v1=(4,0,0) — endpoints of the cap edge
  v2=(2,1,0)             — apex of outer triangle t0 (healthy, area=2)
  v3=(2,0,0)             — opposite vertex ov1 of cap sub-triangles; lies strictly
                           inside segment v0-v1 (T-junction)

  t0 = (v0, v1, v2)  — triangle whose edge (v0, v1) is the cap edge; area=2
  t1 = (v0, v3, v2)  — left cap sub-triangle; ov1=v3 on inner segment of (v0,v1)
  t2 = (v3, v1, v2)  — right cap sub-triangle completing the fan
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me540",
    title="checkAndRepair::removeDegenerateTriangles CAP_GEOMETRY_OV1: opposite vertex ov1 lies on inner segment of cap edge (T-junction triggers splitEdge)",
    defect_class="degenerate_triangle_cap_geometry_ov1",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left endpoint of cap edge
v1 = m.vertex(4.0, 0.0, 0.0)   # 1 — right endpoint of cap edge
v2 = m.vertex(2.0, 1.0, 0.0)   # 2 — apex; completes outer triangle t0
v3 = m.vertex(2.0, 0.0, 0.0)   # 3 — ov1: strictly inside segment v0-v1

# t0: triangle whose long edge (v0, v1) is the cap edge under examination.
t0 = m.triangle(v0, v1, v2)    # 0 — outer triangle; area=2
# t1, t2: cap sub-triangles; t1's opposite vertex v3 is on inner segment of (v0,v1).
t1 = m.triangle(v0, v3, v2)    # 1 — left sub-triangle; ov1=v3 on (v0,v1)
t2 = m.triangle(v3, v1, v2)    # 2 — right sub-triangle

# Branch 1 predicate: v3 lies strictly inside segment v0-v1 (pointInInnerSegment).
m.assert_vertex_on_edge(v3, v0, v1)

# Confirm triangle areas (none degenerate in input; defect is the T-junction cap).
m.assert_triangle_area_lt(0, 3.0)   # t0: area=2 < 3
m.assert_triangle_area_lt(1, 2.0)   # t1: area=1 < 2
m.assert_triangle_area_lt(2, 2.0)   # t2: area=1 < 2

# Topology: edge (v2,v3) is shared by t1 and t2; boundary edges are n=1.
m.assert_edge_shared(v2, v3, 2)    # interior edge between cap sub-triangles
m.assert_edge_shared(v0, v3, 1)    # boundary
m.assert_edge_shared(v3, v1, 1)    # boundary
