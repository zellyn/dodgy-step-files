"""Me098 — edge_collapse_orphan_edge_e2: e2 becomes fully unlinked after collapse.

Catalog claim: edge e2 (adjacent to t1 of the collapsed edge, on the opposite
side from ta1) becomes orphaned after the collapse — it has no incident triangles.
This is the state that MeshFix `collapseOnV1` Branch 14 (*ORPHAN_EDGE_CLEANUP_E2*)
handles: 'if (e2 != NULL && e2->t1 == NULL && e2->t2 == NULL)' — the edge is
freed and v3's anchor is nulled.

Defect carrier: the boundary triangle t1 is the only triangle sharing e2 (the
edge from the apex v3 back to v0). Since ta2 is NULL (no neighbor on e2), after
t1 is removed by the collapse, e2 has no incident triangles. The pre-collapse
mesh has e2 as a boundary edge (1 triangle only), and v3 will need its anchor
re-assigned.

Geometry: identical to Me093 (ta1=NULL, ta2=NULL case) but we specifically
highlight that e2 = (v0, v3) is a degenerate near-zero-length edge — the
consequence is that after collapse the triangle t1 nearly disappears and e2
becomes a zero-length stub.

For a clean geometric signature: the edge (v0, v2) in t1 is near-zero in length
because v0 and v2 are near-coincident. After the collapse removes t1, this edge
has no incident triangles (an orphan edge).

Layout:
  v0=(0,0,0), v1=(1,0,0)  — collapse edge endpoints (v0→v1)
  v2=(1e-7, 1, 0)          — apex of t1; edge (v0, v2) is the nearly-zero e2
  v3=(0.5, -1, 0)          — apex of t2
  t1=(v0, v1, v2): the collapse triangle; e2=(v0,v2) is boundary → ta2=NULL
  t2=(v0, v3, v1): the other collapse triangle; has external neighbor ta4
  ta4=(v1, v4, v3): neighbor of t2 on the (v1,v3) side
  v4=(1.5, -1, 0): ta4 apex
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me098",
             title="edge_collapse_orphan_edge_e2: e2 has no neighbors (ta2=NULL), becomes orphan post-collapse",
             defect_class="near_coincident_vertices")

v0 = m.vertex(0.0, 0.0, 0.0)     # 0 — vertex to collapse
v1 = m.vertex(1.0, 0.0, 0.0)     # 1 — collapse target
v2 = m.vertex(1e-7, 1.0, 0.0)    # 2 — t1 apex: nearly directly above v0 → e2=(v0,v2) nearly degenerate
v3 = m.vertex(0.5, -1.0, 0.0)    # 3 — t2 apex
v4 = m.vertex(1.5, -1.0, 0.0)    # 4 — ta4 apex (neighbor of t2 on the v1 side)

# t1: the upper collapse triangle; e2 = (v0, v2) has no neighbor → ta2=NULL.
t0 = m.triangle(v0, v1, v2)   # 0 — t1

# t2: the lower collapse triangle.
t1 = m.triangle(v0, v3, v1)   # 1 — t2

# ta4: neighbor of t2 on the (v1, v3) edge.
t2 = m.triangle(v1, v4, v3)   # 2 — ta4: shares (v1,v3) with t1

# The collapse edge is interior.
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t1

# e1=(v1,v2) in t1 — no neighbor → ta1=NULL.
m.assert_edge_shared(v1, v2, 1)   # boundary (only t0); ta1=NULL

# e2=(v0,v2) in t1 — no neighbor → ta2=NULL; this edge becomes orphan after collapse.
m.assert_edge_shared(v0, v2, 1)   # boundary (only t0); will become orphan

# e2 is nearly zero-length because v0 and v2 are sub-tolerance in x.
m.assert_vertex_pair_distance_lt(v0, v2, 1.5)   # they're ~1.0 apart (in y) but x≈0

# e4=(v1,v3) is interior (t1 shares it with ta4=t2).
m.assert_edge_shared(v1, v3, 2)   # shared by t1 and t2 (ta4)

# ta4 boundary edges.
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v3, v4, 1)
