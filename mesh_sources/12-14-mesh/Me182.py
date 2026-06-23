"""Me182 — split_edge_opposite_vertex_t1: t1 exists, extract v3 opposite to edge in t1.

Catalog claim: edge e=(v0,v1) has a triangle t1 on one side. splitEdge must
extract v3, the vertex in t1 that is opposite to edge e. This is the first
geometry-extraction step: `v3 = e->t1->oppositeVertex(e)`.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 3 (*opposite_vertex_t1*):
`if (e->t1 != NULL) v3 = e->t1->oppositeVertex(e)` — t1 is non-NULL so v3 is
extracted.

Defect carrier: a boundary edge e=(v0,v1) with exactly one incident triangle t0
(= t1 in MeshFix naming). Vertex v2 is the opposite vertex. The fixture records
the pre-split state where e has t1 set but t2 is NULL (boundary edge).

Geometry (flat XY plane):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0)  — opposite vertex in t1
  t0=(v0,v1,v2)   (t1 in MeshFix)

Edge e=(v0,v1) is a boundary edge (n=1). t1=t0 exists; t2=NULL.
Split point p=(1,0,0) is the midpoint of e.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me182",
             title="split_edge_opposite_vertex_t1: t1 exists, v3 extracted as oppositeVertex",
             defect_class="split_edge_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — edge v1 endpoint
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — edge v2 endpoint
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — v3: opposite vertex in t1

t0 = m.triangle(v0, v1, v2)   # 0 — t1 in MeshFix; t2 is NULL (boundary)

# e=(v0,v1) is a boundary edge: n=1 (only t1 exists, t2=NULL).
m.assert_edge_shared(v0, v1, 1)   # e: boundary (t1 set, t2=NULL)
m.assert_edge_shared(v0, v2, 1)   # boundary spoke
m.assert_edge_shared(v1, v2, 1)   # boundary spoke

# v2 is the opposite vertex to edge (v0,v1) in t0.
# Post-split, vn=(1,0,0) would lie on the segment (v0,v1).
vn = m.vertex(1.0, 0.0, 0.0)   # 3 — proposed split midpoint (not yet inserted)
m.assert_vertex_on_edge(vn, v0, v1)   # midpoint lies on e
