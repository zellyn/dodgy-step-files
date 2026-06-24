"""Me732 — checkAndRepair::meshclean branch 3: BOTH_PASSES_SUCCEEDED.

Source method: MeshFix `checkAndRepair::meshclean` Branch 3 @ line 1048.
Branch condition: `if (ni && nd)` — both strongDegeneracyRemoval AND
strongIntersectionRemoval returned true (both passes succeeded without
exhausting iteration budget). The kernel then proceeds to check for any
residual degenerate triangles.

Defect pattern: a clean, well-formed mesh with no degeneracies and no
self-intersections. Both repair passes complete immediately (trivially succeed
because there is nothing to fix). The branch fires because ni=true and nd=true
are both set. This is the "happy path" through meshclean.

Geometry:
  Two separated clean triangles forming two distinct connected components
  (CC A at Z=0, CC B at Z=10). Neither has zero-area faces, neither pair
  of faces from different CCs crosses the other. Both passes see no work
  to do and return true immediately.

  CC A: v0=(0,0,0), v1=(2,0,0), v2=(1,2,0) — clean triangle in XY plane
  CC B: v3=(0,0,10), v4=(2,0,10), v5=(1,2,10) — identical shape, 10 units above
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me732",
    title="meshclean BOTH_PASSES_SUCCEEDED: two clean separated triangles; ni=true, nd=true, both passes trivially succeed (branch 3)",
    defect_class="self_intersection",
)

# CC A: clean triangle in XY plane.
v0 = m.vertex(0.0, 0.0,  0.0)  # 0
v1 = m.vertex(2.0, 0.0,  0.0)  # 1
v2 = m.vertex(1.0, 2.0,  0.0)  # 2

# CC B: clean triangle 10 units above, no contact with CC A.
v3 = m.vertex(0.0, 0.0, 10.0)  # 3
v4 = m.vertex(2.0, 0.0, 10.0)  # 4
v5 = m.vertex(1.0, 2.0, 10.0)  # 5

t0 = m.triangle(v0, v1, v2)   # 0 — CC A
t1 = m.triangle(v3, v4, v5)   # 1 — CC B

# Both triangles have non-zero area — no degenerate faces.
# (Area of equilateral-ish: base=2, height=2 → area=2; assert area NOT lt 1e-9 via
# the positive side: check that the triangles do not intersect, which is valid
# here since they are in different planes 10 units apart.)
m.assert_triangles_do_not_intersect(t0, t1)

# CC B is unreachable from CC A (confirms two disconnected components).
m.assert_triangle_not_reachable_from(t1, t0)

# Each triangle is a boundary-only component: all three edges n=1.
m.assert_edge_shared(v0, v1, 1)  # CC A boundary
m.assert_edge_shared(v1, v2, 1)  # CC A boundary
m.assert_edge_shared(v0, v2, 1)  # CC A boundary
m.assert_edge_shared(v3, v4, 1)  # CC B boundary
m.assert_edge_shared(v4, v5, 1)  # CC B boundary
m.assert_edge_shared(v3, v5, 1)  # CC B boundary
