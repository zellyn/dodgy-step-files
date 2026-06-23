"""Me209 — zip_recursive_zip: merged vertex ov1 triggers a recursive zip() call.

MeshFix `Vertex.zip` Branch 10 (*recursive_zip*) @ line 586:
  'ret += ov1->zip(check_geom)'
  After merging ov2 into ov1 and updating the triangle edge records, zip recurses on ov1.
  This handles chains of adjacent open seam vertices: after zipping v0, ov1 may itself
  be a boundary vertex eligible for a further zip that closes the next link in the chain.
  Branch 10 covers this recursive accumulation pattern.

Defect pattern: a chain of two adjacent seam vertices. After zip(v0) merges the first
boundary pair, ov1 becomes eligible for a further zip. The fixture shows a two-level
chain: v0 is the first zip vertex, and ov1 (v2/v5 merged position) is the next seam
junction that would itself be zipped recursively.

Geometry: two open patches forming a two-vertex chain seam.
  Patch A: v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(1,1,0)
           t0=(v0,v1,v3), t1=(v1,v2,v3)  — two-triangle strip; open at both ends
  Patch B: v4=(0,0,0), v5=(1,0,0), v6=(2,0,0), v7=(1,-1,0)
           t2=(v4,v7,v5), t3=(v5,v7,v6)  — mirror strip; open at both ends

Near-coincident pairs: v0≈v4, v1≈v5, v2≈v6 — the two patches are geometrically
coincident but stored as separate vertices (unstitched). zip(v0) merges v4→v0 and
then recurses on ov1=v1≈v5 for the next step. Branch 10 adds the recursive count.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me209",
             title="zip_recursive_zip: after zipping v0→ov1 merge, zip recurses on ov1 to close chain seam",
             defect_class="zip_recursive_zip")

# Patch A: two-triangle strip
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — first zip vertex
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — ov1 after first zip; next recursion target
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — chain end
v3 = m.vertex(1.0, 1.0, 0.0)   # 3 — shared interior apex for Patch A

# Patch B: mirror strip (geometrically coincident, separate objects)
v4 = m.vertex(0.0, 0.0, 0.0)   # 4 ≈ v0 (unstitched)
v5 = m.vertex(1.0, 0.0, 0.0)   # 5 ≈ v1 (ov2 for first zip; ov1 for second)
v6 = m.vertex(2.0, 0.0, 0.0)   # 6 ≈ v2 (chain end on Patch B)
v7 = m.vertex(1.0, -1.0, 0.0)  # 7 — shared interior apex for Patch B

t0 = m.triangle(v0, v1, v3)    # 0 — Patch A, first triangle
t1 = m.triangle(v1, v2, v3)    # 1 — Patch A, second triangle
t2 = m.triangle(v4, v7, v5)    # 2 — Patch B, first triangle
t3 = m.triangle(v5, v7, v6)    # 3 — Patch B, second triangle

# Boundary edges on Patch A
m.assert_edge_shared(v0, v1, 1)  # be1 of first zip
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v1, v2, 1)  # shared interior? No — t0 shares (v1,v3) not (v1,v2)

# Interior shared edges on Patch A
m.assert_edge_shared(v1, v3, 2)  # shared by t0 and t1

# Boundary edges on Patch B
m.assert_edge_shared(v4, v5, 1)  # be2 of first zip (≈ be1=(v0,v1))
m.assert_edge_shared(v4, v7, 1)
m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v5, v6, 1)

# Interior shared edges on Patch B
m.assert_edge_shared(v5, v7, 2)  # shared by t2 and t3

# Near-coincident pairs: the two-vertex chain seam
m.assert_vertex_pair_distance_lt(v0, v4, 1e-9)  # first zip vertex pair
m.assert_vertex_pair_distance_lt(v1, v5, 1e-9)  # ov1/ov2 pair → recursive zip
m.assert_vertex_pair_distance_lt(v2, v6, 1e-9)  # chain end pair
