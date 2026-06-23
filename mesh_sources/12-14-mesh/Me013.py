"""Me013 — boundary_gap_thin: two patches whose shared boundary is epsilon-displaced.

Catalog claim: two triangulated patches that should share a boundary cycle are
stored with their shared boundary vertices eps-displaced by 2e-7 (half the
typical CAD tolerance of 1e-6). Each patch has an open boundary; the two
boundary cycles are geometrically almost coincident but topologically
disconnected. CGAL stitch_borders / merge_duplicated_vertices_in_boundary_cycles
and MeshFix mergeCoincidentEdges must detect and close this gap.

Defect carrier: patch A uses vertices v0-v3; patch B uses v4-v7 where v4 and
v5 are the "should be v1/v2" counterparts, displaced by 2e-7 in Y.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me013",
             title="boundary gap (thin): two patches share near-coincident boundary displaced by 2e-7",
             defect_class="boundary_gap_thin")

# Patch A: two triangles, open on the right edge (x=1).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)    # right boundary vertex, bottom
v2 = m.vertex(1.0, 1.0, 0.0)    # right boundary vertex, top
v3 = m.vertex(0.0, 1.0, 0.0)
m.triangle(v0, v1, v2)           # face 0: lower-right
m.triangle(v0, v2, v3)           # face 1: upper-left

# Patch B: two triangles, open on the left edge (x=1 + eps) — eps-displaced from A.
EPS = 2e-7
v4 = m.vertex(1.0 + EPS, 0.0, 0.0)   # should be v1 but displaced by 2e-7
v5 = m.vertex(1.0 + EPS, 1.0, 0.0)   # should be v2 but displaced by 2e-7
v6 = m.vertex(2.0, 0.0, 0.0)
v7 = m.vertex(2.0, 1.0, 0.0)
m.triangle(v4, v6, v7)           # face 2: lower-right of patch B
m.triangle(v4, v7, v5)           # face 3: upper-left of patch B

# The gap: v1 and v4 should be the same point; v2 and v5 should be the same.
m.assert_vertex_pair_distance_lt(v1, v4, 1e-6)
m.assert_vertex_pair_distance_lt(v2, v5, 1e-6)

# Confirm boundary edges on each side of the gap (each incident on exactly 1 triangle).
m.assert_edge_shared(v1, v2, 1)   # boundary of patch A
m.assert_edge_shared(v4, v5, 1)   # boundary of patch B — the gap seam
