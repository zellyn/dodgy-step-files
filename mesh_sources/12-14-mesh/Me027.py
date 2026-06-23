"""Me027 — adjacent_degenerate_faces_missed: partial input range misses connected neighbor (Branch 3).

Catalog claim: a cluster of three degenerate triangles shares edges. The
first (triangle 0) is collinear; it touches triangle 1 (also collinear) via
a shared edge. Triangle 2 (non-degenerate) provides context geometry. When
repair is called on only triangle 0, the adjacent degenerate triangle 1 must
be discovered and added to the degenerate set via the is_range_full_mesh /
faces_to_visit expansion path.

Source: CGAL PMP.remove_degenerate_faces Branch 3 @ line 2061 —
*adjacent-degenerate-faces-missed*: when input range is partial, the
sanitize step expands the set to include connected degenerate neighbors via
faces_to_visit walk.

Defect carrier: triangle 0 and triangle 1 are both collinear (zero area) and
share edge (v1, v2). Triangle 2 is a clean control. The two adjacent degenerate
faces must be discovered together for correct repair.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me027",
             title="adjacent degenerate faces: two collinear triangles sharing an edge — expansion branch",
             defect_class="degenerate_triangle")

# Two collinear degenerate triangles sharing edge (v1, v2).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(2.0, 0.0, 0.0)
v3 = m.vertex(3.0, 0.0, 0.0)

t0 = m.triangle(v0, v1, v2)   # collinear along y=0 — degenerate face 0
t1 = m.triangle(v1, v2, v3)   # collinear, shares edge (v1,v2) — degenerate face 1

# Clean control triangle (non-degenerate).
v4 = m.vertex(0.0, 0.0, 0.0)
v5 = m.vertex(1.0, 0.0, 0.0)
v6 = m.vertex(0.5, 1.0, 0.0)
t2 = m.triangle(v4, v5, v6)   # face 2: clean, non-degenerate

# Assert both degenerate triangles have zero area.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)

# Assert the shared edge between the two degenerate faces.
m.assert_edge_shared(v1, v2, 2)
