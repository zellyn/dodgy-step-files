"""Me196 — splitTriangle_new_edge_ne3_adjacency: ne3 bridging nt2 and nt1.

MeshFix `Basic_TMesh.splitTriangle` Branch 7 (*new_edge_ne3_adjacency*) @ line 1927:
  'ne3->t1 = nt2; ne3->t2 = nt1'
  New inner edge ne3 is created between nv and v2 (the vertex shared by nt1
  and nt2). Its triangle slots are: t1=nt2 and t2=nt1. This inner edge stitches
  the two new child triangles nt1 and nt2 together, completing the 3-way split.

Geometry: same 3-way interior split. ne3 = edge (nv, v2).
  t   := (v0, v1, nv)   index 0
  nt1 := (nv, v2, v0)   index 1  ← ne3.t2
  nt2 := (nv, v1, v2)   index 2  ← ne3.t1

The defect: without ne3 wired to nt2 and nt1, those two new triangles would
form a crack along the nv-v2 edge. The geometry confirms ne3 = (nv, v2) is
shared by exactly 2 triangles (nt2 as t1 and nt1 as t2).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me196",
             title="splitTriangle_new_edge_ne3_adjacency: inner edge ne3=(nv,v2) bridges nt2 and nt1",
             defect_class="split_triangle_inner_edge_adjacency")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
nv = m.vertex(1.0, 0.7, 0.0)   # 3 — interior vertex

t0  = m.triangle(v0, v1, nv)   # 0 — t (original slot)
nt1 = m.triangle(nv, v2, v0)   # 1 — nt1: ne3.t2
nt2 = m.triangle(nv, v1, v2)   # 2 — nt2: ne3.t1

# Core assertion: ne3 = (nv, v2) is shared by exactly 2 triangles (nt1 and nt2).
m.assert_edge_shared(nv, v2, 2)   # ne3: nt1 and nt2 — Branch 7

# Confirm the other inner edges are also properly shared.
m.assert_edge_shared(nv, v0, 2)   # ne2: t0 and nt1
m.assert_edge_shared(nv, v1, 2)   # ne1: t0 and nt2

# Outer edges: each owned by exactly one child.
m.assert_edge_shared(v0, v1, 1)   # e2: boundary (t0)
m.assert_edge_shared(v2, v0, 1)   # e3: boundary (nt1)
m.assert_edge_shared(v1, v2, 1)   # e1: boundary (nt2)
