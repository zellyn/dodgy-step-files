"""Me125 — inverse_collapse_multi_redirection: multiple intermediate edges redirected to v2.

Catalog claim: vertex v0 has a 6-triangle fan where the split sector spans 3
triangles. The vertex_redirection branch (Branch 5) fires 2 times — one for each
of the 2 intermediate spokes in the sector that get reassigned from v0 to v_new.

This exercises MeshFix `Vertex.inverseCollapse` Branch 5 (*vertex_redirection_e2_to_e3*)
with N=2 iterations of `f->replaceVertex(this, v2)`. The geometry has 2 interior
spoke edges between e3 and e2 in the ring, so the replaceVertex loop runs twice.

Defect carrier: 6-triangle closed fan at interior v0. The split sector contains
3 triangles (t2, t3, t4) with e2=(v0,v3) and e3=(v0,v6). The two intermediate
spokes (v0,v4) and (v0,v5) are both redirected.

Geometry (interior vertex with 6 triangles):
  v0=(0,0,0) — fully interior vertex
  v1=(1,0,0), v2=(0.5,0.87,0), v3=(-0.5,0.87,0),
  v4=(-1,0,0), v5=(-0.5,-0.87,0), v6=(0.5,-0.87,0)

  t0=(v0,v1,v2), t1=(v0,v2,v3): non-sector triangles
  t2=(v0,v3,v4): sector start (e2=(v0,v3))
  t3=(v0,v4,v5): sector interior — (v0,v4) redirected
  t4=(v0,v5,v6): sector interior — (v0,v5) redirected
  t5=(v0,v6,v1): sector end (e3=(v0,v6))
"""
from step_corpus.mesh_builder import MeshFile

import math

m = MeshFile(catalog_id="Me125",
             title="inverse_collapse_multi_redirection: 2 intermediate edges redirected to v_new",
             defect_class="inverse_collapse_split_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — interior vertex to split
r = 1.0
for k in range(6):
    angle = 2 * math.pi * k / 6
    m.vertex(round(r * math.cos(angle), 6), round(r * math.sin(angle), 6), 0.0)
v1, v2, v3, v4, v5, v6 = 1, 2, 3, 4, 5, 6

t0 = m.triangle(v0, v1, v2)   # 0 — non-sector
t1 = m.triangle(v0, v2, v3)   # 1 — non-sector
t2 = m.triangle(v0, v3, v4)   # 2 — sector start; e2=(v0,v3)
t3 = m.triangle(v0, v4, v5)   # 3 — sector interior; (v0,v4) redirected
t4 = m.triangle(v0, v5, v6)   # 4 — sector interior; (v0,v5) redirected
t5 = m.triangle(v0, v6, v1)   # 5 — sector end; e3=(v0,v6)

# All spoke edges from v0 are interior (closed fan).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)   # e2
m.assert_edge_shared(v0, v4, 2)   # intermediate redirected
m.assert_edge_shared(v0, v5, 2)   # intermediate redirected
m.assert_edge_shared(v0, v6, 2)   # e3

# Ring boundary edges.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v6, v1, 1)
