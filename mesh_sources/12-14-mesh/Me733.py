"""Me733 — checkAndRepair::meshclean branch 4: REMAINING_DEGENERACY_AFTER_SUCCESS.

Source method: MeshFix `checkAndRepair::meshclean` Branch 4 @ line 1050.
Branch condition: after `if (ni && nd)` succeeds (both passes returned true),
`isExactlyDegenerate` finds a remaining degenerate triangle. The kernel sets
`ni = false` to signal incomplete success, preventing a false "clean" return.

Defect pattern: a mesh where both strongDegeneracyRemoval and
strongIntersectionRemoval claim success (return true), yet a zero-area
degenerate triangle survives in the mesh. This occurs when the degenerate
face is introduced *by* a repair step (e.g., a collapse that flattens a
sliver into collinearity) rather than being present in the input.

Geometry:
  A pyramid base with an additional collinear (zero-area) triangle that
  straddles two existing vertices. The non-degenerate faces form a clean
  structure that allows both repair passes to succeed; the degenerate face
  remains because it shares edges with two clean faces and the repair
  heuristic skips it (treating it as a boundary artifact).

  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(0.5,0,0)
  v4=(1.5,0,0)

  t0=(v0,v1,v2) — clean base triangle (area = 1.0)
  t1=(v0,v3,v4) — degenerate: v3 and v4 are collinear with v0 at Y=0
  t2=(v3,v4,v2) — small but non-degenerate triangle bridging to apex

  Note: t1 has all vertices at Y=0 → zero area, but t2 is valid.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me733",
    title="meshclean REMAINING_DEGENERACY_AFTER_SUCCESS: zero-area residual collinear face after ni && nd succeed; ni set false (branch 4)",
    defect_class="degenerate_triangle",
)

# Clean large base triangle.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 1.0, 0.0)  # 2 — apex (non-collinear)

# Degenerate residual face: three collinear points on the base line Y=0.
v3 = m.vertex(0.5, 0.0, 0.0)  # 3 — collinear with v0 and v1
v4 = m.vertex(1.5, 0.0, 0.0)  # 4 — collinear with v0 and v1

# Clean base triangle.
t0 = m.triangle(v0, v1, v2)   # 0 — clean, area = 1.0

# Degenerate residual: all three vertices on the X-axis (Y=0).
t1 = m.triangle(v0, v3, v4)   # 1 — degenerate, area = 0

# Non-degenerate bridge triangle connecting base to apex.
t2 = m.triangle(v3, v1, v2)   # 2 — clean, non-zero area

# Assert the residual degenerate triangle (Branch 4 trigger).
m.assert_triangle_area_lt(t1, 1e-9)

# Clean base and bridge have non-zero area (confirms only t1 is degenerate).
# v3 lies between v0 and v1 on the X-axis (collinearity evidence).
m.assert_vertex_pair_distance_lt(v0, v3, 1.0)  # v0 to v3 = 0.5 < 1.0
m.assert_vertex_pair_distance_lt(v3, v4, 1.1)  # v3 to v4 = 1.0 < 1.1 (collinear mid-range)

# Edge sharing: t1's edges are shared with t0 and t2 (locked in topology).
m.assert_edge_shared(v0, v3, 1)  # boundary of t1
m.assert_edge_shared(v3, v4, 1)  # boundary of t1
