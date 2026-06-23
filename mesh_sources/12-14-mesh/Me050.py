"""Me050 — degenerate collinear face triggers (f,f) self-pair in SI detection.

Catalog claim: a collinear (zero-area) triangle is present alongside a valid
triangle. CGAL PMP.self_intersections_impl Branch 3 @ line 400 tests each face
for degeneracy before building its bounding box for the AABB tree: if the face
is collinear, the implementation reports a self-intersection pair (f, f) rather
than inserting the degenerate face into the spatial index.

Source: CGAL PMP.self_intersections_impl Branch 3 @ line 400 —
*degenerate-face-vs-real-si*: collinear face is detected early; reported as
(f,f) pair (or bbox-skip depending on throw_on_SI flag) rather than entering
the AABB traversal.

Defect carrier: triangle 0 is collinear (v0, v1, v2 all on the X-axis).
Triangle 1 is a valid upright triangle for context; the two triangles do not
actually cross. The collinear triangle has area = 0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me050",
             title="Degenerate collinear face: SI-impl detects (f,f) self-pair",
             defect_class="self_intersection_degenerate_face")

# Triangle 0: collinear — three points on the X-axis (zero area).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — collinear with v0, v1

# Triangle 1: valid non-degenerate triangle (separated, no crossing).
v3 = m.vertex(5.0,  0.0, 0.0)  # 3
v4 = m.vertex(6.0,  1.0, 0.0)  # 4
v5 = m.vertex(6.0, -1.0, 0.0)  # 5

m.triangle(v0, v1, v2)   # tri 0 — collinear / degenerate
m.triangle(v3, v4, v5)   # tri 1 — valid reference triangle

# Assert: triangle 0 is degenerate (area = 0, below any positive threshold).
m.assert_triangle_area_lt(0, 1e-9)
