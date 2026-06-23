"""Me006 — duplicate_triangle: two triangles with identical vertex tuples.

Catalog claim: triangles 1 and 2 reference the same three vertex indices
(0, 1, 2) in the same winding order. Redundant faces inflate face counts,
break Euler characteristic checks, and cause double-lighting artefacts in
rendering pipelines.

Defect carrier: triangle list contains (0,1,2) twice. A healer running
CGAL merge_duplicate_polygons_in_polygon_soup or MeshFix
removeDuplicatedTriangles must detect and remove the copy.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me006",
             title="duplicate triangle: triangles 1 and 2 share identical vertex tuple",
             defect_class="duplicate_triangles")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(0.5, -1.0, 0.0)

m.triangle(v0, v3, v1)   # face 0: clean control triangle below X-axis
m.triangle(v0, v1, v2)   # face 1: the original upper triangle
m.triangle(v0, v1, v2)   # face 2: exact duplicate of face 1

m.assert_duplicate_triangle_pair(1, 2)
