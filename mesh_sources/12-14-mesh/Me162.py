"""Me162 — stitch_boundary_walk_v1: boundary traversal from v1 finds coincident edge.

MeshFix `Edge.stitch` Branch 3 (*BOUNDARY_WALK_V1*) @ line 375:
  'for (v0 = v1; v0 != NULL', 't = e1->oppositeTriangle(t)'
  After selecting the start triangle, stitch walks the boundary chain from vertex
  v1 (one endpoint of the stitch edge) following the nextEdge() / oppositeTriangle()
  chain until it reaches a candidate edge e1 whose opposite vertex matches the
  stitch edge's own opposite vertex. Branch 3 covers the v1-side walk.

Defect pattern: a three-triangle open strip with a boundary gap. One pair of
boundary edges is geometrically coincident (unstitched seam). The walk starting
from v1 of the target boundary edge traverses through one intermediate triangle
before finding the coincident candidate edge.

Geometry: L-shaped open strip in the XY plane.
  t0 = (v0, v1, v2) — base triangle; target boundary edge is (v1,v2)
  t1 = (v1, v3, v2) — shares interior edge (v1,v2) with t0; its boundary
       edge (v1,v3) is the walk-entry
  t2 = (v4, v5, v6) — second patch; boundary edge (v4,v5) is geometrically
       coincident to (v1,v2) but unstitched

The walk from v1 along (v1,v2) traverses into t1 via nextEdge and finds the
opposing boundary edge at the end of the chain. Oracle confirms (v1,v2) is
interior (n=2) and (v4,v5) is boundary (n=1) and near-coincident to (v1,v2).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me162",
             title="stitch_boundary_walk_v1: boundary chain walk from v1 endpoint traverses to find coincident candidate",
             defect_class="stitch_boundary_walk_v1")

# Patch A: two connected triangles
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — stitch edge v1 endpoint
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — stitch edge v2 endpoint; also shared
v3 = m.vertex(1.5, 1.0, 0.0)   # 3 — outer vertex of t1

# Patch B: single triangle with coincident boundary
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — same position as v1 (unstitched)
v5 = m.vertex(0.5, 1.0, 0.0)   # 5 — same position as v2 (unstitched)
v6 = m.vertex(2.0, 0.5, 0.0)   # 6 — far vertex of patch B

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v1, v3, v2)    # 1 — shares (v1,v2) with t0
t2 = m.triangle(v4, v5, v6)    # 2 — second patch

# (v1,v2) is interior — shared by t0 and t1.
m.assert_edge_shared(v1, v2, 2)

# The candidate stitch edge on Patch B is a boundary edge.
m.assert_edge_shared(v4, v5, 1)

# Near-coincident pairs: unstitched seam
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)
m.assert_vertex_pair_distance_lt(v2, v5, 1e-9)

# Other boundary edges
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
