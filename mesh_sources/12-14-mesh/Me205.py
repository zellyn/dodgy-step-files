"""Me205 — zip_opposite_vertices_distinct: ov1 != ov2 objects → merge proceeds.

MeshFix `Vertex.zip` Branch 6 (*opposite_vertices_distinct*) @ line 573:
  'if (ov1 != ov2)'
  When check_geom is disabled (or ov coords match), zip tests whether ov1 and ov2 are
  distinct objects. If they ARE distinct, zip proceeds with the merge: all edges incident
  to ov2 are redirected to ov1, collapsing the seam. Branch 6 covers the merge path.

Defect pattern: two separate open patches sharing a coincident seam. The zip vertex v0
lies at one end of the seam. ov1 and ov2 are two distinct vertex objects at near-identical
positions (the unmerged opposite boundary vertices). zip merges them because check_geom=false
(or coords match), the merge proceeds.

Geometry: two open triangles sharing coincident boundary edges meeting at v0.
  Patch A: t0=(v0,v1,v2) — (v0,v1) boundary, (v0,v2) boundary
  Patch B: t1=(v3,v4,v5) — (v3,v4) boundary, coincident to (v0,v1)
  v0=(v3) position, v1=(v4) position but distinct objects → ov1!=ov2 triggers merge.

Near-coincident pairs confirm ov1 and ov2 are the distinct objects to be merged.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me205",
             title="zip_opposite_vertices_distinct: ov1 and ov2 are distinct objects at coincident positions → zip merge proceeds",
             defect_class="zip_opposite_vertices_distinct")

# Patch A: open triangle
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — zip vertex (junction); same pos as v3
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — be1 endpoint (ov2 candidate on Patch A)
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — opposite vertex ov1

# Patch B: coincident open triangle with distinct vertex objects
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — same position as v0 (unstitched seam)
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — same position as v1 (ov2 on Patch B)
v5 = m.vertex(0.5, -1.0, 0.0)  # 5 — far side of Patch B

t0 = m.triangle(v0, v1, v2)    # 0 — Patch A
t1 = m.triangle(v3, v4, v5)    # 1 — Patch B

# Boundary edges on both patches (each incident on exactly 1 triangle)
m.assert_edge_shared(v0, v1, 1)  # Patch A boundary (be1 at zip vertex)
m.assert_edge_shared(v0, v2, 1)  # Patch A boundary (be2 at zip vertex)
m.assert_edge_shared(v3, v4, 1)  # Patch B coincident boundary — ov1 candidate
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v1, v2, 1)

# Near-coincident vertex pairs confirm ov1 and ov2 are distinct objects at same location
m.assert_vertex_pair_distance_lt(v0, v3, 1e-9)  # zip vertex duplicates
m.assert_vertex_pair_distance_lt(v1, v4, 1e-9)  # ov1 != ov2; merge target
