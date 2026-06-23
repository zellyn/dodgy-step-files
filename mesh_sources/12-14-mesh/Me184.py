"""Me184 — split_edge_new_edge_t1_creation: t1 exists, create ne1 from split vertex to v3.

Catalog claim: after inserting the new split vertex vn at midpoint p, a new edge
ne1=(vn, v3) must be created to span from the split point to the opposite vertex
in t1. This subdivides the old triangle t1 into two: the original t1 (now
covering v1-v2-vn half) and a new triangle nt1 (covering v1-v2-vn other side).

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 5 (*new_edge_t1_creation*):
`if (e->t1 != NULL) ne1 = newEdge(v, v3)` — a new edge is allocated connecting
the new split vertex to v3.

Defect carrier: a boundary edge e=(v0,v1) with one incident triangle t0. v2 is
the opposite vertex. After split at midpoint vn=(1,0,0), the geometry has:
  - original t1 shrunk to (v0, vn, v2)
  - new triangle nt1=(vn, v1, v2)
  - new edge ne1=(vn, v2) created to connect split point to v3=v2

The fixture shows the POST-SPLIT state: vn is present and ne1=(vn,v2) is a
new interior edge shared by the two new triangles.

Geometry (post-split):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), vn=(1,0,0) — split vertex
  t0=(v0,vn,v2): left half of original t1
  t1=(vn,v1,v2): right half (nt1)
  ne1=(vn,v2): new edge connecting split vertex to opposite vertex v3=v2
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me184",
             title="split_edge_new_edge_t1_creation: ne1=(vn,v3) created after boundary edge split",
             defect_class="split_edge_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — original v1 endpoint
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — original v2 endpoint
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — v3: opposite vertex in t1
vn = m.vertex(1.0, 0.0, 0.0)   # 3 — new split vertex at midpoint of (v0,v1)

t0 = m.triangle(v0, vn, v2)   # 0 — left half of original t1 (v0 to vn side)
t1 = m.triangle(vn, v1, v2)   # 1 — nt1: right half (new triangle)

# New edge ne1=(vn,v2) is interior: shared by t0 and t1.
m.assert_edge_shared(vn, v2, 2)   # ne1: interior — connects split vertex to v3

# Original edge was split: now (v0,vn) and (vn,v1) are boundary edges.
m.assert_edge_shared(v0, vn, 1)   # left half of original edge
m.assert_edge_shared(vn, v1, 1)   # right half of original edge

# Boundary spokes to v3.
m.assert_edge_shared(v0, v2, 1)   # boundary
m.assert_edge_shared(v1, v2, 1)   # boundary

# vn lies on the original edge (v0,v1).
m.assert_vertex_on_edge(vn, v0, v1)   # vn is midpoint of original edge
