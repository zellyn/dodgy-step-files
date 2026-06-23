"""Me164 — stitch_candidate_found: boundary walk finds coincident edge via opposite-vertex match.

MeshFix `Edge.stitch` Branch 5 (*STITCH_CANDIDATE_FOUND*) @ line 384:
  'if (e1->oppositeVertex(v0) == oppositeVertex(v0))'
  During the boundary walk, each traversed edge e1 is tested: does e1's opposite
  vertex (relative to the walk's current anchor vertex v0) match this edge's
  own opposite vertex? When they match, the walk has found the correct partner
  edge for stitching. Branch 5 fires when the condition is true (candidate found).

Defect pattern: two open patches whose boundary edges are geometrically coincident.
The opposite-vertex test matches: the third vertex of the boundary walk edge (seen
from the shared endpoint) equals the third vertex of the stitch edge.

Geometry: two separate triangles with a coincident boundary edge.
  Patch A: t0=(v0,v1,v2); boundary edge (v0,v1); opposite vertex = v2
  Patch B: t1=(v3,v4,v5); boundary edge (v3,v4); opposite vertex = v5
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)
  v3=(0,0,0), v4=(1,0,0), v5=(0.5,1,0)  [coincident to Patch A]

The walk from v0 on edge (v0,v1) finds e1=(v3,v4); its oppositeVertex(v0) = v5
which matches this edge's oppositeVertex(v0) = v2 (same position). Branch 5 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me164",
             title="stitch_candidate_found: opposite-vertex match confirms coincident boundary edge pair for stitching",
             defect_class="stitch_candidate_found_opposite_vertex_match")

# Patch A
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — opposite vertex of stitch edge

# Patch B — fully coincident to Patch A (unstitched duplicate boundary)
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — coincident to v0
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — coincident to v1
v5 = m.vertex(0.5, 1.0, 0.0)   # 5 — coincident to v2

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A
t1 = m.triangle(v3, v4, v5)    # 1 — Patch B

# Both boundary edges are incident on exactly one triangle.
m.assert_edge_shared(v0, v1, 1)  # Patch A stitch edge (target)
m.assert_edge_shared(v3, v4, 1)  # Patch B candidate edge

# All three vertex pairs are near-coincident (fully coincident geometry).
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v2, v5, 1e-9)

# Other boundary edges
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
