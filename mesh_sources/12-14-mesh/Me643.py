"""Me643 — holeFilling::fillSmallBoundaries SMALL_BOUNDARY_THRESHOLD: 3-edge hole added to fill list (Branch 4).

MeshFix `holeFilling::fillSmallBoundaries` Branch 4 (*SMALL_BOUNDARY_THRESHOLD*) @ line 547:
  'if (grd <= nbe) { bdrs.appendHead(e); }' — after traversing a hole boundary loop
  and counting boundary edges (grd), the algorithm checks whether the hole is small
  enough to fill (grd <= nbe). If so, the starting boundary edge is appended to the
  fill list `bdrs` for subsequent TriangulateHole processing. This branch fires for
  any hole whose boundary edge count does not exceed the small-hole threshold nbe.

Defect pattern: a minimal triangular hole (3-edge boundary loop) — the smallest
  possible hole in a triangle mesh. Three outer triangles surround the hole, each
  contributing one boundary edge. The boundary count grd=3 satisfies grd<=nbe when
  nbe>=3 (default MeshFix behavior), so the hole is added to bdrs → Branch 4 fires.

This is the canonical small-hole case: a single missing interior triangle.

Geometry (flat XY plane):
  Hole boundary: h0=(0,0,0), h1=(2,0,0), h2=(1,2,0)
  Frame anchor: a=(1,-1.5,0) — shared outer vertex for all three frame triangles
  Outer frame vertices: f0=(-1.5,1,0), f1=(3.5,1,0), f2=(1,3.5,0)
  Frame triangles (surrounding the hole):
    tf0=(h0,h1,a):  bottom frame
    tf1=(h1,h2,f1): right frame
    tf2=(h2,h0,f0): left frame
  Hole boundary edges: (h0,h1) n=1, (h1,h2) n=1, (h2,h0) n=1.
  grd=3 <= nbe=3 → Branch 4: bdrs.appendHead(edge_h0_h1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me643",
    title="holeFilling::fillSmallBoundaries SMALL_BOUNDARY_THRESHOLD: 3-edge triangular hole; grd=3 <= nbe; added to fill list bdrs (Branch 4)",
    defect_class="boundary_hole",
)

# Triangular hole boundary vertices.
h0 = m.vertex(0.0,  0.0, 0.0)   # 0 — hole corner left
h1 = m.vertex(2.0,  0.0, 0.0)   # 1 — hole corner right
h2 = m.vertex(1.0,  2.0, 0.0)   # 2 — hole corner top

# Outer frame vertices (one per frame triangle, beyond the hole).
f0 = m.vertex(-1.5, 1.0, 0.0)   # 3 — left frame outer
f1 = m.vertex(3.5,  1.0, 0.0)   # 4 — right frame outer
fa = m.vertex(1.0, -1.5, 0.0)   # 5 — bottom frame outer

# Three frame triangles surrounding the triangular hole.
# Each contributes exactly one hole-adjacent boundary edge (n=1).
tf0 = m.triangle(h0, h1, fa)    # 0: bottom frame; hole edge (h0,h1)
tf1 = m.triangle(h1, h2, f1)    # 1: right frame; hole edge (h1,h2)
tf2 = m.triangle(h2, h0, f0)    # 2: left frame; hole edge (h2,h0)

# Edge counts:
# tf0=(0,1,5): (0,1),(1,5),(0,5)
# tf1=(1,2,4): (1,2),(2,4),(1,4)
# tf2=(2,0,3): (2,0),(0,3),(2,3)
# Hole boundary edges (n=1 each):
# (0,1)=(h0,h1): only in tf0 ✓
# (1,2)=(h1,h2): only in tf1 ✓
# (0,2)=(h0,h2): only in tf2 ✓
# All other edges appear in exactly 1 triangle (outer boundary).

# Triangular hole: the missing interior triangle (h0,h1,h2).
# grd=3 (three boundary edges), nbe=3 → grd<=nbe → bdrs.appendHead fires (Branch 4).
m.assert_hole_boundary([h0, h1, h2])

# Hole boundary edges (n=1 each — each borders exactly one frame triangle).
m.assert_edge_shared(h0, h1, 1)   # (0,1): only in tf0; starting edge for bdrs.appendHead
m.assert_edge_shared(h1, h2, 1)   # (1,2): only in tf1
m.assert_edge_shared(h0, h2, 1)   # (0,2): only in tf2

# Outer frame boundary edges (n=1 each — open mesh exterior).
m.assert_edge_shared(h0, fa, 1)   # (0,5): only in tf0
m.assert_edge_shared(h1, fa, 1)   # (1,5): only in tf0
m.assert_edge_shared(h1, f1, 1)   # (1,4): only in tf1
m.assert_edge_shared(h2, f1, 1)   # (2,4): only in tf1
m.assert_edge_shared(h2, f0, 1)   # (2,3): only in tf2
m.assert_edge_shared(h0, f0, 1)   # (0,3): only in tf2

# Euler: V=6, E=9 (3 hole + 6 outer), F=3, chi = 6 - 9 + 3 = 0.
# Wait: each frame triangle has 3 edges; 3 triangles × 3 = 9 edges total;
# 3 hole edges each appear once, 6 outer edges each appear once → 9 distinct edges.
m.assert_euler_characteristic(v=6, e=9, f=3, chi=0)
