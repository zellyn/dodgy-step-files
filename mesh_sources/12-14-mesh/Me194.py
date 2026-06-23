"""Me194 — splitTriangle_new_edge_ne1_adjacency: ne1 bridging t and nt2.

MeshFix `Basic_TMesh.splitTriangle` Branch 5 (*new_edge_ne1_adjacency*) @ line 1925:
  'ne1->t1 = t; ne1->t2 = nt2'
  A new inner edge ne1 is created between nv and v1 (the vertex shared by the
  original t slot and nt2). Its two triangle slots are set to: t1=t (original
  slot) and t2=nt2. This inner edge stitches t and nt2 together.

Geometry: same 3-way interior split. ne1 = edge (nv, v1).
  t   := (v0, v1, nv)   index 0  ← ne1.t1
  nt1 := (nv, v2, v0)   index 1
  nt2 := (nv, v1, v2)   index 2  ← ne1.t2

The defect: without ne1 properly wired to both t and nt2, the two triangles
would not recognise each other as neighbours — a split that left a crack where
ne1 should bridge. The geometry shows ne1 = (nv, v1) shared by exactly 2
triangles (t and nt2).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me194",
             title="splitTriangle_new_edge_ne1_adjacency: inner edge ne1=(nv,v1) bridges t and nt2",
             defect_class="split_triangle_inner_edge_adjacency")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
nv = m.vertex(1.0, 0.7, 0.0)   # 3 — interior vertex

t0  = m.triangle(v0, v1, nv)   # 0 — t: ne1.t1
nt1 = m.triangle(nv, v2, v0)   # 1
nt2 = m.triangle(nv, v1, v2)   # 2 — nt2: ne1.t2

# Core assertion: ne1 = (nv, v1) is shared by exactly 2 triangles (t0 and nt2).
m.assert_edge_shared(nv, v1, 2)   # ne1: t0 and nt2 — Branch 5

# Confirm the other inner edges are also properly shared.
m.assert_edge_shared(nv, v0, 2)   # ne2: t0 and nt1
m.assert_edge_shared(nv, v2, 2)   # ne3: nt1 and nt2

# Outer edges: each owned by exactly one child.
m.assert_edge_shared(v0, v1, 1)   # e2: boundary (t0)
m.assert_edge_shared(v2, v0, 1)   # e3: boundary (nt1)
m.assert_edge_shared(v1, v2, 1)   # e1: boundary (nt2)
