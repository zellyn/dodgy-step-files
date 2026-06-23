"""Me015 — polygon_with_repeated_vertex: a triangle listing the same vertex index twice.

Catalog claim: triangle 1 has vertex list (v1, v1, v2) — vertex 1 appears
twice. The "triangle" is degenerate: it collapses to the line segment (v1, v2)
with zero area and undefined normal. CGAL repair_polygon_soup detects and
removes polygons with repeated vertices; the zero-area fallback check is also
sufficient.

Defect carrier: triangle 1 references vertex 1 twice in its index list. Every
traversal that assumes i0 ≠ i1 ≠ i2 will produce undefined normals or
divide-by-zero in barycentric computations.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me015",
             title="polygon with repeated vertex: triangle 1 is (v1, v1, v2) — degenerate",
             defect_class="polygon_with_repeated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

m.triangle(v0, v1, v2)   # face 0: clean control
m.triangle(v1, v1, v2)   # face 1: v1 appears twice → zero area, degenerate

# Area = 0 because two vertices are the same point.
m.assert_triangle_area_lt(1, 1e-12)
