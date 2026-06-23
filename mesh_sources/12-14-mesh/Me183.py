"""Me183 — split_edge_opposite_vertex_t2: t2 exists, extract v4 opposite to edge in t2.

Catalog claim: edge e=(v0,v1) has triangles on both sides (t1 and t2). splitEdge
must extract v4, the vertex in t2 that is opposite to edge e:
`v4 = e->t2->oppositeVertex(e)`.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 4 (*opposite_vertex_t2*):
`if (e->t2 != NULL) v4 = e->t2->oppositeVertex(e)` — t2 is non-NULL so v4 is
extracted.

Defect carrier: an interior edge e=(v0,v1) shared by two triangles t0 and t1.
v2 is opposite in t0 (= t1 in MeshFix); v3 is opposite in t1 (= t2 in MeshFix).
The fixture shows the classic two-triangle diamond (quad) that a splitEdge
on the shared interior edge would refine.

Geometry (flat XY plane):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(1,-1,0)
  t0=(v0,v1,v2)   — t1 in MeshFix (v2 = v3 in MeshFix)
  t1=(v0,v3,v1)   — t2 in MeshFix (v3 = v4 in MeshFix, opposite vertex below)

Edge e=(v0,v1) is interior (n=2). Both v3 extractions fire.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me183",
             title="split_edge_opposite_vertex_t2: t2 exists, v4 extracted as oppositeVertex",
             defect_class="split_edge_interior")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — edge v1 endpoint
v1 = m.vertex(2.0,  0.0, 0.0)   # 1 — edge v2 endpoint
v2 = m.vertex(1.0,  1.0, 0.0)   # 2 — v3 (opposite in t1)
v3 = m.vertex(1.0, -1.0, 0.0)   # 3 — v4 (opposite in t2)

t0 = m.triangle(v0, v1, v2)   # 0 — t1 in MeshFix; v3 extracted from here
t1 = m.triangle(v0, v3, v1)   # 1 — t2 in MeshFix; v4 extracted from here

# e=(v0,v1): interior edge (both t1 and t2 set → n=2).
m.assert_edge_shared(v0, v1, 2)   # e: interior — both t1 and t2 non-NULL

# The four boundary spokes of the diamond.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
