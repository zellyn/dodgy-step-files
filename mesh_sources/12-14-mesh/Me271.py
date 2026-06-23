"""Me271 — autorefine_triangle_soup: degenerate-face-tagging (Branch 2).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 2 @ line 1055:
  'p.first == p.second' — when the bbox intersection result contains a pair where
  both face descriptors are the same face (a self-pair), the face is tagged as
  degenerate (is_degen) and excluded from the refinement pipeline.

A collinear (zero-area) triangle has a degenerate bounding box. CGAL's AABB query
returns (f, f) self-pairs for such faces. Branch 2 catches this pattern: the pair's
first and second descriptors are identical, so the face is marked degenerate and
skipped in all subsequent intersection-point computation.

Geometry: one collinear degenerate triangle (three collinear points → area = 0)
plus one well-formed reference triangle that does not intersect anything. The (f,f)
self-pair causes Branch 2 to fire for the degenerate face.

Keywords: p.first==p.second, is_degen, degenerate face tagging.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me271",
             title="autorefine_triangle_soup degenerate-face-tagging: (f,f) self-pair → is_degen flag",
             defect_class="autorefine_degenerate_face_tag")

# Triangle 0: collinear — three vertices on the X-axis, area = 0.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — collinear with v0 and v1

# Triangle 1: valid non-degenerate triangle, well separated.
v3 = m.vertex(5.0, 0.0, 0.0)   # 3
v4 = m.vertex(6.0, 1.0, 0.0)   # 4
v5 = m.vertex(5.0, 1.0, 0.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0 — degenerate collinear face
t1 = m.triangle(v3, v4, v5)   # 1 — reference valid face

# Triangle 0 is degenerate: area below any positive threshold.
m.assert_triangle_area_lt(t0, 1e-9)

# Triangle 1 has non-zero area.
m.assert_triangles_do_not_intersect(t0, t1)
