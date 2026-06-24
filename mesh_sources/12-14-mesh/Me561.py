"""Me561 — loopSubdivision selection_constrained_vs_global: partial triangle selection drives edge marking.

Basic_TMesh.loopSubdivision Branch 2 (*selection_constrained_vs_global*) @ line 108:
  'if(is_selection) { if(!IS_VISITED(t)) continue; }'
  — When loopSubdivision is called with is_selection=true, only triangles marked
  IS_VISITED (pre-selected) are processed. Unvisited triangles are skipped entirely.
  This branch fires when the mesh has a mix of selected (IS_VISITED) and unselected
  triangles, so some edges are marked for subdivision while others are not.

Fixture: 5 triangles arranged as two connected groups — 3 triangles form the
  selected sub-region (the "visited" patch) and 2 triangles are unselected. The
  interface edge between groups is shared and would appear in both groups' edge
  lists, but only the visited group's half triggers the subdivision mark.

Geometric signature:
  The "selected" patch: t0, t1, t2 share edges among themselves.
  The "unselected" patch: t3, t4 share the boundary edge with t2 but are skipped.
  The bridge edge (v3, v4) connects the two regions: n=2 (shared by t2 and t3).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me561",
    title="loopSubdivision selection_constrained_vs_global: t0+t1+t2 form selected patch; t3+t4 unselected; bridge edge (v3,v4) n=2 (Branch 2)",
    defect_class="loop_subdivision",
)

# Selected patch vertices.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 1.5, 0.0)  # 2
v3 = m.vertex(3.0, 1.5, 0.0)  # 3

# Unselected patch vertices.
v4 = m.vertex(4.0, 0.0, 0.0)  # 4
v5 = m.vertex(5.0, 1.5, 0.0)  # 5

# Selected triangles (the "visited" region).
t0 = m.triangle(v0, v1, v2)   # 0 — selected
t1 = m.triangle(v1, v3, v2)   # 1 — selected; shares (v1,v2) with t0... wait (v2,v3) with t2
# Actually: t1 shares (v1,v3) with t2 below, so edges of t1: (1,3),(3,2),(2,1)
# t0 edges: (0,1),(1,2),(0,2); t1 edges: (1,3),(2,3),(1,2); share (1,2) ✓
t2 = m.triangle(v1, v3, v4)   # 2 — selected; shares (v1,v3) with t1; bridges to unselected via (v3,v4)
# t2 edges: (1,3),(3,4),(1,4)

# Unselected triangles.
t3 = m.triangle(v3, v4, v5)   # 3 — unselected; shares (v3,v4) with t2
t4 = m.triangle(v1, v4, v5)   # 4 — unselected; shares (v1,v4) with t2 and (v4,v5) with t3

# Bridge edge between selected and unselected regions — interior, n=2.
m.assert_edge_shared(v3, v4, 2)  # shared by t2 (selected) and t3 (unselected)
m.assert_edge_shared(v1, v4, 2)  # shared by t2 (selected) and t4 (unselected)

# Interior edge within selected patch.
m.assert_edge_shared(v1, v2, 2)  # shared by t0 and t1
m.assert_edge_shared(v1, v3, 2)  # shared by t1 and t2

# Interior edge within unselected patch.
m.assert_edge_shared(v4, v5, 2)  # shared by t3 and t4

# Boundary edges (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v1, v5, 1)

# Euler characteristic: V=6, E=10, F=5, chi=1 (open disk).
m.assert_euler_characteristic(6, 10, 5, 1)
