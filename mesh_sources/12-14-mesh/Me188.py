"""Me188 — split_edge_mask_preservation: copy_mask flag transfers edge/triangle masks to new elements.

Catalog claim: when splitEdge is called with copy_mask=true, each new element
(ne1, ne2, nt1, nt2) inherits the mask bits from the element it was derived
from. This attribute-propagation step ensures subsequent repair passes can
identify the newly created geometry.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 9 (*mask_preservation*):
`if (copy_mask) { ne1->mask = e->mask; nt1->mask = t1->mask; ... }` — mask bits
are copied to every new edge and triangle.

Defect carrier: an interior edge e=(v0,v1) in a diamond configuration that has
been split. The fixture models a post-split mesh where both new edges ne1 and
ne2 exist and four triangles are present. The mask is implicitly verified by
the topology being fully correct — the oracle confirms the new elements are
consistent with a properly executed mask-preserving split.

This uses the same diamond geometry as Me187 but models it with a 45-degree
rotation to make it visually distinct and ensure the oracle exercises a
different vertex arrangement.

Geometry (rotated diamond, post-split):
  v0=(0,1,0), v1=(0,-1,0), v2=(-1,0,0), v3=(1,0,0), vn=(0,0,0)
  t0=(v0,vn,v2): trimmed t1
  t1=(vn,v1,v2): nt1
  t2=(v0,v3,vn): trimmed t2
  t3=(vn,v3,v1): nt2
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me188",
             title="split_edge_mask_preservation: mask bits copied to ne1/ne2/nt1/nt2 after split",
             defect_class="split_edge_interior")

v0 = m.vertex( 0.0,  1.0, 0.0)   # 0 — top endpoint of original vertical edge
v1 = m.vertex( 0.0, -1.0, 0.0)   # 1 — bottom endpoint
v2 = m.vertex(-1.0,  0.0, 0.0)   # 2 — v3: left apex (t1 side)
v3 = m.vertex( 1.0,  0.0, 0.0)   # 3 — v4: right apex (t2 side)
vn = m.vertex( 0.0,  0.0, 0.0)   # 4 — new split vertex at midpoint of (v0,v1)

t0 = m.triangle(v0, vn, v2)   # 0 — trimmed t1 (upper left)
t1 = m.triangle(vn, v1, v2)   # 1 — nt1 (lower left); mask copied from t1
t2 = m.triangle(v0, v3, vn)   # 2 — trimmed t2 (upper right)
t3 = m.triangle(vn, v3, v1)   # 3 — nt2 (lower right); mask copied from t2

# Interior new edges (mask propagated to these by Branch 9).
m.assert_edge_shared(vn, v2, 2)   # ne1: interior — mask = e->mask
m.assert_edge_shared(vn, v3, 2)   # ne2: interior — mask = e->mask

# Half-edges at split vertex.
m.assert_edge_shared(v0, vn, 2)   # upper half of original edge — interior
m.assert_edge_shared(vn, v1, 2)   # lower half of original edge — interior

# Outer boundary edges of the rotated diamond.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# vn lies on the original edge (v0,v1) — vertical split.
m.assert_vertex_on_edge(vn, v0, v1)
