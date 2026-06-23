"""Me312 — watsonInsert_cavity_vertex_v2: vertex v2 added to cavity boundary set.

MeshFix `holeFilling::watsonInsert` Branch 3 (*CAVITY_VERTEX_V2*) @ line 313:
  'bdr.appendHead(v2); MARK_BIT(v2, 5)'
  When a triangle is marked for removal, Branch 3 fires for v2 (the third
  vertex) — analogous to Branch 2 but for the third vertex slot. In practice
  both Branch 2 and Branch 3 fire for every removed triangle since all three
  vertices are checked; this fixture emphasises v2's role in the boundary list.

Defect pattern: a 4-triangle ring around a square hole. When the Bowyer-Watson
  cavity is excavated, the triangle being removed has v2 as a new boundary
  vertex. We model a square mesh with a 3-triangle cavity zone where v2 of
  the first removed triangle is a distinct vertex not yet in 'bdr'.

Geometry: 5 vertices forming a quad + apex.
  v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0), v4=(1,1,0)

  t0=(v0,v1,v4): lower triangle — first cavity candidate
  t1=(v1,v2,v4): right triangle
  t2=(v2,v3,v4): upper triangle
  t3=(v3,v0,v4): left triangle

  When the algorithm removes t0 from the cavity, v2=v4 (the hub) is the
  'v2 slot' vertex of t0 — it gets appended to bdr (Branch 3). The remaining
  triangles reveal the boundary edge loop.

We assert the hub edges and the outer boundary to confirm topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me312",
             title="watsonInsert_cavity_vertex_v2: v2 of removed triangle appended to cavity boundary (Branch 3)",
             defect_class="hole_in_hull")

# 4-triangle fan: outer square v0-v3, hub v4.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — hub (v2 slot in t0=(v0,v1,v4))

t0 = m.triangle(v0, v1, v4)   # 0 — v4 is v2 slot → Branch 3 bdr.appendHead(v2=v4)
t1 = m.triangle(v1, v2, v4)   # 1
t2 = m.triangle(v2, v3, v4)   # 2
t3 = m.triangle(v3, v0, v4)   # 3

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

# Outer loop: 4-vertex boundary visible when any hub triangle is excavated.
m.assert_hole_boundary([v0, v1, v2, v3])
