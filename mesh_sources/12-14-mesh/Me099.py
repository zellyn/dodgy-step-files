"""Me099 — edge_collapse_orphan_edge_e3: e3 becomes fully unlinked after collapse.

Catalog claim: edge e3 (adjacent to t2 of the collapsed edge, from the apex v4
back to v1) becomes orphaned after the collapse — it has no incident triangles
post-collapse. This is the state that MeshFix `collapseOnV1` Branch 15
(*ORPHAN_EDGE_CLEANUP_E3*) handles: 'if (e3 != NULL && e3->t1 == NULL &&
e3->t2 == NULL)' — the edge is freed and v4's anchor is nulled.

Defect carrier: the boundary triangle t2 is the only triangle sharing e3 (the
edge from v1 back to the apex v4). Since ta3 is NULL (no neighbor on e3), after
t2 is removed by the collapse, e3 has no incident triangles. The pre-collapse
mesh has e3 as a boundary edge (1 triangle only).

This is the symmetric counterpart to Me098 (Branch 14 / ORPHAN_EDGE_CLEANUP_E2):
Me098 demonstrates e2 becoming orphaned (the t1-side boundary), while Me099
demonstrates e3 becoming orphaned (the t2-side boundary).

Geometry:
  v0=(0,0,0), v1=(1,0,0)  — collapse edge
  v2=(0.5,1,0)             — t1 apex; ta1 exists on (v1,v2) side
  v3=(0.5,-1,0)            — t2 apex; v1 side edge e3=(v1,v3) has NO neighbor
  v4=(1.5,1,0)             — ta1 apex (neighbor of t1 on the (v1,v2) side)
  t1=(v0,v1,v2): e3-analog edge is e1=(v1,v2) — has ta1
  t2=(v0,v3,v1): e3=(v1,v3) — NO neighbor → ta3=NULL → e3 becomes orphan after collapse
  ta1=(v1,v4,v2): neighbor of t1 on (v1,v2) side
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me099",
             title="edge_collapse_orphan_edge_e3: e3 has no neighbors (ta3=NULL), becomes orphan post-collapse",
             defect_class="near_coincident_vertices")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — vertex to collapse
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — collapse target
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — t1 apex
v3 = m.vertex(0.5, -1.0, 0.0)  # 3 — t2 apex; e3=(v1,v3) will become orphan
v4 = m.vertex(1.5, 1.0, 0.0)   # 4 — ta1 apex (neighbor of t1 on v1 side)

# t1: upper collapse triangle; e1=(v1,v2) has neighbor ta1.
t0 = m.triangle(v0, v1, v2)   # 0 — t1

# t2: lower collapse triangle; e3=(v1,v3) has NO neighbor → ta3=NULL.
t1 = m.triangle(v0, v3, v1)   # 1 — t2

# ta1: neighbor of t1 on the (v1,v2) edge.
t2 = m.triangle(v1, v4, v2)   # 2 — ta1

# The collapse edge is interior.
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t1

# e1=(v1,v2) is interior — ta1 is present.
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t2 (ta1)

# e3=(v1,v3) is boundary — ta3=NULL; will become orphan after collapse.
m.assert_edge_shared(v1, v3, 1)   # boundary (only t1); ta3=NULL → orphan after collapse

# e2=(v0,v2) in t1 — boundary.
m.assert_edge_shared(v0, v2, 1)   # boundary (only t0)

# e4 in t2 = (v0,v3) — boundary.
m.assert_edge_shared(v0, v3, 1)   # boundary (only t1)

# ta1 external edges.
m.assert_edge_shared(v1, v4, 1)   # boundary
m.assert_edge_shared(v2, v4, 1)   # boundary

# v0 and v1 are close enough to be collapse candidates.
m.assert_vertex_pair_distance_lt(v0, v1, 2.0)
