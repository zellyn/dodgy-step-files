"""Me092 — edge_collapse_degenerate_t2_side: ta3 and ta4 share opposite vertex.

Catalog claim: collapsing edge (v0, v1) would produce a duplicate triangle on
the *t2 side* — the two triangles (ta3 and ta4) adjacent to t2's boundary
edges both share the same opposite vertex. This is the symmetric counterpart
to Me091 (Branch 4) but on the t2 side of the collapsed edge.

This exercises MeshFix `Edge.collapseOnV1` Branch 5
(*DEGENERATE_DOUBLE_TRIANGLE_T2*): 'if (ta3 != NULL && ta4 != NULL &&
ta3->oppositeVertex(e3) == ta4->oppositeVertex(e4))' — the algorithm checks
the t2 neighborhood separately.

Defect carrier: edge (v0, v1) is interior (shared by 2 triangles — t1 above,
t2 below). The t2 neighbors on both sides of v0 point to the same apex vertex,
so collapse would create a duplicate on the t2 side.

Geometry:
  t1 (above): v0=(0,0,0), v1=(2,0,0), v_top=(1,2,0) — safe upper triangle
  t2 (below): v0, v1, v_bot=(1,-2,0) — the "t2" triangle
  ta3: adjacent to (v1, v_bot) with opposite vertex = v_mid=(3,-1,0)
  ta4: adjacent to (v_bot, v0) with opposite vertex = v_mid (SAME)
  → ta3 and ta4 both share v_mid as opposite vertex.
  After collapsing v0→v1: ta3 and ta4 would both become (v1, v_bot, v_mid).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me092",
             title="edge_collapse_degenerate_t2_side: collapsing edge creates duplicate triangle on t2 side",
             defect_class="edge_collapse_would_duplicate")

v0 = m.vertex(0.0, 0.0, 0.0)     # 0 — vertex to collapse
v1 = m.vertex(2.0, 0.0, 0.0)     # 1 — collapse target
v_top = m.vertex(1.0, 2.0, 0.0)  # 2 — safe upper apex for t1
v_bot = m.vertex(1.0, -2.0, 0.0) # 3 — lower apex for t2
v_mid = m.vertex(3.0, -1.0, 0.0) # 4 — SHARED opposite apex for ta3 AND ta4

# t1 (above the collapse edge): safe triangle.
t0 = m.triangle(v0, v_top, v1)   # 0 — t1; shares (v0,v1) with t1_below

# t2 (below the collapse edge): will be removed by collapse.
t1 = m.triangle(v0, v1, v_bot)   # 1 — t2

# ta3: adjacent to edge (v1, v_bot) in t2 — opposite vertex = v_mid.
t2 = m.triangle(v1, v_mid, v_bot) # 2 — ta3; shares (v1,v_bot) with t1

# ta4: adjacent to edge (v_bot, v0) in t2 — opposite vertex = v_mid (SAME as ta3).
t3 = m.triangle(v_bot, v_mid, v0) # 3 — ta4; shares (v_bot,v0) with t1

# The collapse edge (v0,v1) is interior — shared by t1 (above) and t2 (below).
m.assert_edge_shared(v0, v1, 2)   # interior collapse edge

# Both ta3 and ta4 share edge to v_mid.
m.assert_edge_shared(v1, v_bot, 2)   # shared by t2 and ta3
m.assert_edge_shared(v0, v_bot, 2)   # shared by t2 and ta4

# v_mid appears in both ta3 and ta4 but as opposite vertex, not as a shared edge.
# Each edge to v_mid is a boundary edge (only 1 incident triangle each).
m.assert_edge_shared(v1, v_mid, 1)   # boundary: only ta3
m.assert_edge_shared(v0, v_mid, 1)   # boundary: only ta4

# v0 and v1 are candidates for edge collapse.
m.assert_vertex_pair_distance_lt(v0, v1, 3.0)
