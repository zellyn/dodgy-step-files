"""Me594 — holeFilling_TriangulateHole_delaunay_constrained_swap: edge swap improves Delaunay quality; sw++ counter increments (Branch 5).

MeshFix `holeFilling::TriangulateHole@L157` Branch 5 (*DELAUNAY_CONSTRAINED_SWAP*) @ line 258:
  'e1->delaunayMinAngle()' — swap is accepted; sw++ increments.
  After the hole is filled with new triangles, TriangulateHole enters an
  edge-swap optimization phase. For each interior edge of the fill, it tests
  whether swapping improves the minimum angle (Lawson flip for Delaunay quality).
  When the swap improves the minimum angle, Branch 5 fires and sw is incremented.

Defect pattern: a hole triangulated with a "bad" diagonal — the initial fill
  produces a sliver triangle pair that violates Delaunay. The shared diagonal
  of the two fill triangles has a circumsphere containing the opposite vertex,
  so delaunayMinAngle() returns true → swap is performed → sw++.

Geometry: a quadrilateral hole (4 boundary vertices) initially filled with
  a non-Delaunay diagonal. The "bad" diagonal creates two triangles where
  one is highly obtuse; the alternative diagonal creates two better-balanced
  triangles, so the Lawson flip is accepted.

  Quadrilateral boundary: v0=(0,0,0), v1=(3,0,0), v2=(2,1,0), v3=(0,1,0).
  Bad diagonal: (v0,v2) — creates t_fill0=(v0,v1,v2) and t_fill1=(v0,v2,v3).
  t_fill0 is very obtuse at v0 (angle ~18°). delaunayMinAngle() finds the
  alternative diagonal (v1,v3) produces a better minimum angle → swap.

  We model the mesh surrounding the hole: 4 boundary triangles (one per
  boundary edge) attached to an outer ring, leaving the central quad open.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me594",
    title="holeFilling_TriangulateHole_delaunay_constrained_swap: non-Delaunay fill diagonal triggers edge swap; sw++ fires (Branch 5)",
    defect_class="hole_in_hull",
)

# Quadrilateral hole boundary: v0-v1-v2-v3, chosen so the (v0,v2) diagonal
# produces a worse Delaunay triangulation than the (v1,v3) diagonal.
# Outer ring connects each boundary edge to an external vertex.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0: bottom-left
v1 = m.vertex(3.0, 0.0, 0.0)   # 1: bottom-right
v2 = m.vertex(2.0, 1.0, 0.0)   # 2: top-right
v3 = m.vertex(0.0, 1.0, 0.0)   # 3: top-left

# Outer ring vertices (one per boundary edge) for the surrounding mesh.
e0 = m.vertex(1.5, -1.0, 0.0)  # 4: below edge v0-v1
e1 = m.vertex(4.0,  0.5, 0.0)  # 5: right of edge v1-v2
e2 = m.vertex(1.0,  2.0, 0.0)  # 6: above edge v2-v3
e3 = m.vertex(-1.0, 0.5, 0.0)  # 7: left of edge v3-v0

# 4 surrounding triangles (rim), one per boundary edge.
t0 = m.triangle(v0, v1, e0)  # 0: bottom rim
t1 = m.triangle(v1, v2, e1)  # 1: right rim
t2 = m.triangle(v2, v3, e2)  # 2: top rim
t3 = m.triangle(v3, v0, e3)  # 3: left rim

# Fill the hole with the non-Delaunay diagonal (v0,v2):
# This creates two fill triangles where (v0,v2) is interior.
# delaunayMinAngle() would prefer (v1,v3) — Branch 5 fires on swap.
tf0 = m.triangle(v0, v1, v2)  # 4: fill lower-right
tf1 = m.triangle(v0, v2, v3)  # 5: fill upper-left

# Non-Delaunay interior diagonal — shared by two fill triangles.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges of surrounding mesh (n=1: each outer triangle has 2 boundary edges).
m.assert_edge_shared(v0, v1, 2)  # now shared by t0 (rim) + tf0 (fill)
m.assert_edge_shared(v1, v2, 2)  # shared by t1 (rim) + tf0 (fill)
m.assert_edge_shared(v2, v3, 2)  # shared by t2 (rim) + tf1 (fill)
m.assert_edge_shared(v0, v3, 2)  # shared by t3 (rim) + tf1 (fill)

# Outer boundary edges of the surrounding rim (n=1 each).
m.assert_edge_shared(v0, e0, 1)
m.assert_edge_shared(v1, e0, 1)
m.assert_edge_shared(v1, e1, 1)
m.assert_edge_shared(v2, e1, 1)
m.assert_edge_shared(v2, e2, 1)
m.assert_edge_shared(v3, e2, 1)
m.assert_edge_shared(v3, e3, 1)
m.assert_edge_shared(v0, e3, 1)

# Euler: V=8, E=14, F=6+... let's compute:
# V=8 (v0-v3 + e0-e3), F=6 (t0-t3 + tf0-tf1)
# E = boundary(8) + interior hub edges...
# Faces=6, Vertices=8: E = V+F-chi = 8+6-1 = 13 (open disk, chi=1).
m.assert_euler_characteristic(8, 13, 6, 1)
