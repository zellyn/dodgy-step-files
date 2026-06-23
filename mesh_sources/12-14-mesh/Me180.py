"""Me180 — split_edge_point_equals_v1: split point coincides with v1, no split performed.

Catalog claim: when the split point p equals edge endpoint v1, splitEdge
returns v1 immediately without creating any new geometry. This is a degenerate
guard: (*p)==(*(e->v1)) triggers an early return.

This exercises MeshFix `Basic_TMesh.splitEdge` Branch 1 (*point_equals_v1*):
`if ((*p)==(*(e->v1))) return e->v1;` — the code detects the zero-length
split and short-circuits.

Defect carrier: an edge e=(v0,v1) in a single open triangle, plus an extra
vertex vp that is geometrically coincident with v0 (representing the proposed
split point p). The healer would call splitEdge(e, vp) but vp == v0 so no
new geometry is created — the split point equals v1 in MeshFix naming.

Geometry (flat XY plane):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)  — open triangle
  vp=(0,0,0)  — proposed split point, coincident with v0 (= e->v1)
  t0=(v0,v1,v2) — the triangle whose edge will be split (but isn't, due to guard)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me180",
             title="split_edge_point_equals_v1: split point coincides with v1, early return",
             defect_class="split_edge_degenerate")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — edge endpoint v1 (in MeshFix naming)
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — edge endpoint v2
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — opposite vertex
vp = m.vertex(0.0, 0.0, 0.0)   # 3 — proposed split point p: coincident with v0

t0 = m.triangle(v0, v1, v2)   # 0 — single boundary triangle

# The edge to split (v0,v1): boundary edge (1 incident triangle).
m.assert_edge_shared(v0, v1, 1)   # edge e: boundary
m.assert_edge_shared(v0, v2, 1)   # boundary edge
m.assert_edge_shared(v1, v2, 1)   # boundary edge

# Split point p (vertex 3) is coincident with v0 (vertex 0): distance = 0.
# This is the condition (*p)==(*(e->v1)) that triggers early return.
m.assert_vertex_pair_distance_lt(v0, vp, 1e-9)   # p == v1: degenerate split
