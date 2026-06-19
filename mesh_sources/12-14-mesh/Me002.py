"""Me002 — degenerate_triangle: zero-area face (collinear vertices).

Catalog claim: triangle 1 has three vertices collinear along the X axis
(0, 0, 0), (1, 0, 0), (2, 0, 0). Area is exactly 0; normal is undefined.

Defect carrier: triangle index 1 in the list has indices that map to
collinear points. Computed cross product gives zero vector — every
triangle-based traversal that uses the normal breaks.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me002",
             title="degenerate triangle: three collinear vertices, area=0",
             defect_class="degenerate_triangle")

# A clean triangle as control.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(2.0, 0.0, 0.0)
v2 = m.vertex(1.0, 2.0, 0.0)
m.triangle(v0, v1, v2)   # face 0: clean

# Three collinear vertices along X axis.
v3 = m.vertex(0.0, -1.0, 0.0)
v4 = m.vertex(1.0, -1.0, 0.0)
v5 = m.vertex(2.0, -1.0, 0.0)
m.triangle(v3, v4, v5)   # face 1: zero area, collinear

m.assert_triangle_area_lt(1, 1e-12)
