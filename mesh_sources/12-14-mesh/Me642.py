"""Me642 — holeFilling::fillSmallBoundaries BOUNDARY_CROSSING_CONSTRAINT: selection-boundary vertex blocks fill (Branch 3).

MeshFix `holeFilling::fillSmallBoundaries` Branch 3 (*BOUNDARY_CROSSING_CONSTRAINT*) @ line 542:
  'if (IS_BIT(w, 6)) { grd = nbe + 1; break; }' — when the hole boundary loop
  being evaluated passes through a vertex that was marked as a selection boundary
  vertex (bit 6 set by Branch 1's IS_VISITED scan), the fill count grd is forced
  to nbe+1 (above threshold) and the inner boundary-traversal loop breaks. This
  prevents the hole from being filled when its boundary crosses into a selected region.

Defect pattern: a mesh where the triangular hole (h0,h1,h2) has one vertex (h0)
  that is also adjacent to a "selected" (IS_VISITED) triangle. After the selected-
  triangle scan (Branch 1) sets IS_BIT(h0, 6), the boundary-traversal loop for the
  hole visits h0, triggering Branch 3: grd is set to nbe+1 and the loop breaks,
  skipping this hole.

Geometry:
  Selected-triangle pair (IS_VISITED): ts0=(s0,s1,h0), ts1=(s0,h0,s2)
    — h0 is shared with the hole; IS_BIT(h0,6) gets set.
  Hole frame: three triangles (tf0-tf2) surrounding triangular hole (h0,h1,h2).
    tf0=(h0,h1,a): left frame; edge (h0,h1) n=1 (hole boundary)
    tf1=(h1,h2,a): right frame; edge (h1,h2) n=1 (hole boundary)
    tf2=(h2,h0,a): top frame; edge (h2,h0) n=1 (hole boundary)
  Anchor vertex a=(2,0,0) sits below; all three frame triangles share it.
  Hole boundary: h0-h1-h2, each edge n=1. h0 has IS_BIT(6) → Branch 3.

Vertices:
  h0=(1,2,0) — hole corner + selection-adjacent (IS_BIT(h0,6) set)
  h1=(0,0,0), h2=(2,0,0) — other hole corners
  a=(1,-1,0) — frame anchor
  s0=(0,3,0), s1=(-1,1,0), s2=(2,3,0) — selected-patch outer vertices
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me642",
    title="holeFilling::fillSmallBoundaries BOUNDARY_CROSSING_CONSTRAINT: IS_BIT(h0,6) set; grd forced to nbe+1; hole traversal aborted (Branch 3)",
    defect_class="boundary_hole",
)

# Hole boundary vertex shared with selected patch.
h0 = m.vertex(1.0,  2.0, 0.0)   # 0 — shared; IS_BIT(6) set after selected-patch scan
h1 = m.vertex(0.0,  0.0, 0.0)   # 1 — hole corner
h2 = m.vertex(2.0,  0.0, 0.0)   # 2 — hole corner
a  = m.vertex(1.0, -1.0, 0.0)   # 3 — frame anchor below hole

# Selected-patch outer vertices.
s0 = m.vertex(0.0,  3.0, 0.0)   # 4
s1 = m.vertex(-1.0, 1.0, 0.0)   # 5
s2 = m.vertex(2.0,  3.0, 0.0)   # 6

# Selected triangles (IS_VISITED): share vertex h0.
# Branch 1 sets IS_BIT(h0, 6) because h0 is a vertex of an IS_VISITED triangle.
ts0 = m.triangle(s0, s1, h0)    # 0 — selected
ts1 = m.triangle(s0, h0, s2)    # 1 — selected

# Hole frame triangles (unselected) surrounding the triangular hole.
# Each frame triangle contributes one hole-boundary edge (n=1).
tf0 = m.triangle(h0, h1, a)     # 2: left frame; contributes edge (h0,h1)
tf1 = m.triangle(h1, h2, a)     # 3: bottom frame; contributes edge (h1,h2)
tf2 = m.triangle(h2, h0, a)     # 4: right frame; contributes edge (h2,h0)

# Edge verification:
# ts0=(4,5,0): (4,5),(5,0),(4,0)
# ts1=(4,0,6): (4,0),(0,6),(4,6)
# tf0=(0,1,3): (0,1),(1,3),(0,3)
# tf1=(1,2,3): (1,2),(2,3),(1,3)
# tf2=(2,0,3): (2,0),(0,3),(2,3)
# Hole boundary edges: (0,1),(1,2),(2,0) — each appears in exactly one tf. ✓
# (h0,h1)=(0,1): in tf0 only. n=1 ✓
# (h1,h2)=(1,2): in tf1 only. n=1 ✓
# (h0,h2)=(0,2): in tf2 only. n=1 ✓
# Interior shared edges:
# (1,3)=(h1,a): in tf0 and tf1. n=2 ✓
# (2,3)=(h2,a): in tf1 and tf2. n=2 ✓
# (0,3)=(h0,a): in tf0 and tf2. n=2 ✓
# (4,0)=(s0,h0): in ts0 and ts1. n=2 ✓

# Triangular hole boundary: h0-h1-h2. h0 has IS_BIT(6) → Branch 3.
m.assert_hole_boundary([h0, h1, h2])

# Hole boundary edges (n=1 each).
m.assert_edge_shared(h0, h1, 1)   # (0,1): only in tf0
m.assert_edge_shared(h1, h2, 1)   # (1,2): only in tf1
m.assert_edge_shared(h0, h2, 1)   # (0,2): only in tf2

# Interior edges confirming mesh connectivity.
m.assert_edge_shared(h0, a, 2)    # (0,3): tf0 and tf2
m.assert_edge_shared(h1, a, 2)    # (1,3): tf0 and tf1
m.assert_edge_shared(h2, a, 2)    # (2,3): tf1 and tf2
m.assert_edge_shared(s0, h0, 2)   # (4,0): ts0 and ts1
