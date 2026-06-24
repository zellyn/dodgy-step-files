"""Me640 — holeFilling::fillSmallBoundaries SELECTION_PRESENT: pre-selected triangles constrain hole filling (Branch 1).

MeshFix `holeFilling::fillSmallBoundaries` Branch 1 (*SELECTION_PRESENT*) @ line 523:
  'if (IS_VISITED(t)) { ... }' — when some triangles are pre-selected (marked
  IS_VISITED), the algorithm marks their surrounding vertices so that the boundary
  fill is constrained to the unselected region. The selected patch forms an island
  whose border vertices act as fill constraints.

Defect pattern: a mesh with two distinct components. A "selected" triangular patch
  (three triangles surrounding an inner vertex) sits adjacent to an open-boundary
  region with a triangular hole. Branch 1 fires because at least one triangle is
  IS_VISITED; the surrounding vertices of selected triangles are flagged to constrain
  the fill.

Geometry (flat XY plane):
  Selected patch (3 triangles, no hole):
    s0=(0,0,0), s1=(2,0,0), s2=(1,2,0) — outer triangle
    sc=(1,0.7,0) — inner shared vertex
    ts0=(s0,s1,sc), ts1=(s1,s2,sc), ts2=(s2,s0,sc) — fan from sc

  Hole region (separate from selected patch):
    h0=(5,0,0), h1=(7,0,0), h2=(8,2,0), h3=(4,2,0) — frame vertices
    hc0=(6,0.5,0), hc1=(6,1.5,0) — sides of the hole approach
    th0=(h0,h1,hc0) — bottom frame
    th1=(h1,h2,hc1) — right frame
    th2=(h2,h3,hc1) — top frame
    th3=(h3,h0,hc0) — left frame
    Hole: triangular gap whose boundary is hc0-h1-hc1 (each edge n=1).

IS_VISITED context: ts0 carries the selection flag. With 3 selected triangles the
  algorithm marks s0, s1, s2, sc as "selection boundary" vertices to constrain fill.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me640",
    title="holeFilling::fillSmallBoundaries SELECTION_PRESENT: IS_VISITED triangles mark vertices, constraining fill to unselected region (Branch 1)",
    defect_class="boundary_hole",
)

# === Selected patch (3-triangle fan; IS_VISITED in MeshFix) ===
s0 = m.vertex(0.0, 0.0, 0.0)   # 0
s1 = m.vertex(2.0, 0.0, 0.0)   # 1
s2 = m.vertex(1.0, 2.0, 0.0)   # 2
sc = m.vertex(1.0, 0.7, 0.0)   # 3 — inner vertex of selected fan

# Fan triangles (selected — IS_VISITED).
ts0 = m.triangle(s0, s1, sc)   # 0
ts1 = m.triangle(s1, s2, sc)   # 1
ts2 = m.triangle(s2, s0, sc)   # 2

# Interior edges of selected fan (n=2 — shared by two fan triangles).
m.assert_edge_shared(s0, sc, 2)   # shared by ts0 and ts2
m.assert_edge_shared(s1, sc, 2)   # shared by ts0 and ts1
m.assert_edge_shared(s2, sc, 2)   # shared by ts1 and ts2

# === Hole region (unselected — candidate for fillSmallBoundaries) ===
h0 = m.vertex(5.0, 0.0, 0.0)   # 4
h1 = m.vertex(7.0, 0.0, 0.0)   # 5
h2 = m.vertex(8.0, 2.0, 0.0)   # 6
h3 = m.vertex(4.0, 2.0, 0.0)   # 7
# Hole boundary vertices (inner triangle of the hole).
hc0 = m.vertex(6.0, 0.5, 0.0)  # 8 — hole corner bottom
hc1 = m.vertex(7.0, 1.5, 0.0)  # 9 — hole corner right
hc2 = m.vertex(5.0, 1.5, 0.0)  # 10 — hole corner left

# Frame triangles surrounding the triangular hole (unselected).
th0 = m.triangle(h0, h1, hc0)    # 3 — bottom frame
th1 = m.triangle(h1, h2, hc1)    # 4 — right frame
th2 = m.triangle(h2, h3, hc2)    # 5 — top frame
th3 = m.triangle(h3, h0, hc2)    # 6 — left frame
th4 = m.triangle(h0, hc0, hc2)   # 7 — lower-left bridge
th5 = m.triangle(hc0, h1, hc1)   # 8 — lower-right bridge (creates hole edge hc0-hc1)
th6 = m.triangle(hc1, h2, hc2)   # 9 — upper-right bridge (creates hole edge hc1-hc2)

# Triangular hole boundary: hc0-hc1-hc2; each hole edge borders exactly 1 triangle.
m.assert_hole_boundary([hc0, hc1, hc2])

m.assert_edge_shared(hc0, hc1, 1)   # n=1: hole bottom-right edge (only in th5)
m.assert_edge_shared(hc1, hc2, 1)   # n=1: hole top edge (only in th6)
m.assert_edge_shared(hc0, hc2, 1)   # n=1: hole left edge (only in th4)
