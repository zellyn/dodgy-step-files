"""Me195 — splitTriangle_new_edge_ne2_adjacency: ne2 bridging nt1 and t.

MeshFix `Basic_TMesh.splitTriangle` Branch 6 (*new_edge_ne2_adjacency*) @ line 1926:
  'ne2->t1 = nt1; ne2->t2 = t'
  New inner edge ne2 is created between nv and v0 (the vertex shared by the
  original t slot and nt1). Its triangle slots are: t1=nt1 and t2=t (original).
  This inner edge stitches nt1 and t together.

Geometry: same 3-way interior split. ne2 = edge (nv, v0).
  t   := (v0, v1, nv)   index 0  ← ne2.t2
  nt1 := (nv, v2, v0)   index 1  ← ne2.t1
  nt2 := (nv, v1, v2)   index 2

The defect: without ne2 properly wired to nt1 and t, those two triangles would
not recognise each other as neighbours. The geometry confirms ne2 = (nv, v0)
is shared by exactly 2 triangles (nt1 as t1 and t as t2).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me195",
             title="splitTriangle_new_edge_ne2_adjacency: inner edge ne2=(nv,v0) bridges nt1 and t",
             defect_class="split_triangle_inner_edge_adjacency")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
nv = m.vertex(1.0, 0.7, 0.0)   # 3 — interior vertex

t0  = m.triangle(v0, v1, nv)   # 0 — t: ne2.t2
nt1 = m.triangle(nv, v2, v0)   # 1 — nt1: ne2.t1
nt2 = m.triangle(nv, v1, v2)   # 2

# Core assertion: ne2 = (nv, v0) is shared by exactly 2 triangles (nt1 and t0).
m.assert_edge_shared(nv, v0, 2)   # ne2: nt1 and t0 — Branch 6

# Confirm the other inner edges are also properly shared.
m.assert_edge_shared(nv, v1, 2)   # ne1: t0 and nt2
m.assert_edge_shared(nv, v2, 2)   # ne3: nt1 and nt2

# Outer edges: each owned by exactly one child.
m.assert_edge_shared(v0, v1, 1)   # e2: boundary (t0)
m.assert_edge_shared(v2, v0, 1)   # e3: boundary (nt1)
m.assert_edge_shared(v1, v2, 1)   # e1: boundary (nt2)
