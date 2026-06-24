"""Me955 — Basic_TMesh.checkGeometry degenerate_angle_180_degrees: triangle angle = 0 or PI (Branch 6).

MeshFix `Basic_TMesh.checkGeometry` Branch 6 (*degenerate_angle_180_degrees*) @ line 238:
  'getDAngle(v1) == 0 || getDAngle(v1) == M_PI' — for each triangle vertex, the
  interior angle is computed. If it equals exactly 0 or π radians, the triangle is
  degenerate (collinear vertices). checkGeometry returns v1 (the degenerate vertex)
  immediately as the defect location.

Note: the 7-branch `Basic_TMesh.checkGeometry` combines both the zero-angle (0°)
and flat-angle (180°) cases into a single Branch 6. The 8-branch
`checkAndRepair::checkGeometry` separates them into Branch 6 (0°) and Branch 7 (π).

This fixture demonstrates the flat-angle (π = 180°) case: vertex p1 lies between
p0 and p2 on a line, so the two edges from p1 point in exactly opposite directions
(anti-parallel) → angle at p1 = π.

Geometry:
  p0=(0,0,0), p1=(1,0,0) [middle], p2=(2,0,0) — three collinear points on X-axis.
  Triangle t0=(p0,p1,p2): angle at p1 is 180°, area = 0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me955",
    title="Basic_TMesh.checkGeometry degenerate_angle_180_degrees: collinear triangle, interior angle PI at middle vertex (Branch 6)",
    defect_class="degenerate_triangle",
)

# Three collinear vertices on the X-axis.
p0 = m.vertex(0.0, 0.0, 0.0)    # 0 — left endpoint
p1 = m.vertex(1.0, 0.0, 0.0)    # 1 — middle pivot: angle = 180°
p2 = m.vertex(2.0, 0.0, 0.0)    # 2 — right endpoint

# Degenerate triangle: all three vertices collinear → area = 0.
t0 = m.triangle(p0, p1, p2)     # 0

# Triangle has zero area (collinear → zero cross product).
m.assert_triangle_area_lt(t0, 1e-12)

# p1 lies exactly on the segment p0→p2 (collinearity evidence).
m.assert_vertex_on_edge(p1, p0, p2)
