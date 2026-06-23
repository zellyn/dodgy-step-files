"""Me122 — inverse_collapse_vertex_edge_list_circular: vertex VE() is a circular ring.

Catalog claim: vertex v0 has a fully-closed circular edge list (all edges are
interior). The inverseCollapse must traverse this ring using VE() to find the
position of e3 within the circular list. When all spokes are interior edges
(no boundary break), the VE() traversal is a true cycle.

This exercises MeshFix `Vertex.inverseCollapse` Branch 3
(*vertex_edge_list_circular*): the code calls VE() to get the circular edge
list, then iterates around looking for e3. A fully closed ring (no boundary)
is the standard case for an over-merged interior vertex.

Defect carrier: a closed 5-triangle fan where v0 is a fully interior vertex
(no boundary edges). The split sector spans two triangles (t2, t3) with e2
at the top and e3 at the bottom of the sector. The VE() circular traversal
is required to locate e3 from the starting edge e2.

Geometry (interior vertex with 5 triangles):
  v0=(0,0,0) — interior over-merged vertex
  v1=(1,0,0), v2=(0.31,0.95,0), v3=(-0.81,0.59,0),
  v4=(-0.81,-0.59,0), v5=(0.31,-0.95,0)  — pentagon ring vertices

  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4) — upper half
  t3=(v0,v4,v5), t4=(v0,v5,v1)                 — lower half

All edges from v0 are interior (each spoke shared by 2 triangles).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me122",
             title="inverse_collapse_vertex_edge_list_circular: fully interior vertex, circular VE() ring",
             defect_class="inverse_collapse_split_vertex")

import math
# Pentagon ring vertices at unit radius.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — fully interior vertex to split
# 5 equally-spaced ring vertices.
r = 1.0
for k in range(5):
    angle = 2 * math.pi * k / 5
    m.vertex(round(r * math.cos(angle), 6), round(r * math.sin(angle), 6), 0.0)
# vertices 1..5 are v1..v5 above.
v1, v2, v3, v4, v5 = 1, 2, 3, 4, 5

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1
t2 = m.triangle(v0, v3, v4)   # 2 — split sector start
t3 = m.triangle(v0, v4, v5)   # 3 — split sector end
t4 = m.triangle(v0, v5, v1)   # 4

# All spoke edges from v0 are interior (circular ring — no boundary at v0).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)   # e2 — split boundary
m.assert_edge_shared(v0, v4, 2)   # interior sector
m.assert_edge_shared(v0, v5, 2)   # e3 — split boundary

# All ring edges are boundary (each ring edge shared by exactly one triangle).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v1, 1)
