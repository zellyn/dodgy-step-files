"""Me026 — all_faces_degenerate: entire mesh is zero-area (Branch 2).

Catalog claim: every triangle in the file is zero-area. All four triangles
are collinear (flat along z=0 with collinear vertices) so the degenerate-
face set equals the full face set.

Source: CGAL PMP.remove_degenerate_faces Branch 2 @ line 2052 —
*all-faces-degenerate*: degenerate_face_set.size() == faces_size triggers
a remove-all-elements path before the main repair loop.

Defect carrier: four triangles whose vertices are all collinear along the
X axis. Every area computation returns 0; no normal is defined anywhere in
the mesh. A healer that calls remove_degenerate_faces on this input hits the
all-faces-degenerate early-exit path.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me026",
             title="all faces degenerate: full mesh is collinear — remove_degenerate_faces all-exit branch",
             defect_class="degenerate_triangle")

# Four collinear triangles along the X axis at different Y offsets.
# Each has three collinear points → area == 0.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(2.0, 0.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # collinear along y=0, z=0

v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(1.0, 1.0, 0.0)
v5 = m.vertex(2.0, 1.0, 0.0)
t1 = m.triangle(v3, v4, v5)   # collinear along y=1, z=0

v6 = m.vertex(0.0, 2.0, 0.0)
v7 = m.vertex(1.0, 2.0, 0.0)
v8 = m.vertex(2.0, 2.0, 0.0)
t2 = m.triangle(v6, v7, v8)   # collinear along y=2, z=0

v9  = m.vertex(0.0, 3.0, 0.0)
v10 = m.vertex(1.0, 3.0, 0.0)
v11 = m.vertex(2.0, 3.0, 0.0)
t3 = m.triangle(v9, v10, v11)  # collinear along y=3, z=0

# Assert all four triangles have zero area.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)
m.assert_triangle_area_lt(t2, 1e-12)
m.assert_triangle_area_lt(t3, 1e-12)
