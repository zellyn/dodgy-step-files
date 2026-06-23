"""Me096 — edge_collapse_adjacency_repair: near-degenerate triangle after collapse.

Catalog claim: edge (v0, v1) is collapsed; the repair of triangle adjacency
pointers (e2->replaceTriangle(t1, ta1) and e3->replaceTriangle(t2, ta4))
is required to maintain a valid mesh. Pre-collapse, the triangles on both
sides of the edge have neighbors. Post-collapse, t1 and t2 are removed,
and their neighbors must now be wired to each other through the updated
adjacency. The resulting triangles adjacent to e2/e3 can become near-degenerate
(very thin) if v0 and v1 are close together.

This exercises MeshFix `Edge.collapseOnV1` Branch 10
(*TRIANGLE_ADJACENCY_REPAIR*): 'if (e2 != NULL) e2->replaceTriangle(t1, ta1);
if (e3 != NULL) e3->replaceTriangle(t2, ta4)'.

Defect carrier: two near-coincident vertices v0 and v1 (2e-6 apart) forming an
interior edge. On both sides of the collapse edge, the adjacent triangles are
well-formed but their wiring through e2 and e3 will be updated after collapse.
The sub-tolerance short edge is the defect.

Geometry:
  v0=(0,0,0), v1=(2e-6,0,0)  — near-coincident pair
  v2=(0,1,0)  — upper apex (apex of t1 = upper collapse triangle)
  v3=(0,-1,0) — lower apex (apex of t2 = lower collapse triangle)
  ta1=(v2, v_tr, v1): neighbor of t1 on e1=(v1,v2) side
  ta4=(v3, v1, v_br): neighbor of t2 on e4=(v3,v1) side
  Use:
    v4=(1,1,0) — ta1 apex
    v5=(1,-1,0) — ta4 apex
  t1=(v0,v1,v2), t2=(v0,v3,v1)
  ta1=(v1,v4,v2): adjacent to e1=(v1,v2) of t1
  ta4=(v3,v5,v1): adjacent to e4=(v3,v1) of t2... actually e4=(v3,v1) reversed = (v1,v3)

Let me rework:
  ta1 should share (v1,v2) with t1: ta1=(v1,v4,v2) — edge (v1,v2) appears in t1 and ta1
  ta4 should share (v3,v1) with t2: ta4=(v3,v1,v5) — edge (v1,v3) appears in t2 and ta4

t1 = (v0,v1,v2): edges (v0,v1), (v1,v2), (v0,v2)
t2 = (v0,v3,v1): edges (v0,v3), (v1,v3), (v0,v1)
ta1 = (v1,v4,v2): edges (v1,v4), (v2,v4), (v1,v2) — shares (v1,v2) with t1 ✓
ta4 = (v3,v1,v5): edges (v1,v3), (v1,v5), (v3,v5) — shares (v1,v3) with t2 ✓
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me096",
             title="edge_collapse_adjacency_repair: near-coincident vertices with bilateral neighbors",
             defect_class="near_coincident_vertices")

v0 = m.vertex(0.0, 0.0, 0.0)     # 0 — near-coincident vertex to collapse
v1 = m.vertex(2e-6, 0.0, 0.0)    # 1 — collapse target (2e-6 away)
v2 = m.vertex(0.0, 1.0, 0.0)     # 2 — upper apex (t1)
v3 = m.vertex(0.0, -1.0, 0.0)    # 3 — lower apex (t2)
v4 = m.vertex(1.0, 1.0, 0.0)     # 4 — ta1 apex
v5 = m.vertex(1.0, -1.0, 0.0)    # 5 — ta4 apex

# t1 and t2: the two triangles sharing the collapse edge (v0, v1).
t0 = m.triangle(v0, v1, v2)   # 0 — t1: upper collapse triangle
t1 = m.triangle(v0, v3, v1)   # 1 — t2: lower collapse triangle

# ta1: neighbor of t1 on the (v1,v2) edge — will be reconnected to e2 after collapse.
t2 = m.triangle(v1, v4, v2)   # 2 — ta1: shares (v1,v2) with t1

# ta4: neighbor of t2 on the (v1,v3) edge — will be reconnected to e3 after collapse.
t3 = m.triangle(v3, v1, v5)   # 3 — ta4: shares (v1,v3) with t2

# Primary defect: near-coincident vertices.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-5)

# Collapse edge is interior.
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t1

# The adjacency edges that will be repaired.
m.assert_edge_shared(v1, v2, 2)   # shared by t0 (t1) and t2 (ta1)
m.assert_edge_shared(v1, v3, 2)   # shared by t1 (t2) and t3 (ta4)
