"""Me017 — SI in one CC; clean second CC (treat_all_CCs branch).

Catalog claim: the mesh has two disconnected connected components. Component A
(triangles 0,1) contains a self-intersecting pair. Component B (triangles 2,3)
is a clean, non-self-intersecting quad patch with no topology errors. The healer
must decide whether to process only the SI-bearing CC or all CCs (treat_all_CCs
parameter, CGAL PMP.remove_self_intersections Branch 2 @ line 2383).

Source: CGAL PMP.remove_self_intersections Branch 2 @ line 2383 —
*treatment-scope-selection*: whether to treat all CCs even without
self-intersections (treat_all_CCs NP) vs only SI-bearing ones.

Defect carrier: two fully disconnected triangle patches (no shared vertices).
CC A = triangles 0 and 1 in crossing XY / XZ planes (self-intersect along X axis).
CC B = triangles 2 and 3 forming a clean flat quad, 50 units away.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me017",
             title="SI in CC-A only; clean CC-B disconnected: treat_all_CCs decision",
             defect_class="self_intersection_multi_cc")

# CC A: XY triangle and XZ triangle crossing along the X axis (like Me005).
a0 = m.vertex(0.0, 0.0, 0.0)    # 0
a1 = m.vertex(1.0, 1.0, 0.0)    # 1
a2 = m.vertex(1.0, -1.0, 0.0)   # 2
a3 = m.vertex(1.0, 0.0, 1.0)    # 3
a4 = m.vertex(1.0, 0.0, -1.0)   # 4
m.triangle(a0, a1, a2)    # tri 0 — CC A, XY plane
m.triangle(a0, a3, a4)    # tri 1 — CC A, XZ plane; crosses tri 0

# CC B: clean flat quad (two triangles) 50 units away along Y axis.
b0 = m.vertex(0.0, 50.0, 0.0)   # 5
b1 = m.vertex(1.0, 50.0, 0.0)   # 6
b2 = m.vertex(1.0, 51.0, 0.0)   # 7
b3 = m.vertex(0.0, 51.0, 0.0)   # 8
m.triangle(b0, b1, b2)    # tri 2 — CC B, clean
m.triangle(b0, b2, b3)    # tri 3 — CC B, clean

# Assert: SI in CC A.
m.assert_triangles_self_intersect(0, 1)

# Assert: CC B is unreachable from CC A (truly disconnected).
m.assert_triangle_not_reachable_from(2, 0)
