"""Me342 — init_edge_copy_iteration: edge count drives FOREACHVEEDGE loop in init.

MeshFix `Basic_TMesh.init` Branch 3 (*EDGE_COPY_ITERATION*) @ line 202:
  'FOREACHVEEDGE((&tin->E), e, n) { ... newEdge(...); e->info = ne; }' — iterates
  through all edges in the source TMesh and creates a clone edge per entry. When the
  input topology has a non-manifold edge (shared by 3+ triangles) the edge list contains
  an entry that has more than 2 incident triangle slots — the clone loop still copies each
  edge object, but the cloned edge will have an inconsistent t1/t2 reference.

Defect pattern: three triangles sharing a single edge (v0,v2). In TMesh representation
  this creates a single Edge entry with 3 incident triangles — one more than the t1/t2
  pair can represent. Branch 3's loop copies every edge object including this over-incident
  entry.

Geometry: v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(0,0,1), v4=(-1,0,0).
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v2,v4) — 3 faces on edge (v0,v2).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me342",
             title="init_edge_copy_iteration: non-manifold edge forces FOREACHVEEDGE to copy over-incident edge entry",
             defect_class="non_manifold_edge")

v0 = m.vertex( 0.0,  0.0, 0.0)
v1 = m.vertex( 1.0,  0.0, 0.0)
v2 = m.vertex( 0.0,  1.0, 0.0)
v3 = m.vertex( 0.0,  0.0, 1.0)
v4 = m.vertex(-1.0,  0.0, 0.0)

m.triangle(v0, v1, v2)   # 0
m.triangle(v0, v2, v3)   # 1
m.triangle(v0, v2, v4)   # 2: third triangle on (v0,v2) — non-manifold

m.assert_edge_shared(v0, v2, 3)
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v2, v4, 1)
