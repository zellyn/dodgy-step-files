"""Me197 — splitTriangle_mask_copy_nt1: original triangle's mask propagated to nt1.

MeshFix `Basic_TMesh.splitTriangle` Branch 8 (*mask_copy_nt1*) @ line 1937:
  'nt1->mask = t->mask'
  When the caller requests mask propagation (copy_mask flag is set), the original
  triangle's mask bits are copied to the first new child triangle nt1. This
  ensures that selection / boundary markers are preserved after the split.

Defect carrier: the pre-split mesh has a marked triangle t(v0,v1,v2) — its mask
is non-zero, indicating it has a special attribute (e.g. selected, on hull
boundary). The split produces nt1 which inherits t's mask. The geometric
signature: nt1 is one of the three child triangles and has finite positive area,
confirming it is a real new triangle (not a degenerate placeholder), and its
existence as a triangle with area less than the original confirms the split
happened and the mask had something to copy to.

Geometry (slightly rotated for visual distinction):
  v0=(0,0,0), v1=(3,0,0), v2=(1.5,2,0) — original triangle (larger)
  nv=(1.5,0.8,0) — interior vertex

Post-split:
  t   := (v0, v1, nv)   index 0
  nt1 := (nv, v2, v0)   index 1 ← mask copied here (Branch 8)
  nt2 := (nv, v1, v2)   index 2
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me197",
             title="splitTriangle_mask_copy_nt1: mask propagated from original t to first new child nt1",
             defect_class="split_triangle_mask_propagation")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.5, 2.0, 0.0)   # 2
nv = m.vertex(1.5, 0.8, 0.0)   # 3 — interior vertex

t0  = m.triangle(v0, v1, nv)   # 0 — original slot
nt1 = m.triangle(nv, v2, v0)   # 1 — Branch 8: mask copied from t to here
nt2 = m.triangle(nv, v1, v2)   # 2

# nt1 (index 1) must exist with finite area — confirming it was created as a real
# triangle and not a degenerate placeholder. Area < original 3.0 (area of v0,v1,v2
# = 0.5*base*h = 0.5*3*2 = 3.0). Each child has area ~1.0.
m.assert_triangle_area_lt(1, 2.0)   # nt1 area < 2.0 (child, not original)
m.assert_triangle_area_lt(0, 2.0)   # t0 (reused slot) also < 2.0
m.assert_triangle_area_lt(2, 2.0)   # nt2 also < 2.0

# All three inner edges (through nv) are interior.
m.assert_edge_shared(nv, v0, 2)   # ne2: t0 and nt1
m.assert_edge_shared(nv, v1, 2)   # ne1: t0 and nt2
m.assert_edge_shared(nv, v2, 2)   # ne3: nt1 and nt2

# Outer edges: each boundary (one child only).
m.assert_edge_shared(v0, v1, 1)   # e2: t0
m.assert_edge_shared(v2, v0, 1)   # e3: nt1
m.assert_edge_shared(v1, v2, 1)   # e1: nt2
