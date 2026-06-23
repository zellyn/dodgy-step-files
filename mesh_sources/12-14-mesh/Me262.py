"""Me262 — range_with_face_set_border_triangle_hole: degenerate border edge bounds 3-edge hole.

Catalog claim: CGAL PMP.remove_degenerate_edges.range_with_face_set Branch 3 @ line 1585
(*border_edge_triangle_hole*): the degenerate edge is a border edge (incident on only 1
triangle) and the border it belongs to forms a 3-edge hole (a triangle-shaped opening).
The algorithm calls Euler::fill_hole to close the triangular hole, removing the degenerate
edge by filling the gap.

Geometric signature: a triangulated patch with a triangular hole. The degenerate border
edge is one of three boundary edges that together form a 3-edge cycle (triangle hole).
The vertices of the hole are nearly-collinear or two of them are nearly coincident,
creating a degenerate border edge.

Vertices v0≈v1 (near-coincident, degenerate border edge). The boundary cycle is:
  v0→v1 (degenerate, near-zero length) → v2 → back to v0
forming a 3-edge triangular hole. The surrounding mesh patch has 3 triangles.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me262",
             title="range_with_face_set border_triangle_hole: degenerate border edge bounds 3-edge hole → fill_hole",
             defect_class="degenerate_edge")

# The hole boundary cycle: v0, v1 (near-coincident = degenerate), v2.
v0 = m.vertex(0.0,  0.0, 0.0)
v1 = m.vertex(1e-10, 0.0, 0.0)   # nearly same as v0 → degenerate border edge

# Hole third vertex.
v2 = m.vertex(0.5, 1.0, 0.0)

# Three outer vertices of the surrounding mesh patch.
v3 = m.vertex(-1.0, 0.0, 0.0)
v4 = m.vertex(0.5,  2.0, 0.0)
v5 = m.vertex(1.5,  0.0, 0.0)

# Three patch triangles that surround the hole (open at the hole).
t0 = m.triangle(v0, v3, v2)   # 0: left flank
t1 = m.triangle(v2, v4, v1)   # 1: top flank
t2 = m.triangle(v1, v5, v0)   # 2: right flank (v1 connects back to v0 via boundary)

# The hole boundary loop is v0 → v1 → v2 → v0.
# Each of these edges must be incident on exactly 1 triangle (true border edges).
m.assert_hole_boundary([v0, v1, v2])

# The degenerate border edge (v0, v1) is a boundary edge (shared by 1 triangle: t2).
m.assert_edge_shared(v0, v1, 1)

# v0 and v1 are nearly coincident.
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)
