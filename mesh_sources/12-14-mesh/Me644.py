"""Me644 — holeFilling::fillSmallBoundaries PATCH_TRIANGULATION_WITH_REFINEMENT: TriangulateHole + refineSelectedHolePatches (Branch 5).

MeshFix `holeFilling::fillSmallBoundaries` Branch 5 (*PATCH_TRIANGULATION_WITH_REFINEMENT*) @ line 556:
  'if (TriangulateHole(e, ...) && refine_patches)
   { refineSelectedHolePatches(num_samples, max_iters, convergence); }'
  — after successfully triangulating a hole via TriangulateHole, if the caller set
  refine_patches=true the newly inserted patch triangles undergo local refinement via
  refineSelectedHolePatches (Laplacian-style smoothing + edge splits). This branch
  fires when the hole was triangulated AND refinement was requested.

Defect pattern: a mesh with a quadrilateral hole (4-edge boundary) that is larger
  than a minimal triangle hole. A 4-sided hole requires TriangulateHole to insert at
  least one diagonal, producing two triangles. With refine_patches=true the fill patch
  is then refined. This models the POST-triangulation state: the hole is filled with
  two triangles and a Steiner point is added at the patch centroid by refineSelectedHolePatches.

Geometry (flat XY plane):
  Quadrilateral hole: h0=(0,0,0), h1=(3,0,0), h2=(3,3,0), h3=(0,3,0)
  Frame outer vertices: f0=(1.5,-2,0), f1=(5,1.5,0), f2=(1.5,5,0), f3=(-2,1.5,0)
  Frame triangles (4, one per hole edge):
    tf0=(h0,h1,f0), tf1=(h1,h2,f1), tf2=(h2,h3,f2), tf3=(h3,h0,f3)
  Fill triangles (TriangulateHole output, plus Steiner point sc at patch centroid):
    sc=(1.5,1.5,0)
    tp0=(h0,h1,sc), tp1=(h1,h2,sc), tp2=(h2,h3,sc), tp3=(h3,h0,sc)
  refineSelectedHolePatches: sc is the inserted Steiner point; all edges from sc n=2.

The four fill triangles (tp0-tp3) form the hole patch. All edges from sc are interior
  (n=2) — confirming the Steiner-point refinement by refineSelectedHolePatches.
  The hole-boundary edges between frame and fill triangles are n=2 after the fill.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me644",
    title="holeFilling::fillSmallBoundaries PATCH_TRIANGULATION_WITH_REFINEMENT: 4-edge hole filled by TriangulateHole; Steiner point sc inserted by refineSelectedHolePatches (Branch 5)",
    defect_class="boundary_hole",
)

# Quadrilateral hole boundary vertices.
h0 = m.vertex(0.0,  0.0, 0.0)   # 0 — hole corner bottom-left
h1 = m.vertex(3.0,  0.0, 0.0)   # 1 — hole corner bottom-right
h2 = m.vertex(3.0,  3.0, 0.0)   # 2 — hole corner top-right
h3 = m.vertex(0.0,  3.0, 0.0)   # 3 — hole corner top-left

# Outer frame vertices (context mesh around the hole).
f0 = m.vertex(1.5, -2.0, 0.0)   # 4 — bottom frame outer
f1 = m.vertex(5.0,  1.5, 0.0)   # 5 — right frame outer
f2 = m.vertex(1.5,  5.0, 0.0)   # 6 — top frame outer
f3 = m.vertex(-2.0, 1.5, 0.0)   # 7 — left frame outer

# Steiner point inserted by refineSelectedHolePatches at patch centroid.
sc = m.vertex(1.5,  1.5, 0.0)   # 8 — interior Steiner point

# Context (frame) triangles surrounding the hole.
tf0 = m.triangle(h0, h1, f0)    # 0 — bottom frame
tf1 = m.triangle(h1, h2, f1)    # 1 — right frame
tf2 = m.triangle(h2, h3, f2)    # 2 — top frame
tf3 = m.triangle(h3, h0, f3)    # 3 — left frame

# Fill triangles inserted by TriangulateHole + refined by refineSelectedHolePatches.
# Four-triangle fan from Steiner point sc covers the quadrilateral hole.
tp0 = m.triangle(h0, h1, sc)    # 4 — fill bottom
tp1 = m.triangle(h1, h2, sc)    # 5 — fill right
tp2 = m.triangle(h2, h3, sc)    # 6 — fill top
tp3 = m.triangle(h3, h0, sc)    # 7 — fill left

# Edge verification:
# tf0=(0,1,4): (0,1),(1,4),(0,4)
# tf1=(1,2,5): (1,2),(2,5),(1,5)
# tf2=(2,3,6): (2,3),(3,6),(2,6)
# tf3=(3,0,7): (3,0),(0,7),(3,7)
# tp0=(0,1,8): (0,1),(1,8),(0,8)
# tp1=(1,2,8): (1,2),(1,8),(2,8) wait: (1,2),(2,8),(1,8)
# tp2=(2,3,8): (2,3),(3,8),(2,8)
# tp3=(3,0,8): (3,0),(0,8),(3,8)

# Hole-boundary edges now interior (n=2) after fill.
m.assert_edge_shared(h0, h1, 2)   # (0,1): tf0 and tp0
m.assert_edge_shared(h1, h2, 2)   # (1,2): tf1 and tp1
m.assert_edge_shared(h2, h3, 2)   # (2,3): tf2 and tp2
m.assert_edge_shared(h3, h0, 2)   # (3,0): tf3 and tp3

# All edges from Steiner point sc are interior (n=2) — confirms refinement.
m.assert_edge_shared(h0, sc, 2)   # (0,8): tp0 and tp3
m.assert_edge_shared(h1, sc, 2)   # (1,8): tp0 and tp1
m.assert_edge_shared(h2, sc, 2)   # (2,8): tp1 and tp2
m.assert_edge_shared(h3, sc, 2)   # (3,8): tp2 and tp3

# Outer frame edges (n=1 — open mesh exterior).
m.assert_edge_shared(h0, f0, 1)   # (0,4): only in tf0
m.assert_edge_shared(h1, f0, 1)   # (1,4): only in tf0
m.assert_edge_shared(h1, f1, 1)   # (1,5): only in tf1
m.assert_edge_shared(h2, f1, 1)   # (2,5): only in tf1
m.assert_edge_shared(h2, f2, 1)   # (2,6): only in tf2
m.assert_edge_shared(h3, f2, 1)   # (3,6): only in tf2
m.assert_edge_shared(h3, f3, 1)   # (3,7): only in tf3
m.assert_edge_shared(h0, f3, 1)   # (0,7): only in tf3

# Euler: V=9, E=16, F=8, chi = 9-16+8 = 1 (open disk).
# Edges: 8 outer (frame-to-outer) + 4 hole-boundary (now interior) + 4 sc-spokes = 16.
m.assert_euler_characteristic(v=9, e=16, f=8, chi=1)
