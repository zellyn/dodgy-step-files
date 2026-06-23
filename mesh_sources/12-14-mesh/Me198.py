"""Me198 — splitTriangle_mask_copy_nt2: original triangle's mask propagated to nt2.

MeshFix `Basic_TMesh.splitTriangle` Branch 9 (*mask_copy_nt2*) @ line 1939:
  'nt2->mask = t->mask'
  When the caller requests mask propagation (copy_mask flag is set), the original
  triangle's mask bits are also copied to the second new child triangle nt2.
  Both nt1 (Branch 8) and nt2 (Branch 9) receive the mask; this fixture isolates
  the nt2 copy specifically.

Defect carrier: the pre-split mesh has a marked triangle t(v0,v1,v2). After
splitTriangle, nt2 inherits t's mask just as nt1 does. The geometric signature:
nt2 (the child on the e1 side) has finite positive area less than the original,
confirming it was constructed as a real triangle that can receive the mask.

Geometry (asymmetric to distinguish from Me197):
  v0=(0,0,0), v1=(4,0,0), v2=(2,3,0) — original triangle (even larger)
  nv=(2,1.2,0) — interior vertex

Post-split:
  t   := (v0, v1, nv)   index 0
  nt1 := (nv, v2, v0)   index 1
  nt2 := (nv, v1, v2)   index 2 ← mask copied here (Branch 9)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me198",
             title="splitTriangle_mask_copy_nt2: mask propagated from original t to second new child nt2",
             defect_class="split_triangle_mask_propagation")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(4.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 3.0, 0.0)   # 2
nv = m.vertex(2.0, 1.2, 0.0)   # 3 — interior vertex

t0  = m.triangle(v0, v1, nv)   # 0 — original slot
nt1 = m.triangle(nv, v2, v0)   # 1
nt2 = m.triangle(nv, v1, v2)   # 2 — Branch 9: mask copied from t to here

# nt2 (index 2) must exist with finite area — original area = 0.5*4*3 = 6.0.
# Each child has area ~2.0. Assert all three < 4.0 (well below original 6.0).
m.assert_triangle_area_lt(2, 4.0)   # nt2 area < 4.0 (child)
m.assert_triangle_area_lt(0, 4.0)   # t0 (reused slot) also < 4.0
m.assert_triangle_area_lt(1, 4.0)   # nt1 also < 4.0

# All three inner edges (through nv) are interior.
m.assert_edge_shared(nv, v0, 2)   # ne2: t0 and nt1
m.assert_edge_shared(nv, v1, 2)   # ne1: t0 and nt2
m.assert_edge_shared(nv, v2, 2)   # ne3: nt1 and nt2

# Outer edges: each boundary.
m.assert_edge_shared(v0, v1, 1)   # e2: t0
m.assert_edge_shared(v2, v0, 1)   # e3: nt1
m.assert_edge_shared(v1, v2, 1)   # e1: nt2
