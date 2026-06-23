"""Me093 — edge_collapse_single_sided_t1: collapse with ta1=NULL and ta2=NULL.

Catalog claim: edge (v0, v1) is a boundary edge with t1 being the sole triangle.
The t1 triangle's neighbor edges (e1 and e2) have no opposite triangles — ta1
and ta2 are both NULL. This is the minimal one-triangle mesh where an edge
collapse degenerates to simply removing t1 and merging v0 into v1.

This exercises MeshFix `Edge.collapseOnV1` Branch 6
(*VERTEX_ANCHOR_EDGE_SELECTION*): 'if (ta1 == NULL && ta2 == NULL) v1->e0 = e3'
— when both neighbors of t1 are absent, the code selects e3 (from the t2 side)
as v1's new anchor edge.

Defect carrier: a minimal "fan" of exactly 2 triangles sharing the target edge.
One triangle (t1) has no external neighbors (all three edges are boundary edges
of the mesh), while the other triangle (t2) has a neighbor on one side. This
arrangement means ta1 and ta2 are NULL for the t1 neighborhood, triggering the
e3-selection branch.

Geometry:
  v0=(0,0,0), v1=(1,0,0)  — collapse edge endpoints
  v2=(0.5, 1,0)            — apex of t1 (no neighbors on e1 or e2)
  v3=(0.5,-1,0)            — apex of t2
  t1: (v0, v1, v2)  — all boundary edges
  t2: (v0, v3, v1)  — shares (v0,v1) with t1; (v0,v3) and (v1,v3) are boundary
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me093",
             title="edge_collapse_single_sided_t1: t1 has no external neighbors (ta1=NULL, ta2=NULL)",
             defect_class="edge_collapse_single_sided_t1")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — vertex to collapse
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — collapse target
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — t1 apex (no external neighbors)
v3 = m.vertex(0.5, -1.0, 0.0)  # 3 — t2 apex

# t1: triangle with no external neighbors (ta1=NULL, ta2=NULL).
t0 = m.triangle(v0, v1, v2)   # 0 — t1; edge (v1,v2) has no neighbor, (v2,v0) has no neighbor

# t2: shares edge (v0,v1) with t1.
t1 = m.triangle(v0, v3, v1)   # 1 — t2

# Edge (v0,v1) is the collapse edge — interior (shared by t0 and t1).
m.assert_edge_shared(v0, v1, 2)   # the collapse edge (interior)

# Edges of t1 other than (v0,v1) are boundary (ta1=NULL, ta2=NULL).
m.assert_edge_shared(v1, v2, 1)   # e1: boundary → ta1=NULL
m.assert_edge_shared(v0, v2, 1)   # e2: boundary → ta2=NULL

# Edges of t2 other than (v0,v1) are also boundary.
m.assert_edge_shared(v0, v3, 1)   # e3 of t2: boundary
m.assert_edge_shared(v1, v3, 1)   # e4 of t2: boundary

# v0 and v1 separated by 1.0 — close enough for collapse consideration.
m.assert_vertex_pair_distance_lt(v0, v1, 2.0)
