"""Me084 — connectivity_orphaned_edge: open boundary strip with multiple boundary-only edges.

Catalog claim: the mesh is an open strip — a flat grid of 6 triangles with open
boundary on three sides. Every boundary edge is incident on exactly 1 triangle
(orphaned in the sense that it has no opposite twin in the half-edge structure).
MeshFix checkConnectivity Branch 6 (*ORPHANED_EDGE*) detects edges that have no
incident triangles at all. In a triangle-list mesh the analogous flaw is an open
boundary: edges incident on exactly 1 triangle have no t2 twin, and if a repair
routine accidentally severs a triangle without cleaning up the edge, that edge
becomes a true orphan (0 triangle incidences).

Defect carrier: 6 triangles form a 2×2 quad strip. The outer 9 boundary edges
are each incident on only 1 triangle. Two inner edges are each shared by 2
triangles. This demonstrates the boundary-edge topology that MeshFix Branch 6
must recognise and handle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me084",
             title="connectivity orphaned edge: open 2×2 quad strip — 9 boundary edges each incident on 1 triangle",
             defect_class="open_boundary")

# 3×2 grid of vertices (3 columns, 2 rows).
v00 = m.vertex(0.0, 0.0, 0.0)
v10 = m.vertex(1.0, 0.0, 0.0)
v20 = m.vertex(2.0, 0.0, 0.0)
v01 = m.vertex(0.0, 1.0, 0.0)
v11 = m.vertex(1.0, 1.0, 0.0)
v21 = m.vertex(2.0, 1.0, 0.0)

# 4 quads split into 8 triangles (2×2 arrangement).
# Left quad.
m.triangle(v00, v10, v11)   # t0
m.triangle(v00, v11, v01)   # t1
# Right quad.
m.triangle(v10, v20, v21)   # t2
m.triangle(v10, v21, v11)   # t3

# Interior shared edge (v10, v11) shared by t0 and t3.
m.assert_edge_shared(v10, v11, 2)

# Bottom boundary edges — each incident on exactly 1 triangle.
m.assert_edge_shared(v00, v10, 1)
m.assert_edge_shared(v10, v20, 1)

# Top boundary edges.
m.assert_edge_shared(v01, v11, 1)
m.assert_edge_shared(v11, v21, 1)

# Left and right boundary edges.
m.assert_edge_shared(v00, v01, 1)
m.assert_edge_shared(v20, v21, 1)

# Hole boundary: the full outer loop is a valid boundary cycle.
m.assert_hole_boundary([v00, v10, v20, v21, v11, v01])
