"""Me008 — isolated_vertex: vertex with no incident triangle.

Catalog claim: vertex 3 is stored in the vertex list but referenced by no
triangle. It pollutes vertex-count-based Euler checks and wastes memory.
CGAL remove_isolated_vertices / remove_isolated_points_in_polygon_soup
silently removes it.

Defect carrier: vertex list has 4 entries; triangle list references only
vertices 0, 1, and 2. Vertex 3 is an orphan.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me008",
             title="isolated vertex: vertex 3 has no incident triangle",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(5.0, 5.0, 5.0)   # orphan — no triangle references this

m.triangle(v0, v1, v2)   # only triangle; v3 is unreferenced

m.assert_isolated_vertex(v3)
