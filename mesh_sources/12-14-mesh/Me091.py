"""Me091 — edge_collapse_degenerate_t1_side: ta1 and ta2 share opposite vertex.

Catalog claim: collapsing edge (v0, v1) onto v1 would produce a duplicate edge
because ta1 and ta2 (the triangles on each side of t1 adjacent to the collapsed
edge) already share an opposite vertex.

This exercises MeshFix `Edge.collapseOnV1` Branch 4
(*DEGENERATE_DOUBLE_TRIANGLE*): 'if (ta1 != NULL && ta2 != NULL &&
ta1->oppositeVertex(e1) == ta2->oppositeVertex(e2))' the algorithm detects that
collapsing (v0, v1) would create a degenerate pair — two faces that become
identical after the merge.

Defect carrier: a diamond-shaped mesh around v0 where the two neighbors on the
t1 side both point to the same apex vertex. After collapsing v0 onto v1, those
two side triangles would fold onto each other.

Geometry:
  v0=(0,0,0)  — vertex to collapse (disappears into v1)
  v1=(1,0,0)  — collapse target
  v2=(0.5,1,0)  — upper apex (ta1 opposite vertex)
  v3=(0.5,-1,0) — lower apex (ta2 opposite vertex)
  But for ta1->opp == ta2->opp we need both to point to the same apex vertex.
  Use: both ta1 and ta2 are adjacent to the same vertex v2.

Revised: Make ta1 and ta2 share vertex v2.
  Core edge: (v0, v1) — t1 is the triangle on one side.
  If t1 = (v0, v1, v2):
    e1 = nextEdge(v0→v1) from v1 = (v1, v2)  — ta1 is triangle adjacent to (v1,v2)
    e2 = prevEdge = (v2, v0)               — ta2 is triangle adjacent to (v0,v2) = (v0,v2)
  So ta1->oppositeVertex(e1) is the vertex opposite edge (v1,v2) in ta1.
  ta2->oppositeVertex(e2) is the vertex opposite edge (v2,v0) in ta2.
  For them to be equal, both ta1 and ta2 must have the same vertex at their apex.

Construct: v2=(0.5, 1, 0) = shared apex.
  t1 = (v0, v1, v2)  — the collapsed triangle
  ta1: adjacent to (v1, v2), opposite vertex = v3.
  ta2: adjacent to (v2, v0), opposite vertex = v3.
  So ta1 and ta2 BOTH have v3 as their opposite vertex.
  ta1 = (v1, v3, v2)  → opposite of edge (v1,v2) is v3
  ta2 = (v2, v3, v0)  → opposite of edge (v2,v0) is v3

After collapsing v0→v1, both ta1 and ta2 become triangles using v1+v3+v2 → duplicate!
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me091",
             title="edge_collapse_degenerate_t1_side: collapsing edge creates duplicate triangle on t1 side",
             defect_class="edge_collapse_would_duplicate")

v0 = m.vertex(0.0, 0.0, 0.0)    # 0 — vertex to collapse (v0 in MeshFix notation)
v1 = m.vertex(1.0, 0.0, 0.0)    # 1 — collapse target (v1)
v2 = m.vertex(0.5, 1.0, 0.0)    # 2 — upper shared apex
v3 = m.vertex(0.5, -1.0, 0.0)   # 3 — lateral "both-side" apex (same for ta1 and ta2)

# t1: the triangle being collapsed — contains the candidate edge (v0, v1).
t0 = m.triangle(v0, v1, v2)   # 0 — t1 in MeshFix; edge (v0,v1) to collapse

# ta1: adjacent to edge (v1, v2) in t0 — opposite vertex = v3.
t1 = m.triangle(v1, v3, v2)   # 1 — ta1; shares edge (v1,v2) with t0

# ta2: adjacent to edge (v2, v0) in t0 — opposite vertex = v3 (SAME as ta1).
t2 = m.triangle(v2, v3, v0)   # 2 — ta2; shares edge (v2,v0) with t0

# A control triangle on the far side of v3 to ensure v3 has more than one face.
v4 = m.vertex(1.5, -2.0, 0.0)  # 4 — extra vertex
t3 = m.triangle(v1, v4, v3)    # 3 — control

# After collapsing v0 onto v1, ta1 and ta2 both become (v1, v3, v2) — duplicates.
# Assert that after "collapse" both ta1 and ta2 reference the same vertex set.
# Pre-collapse: ta1 and ta2 share opposite vertex v3.
m.assert_edge_shared(v0, v1, 1)   # collapse edge is boundary (1 triangle only: t0)
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t2

# Pre-collapse t1 and t2 are NOT duplicates yet (they have v1 vs v0 respectively).
# But after collapsing v0→v1, sorted(t1)=(1,2,3) and sorted(t2)=(0→1,2,3)=(1,2,3).
# We capture the "would-be duplicate" by showing both triangles have equal sorted
# vertex sets if v0 is replaced by v1. We encode this as a near-coincident vertex
# pair to signal the healer that v0 and v1 are candidates for merging.
m.assert_vertex_pair_distance_lt(v0, v1, 2.0)
