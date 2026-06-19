"""Me001 — non_manifold_edge: three triangles share a single edge.

Catalog claim: edge (v0, v2) is incident to three triangle faces, making
the local topology non-manifold. Half-edge data structures cannot
represent this without splitting the edge or duplicating data.

Defect carrier: the triangle list literally contains three triangles
all referencing the edge (0, 2). A healer must split the edge or cut
the mesh along it; it cannot proceed assuming 2-manifold topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me001",
             title="non-manifold edge: three triangles share edge (v0, v2)",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.0, 1.0, 0.0)
v3 = m.vertex(0.0, 0.0, 1.0)
v4 = m.vertex(-1.0, 0.0, 0.0)

m.triangle(v0, v1, v2)   # face 0: +X half
m.triangle(v0, v2, v3)   # face 1: +Z half
m.triangle(v0, v2, v4)   # face 2: -X half — third sharer of edge (v0, v2)

m.assert_edge_shared(v0, v2, 3)
