"""Me1153 — is_degenerate_triangle_face collinear: collinear triangle has zero area.

CGAL PMP `PMP.is_degenerate_triangle_face` Branch 1 (*collinear*) @ line 300:
  The function computes the cross product of the two edge vectors from the
  first vertex; a zero-length cross product (i.e. zero area) signals that
  all three vertices are collinear, and the function returns true immediately.

Defect pattern: a triangle with all three vertices on the same line — the
  classic degenerate "needle" collapsed to a segment. Any positive-area
  triangle would not fire this branch.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — three collinear points on the x-axis.
  t0=(v0,v1,v2): a zero-area degenerate triangle (all y==0, all z==0).
  Cross product: (v1-v0) × (v2-v0) = (1,0,0) × (2,0,0) = (0,0,0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1153",
    title="is_degenerate_triangle_face collinear: zero-area triangle; all three vertices collinear on x-axis",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — origin
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — midpoint
v2 = m.vertex(2.0, 0.0, 0.0)  # 2 — far end; collinear with v0 and v1

# Single degenerate triangle: all vertices on x-axis.
t0 = m.triangle(v0, v1, v2)  # 0: collinear — zero area

# Triangle area is zero (collinear vertices, cross product == 0).
m.assert_triangle_area_lt(t0, 1e-9)

# v1 lies exactly on the segment v0→v2 (midpoint).
m.assert_vertex_on_edge(v1, v0, v2)
