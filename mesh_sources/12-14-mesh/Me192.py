"""Me192 — splitTriangle_edge_e3_adjacency: e3's triangle pointer updated to nt1.

MeshFix `Basic_TMesh.splitTriangle` Branch 3 (*edge_e3_adjacency*) @ line 1921:
  't->e3->replaceTriangle(t, nt1)'
  Original triangle t's e3 edge (the v2→v0 side) used to point back to t.
  After creating nt1, the code replaces t's reference in e3 with nt1 so
  that e3's adjacency list correctly reflects nt1 owns that outer edge.

Defect carrier: the mesh shows a split triangle where e3's outer edge belongs
to nt1, not to the original slot t. A healer reads this and discovers that
e3 has been re-wired to nt1 — the "replaceTriangle" call is the action taken
to fix the dangling adjacency left by the split.

Geometry: same 3-way split layout. e3 = edge between v2 and v0.
  t   := (v0, v1, nv)   index 0
  nt1 := (nv, v2, v0)   index 1 ← e3 belongs here now
  nt2 := (nv, v1, v2)   index 2
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me192",
             title="splitTriangle_edge_e3_adjacency: outer edge e3 re-assigned from t to nt1",
             defect_class="split_triangle_edge_adjacency")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
nv = m.vertex(1.0, 0.7, 0.0)   # 3 — interior vertex

t0  = m.triangle(v0, v1, nv)   # 0 — original slot (no longer has e3)
nt1 = m.triangle(nv, v2, v0)   # 1 — nt1 owns e3 (= v2-v0 edge)
nt2 = m.triangle(nv, v1, v2)   # 2

# Core assertion: e3 (= v2-v0) is a boundary edge owned exclusively by nt1.
# If replaceTriangle failed, e3 would still point to t (index 0), and the mesh
# would have a broken adjacency — e3 used by t0 and nt1 simultaneously, giving n=2
# with wrong attribution, or the outer edge showing in t0 instead of nt1.
m.assert_edge_shared(v2, v0, 1)   # e3: boundary, exclusively owned by nt1

# e2 (v0-v1) is boundary and exclusively in t0 — NOT reassigned.
m.assert_edge_shared(v0, v1, 1)   # e2: boundary, owned by t0

# e1 (v1-v2) is boundary and exclusively in nt2.
m.assert_edge_shared(v1, v2, 1)   # e1: boundary, owned by nt2

# Inner edges — all interior (shared by two child triangles).
m.assert_edge_shared(nv, v0, 2)   # ne2: t0 and nt1
m.assert_edge_shared(nv, v1, 2)   # ne1: t0 and nt2
m.assert_edge_shared(nv, v2, 2)   # ne3: nt1 and nt2
