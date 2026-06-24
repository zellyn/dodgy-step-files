"""Me711 — Basic_TMesh.removeVertices branch 2: orphan_vertex_check.

MeshFix `Basic_TMesh.removeVertices` Branch 2 (*orphan_vertex_check*) @ line 611:
  'if (v->e0 == NULL)' — for each vertex v in the traversal, the code checks
  whether v has a reference edge (e0). An isolated vertex has e0 == NULL and is
  therefore marked for removal. This branch fires when a vertex with no incident
  edge is encountered in the vertex list.

Defect pattern: two triangles sharing a diagonal plus one isolated vertex (v4)
  appended to the vertex list but not referenced by any triangle. When
  removeVertices walks the list it hits v4 and evaluates v->e0 == NULL → true.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0) form a quad split on the
  diagonal (v0,v2). v4=(5,5,0) is the isolated vertex.
  t0=(v0,v1,v2), t1=(v0,v2,v3); diagonal edge n=2; four boundary edges n=1.
  Euler: V=5, E=6, F=2, chi=1 (open surface, extra isolated vertex included).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me711",
    title="Basic_TMesh.removeVertices orphan_vertex_check: isolated vertex v4 has e0==NULL; check fires (Branch 2)",
    defect_class="isolated_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 1.0, 0.0)  # 2
v3 = m.vertex(0.0, 1.0, 0.0)  # 3
v4 = m.vertex(5.0, 5.0, 0.0)  # 4 — isolated; v->e0 == NULL

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v0, v2, v3)

# Shared diagonal.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Isolated vertex — e0 is NULL; orphan_vertex_check fires.
m.assert_isolated_vertex(v4)
