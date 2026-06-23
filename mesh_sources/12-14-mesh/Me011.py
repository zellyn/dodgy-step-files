"""Me011 — non_manifold_vertex (bowtie): two surface patches share only one vertex.

Catalog claim: vertex 0 is a "pinch" or "bowtie" vertex — two triangles share
it but no edge connects them through it. The mesh is not a 2-manifold at v0:
removing it disconnects the neighborhood into two components. Half-edge data
structures that assume a 2-manifold vertex star will corrupt their fan
traversal. MeshFix duplicateNonManifoldVertices / CGAL
duplicate_non_manifold_vertices must split v0 into two copies.

Defect carrier: two triangles share only vertex 0 with no shared edge; the
upper fan (v0,v1,v2) and lower fan (v0,v3,v4) are disjoint except at v0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me011",
             title="non-manifold vertex (bowtie): two triangle fans share only vertex 0",
             defect_class="non_manifold_vertex")

# Bowtie vertex — the pinch point.
v0 = m.vertex(0.0, 0.0, 0.0)

# Upper fan (two triangles above X axis).
v1 = m.vertex(1.0, 1.0, 0.0)
v2 = m.vertex(-1.0, 1.0, 0.0)

# Lower fan (two triangles below X axis).
v3 = m.vertex(1.0, -1.0, 0.0)
v4 = m.vertex(-1.0, -1.0, 0.0)

m.triangle(v0, v1, v2)   # face 0: upper-left fan
m.triangle(v0, v3, v4)   # face 1: lower-right fan — shares only v0, no shared edge

# The edges incident on v0 from face 0 are (v0,v1) and (v0,v2); each appears once.
# The edges incident on v0 from face 1 are (v0,v3) and (v0,v4); each appears once.
# All four edges at v0 are boundary edges (n=1), confirming the bowtie structure.
m.assert_edge_shared(v0, v1, 1)   # boundary edge — only in face 0
m.assert_edge_shared(v0, v3, 1)   # boundary edge — only in face 1
m.assert_vertex_fan_disconnected(v0)
