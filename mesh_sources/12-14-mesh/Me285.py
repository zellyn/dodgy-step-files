"""Me285 — checkGeometry_degenerate_triangle_zero_angle: triangle with 0-degree interior angle (Branch 6).

MeshFix `checkAndRepair::checkGeometry` Branch 6 (*DEGENERATE_TRIANGLE_ZERO_ANGLE*) @ line 237:
  For each triangle, checkGeometry computes the interior angle at vertex v1 (the second
  vertex in the half-edge structure). If the angle equals 0 (edges from v1 point in the
  same direction), the triangle is degenerate. checkGeometry returns v1 immediately.

Geometry: the defective triangle has a pivot vertex p1 at (0,-1,0) with two neighbors
p0=(1,-1,0) and p2=(2,-1,0). All three are collinear along y=-1. The vectors from p1
to p0 and from p1 to p2 are (+1,0,0) and (+2,0,0) — same direction. Dot product = 2,
|a|=1, |b|=2, angle = arccos(1) = 0°. This is the *zero-angle* branch. Area = 0.

Contrast with Branch 7 (flat angle = 180°): there the pivot vertex lies BETWEEN the
other two on the line, so edges point in opposite directions.

Triangle t0 (control, index 0): c0=(0,0,0), c1=(1,0,0), c2=(0.5,1,0) — clean.
Triangle t1 (defect, index 1): p0=(1,-1,0), p1=(0,-1,0), p2=(2,-1,0) — zero angle at p1.

Sources: MeshFix `checkAndRepair::checkGeometry` lines 234–240; MESH_HEAL_COVERAGE.md.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me285",
    title="checkGeometry_degenerate_triangle_zero_angle: interior angle = 0° at pivot vertex (Branch 6)",
    defect_class="degenerate_triangle",
)

# Triangle 0 (control) — clean equilateral-ish triangle.
c0 = m.vertex(0.0, 0.0, 0.0)    # 0
c1 = m.vertex(1.0, 0.0, 0.0)    # 1
c2 = m.vertex(0.5, 1.0, 0.0)    # 2
m.triangle(c0, c1, c2)           # t0 — area ≈ 0.5

# Triangle 1 (defect) — zero angle at pivot p1.
# p0=(1,-1,0), p1=(0,-1,0), p2=(2,-1,0): collinear along y=-1.
# Angle at p1: edge p1→p0=(+1,0,0), edge p1→p2=(+2,0,0) — same direction, angle=0°.
p0 = m.vertex(1.0, -1.0, 0.0)   # 3
p1 = m.vertex(0.0, -1.0, 0.0)   # 4 — pivot (angle measured here = 0°)
p2 = m.vertex(2.0, -1.0, 0.0)   # 5
m.triangle(p0, p1, p2)           # t1 — zero area, zero angle at p1

# Assert: triangle 1 has zero area (all three vertices collinear).
m.assert_triangle_area_lt(1, 1e-12)
