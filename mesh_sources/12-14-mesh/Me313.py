"""Me313 — watsonInsert_cavity_vertex_v3: vertex v3 added to cavity boundary set.

MeshFix `holeFilling::watsonInsert` Branch 4 (*CAVITY_VERTEX_V3*) @ line 314:
  'bdr.appendHead(v3); MARK_BIT(v3, 5)'
  The code refers to three vertex slots of each triangle as v1/v2/v3 in its
  half-edge walk. Branch 4 fires when the 'v3 slot' vertex of a removed
  triangle hasn't yet been added to the boundary list.

Defect pattern: a 4-triangle rectangular grid. When the Bowyer-Watson cavity
  removes triangles, the v3-slot vertex of each triangle is the one that
  becomes a new cavity boundary entry — Branch 4.

Geometry: 2x2 quad split into 4 triangles via a diagonal.
  v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0) — outer square corners.
  v4=(1,1,0) — center hub (v3 slot when it's the third vertex of a triangle).

  t0=(v0,v1,v4): v4 is the 'v3 slot' vertex of this triangle
  t1=(v1,v2,v4): v4 is the 'v3 slot' vertex
  t2=(v2,v3,v4): v4 is the 'v3 slot' vertex
  t3=(v3,v0,v4): v4 is the 'v3 slot' vertex

  When any fan triangle is removed, v4 (hub) is added to bdr as the v3 slot.
  For the next removed triangle, its v3-slot outer vertex is a NEW boundary
  vertex — Branch 4 fires for each new vertex.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me313",
             title="watsonInsert_cavity_vertex_v3: v3-slot vertex of removed triangle appended to cavity boundary (Branch 4)",
             defect_class="hole_in_hull")

# 4-triangle fan: outer square + center hub.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — hub; v3-slot vertex in all 4 fan triangles

t0 = m.triangle(v0, v1, v4)   # 0 — v4 is 'v3 slot'
t1 = m.triangle(v1, v2, v4)   # 1 — v4 is 'v3 slot'
t2 = m.triangle(v2, v3, v4)   # 2 — v4 is 'v3 slot'
t3 = m.triangle(v3, v0, v4)   # 3 — v4 is 'v3 slot'

# Hub edges — each shared by exactly 2 triangles.
m.assert_edge_shared(v0, v4, 2)
m.assert_edge_shared(v1, v4, 2)
m.assert_edge_shared(v2, v4, 2)
m.assert_edge_shared(v3, v4, 2)

# Outer boundary edges — each incident on 1 triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Outer loop: 4-vertex boundary visible when hub triangles are excavated.
m.assert_hole_boundary([v0, v1, v2, v3])
