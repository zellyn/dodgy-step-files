"""Me185 — split_edge_new_edge_t2_creation: t2 exists, create ne2 from split vertex to v4.

Catalog claim: when edge e has a triangle on both sides (t1 and t2), a second new
edge ne2=(vn, v4) is created connecting the split vertex to v4, the opposite
vertex in t2. This symmetric step subdivides t2 similarly to how ne1 subdivides t1.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 6 (*new_edge_t2_creation*):
`if (e->t2 != NULL) ne2 = newEdge(v, v4)` — a second new edge is allocated for
the t2 side.

Defect carrier: an interior edge e=(v0,v1) with two incident triangles (diamond).
v2 is opposite in t1 (above); v3 is opposite in t2 (below). After split at
midpoint vn=(1,0,0), the geometry has 4 triangles and two new edges:
  ne1=(vn,v2): t1 side
  ne2=(vn,v3): t2 side  ← this is the branch we demonstrate

The fixture shows the POST-SPLIT state (all 4 triangles present with both ne1
and ne2 as interior edges of their respective sub-triangles).

Geometry (post-split diamond):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(1,-1,0), vn=(1,0,0)
  t0=(v0,vn,v2): left half of original t1
  t1=(vn,v1,v2): right half (nt1)
  t2=(v0,v3,vn): left half of original t2
  t3=(vn,v3,v1): right half (nt2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me185",
             title="split_edge_new_edge_t2_creation: ne2=(vn,v4) created after interior edge split",
             defect_class="split_edge_interior")

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — original v1 endpoint
v1 = m.vertex(2.0,  0.0, 0.0)   # 1 — original v2 endpoint
v2 = m.vertex(1.0,  1.0, 0.0)   # 2 — v3: opposite in original t1
v3 = m.vertex(1.0, -1.0, 0.0)   # 3 — v4: opposite in original t2
vn = m.vertex(1.0,  0.0, 0.0)   # 4 — new split vertex at midpoint of (v0,v1)

t0 = m.triangle(v0, vn, v2)   # 0 — left half of original t1
t1 = m.triangle(vn, v1, v2)   # 1 — nt1: right half of original t1
t2 = m.triangle(v0, v3, vn)   # 2 — left half of original t2
t3 = m.triangle(vn, v3, v1)   # 3 — nt2: right half of original t2

# ne1=(vn,v2) is interior: shared by t0 and t1.
m.assert_edge_shared(vn, v2, 2)   # ne1: interior

# ne2=(vn,v3) is interior: shared by t2 and t3.
m.assert_edge_shared(vn, v3, 2)   # ne2: interior — connects split vertex to v4

# Original edge split into two boundary halves.
m.assert_edge_shared(v0, vn, 2)   # left half — interior (shared by t0 and t2)
m.assert_edge_shared(vn, v1, 2)   # right half — interior (shared by t1 and t3)

# Outer boundary edges of the diamond.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# vn lies on the original edge.
m.assert_vertex_on_edge(vn, v0, v1)
