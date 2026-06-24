"""Me380 — isDoubleFlat_empty_1ring: vertex has no incident edges; VE() list is empty.

MeshFix `Vertex.isDoubleFlat` Branch 1 (*empty_1ring*) @ line 323:
  'if ((ve = VE()) == NULL) return false;'
  When the vertex-edge list is NULL (no incident edges), isDoubleFlat returns
  false immediately. This is the degenerate case of a completely isolated vertex
  that appears in the vertex list but is not referenced by any triangle.

Geometric signature: vertex v0 is listed in the mesh but no triangle references
it. It has zero incident edges; VE() returns NULL; Branch 1 fires and returns
false. The remaining vertices v1-v4 form two triangles that do not include v0.

Geometry:
  v0 = (0.0, 0.0, 0.0)  — isolated vertex (no incident edges)
  v1 = (1.0, 0.0, 0.0)
  v2 = (2.0, 0.0, 0.0)
  v3 = (1.5, 1.0, 0.0)
  v4 = (0.5, 1.0, 0.0)

  t0 = (v1, v2, v3)
  t1 = (v1, v3, v4)

  v0 is not referenced by any triangle — isolated vertex.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me380",
             title="isDoubleFlat_empty_1ring: isolated vertex v0 has no incident edges; VE() NULL triggers Branch 1 return false",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — isolated (no incident edges)
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3
v4 = m.vertex(0.5, 1.0, 0.0)   # 4

t0 = m.triangle(v1, v2, v3)    # 0
t1 = m.triangle(v1, v3, v4)    # 1

# v0 has no incident edges — isolated vertex; Branch 1 of isDoubleFlat fires.
m.assert_isolated_vertex(v0)

# The two triangles share edge (v1,v3).
m.assert_edge_shared(v1, v3, 2)

# Boundary edges of the triangle pair are each shared by 1 triangle.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)
