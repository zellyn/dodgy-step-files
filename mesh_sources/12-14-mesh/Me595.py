"""Me595 — holeFilling_TriangulateHole_watson_insert_failure: watsonInsert returns NULL; interior point outside triangulation (Branch 6).

MeshFix `holeFilling::TriangulateHole@L157` Branch 6 (*WATSON_INSERT_FAILURE*) @ line 270:
  'watsonInsert(p, ...)== NULL' → skip interior point; continue with next.
  After initial hole triangulation, TriangulateHole optionally refines the
  fill by inserting interior points (barycenters of large triangles). For
  each candidate interior point p, it calls watsonInsert(). If watsonInsert
  returns NULL (the point falls outside the triangulation domain or the
  insertion fails due to degenerate configuration), Branch 6 fires and p
  is skipped.

Defect pattern: a hole that has been triangulated (fill triangles present),
  followed by an interior point p that lies just outside the fill domain.
  In MeshFix, this can occur when the candidate point is the centroid of a
  large fill triangle but the triangulation domain is non-convex — the
  centroid lies outside the actual triangulated region.

Geometry: an L-shaped (non-convex) hole where the fill centroid of one
  triangle falls in the concave notch region — outside the triangulation.
  We model the surrounding mesh as a 5-triangle ring with an L-shaped inner
  boundary, and a single fill triangle whose centroid is the insertion candidate.

  Outer boundary: v0=(0,0,0), v1=(4,0,0), v2=(4,2,0), v3=(2,2,0),
                  v4=(2,4,0), v5=(0,4,0) — L-shape.
  The centroid of a naive fill triangle (v0,v2,v5) would be at (~1.33,~2,0),
  which lies in the concave region of the L — outside the valid triangulation
  → watsonInsert returns NULL → Branch 6.

  We provide the surrounding ring as 5 triangles with a hub at the concave
  corner, leaving the L boundary open.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me595",
    title="holeFilling_TriangulateHole_watson_insert_failure: L-shaped hole; interior insertion candidate falls in concave notch; watsonInsert returns NULL (Branch 6)",
    defect_class="hole_in_hull",
)

# L-shaped hole boundary (6 vertices).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0: outer bottom-left
v1 = m.vertex(4.0, 0.0, 0.0)   # 1: outer bottom-right
v2 = m.vertex(4.0, 2.0, 0.0)   # 2: outer right
v3 = m.vertex(2.0, 2.0, 0.0)   # 3: inner concave corner
v4 = m.vertex(2.0, 4.0, 0.0)   # 4: outer top-right
v5 = m.vertex(0.0, 4.0, 0.0)   # 5: outer top-left

# Hub vertex at origin of the L-shape (interior anchor for rim triangles).
vh = m.vertex(0.0, 2.0, 0.0)   # 6: left-mid hub

# 5 rim triangles forming the border around the L-shaped hole.
# The L-shaped inner boundary: v0 → v1 → v2 → v3 → v4 → v5 → v0.
t0 = m.triangle(v0, v1, v2)   # 0: bottom-right rect
t1 = m.triangle(v0, v2, v3)   # 1: middle-right
t2 = m.triangle(v3, v4, v5)   # 2: top section
t3 = m.triangle(v0, v3, v5)   # 3: diagonal bridge
t4 = m.triangle(v0, v5, vh)   # 4: left strip

# Interior shared edges of rim.
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t3
m.assert_edge_shared(v0, v5, 2)   # shared by t3 and t4
m.assert_edge_shared(v3, v5, 2)   # shared by t2 and t3

# Boundary edges (n=1): outer perimeter of the rim.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v5, vh, 1)
m.assert_edge_shared(v0, vh, 1)

# The hole boundary is the L-shaped perimeter of the inner region.
# The concave notch at (v3) makes interior point insertion fail.
m.assert_hole_boundary([v0, v1, v2, v3, v4, v5])

# Euler: V=7, E=11, F=5, chi=1 (open disk).
m.assert_euler_characteristic(7, 11, 5, 1)
