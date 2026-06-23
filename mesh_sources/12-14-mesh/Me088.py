"""Me088 — connectivity_duplicate_triangle_edges: two triangles with identical vertex sets.

Catalog claim: triangles t0 and t1 reference the exact same vertex indices
{v0, v1, v2}, producing duplicate edges. MeshFix checkConnectivity Branch 12
(*DUPLICATE_TRIANGLE_EDGES*) detects a triangle where two of its three edges
are the same edge — which happens when two triangles are geometrically identical.
The half-edge structure cannot assign t1 and t2 consistently for any of the
shared edges because both triangles compete for the same three edge slots.

Defect carrier: t0 = (v0, v1, v2) and t1 = (v0, v1, v2) — exact duplicates.
Every edge between v0-v1, v1-v2, and v0-v2 is therefore incident on 2 triangles,
but since both triangles are identical, the half-edge topology is degenerate:
each edge has t1 = t0 and t2 = t1, making it appear the edge "owns" neither face.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me088",
             title="connectivity duplicate triangle edges: t0 and t1 are exact duplicates — same vertex indices (v0,v1,v2)",
             defect_class="duplicate_triangle")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

# Valid first triangle.
t0 = m.triangle(v0, v1, v2)

# Exact duplicate.
t1 = m.triangle(v0, v1, v2)

# Assert the two triangles are duplicates.
m.assert_duplicate_triangle_pair(t0, t1)

# Each edge is now shared by 2 triangles (the two identical faces).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v2, 2)
