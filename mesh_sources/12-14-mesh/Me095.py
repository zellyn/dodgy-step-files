"""Me095 — edge_collapse_vertex_merge: near-coincident vertices indicate merge target.

Catalog claim: vertices v0 and v1 are extremely close together (1e-6 separation)
and connected by an edge. After collapsing v0 onto v1, all edges formerly incident
to v0 are re-routed to v1 — this is the `replaceVertex(v2, v1)` pass in MeshFix
`collapseOnV1` Branch 9 (*VERTEX_MERGE*). The pre-collapse mesh has v0 shared by
multiple triangles; post-collapse all those triangles reference v1 instead.

This exercises MeshFix `Edge.collapseOnV1` Branch 9
(*VERTEX_MERGE*): 'e->replaceVertex(v2, v1) for all edges incident to v2'
— the merge loop touches every edge in v0's one-ring.

Defect carrier: a mesh where v0 is nearly coincident with v1 (1e-6 apart) and
v0 is referenced by three triangles forming a small fan. The very short edge
(v0, v1) is the defect — it should be collapsed. Post-collapse the fan folds
cleanly around v1.

Geometry:
  v0=(0, 0, 0), v1=(1e-6, 0, 0)  — the near-coincident pair to collapse
  v2=(0, 1, 0), v3=(1, 1, 0), v4=(1, 0, 0)  — fan vertices around v0
  t0=(v0, v1, v3): upper-right triangle
  t1=(v0, v3, v2): upper triangle
  t2=(v0, v4, v1): lower-right (connects to v1 on the other side)
  → v0 is referenced by t0, t1, t2 — a 3-triangle fan
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me095",
             title="edge_collapse_vertex_merge: near-coincident v0 and v1, 3-triangle fan on v0",
             defect_class="near_coincident_vertices")

v0 = m.vertex(0.0, 0.0, 0.0)       # 0 — near-coincident, will be merged into v1
v1 = m.vertex(1e-6, 0.0, 0.0)      # 1 — collapse target (1e-6 away)
v2 = m.vertex(0.0, 1.0, 0.0)       # 2 — upper left
v3 = m.vertex(1.0, 1.0, 0.0)       # 3 — upper right
v4 = m.vertex(1.0, 0.0, 0.0)       # 4 — right

# 3-triangle fan referencing v0 (and v1 on the interior edge).
t0 = m.triangle(v0, v1, v3)   # 0 — upper-right
t1 = m.triangle(v0, v3, v2)   # 1 — upper
t2 = m.triangle(v0, v4, v1)   # 2 — lower-right

# The near-coincident pair is the primary defect assertion.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-5)

# The collapse edge (v0, v1) is interior — shared by t0 and t2.
m.assert_edge_shared(v0, v1, 2)   # interior edge to collapse

# v0's other edges are shared with neighboring triangles.
m.assert_edge_shared(v0, v3, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v2, 1)   # boundary (only t1)
m.assert_edge_shared(v0, v4, 1)   # boundary (only t2)
