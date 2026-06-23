"""Me167 — stitch_anchor_update: vertex edge-anchors updated to stitch edge after merge.

MeshFix `Edge.stitch` Branch 8 (*STITCH_ANCHOR_UPDATE*) @ line 388:
  'v1->e0 = v2->e0 = this'
  After the triangle merge, both endpoint vertices (v1 and v2 of the stitch edge)
  have their edge anchors (e0 fields) updated to point to 'this' (the surviving
  stitch edge). This ensures the vertex→edge adjacency pointers remain consistent
  after e1 is retired.

Defect pattern: a boundary gap where two patches share coincident vertices but
inconsistent anchor pointers. After stitching, the two boundary vertices must
update their e0 anchors to the surviving stitch edge. The fixture shows the
pre-stitch state: two open triangles with coincident vertices whose v->e0 anchors
would need updating.

Geometry: two-patch gap with coincident endpoints.
  Patch A: t0=(v0,v1,v2), stitch edge (v1,v2) — endpoints v1 and v2 anchor here
  Patch B: t1=(v3,v4,v5), candidate edge (v3,v4) — coincident to (v1,v2)

Post-stitch: v1->e0 = v2->e0 = stitch_edge; e1=(v3,v4) is orphaned.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me167",
             title="stitch_anchor_update: v1->e0 and v2->e0 updated to stitch edge after boundary merge",
             defect_class="stitch_anchor_update")

# Patch A — stitch edge is (v1,v2)
v0 = m.vertex(0.0, 0.5, 0.0)   # 0 — outer vertex of Patch A
v1 = m.vertex(0.0, 0.0, 0.0)   # 1 — stitch edge endpoint; anchor updated post-stitch
v2 = m.vertex(1.0, 0.0, 0.0)   # 2 — stitch edge endpoint; anchor updated post-stitch

# Patch B — candidate edge (v3,v4) coincident to (v1,v2)
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — coincident to v1
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident to v2
v5 = m.vertex(0.5, -1.0, 0.0)  # 5 — outer vertex of Patch B (below seam)

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A
t1 = m.triangle(v3, v4, v5)    # 1 — Patch B; e1=(v3,v4) is candidate

# Both edges are boundary — each incident on one triangle.
m.assert_edge_shared(v1, v2, 1)  # stitch edge; v1 and v2 anchors update here
m.assert_edge_shared(v3, v4, 1)  # candidate e1 (will be orphaned after stitch)

# Coincident vertex pairs confirm anchor update is needed.
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v2, v4, 1e-9)

# Remaining boundary edges
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
