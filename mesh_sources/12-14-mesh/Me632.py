"""Me632 — Basic_TMesh.growSelection branch 3: unselected_triangle_neighbor_check.

MeshFix `Basic_TMesh.growSelection` Branch 3 (*unselected_triangle_neighbor_check*)
@ line 702:
  'if (!IS_VISITED(t)) { if (IS_VISITED(v1) || IS_VISITED(v2) || IS_VISITED(v3)) … }'
  — the second scan iterates all triangles again; for unselected triangles
  (!IS_VISITED(t)) the algorithm checks whether any of the triangle's three
  vertices carry the VISITED mark that was laid down in the first pass.
  Branch 3 fires for every triangle that is NOT selected.

Defect pattern: a 3-triangle strip (t0 selected, t1 and t2 unselected) where:
  - t0=(v0,v1,v2) is the pre-selected seed; growSelection first marks v0,v1,v2.
  - t1=(v1,v2,v3) is unselected and shares edge (v1,v2) with t0, so both v1
    and v2 are already marked → !IS_VISITED(t1) is true → Branch 3 fires.
  - t2=(v3,v4,v5) is unselected and shares no marked vertex with t0; it still
    reaches Branch 3 (!IS_VISITED(t2) = true) but the IS_VISITED check for
    its vertices returns false.
  Together t1 and t2 both exercise Branch 3; t1 also exercises Branch 4
  (vertex_neighbor_selection), but this fixture's focus is Branch 3.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0) — t0 vertices (selected)
  v3=(1,1,0) — shared apex of t1; connects t0's edge to t1
  v4=(2,0,0), v5=(2,1,0) — t2 vertices (unselected, no shared mark)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me632",
    title="growSelection unselected_triangle_neighbor_check: !IS_VISITED(t1) and !IS_VISITED(t2) both enter Branch 3; 3-triangle strip with selected seed t0 (Branch 3)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — t0 corner
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — t0/t1 shared boundary
v2 = m.vertex(0.0, 1.0, 0.0)  # 2 — t0/t1 shared boundary
v3 = m.vertex(1.0, 1.0, 0.0)  # 3 — t1 apex
v4 = m.vertex(2.0, 0.0, 0.0)  # 4 — t2 corner (no shared marked vertex)
v5 = m.vertex(2.0, 1.0, 0.0)  # 5 — t2 apex

# Pre-selected triangle (seed).
t0 = m.triangle(v0, v1, v2)  # 0: selected; marks v0, v1, v2 in first pass

# Unselected triangle sharing edge (v1,v2) with t0 → Branch 3 fires; v1,v2 marked.
t1 = m.triangle(v1, v2, v3)  # 1: !IS_VISITED, shared edge → Branch 3 + 4

# Unselected triangle with no marked vertices → Branch 3 fires; check fails.
t2 = m.triangle(v3, v4, v5)  # 2: !IS_VISITED, no shared marked vertex → Branch 3 only

# Shared edge between t0 and t1 — the bridge for mark propagation.
m.assert_edge_shared(v1, v2, 2)  # t0 and t1; v1,v2 marked → triggers Branch 3 for t1

# t1 and t2 share vertex v3 only (no shared edge between them).
m.assert_edge_shared(v3, v4, 1)  # boundary: only t2 owns this edge
m.assert_edge_shared(v3, v5, 1)  # boundary: only t2 owns this edge

# Boundary edges (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v4, v5, 1)

# Euler: V=6, E=8, F=3, chi=1 (open strip).
m.assert_euler_characteristic(6, 8, 3, 1)
