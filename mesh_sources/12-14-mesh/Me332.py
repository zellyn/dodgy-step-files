"""Me332 — pinch_non_manifold_vertex_not_found: no boundary match from v1, fallback search from v2.

MeshFix `Basic_TMesh.pinch` Branch 3 (*NON_MANIFOLD_VERTEX_NOT_FOUND*) @ line 931:
  'if (n == NULL) { e1->v2->e0 = e1; ... }'
  After scanning v1's edge-ring for a boundary edge whose opposite endpoint
  matches e1->v2, the search returns NULL (no match). The algorithm then
  restarts the search from v2's perspective by temporarily setting v2->e0=e1
  as the new scan anchor. This covers the case where v1 has no such boundary
  neighbor but v2 does.

Defect pattern: an asymmetric non-manifold vertex configuration where v0
has no outgoing boundary edge toward v1, but v1 does have a boundary edge
toward v0. The boundary edge can only be found by restarting from v2.

Geometry: bowtie-like mesh. Two triangle fans share vertex v0 but their
  edge rings are disconnected (v0 is a non-manifold pinch vertex).

  Fan A: t0=(v0,v1,v2), t1=(v0,v2,v3) — two triangles sharing v0 and edge (v0,v2).
  Fan B: t2=(v0,v4,v5) — isolated triangle at v0 in a disconnected fan.

  The vertex fan at v0 is disconnected: Fan A triangles are reachable from each
  other via edge (v0,v2), but Fan B (t2) is not reachable from Fan A via any
  shared edge through v0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me332",
             title="pinch_non_manifold_vertex_not_found: no v1-side boundary match; fallback scan from v2",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — pinch vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(-0.5, 1.0, 0.0)  # 3
v4 = m.vertex(-1.0, 0.0, 0.0)  # 4
v5 = m.vertex(-0.5, -1.0, 0.0) # 5

t0 = m.triangle(v0, v1, v2)   # 0 — Fan A tri 0
t1 = m.triangle(v0, v2, v3)   # 1 — Fan A tri 1
t2 = m.triangle(v0, v4, v5)   # 2 — Fan B (disconnected)

# Edge (v0,v2) is shared by fan A triangles — manifold within Fan A.
m.assert_edge_shared(v0, v2, 2)

# v0 fans are disconnected: t2 not reachable from t0 via shared edges.
m.assert_vertex_fan_disconnected(v0)

# Fan A outer boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Fan B boundary edges.
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v0, v5, 1)
