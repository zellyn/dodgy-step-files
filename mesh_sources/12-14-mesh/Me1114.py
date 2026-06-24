"""Me1114 — all candidate faces degenerate after prior pass: faces_to_treat empties.

Tests precondition that faces_to_treat.empty() would fire: a mesh where every
triangle in the self-intersection candidate set has zero area (degenerate), so
after the prior iteration processes and removes them the candidate set is empty
and the algorithm exits the SI loop early rather than recomputing intersections.

Source: CGAL PMP.remove_self_intersections Branch 5 @ line 2463 —
*face-selection-emptiness-detection*: faces_to_treat.empty() is checked after
topology blockers evict candidates; when empty the loop exits without recomputing
self-intersections.

Geometry:
  Triangles 0,2 are valid non-degenerate triangles forming control geometry.
  Triangles 1,3 are zero-area (all three vertices collinear) — these are the
  "topology-blocker" faces that would be evicted from faces_to_treat in the
  prior SI iteration. With both blocking faces removed the candidate set is
  empty, satisfying the Branch 5 emptiness check.

  tri 0: valid right triangle in Z=2 plane.
  tri 1: three collinear vertices along the Y-axis (area=0) — degenerate blocker.
  tri 2: valid equilateral-ish triangle in X=3 plane.
  tri 3: three collinear vertices along the X-axis (area=0) — degenerate blocker.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1114",
    title="zero-area degenerate faces empty the SI candidate set: faces_to_treat emptiness detection",
    defect_class="self_intersection_degenerate_cluster",
)

# Valid triangle 0: right triangle in Z=2 plane.
v0 = m.vertex(0.0, 0.0, 2.0)  # 0
v1 = m.vertex(1.0, 0.0, 2.0)  # 1
v2 = m.vertex(0.0, 1.0, 2.0)  # 2
m.triangle(v0, v1, v2)    # tri 0 — valid

# Degenerate triangle 1: collinear along Y-axis (area = 0).
v3 = m.vertex(0.0, 1.0, 0.0)  # 3
v4 = m.vertex(0.0, 3.0, 0.0)  # 4
v5 = m.vertex(0.0, 2.0, 0.0)  # 5 — collinear between v3 and v4
m.triangle(v3, v4, v5)    # tri 1 — degenerate: collinear Y-axis, area=0

# Valid triangle 2: triangle in X=3 plane.
v6 = m.vertex(3.0, 0.0, 0.0)  # 6
v7 = m.vertex(3.0, 1.0, 0.0)  # 7
v8 = m.vertex(3.0, 0.5, 1.0)  # 8
m.triangle(v6, v7, v8)    # tri 2 — valid

# Degenerate triangle 3: collinear along X-axis (area = 0).
v9  = m.vertex(1.0, 0.0, 0.0)  # 9
v10 = m.vertex(4.0, 0.0, 0.0)  # 10
v11 = m.vertex(2.5, 0.0, 0.0)  # 11 — collinear between v9 and v10
m.triangle(v9, v10, v11)  # tri 3 — degenerate: collinear X-axis, area=0

# Assert: both degenerate triangles have zero area.
m.assert_triangle_area_lt(1, 1e-12)
m.assert_triangle_area_lt(3, 1e-12)
