"""Me123 — inverse_collapse_find_e3_position: e3 found at non-zero position in ring.

Catalog claim: vertex v0 has a 6-edge ring. In the inverseCollapse ring traversal,
the algorithm starts at the first edge and advances until it hits e3. Here e3 is at
position 3 in a 6-edge ring — the traversal must advance 3 steps before breaking.
This is the 'if (f == e3) break' condition triggered at a non-trivial position.

This exercises MeshFix `Vertex.inverseCollapse` Branch 4 (*find_e3_position*):
the circular ring iteration `do { f = VE()->t(); ... } while (f != VE()->t())`
hits the break condition `if (f == e3) break` at position k > 0. The geometry
has 6 triangles so e3 is encountered only after traversing 3 edges.

Defect carrier: 6-triangle closed fan at fully interior v0. The split sector
spans triangles t3 and t4 with e3=(v0,v4) at angular position 3/6 in the ring.
The traversal from e2=(v0,v3) forward hits e3 after 3 ring steps.

Geometry (interior vertex with 6 triangles — hexagonal fan):
  v0=(0,0,0) — interior vertex (6-way merge target, to be split)
  v1..v6 = hexagon ring vertices at angles 0°, 60°, 120°, 180°, 240°, 300°

  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4): upper semicircle
  t3=(v0,v4,v5), t4=(v0,v5,v6), t5=(v0,v6,v1): lower semicircle

Split sector: t2, t3 (two triangles). e2=(v0,v3) at position 2; e3=(v0,v5) at
position 4 — traversal must pass through positions 2,3,4 to find e3.
"""
from step_corpus.mesh_builder import MeshFile

import math

m = MeshFile(catalog_id="Me123",
             title="inverse_collapse_find_e3_position: e3 at position 3 in 6-edge ring, break triggered at k>0",
             defect_class="inverse_collapse_split_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — fully interior vertex to split
# 6 equally-spaced ring vertices.
r = 1.0
for k in range(6):
    angle = 2 * math.pi * k / 6
    m.vertex(round(r * math.cos(angle), 6), round(r * math.sin(angle), 6), 0.0)
v1, v2, v3, v4, v5, v6 = 1, 2, 3, 4, 5, 6

t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v0, v2, v3)   # 1
t2 = m.triangle(v0, v3, v4)   # 2 — sector start (e2=(v0,v3))
t3 = m.triangle(v0, v4, v5)   # 3 — sector interior
t4 = m.triangle(v0, v5, v6)   # 4 — sector end (e3=(v0,v5) at position 4)
t5 = m.triangle(v0, v6, v1)   # 5

# All spoke edges from v0 are interior.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)   # e2
m.assert_edge_shared(v0, v4, 2)   # sector interior
m.assert_edge_shared(v0, v5, 2)   # e3 — found at position 4 in traversal
m.assert_edge_shared(v0, v6, 2)

# Ring edges are boundary (one triangle each).
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v6, v1, 1)
