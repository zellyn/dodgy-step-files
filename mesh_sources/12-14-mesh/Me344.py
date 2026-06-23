"""Me344 — init_vertex_edge_reference_link: vertex e0 pointer set to copied edge during init.

MeshFix `Basic_TMesh.init` Branch 5 (*VERTEX_EDGE_REFERENCE_LINK*) @ line 208:
  '((Vertex *)v->info)->e0 = (Edge *)v->e0->info' — for each vertex, the clone vertex's
  e0 edge pointer is set to the corresponding cloned edge. If a vertex in the source mesh
  has its e0 pointing to a non-manifold or boundary edge, that same connectivity is
  reconstructed in the clone. A bowtie vertex (disconnected fan) has its e0 linking into
  only one of the two disconnected fan groups; the clone inherits this broken reference.

Defect pattern: a bowtie (non-manifold vertex) where vertex v4 is shared by two
  triangle fans that do not share any edge. When init reconstructs the clone, v4->e0
  can only point to one of the two fan groups — the clone has a disconnected vertex fan.

Geometry: bowtie at v4=(0,0,0).
  Fan A: v0=(-1,-1,0), v1=(1,-1,0), v4=(0,0,0) — t0.
  Fan B: v2=(-1,1,0), v3=(1,1,0), v4=(0,0,0) — t1.
  v4 is shared by t0 and t1 but the two fans touch only at v4 (bowtie vertex).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me344",
             title="init_vertex_edge_reference_link: bowtie vertex v4 e0 links into only one fan group",
             defect_class="non_manifold_vertex")

v0 = m.vertex(-1.0, -1.0, 0.0)   # fan A lower-left
v1 = m.vertex( 1.0, -1.0, 0.0)   # fan A lower-right
v2 = m.vertex(-1.0,  1.0, 0.0)   # fan B upper-left
v3 = m.vertex( 1.0,  1.0, 0.0)   # fan B upper-right
v4 = m.vertex( 0.0,  0.0, 0.0)   # bowtie hub — shared but fans are disconnected

t0 = m.triangle(v0, v1, v4)   # 0: fan A
t1 = m.triangle(v2, v3, v4)   # 1: fan B

# Bowtie: v4's incident triangles are in two disconnected groups.
m.assert_vertex_fan_disconnected(v4)

# All edges are boundary (open mesh — each triangle is isolated except at v4).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v3, v4, 1)
