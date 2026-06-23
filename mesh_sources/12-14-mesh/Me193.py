"""Me193 — splitTriangle_edge_e1_adjacency: e1's triangle pointer updated to nt2.

MeshFix `Basic_TMesh.splitTriangle` Branch 4 (*edge_e1_adjacency*) @ line 1922:
  't->e1->replaceTriangle(t, nt2)'
  Original triangle t's e1 edge (the v1→v2 side) used to point back to t.
  After creating nt2, the code replaces t's reference in e1 with nt2 so that
  e1's adjacency correctly reflects nt2 owns that outer edge.

This is symmetric to Branch 3 but for e1 (the v1-v2 outer edge).

Geometry: same canonical 3-way interior split. e1 = edge between v1 and v2.
  t   := (v0, v1, nv)   index 0
  nt1 := (nv, v2, v0)   index 1
  nt2 := (nv, v1, v2)   index 2 ← e1 belongs here now
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me193",
             title="splitTriangle_edge_e1_adjacency: outer edge e1 re-assigned from t to nt2",
             defect_class="split_triangle_edge_adjacency")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
nv = m.vertex(1.0, 0.7, 0.0)   # 3 — interior vertex

t0  = m.triangle(v0, v1, nv)   # 0 — original slot (no longer has e1)
nt1 = m.triangle(nv, v2, v0)   # 1
nt2 = m.triangle(nv, v1, v2)   # 2 — nt2 owns e1 (= v1-v2 edge)

# Core assertion: e1 (= v1-v2) is boundary, exclusively owned by nt2.
m.assert_edge_shared(v1, v2, 1)   # e1: boundary, owned by nt2

# e3 (v2-v0) is boundary and exclusively in nt1 — not in scope here.
m.assert_edge_shared(v2, v0, 1)   # e3: boundary, owned by nt1

# e2 (v0-v1) is boundary and exclusively in t0.
m.assert_edge_shared(v0, v1, 1)   # e2: boundary, owned by t0

# Inner edges — all interior.
m.assert_edge_shared(nv, v0, 2)   # ne2: t0 and nt1
m.assert_edge_shared(nv, v1, 2)   # ne1: t0 and nt2
m.assert_edge_shared(nv, v2, 2)   # ne3: nt1 and nt2
