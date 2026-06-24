"""Me1111 — two-CC mesh: SI in CC-A, clean CC-B; treat_all_CCs scope decision.

Tests precondition that NP treat_all_CCs would act on: a mesh with two fully
disconnected connected components where only one CC contains a self-intersection.
When treat_all_CCs=false the clean CC is skipped; when true it is also processed.

Source: CGAL PMP.remove_self_intersections Branch 2 @ line 2383 —
*treatment-scope-selection*: treat_all_CCs NP controls whether all connected
components are processed or only those with internal self-intersections.

Geometry:
  CC-A (triangles 0,1): two triangles in perpendicular planes sharing a single
  vertex at the origin. The XY-plane triangle (tri 0) and the XZ-plane triangle
  (tri 1) cross along the Y=0, Z=0 line — a geometric self-intersection.
  CC-B (triangles 2,3): a clean right-triangle quad patch at X=10, no SI.
  The two CCs share no vertices, so they are fully disconnected.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1111",
    title="SI in CC-A; clean CC-B: treat_all_CCs processing-scope decision",
    defect_class="self_intersection_multi_cc",
)

# CC-A: XY-plane and XZ-plane triangles crossing at origin.
ca0 = m.vertex(0.0, 0.0,  0.0)  # 0 — shared apex of crossing pair
ca1 = m.vertex(0.0, 2.0,  0.0)  # 1 — XY-plane vertex
ca2 = m.vertex(0.0, -2.0, 0.0)  # 2 — XY-plane vertex
ca3 = m.vertex(0.0, 0.0,  2.0)  # 3 — XZ-plane vertex
ca4 = m.vertex(0.0, 0.0, -2.0)  # 4 — XZ-plane vertex
m.triangle(ca0, ca1, ca2)   # tri 0 — CC-A, in XY plane (Z=0)
m.triangle(ca0, ca3, ca4)   # tri 1 — CC-A, in XZ plane (Y=0); crosses tri 0

# CC-B: clean flat quad at X=10, well away from CC-A.
cb0 = m.vertex(10.0, 0.0, 0.0)  # 5
cb1 = m.vertex(11.0, 0.0, 0.0)  # 6
cb2 = m.vertex(11.0, 1.0, 0.0)  # 7
cb3 = m.vertex(10.0, 1.0, 0.0)  # 8
m.triangle(cb0, cb1, cb2)   # tri 2 — CC-B, clean
m.triangle(cb0, cb2, cb3)   # tri 3 — CC-B, clean

# Assert: SI within CC-A (crossing triangles).
m.assert_triangles_self_intersect(0, 1)

# Assert: CC-B is unreachable from CC-A (confirms separate components).
m.assert_triangle_not_reachable_from(2, 0)
