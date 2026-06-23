"""Me181 — split_edge_point_equals_v2: split point coincides with v2, no split performed.

Catalog claim: when the split point p equals edge endpoint v2, splitEdge
returns v2 immediately without creating any new geometry. This is the mirror
of Branch 1: (*p)==(*(e->v2)) triggers an early return.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 2 (*point_equals_v2*):
`if ((*p)==(*(e->v2))) return e->v2;` — the code detects that the proposed
midpoint coincides with the far endpoint and short-circuits.

Defect carrier: an edge e=(v0,v1) in a single open triangle, plus an extra
vertex vp that is geometrically coincident with v1 (representing the proposed
split point p). The healer would call splitEdge(e, vp) but vp == v1 so no
new geometry is created — the split point equals v2 in MeshFix naming.

Geometry (flat XY plane):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)  — open triangle
  vp=(1,0,0)  — proposed split point, coincident with v1 (= e->v2)
  t0=(v0,v1,v2) — triangle whose edge would be split (but isn't, due to guard)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me181",
             title="split_edge_point_equals_v2: split point coincides with v2, early return",
             defect_class="split_edge_degenerate")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — edge endpoint v1 (MeshFix naming)
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — edge endpoint v2 (MeshFix naming)
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — opposite vertex
vp = m.vertex(1.0, 0.0, 0.0)   # 3 — proposed split point p: coincident with v1

t0 = m.triangle(v0, v1, v2)   # 0 — single boundary triangle

# Edge e=(v0,v1): boundary (1 triangle).
m.assert_edge_shared(v0, v1, 1)   # edge e: boundary
m.assert_edge_shared(v0, v2, 1)   # boundary
m.assert_edge_shared(v1, v2, 1)   # boundary

# Split point p (vertex 3) is coincident with v1 (vertex 1): distance = 0.
# This is the condition (*p)==(*(e->v2)) that triggers early return.
m.assert_vertex_pair_distance_lt(v1, vp, 1e-9)   # p == v2: degenerate split
