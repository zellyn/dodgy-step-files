"""Me187 — split_edge_new_triangle_t2: t2 exists, create nt2 on the other side of the split.

Catalog claim: when the edge e is interior (both t1 and t2 non-NULL), a second
new triangle nt2 is created on the t2 side of the split, symmetric to nt1.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 8 (*new_triangle_t2*):
`if (e->t2 != NULL) nt2 = newTriangle(v, v4, e->v2)` (or equivalent) — a new
triangle is allocated and wired on the t2 side.

The complete interior split creates 4 triangles from the original 2:
  From t1: trimmed_t1=(v0,vn,v2) + nt1=(vn,v1,v2)
  From t2: trimmed_t2=(v0,v3,vn) + nt2=(vn,v3,v1)   ← nt2 is Branch 8

The fixture models a slightly larger diamond to distinguish from Me185/Me183,
with the four-triangle post-split configuration prominently showing nt2.

Geometry (post-split interior):
  v0=(0,0,0), v1=(4,0,0), v2=(2,2,0), v3=(2,-2,0), vn=(2,0,0)
  t0=(v0,vn,v2): trimmed t1
  t1=(vn,v1,v2): nt1
  t2=(v0,v3,vn): trimmed t2
  t3=(vn,v3,v1): nt2 — new triangle created by Branch 8
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me187",
             title="split_edge_new_triangle_t2: nt2 created on t2 side after interior edge split",
             defect_class="split_edge_interior")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — left endpoint
v1 = m.vertex(4.0,  0.0, 0.0)   # 1 — right endpoint
v2 = m.vertex(2.0,  2.0, 0.0)   # 2 — v3: apex above (t1 side)
v3 = m.vertex(2.0, -2.0, 0.0)   # 3 — v4: apex below (t2 side)
vn = m.vertex(2.0,  0.0, 0.0)   # 4 — new split vertex at midpoint

t0 = m.triangle(v0, vn, v2)   # 0 — trimmed t1 (left top)
t1 = m.triangle(vn, v1, v2)   # 1 — nt1 (right top)
t2 = m.triangle(v0, v3, vn)   # 2 — trimmed t2 (left bottom)
t3 = m.triangle(vn, v3, v1)   # 3 — nt2: new triangle on t2 side (Branch 8)

# Both new interior edges ne1 and ne2.
m.assert_edge_shared(vn, v2, 2)   # ne1: interior (t0 and t1)
m.assert_edge_shared(vn, v3, 2)   # ne2: interior (t2 and t3) — needed by nt2 (Branch 8)

# The half-edges at vn are interior (shared by t-pairs across the split axis).
m.assert_edge_shared(v0, vn, 2)   # (v0,vn): interior (t0 and t2)
m.assert_edge_shared(vn, v1, 2)   # (vn,v1): interior (t1 and t3)

# Outer boundary edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# vn on original edge.
m.assert_vertex_on_edge(vn, v0, v1)
