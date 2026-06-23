"""Me080 — connectivity_null_vertex: orphan vertex not referenced by any triangle.

Catalog claim: vertex 4 is completely isolated — it appears in the vertex list
but is not referenced by any triangle. MeshFix checkConnectivity Branch 1
(*NULL_VERTEX_ELEMENT*) detects vertices that have no valid edge pointer (the
e0 field is NULL), which occurs when a vertex is allocated but never connected
into the half-edge structure. The closest representable defect in a flat
triangle-list mesh is a vertex that is present in the vertex array but absent
from all triangles — an "orphan" vertex.

Defect carrier: 4 triangles form a closed quad shell (a square pyramid); vertex 4
is inserted into the vertex list at index 4 but no triangle references it.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me080",
             title="connectivity null vertex: vertex 4 is orphan — not referenced by any triangle",
             defect_class="isolated_vertex")

# Four vertices of a quad in the XY plane.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)

# Orphan vertex — never used in any triangle.
# Simulates NULL_VERTEX_ELEMENT: v4 is in the vertex list but has no e0 pointer.
v4 = m.vertex(5.0, 5.0, 5.0)

# Two triangles forming the quad — neither uses v4.
m.triangle(v0, v1, v2)
m.triangle(v0, v2, v3)

m.assert_isolated_vertex(v4)
