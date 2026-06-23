"""Me030 — degree3_vertex_cap: center vertex with exactly 3 neighbors forms near-cap (Branch 7).

Catalog claim: vertex 0 (the cap center) is shared by exactly 3 triangles
(faces 0, 1, 2) that form a triangular patch. Each neighbor of vertex 0 has
degree 3 when only counting the cap cluster. CGAL PMP.remove_degenerate_faces
detects the degree==3 condition and removes the center vertex via Euler's
remove_center_vertex operator (flattening the 3 faces into a single triangle).

Source: CGAL PMP.remove_degenerate_faces Branch 7 @ line 2186 —
*degree-3-vertex-in-cap*: vertex with exactly 3 incident triangles in the
degenerate cluster; removal via Euler remove_center_vertex.

Defect carrier: apex vertex 0 at (0.5, 0.5, 0.5) is shared by 3 near-flat
coplanar triangles fan. The apex is very close to the base plane (z=0.001),
making the cap nearly degenerate (effectively a flat patch with a small spike).
Triangles are face 0 = (apex, A, B), face 1 = (apex, B, C), face 2 = (apex, C, A).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me030",
             title="degree-3 vertex cap: apex with 3 incident triangles — remove_center_vertex branch",
             defect_class="degenerate_triangle")

# Cap apex (the degree-3 center vertex) — very slightly above the base plane.
# Base is a unit-side triangle; apex sits at centroid (0.5, 0.333, 0) raised
# by only 0.0001 units in z, making the cap almost flat (near-degenerate).
# Area of each panel ≈ 0.5 * |base_edge| * 0.0001 ≪ 0.01.
apex = m.vertex(0.5, 0.333, 0.0001)   # 0 — near-planar apex

# Base vertices forming the cap's outer triangle (unit-ish size).
vA = m.vertex(0.0, 0.0, 0.0)   # 1
vB = m.vertex(1.0, 0.0, 0.0)   # 2
vC = m.vertex(0.5, 0.666, 0.0) # 3

# Three triangles sharing the apex — a degree-3 fan.
t0 = m.triangle(apex, vA, vB)   # face 0
t1 = m.triangle(apex, vB, vC)   # face 1
t2 = m.triangle(apex, vC, vA)   # face 2

# Each apex edge is shared by exactly 2 triangles (interior fan edges).
# This is the key structural assertion: apex (vertex 0) has degree 3.
m.assert_edge_shared(apex, vA, 2)
m.assert_edge_shared(apex, vB, 2)
m.assert_edge_shared(apex, vC, 2)

# The outer base edges are boundary edges (shared by 1 face only).
m.assert_edge_shared(vA, vB, 1)
m.assert_edge_shared(vB, vC, 1)
m.assert_edge_shared(vC, vA, 1)
