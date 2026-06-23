"""Me264 — range_with_face_set_both_on_boundary: both endpoints of degenerate edge are on the mesh border.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 5 @ line 1630
(*both_endpoints_on_boundary*): the zero-length edge to collapse has BOTH of its
endpoints on the mesh boundary. In this case, edge collapse would disconnect the
boundary or create a non-manifold configuration, so the algorithm marks the edge
as impossible to remove (impossible = true) and uses halfedges_around to check.

Geometric signature: an open mesh (not closed) where the near-degenerate interior edge
(v0, v1) has both v0 and v1 on the boundary. The mesh is an open fan/strip where
every vertex except an interior one is on the boundary.

Both v0 and v1 are on the border:
  - v0 is incident on at least one boundary edge (edge shared by 1 triangle).
  - v1 is incident on at least one boundary edge (edge shared by 1 triangle).
The degenerate edge (v0, v1) is itself interior (shared by 2 triangles), but both
endpoints are on the outer boundary ring.

Configuration: a minimal strip of 4 triangles forming an open surface. v0 and v1
are interior vertices of the strip but connected to boundary edges.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me264",
             title="range_with_face_set both_on_boundary: near-zero interior edge with both endpoints on mesh border → impossible=true",
             defect_class="degenerate_edge")

# v0 and v1: near-coincident, interior edge, but BOTH are also boundary vertices.
v0 = m.vertex(0.0,   0.5, 0.0)
v1 = m.vertex(1e-10, 0.5, 0.0)   # nearly same as v0

# Open mesh boundary vertices.
v2 = m.vertex(0.0,  0.0, 0.0)   # bottom-left boundary
v3 = m.vertex(1.0,  0.0, 0.0)   # bottom-right boundary
v4 = m.vertex(0.0,  1.0, 0.0)   # top-left boundary
v5 = m.vertex(1.0,  1.0, 0.0)   # top-right boundary

# Four triangles forming an open rectangular strip.
# v0 and v1 each share a boundary edge.
t0 = m.triangle(v2, v3, v0)   # 0: bottom-left — edges (2,3),(3,0),(0,2)
t1 = m.triangle(v3, v1, v0)   # 1: bottom-right — edges (3,1),(1,0),(0,3) → shares (v0,v1)
t2 = m.triangle(v0, v1, v4)   # 2: top-left — edges (0,1),(1,4),(4,0) → shares (v0,v1)
t3 = m.triangle(v1, v5, v4)   # 3: top-right — edges (1,5),(5,4),(4,1)

# The degenerate near-zero edge (v0,v1) is interior: shared by t1 and t2.
m.assert_edge_shared(v0, v1, 2)

# v0 and v1 are nearly coincident.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)

# v0 is on the boundary: edge (v2,v0) is a boundary edge (only in t0).
m.assert_edge_shared(v2, v0, 1)

# v1 is on the boundary: edge (v1,v5) is a boundary edge (only in t3).
m.assert_edge_shared(v1, v5, 1)
