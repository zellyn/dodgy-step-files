"""Me770 — is_needle_triangle_face aspect_ratio_below_threshold: well-formed near-equilateral triangle; aspect ratio under needle threshold; returns null_halfedge (Branch 1).

CGAL PMP `PMP.is_needle_triangle_face` Branch 1 (*aspect_ratio_extreme*) @ line 428:
  'if(res == -1) return halfedge_descriptor();'
  — when the triangle's aspect ratio (longest_edge / shortest_altitude) is below
  the needle threshold the function returns a null halfedge, indicating the face
  is NOT a needle. Branch 1 fires for any well-formed, non-degenerate triangle
  whose proportions are close to equilateral.

Defect pattern: a single equilateral (or near-equilateral) triangle. No edge is
  dramatically shorter than the others; the shortest altitude is comparable to the
  edge lengths. Aspect ratio ≈ 1.15 for equilateral, well under the CGAL default
  threshold of 4.0.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5, 0.866, 0) — near-equilateral triangle.
  All three edge lengths ≈ 1.0; aspect ratio ≈ 1.15.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me770",
    title="is_needle_triangle_face aspect_ratio_below_threshold: near-equilateral triangle; aspect ratio < needle threshold; res==-1 returns null_halfedge (Branch 1)",
    defect_class="degenerate_triangle",
)

# Near-equilateral triangle — all edges approximately equal length 1.0.
v0 = m.vertex(0.0, 0.0,   0.0)  # 0
v1 = m.vertex(1.0, 0.0,   0.0)  # 1
v2 = m.vertex(0.5, 0.866, 0.0)  # 2 — apex at approx sqrt(3)/2

t0 = m.triangle(v0, v1, v2)  # 0

# All three edges are boundary edges (open single triangle).
m.assert_edge_shared(v0, v1, 1)  # e0: halfedge h
m.assert_edge_shared(v1, v2, 1)  # e1: next(h)
m.assert_edge_shared(v0, v2, 1)  # e2: prev(h)

# Triangle has positive area — not degenerate.
# area ≈ 0.5 * base * height = 0.5 * 1.0 * 0.866 ≈ 0.433
# Aspect ratio for equilateral ≈ 1.15; well below the default CGAL threshold (~4.0).
# is_needle_triangle_face returns null_halfedge (Branch 1 fires; res == -1).

# Euler: V=3, E=3, F=1, chi=1 (open disk / single triangle).
m.assert_euler_characteristic(3, 3, 1, 1)
