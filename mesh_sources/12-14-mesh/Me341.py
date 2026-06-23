"""Me341 — init_vertex_copy_iteration: vertex count drives FOREACHVVVERTEX loop in init.

MeshFix `Basic_TMesh.init` Branch 2 (*VERTEX_COPY_ITERATION*) @ line 197:
  'FOREACHVVVERTEX((&tin->V), v, n) { ... newVertex(...); v->info = nv; }' — iterates
  through all vertices in the source mesh, creating a new vertex per entry and storing a
  back-pointer in v->info. If the vertex list contains isolated (unreferenced) vertices,
  the iteration still creates clone-vertex objects for them — the info link is set even
  for orphan entries.

Defect pattern: a single triangle plus 2 isolated vertices not referenced by any triangle.
  The vertex list has 5 entries; init will iterate all 5 via FOREACHVVVERTEX and create
  clone nodes for each, including the 2 orphans. This exercises the full vertex-copy loop
  including orphan vertices that would cause problems in downstream Euler-characteristic
  computation.

Geometry: v0,v1,v2 form triangle t0; v3 and v4 are isolated orphan vertices at (5,0,0)
  and (0,5,0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me341",
             title="init_vertex_copy_iteration: 2 isolated vertices in vertex list drive FOREACHVVVERTEX over 5 entries",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(5.0, 0.0, 0.0)   # isolated — no triangle references this
v4 = m.vertex(0.0, 5.0, 0.0)   # isolated — no triangle references this

m.triangle(v0, v1, v2)   # only triangle

m.assert_isolated_vertex(v3)
m.assert_isolated_vertex(v4)

# All three triangle edges are boundary (open mesh).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
