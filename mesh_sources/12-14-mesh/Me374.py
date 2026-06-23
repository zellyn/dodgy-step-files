"""Me374 — isSelectionSimple_disconnected_selection: nv != s->numels(), return 0 (Branch 5).

MeshFix `Basic_TMesh.isSelectionSimple` Branch 5 (*disconnected_selection*) @ line 1018:
  `if (nv != s->numels()) { ...; return 0; }` — after the BFS from the first
  selected triangle, the count of visited triangles `nv` does not match the
  total count of selected triangles `s->numels()`. The selection is not
  connected (two or more disconnected groups are both selected), so
  `isSelectionSimple` returns 0 (false).

This is distinct from Branch 4: here the selection is an interior region
(all boundary edges are between selected and unselected triangles, not
mesh boundary) but the selected set has two disconnected components.

Geometry: a 5-triangle mesh where:
  - Patch A: t0=(v0,v1,v2) — isolated selection patch in the interior
  - Patch B: t1=(v3,v4,v5) — second isolated selection patch
  - Neither patch shares an edge with the other.

Both patches are in the "selected" set (IS_VISITED). BFS from t0 only
reaches t0 (nv=1), but s->numels()=2 → Branch 5 fires → return 0.

The mesh has no shared edges between t0 and t1 (all edges n=1), confirming
the disconnected topology.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me374",
    title="isSelectionSimple_disconnected_selection: two disjoint selected patches, BFS visits 1 but numels==2 → return 0 (Branch 5)",
    defect_class="selection_disconnected",
)

# Patch A — first selected group.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.5, 1.0, 0.0)  # 2

# Patch B — second selected group, far away.
v3 = m.vertex(8.0, 0.0, 0.0)  # 3
v4 = m.vertex(9.0, 0.0, 0.0)  # 4
v5 = m.vertex(8.5, 1.0, 0.0)  # 5

t0 = m.triangle(v0, v1, v2)  # 0: Patch A
t1 = m.triangle(v3, v4, v5)  # 1: Patch B

# All edges in both patches are boundary (n=1): fully disconnected.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

# t1 is not reachable from t0 — confirming disconnected selection.
m.assert_triangle_not_reachable_from(target=t1, source=t0)

# Euler: V=6, E=6, F=2, chi=2 (two disjoint open triangles).
m.assert_euler_characteristic(6, 6, 2, 2)
