"""Me083 — connectivity_coincident_endpoints: edge between two vertices at identical positions.

Catalog claim: vertices v2 and v3 are at the same position (0.0, 0.0, 1.0).
Triangle t1 uses v2 and v3 as two of its corners — the edge (v2, v3) has zero
length (coincident endpoints). MeshFix checkConnectivity Branch 5
(*COINCIDENT_EDGE_ENDPOINTS*) detects edges whose two endpoint vertices occupy
the same position. Although the vertex indices are distinct, the geometric edge
length is zero, causing degenerate normals and invalid fan traversal.

Defect carrier: v2 and v3 share the exact same coordinates. Triangle t1 =
(v0, v2, v3) has a zero-length edge between v2 and v3.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me083",
             title="connectivity coincident edge endpoints: edge (v2,v3) has zero length — both at (0,0,1)",
             defect_class="near_coincident_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)

# Two distinct vertex indices but at the same position.
v2 = m.vertex(0.0, 0.0, 1.0)
v3 = m.vertex(0.0, 0.0, 1.0)   # coincident with v2

# Valid triangle using v0, v1, v2.
m.triangle(v0, v1, v2)

# Degenerate triangle: edge (v2, v3) is zero-length since v2 == v3 in position.
m.triangle(v0, v2, v3)

# v2 and v3 are at distance 0 — coincident endpoint pair.
m.assert_vertex_pair_distance_lt(v2, v3, 1e-12)

# Degenerate triangle t1 has zero area.
m.assert_triangle_area_lt(1, 1e-12)
