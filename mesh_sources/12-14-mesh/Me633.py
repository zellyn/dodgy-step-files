"""Me633 — Basic_TMesh.growSelection branch 4: vertex_neighbor_selection.

MeshFix `Basic_TMesh.growSelection` Branch 4 (*vertex_neighbor_selection*)
@ line 705:
  'if (IS_VISITED(v1) || IS_VISITED(v2) || IS_VISITED(v3)) { MARK_VISIT(t); ns++; }'
  — in the second scan, after !IS_VISITED(t) is confirmed (Branch 3),
  the algorithm checks whether ANY of the triangle's three vertices carry
  the VISITED mark laid down in the first pass. If at least one does, the
  triangle is selected (MARK_VISIT(t)) and the selection count is incremented.
  Branch 4 fires when a previously-unselected triangle shares at least one
  vertex with the selected region.

Defect pattern: a 5-triangle mesh where the seed selection t0 marks v0, v1, v2
  in the first pass. Triangle t1 shares exactly ONE marked vertex (v2) with t0
  via a vertex-only touch (no shared edge), and is therefore selected by Branch 4.
  Triangle t2 shares edge (v0,v1) with t0 (both v0 and v1 are marked), also
  selected by Branch 4. Triangles t3 and t4 share no marked vertex and are
  NOT selected.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0) — t0 vertices (selected seed)
  v3=(1,3,0) — apex of t1; t1 shares ONLY v2=(1,2,0) with t0
  v4=(3,1,0) — apex shared by t1 and t2; t1=(v2,v3,v4) touches t0 at v2 only
  v5=(-1,1,0) — apex of a non-neighbor far triangle t3
  v6=(3,3,0) — apex of t4; no shared vertex with t0

  t0=(v0,v1,v2) selected seed
  t1=(v2,v3,v4) unselected; IS_VISITED(v2) → Branch 4 selects it
  t2=(v0,v1,v5) unselected; shares edge (v0,v1) → v0 AND v1 marked → Branch 4
  t3=(v3,v4,v6) unselected; v3,v4 not marked → Branch 4 check fails, not selected
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me633",
    title="growSelection vertex_neighbor_selection: IS_VISITED(v2) selects t1 (vertex-only touch); IS_VISITED(v0)||IS_VISITED(v1) selects t2 (shared edge); 4-triangle mesh (Branch 4)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — t0 corner; marked by first pass
v1 = m.vertex(2.0,  0.0, 0.0)  # 1 — t0 corner; marked by first pass
v2 = m.vertex(1.0,  2.0, 0.0)  # 2 — t0 apex; marked by first pass; shared with t1
v3 = m.vertex(1.0,  3.0, 0.0)  # 3 — t1 apex (not marked)
v4 = m.vertex(3.0,  1.0, 0.0)  # 4 — t1 outer corner (not marked)
v5 = m.vertex(-1.0, 1.0, 0.0)  # 5 — t2 apex (not marked)
v6 = m.vertex(3.0,  3.0, 0.0)  # 6 — t3 apex (not marked, not neighbor)

# Pre-selected seed.
t0 = m.triangle(v0, v1, v2)  # 0: selected; marks v0, v1, v2

# Branch 4 fires for t1: shares vertex v2 only (no shared edge with t0).
t1 = m.triangle(v2, v3, v4)  # 1: IS_VISITED(v2) → MARK_VISIT(t1); ns++

# Branch 4 fires for t2: shares edge (v0,v1) — both v0 and v1 are marked.
t2 = m.triangle(v0, v1, v5)  # 2: IS_VISITED(v0)||IS_VISITED(v1) → MARK_VISIT(t2)

# Branch 4 check fails for t3: no vertex from {v3,v4,v6} is marked.
t3 = m.triangle(v3, v4, v6)  # 3: none of v3,v4,v6 marked → Branch 3 only, not selected

# Edge (v0,v1) is shared by t0 and t2 — demonstrates shared-edge propagation.
m.assert_edge_shared(v0, v1, 2)  # t0 and t2

# Edge (v2,v3) is shared by t1 only (boundary).
m.assert_edge_shared(v2, v3, 1)
# Edge (v2,v4) is shared by t1 only (boundary).
m.assert_edge_shared(v2, v4, 1)
# t1 and t3 share edge (v3,v4).
m.assert_edge_shared(v3, v4, 2)  # t1 and t3

# v2 is only shared between t0 and t1 as a single vertex (no shared edge t0-t1).
m.assert_edge_shared(v0, v2, 1)  # t0 boundary
m.assert_edge_shared(v1, v2, 1)  # t0 boundary

# Boundary edges of t2.
m.assert_edge_shared(v0, v5, 1)
m.assert_edge_shared(v1, v5, 1)

# Boundary edges of t3.
m.assert_edge_shared(v4, v6, 1)
m.assert_edge_shared(v3, v6, 1)

# Euler: V=7, E=10, F=4, chi=1 (open disk).
m.assert_euler_characteristic(7, 10, 4, 1)
