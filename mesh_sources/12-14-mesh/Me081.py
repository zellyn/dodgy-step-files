"""Me081 — connectivity_null_edge_ref: interior vertex with no incident edge pointer.

Catalog claim: vertex 4 sits geometrically inside the mesh boundary but is not
referenced by any triangle, giving it a NULL e0 pointer in the half-edge
structure. MeshFix checkConnectivity Branch 2 (*NULL_EDGE_REFERENCE*) fires
when it encounters a vertex whose e0 field is NULL — meaning no edge has been
linked to that vertex. In a flat triangle list this corresponds to a vertex that
is present in the vertex array but not referenced by any face.

Defect carrier: triangles t0–t3 form a triangulated square; vertex v4 is
geometrically at the centroid (0.5, 0.5, 0) but appears nowhere in the triangle
list. This is the "interior orphan" pattern: the vertex logically belongs inside
the mesh but was never stitched in.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me081",
             title="connectivity null edge ref: interior orphan vertex v4 at centroid, no triangles reference it",
             defect_class="isolated_vertex")

# Square corners.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)

# Orphan vertex at centroid — geometrically plausible but not wired in.
v4 = m.vertex(0.5, 0.5, 0.0)

# Two triangles forming the square — v4 not referenced.
m.triangle(v0, v1, v2)
m.triangle(v0, v2, v3)

m.assert_isolated_vertex(v4)
