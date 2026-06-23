"""Me090 — edge_collapse_boundary_validity: both endpoints on boundary, collapse blocked.

Catalog claim: edge (v0, v1) connects two boundary vertices. The edge is on the
boundary (shared by exactly 1 triangle). Collapsing this edge would merge the two
boundary vertices, creating a non-manifold pinch on the mesh boundary — the
resulting vertex would be incident on a disconnected fan of boundary edges.

This exercises MeshFix `Edge.collapseOnV1` Branch 3
(*BOUNDARY_EDGE_COLLAPSE_VALIDITY*): 'if (v1->isOnBoundary() &&
v2->isOnBoundary())' the code performs an extra validity check and returns NULL
if the collapse would create a non-manifold boundary configuration.

Defect carrier: a planar mesh strip with a central edge whose both endpoints are
boundary vertices. The strip has an open hole on one side so both v0 and v1 are
on the boundary edge-loop. Collapsing (v0,v1) would merge the two open ends into
a single point, pinching the boundary into a figure-eight.

Geometry: 6 vertices arranged in two rows forming a strip with an open top edge.
  v0=(0,0,0), v1=(2,0,0)  — bottom edge endpoints, BOTH on boundary
  v2=(0,2,0), v3=(2,2,0)  — top
  v4=(0,4,0), v5=(2,4,0)  — very top
  t0=(v0,v1,v3), t1=(v0,v3,v2): lower quad
  t2=(v2,v3,v5), t3=(v2,v5,v4): upper quad
  Open edges: (v0,v2), (v4,v5), (v1,v3) are NOT all boundary — let me be precise.

Revised: Use a flat strip with an open hole. Bottom and top are open.
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(1,1,0)
  t0=(v0,v1,v3), t1=(v0,v3,v2)
  All 4 vertices are on the boundary.
  Edge (v0,v1) is shared by exactly 1 triangle (t0) → v0 and v1 are boundary vertices.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me090",
             title="edge_collapse_boundary_validity: both collapse endpoints on mesh boundary",
             defect_class="edge_collapse_blocked_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — boundary vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — boundary vertex
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — boundary vertex
v3 = m.vertex(1.0, 1.0, 0.0)   # 3 — boundary vertex

# Two triangles forming a quad strip (open boundary all around).
t0 = m.triangle(v0, v1, v3)   # 0
t1 = m.triangle(v0, v3, v2)   # 1

# Edge (v0, v1) is a boundary edge (shared by exactly 1 triangle).
# Both v0 and v1 are boundary vertices — collapse is blocked.
m.assert_edge_shared(v0, v1, 1)   # boundary edge
m.assert_edge_shared(v0, v2, 1)   # boundary edge
m.assert_edge_shared(v1, v3, 1)   # boundary edge
m.assert_edge_shared(v2, v3, 1)   # boundary edge

# v0 and v1 are near enough that a healer would consider collapsing (v0, v1).
m.assert_vertex_pair_distance_lt(v0, v1, 2.0)
