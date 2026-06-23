"""Me286 — checkGeometry_degenerate_triangle_flat_angle: triangle with 180-degree interior angle (Branch 7).

MeshFix `checkAndRepair::checkGeometry` Branch 7 (*DEGENERATE_TRIANGLE_FLAT_ANGLE*) @ line 239:
  `ang == M_PI` — the interior angle at vertex v1 is exactly π radians (180°). This
  means v1 lies between v0 and v2 on a straight line (the pivot vertex is in the
  MIDDLE of the three collinear points). checkGeometry returns v1 as the defect location.

Geometry: the defective triangle has its pivot vertex q1 at (1,-1,0) with neighbors
q0=(0,-1,0) and q2=(2,-1,0). All three are collinear along y=-1, with q1 between q0
and q2. Vectors from q1 to q0=(-1,0,0) and from q1 to q2=(+1,0,0) are anti-parallel.
Dot product = -1, angle = arccos(-1) = π = 180°. Area = 0.

Contrast with Branch 6 (zero angle = 0°): there the pivot vertex is at the END of
the collinear triple, so both edges point in the same direction.

Triangle t0 (control, index 0): c0=(0,0,0), c1=(1,0,0), c2=(0.5,1,0) — clean.
Triangle t1 (defect, index 1): q0=(0,-1,0), q1=(1,-1,0), q2=(2,-1,0) — 180° angle at q1.

Sources: MeshFix `checkAndRepair::checkGeometry` lines 237–242; MESH_HEAL_COVERAGE.md.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me286",
    title="checkGeometry_degenerate_triangle_flat_angle: interior angle = 180° (pi) at pivot vertex (Branch 7)",
    defect_class="degenerate_triangle",
)

# Triangle 0 (control) — clean equilateral-ish triangle.
c0 = m.vertex(0.0, 0.0, 0.0)    # 0
c1 = m.vertex(1.0, 0.0, 0.0)    # 1
c2 = m.vertex(0.5, 1.0, 0.0)    # 2
m.triangle(c0, c1, c2)           # t0 — area ≈ 0.5

# Triangle 1 (defect) — 180° flat angle at pivot q1.
# q0=(0,-1,0), q1=(1,-1,0), q2=(2,-1,0): collinear along y=-1.
# Angle at q1: edge q1→q0=(-1,0,0), edge q1→q2=(+1,0,0) — anti-parallel, angle=180°.
q0 = m.vertex(0.0, -1.0, 0.0)   # 3
q1 = m.vertex(1.0, -1.0, 0.0)   # 4 — pivot (angle measured here = 180°)
q2 = m.vertex(2.0, -1.0, 0.0)   # 5
m.triangle(q0, q1, q2)           # t1 — zero area, flat angle at q1

# Assert: triangle 1 has zero area (all three vertices collinear).
m.assert_triangle_area_lt(1, 1e-12)
