"""Me370 — isSelectionSimple_empty_selection: empty selection returns false (Branch 1).

MeshFix `Basic_TMesh.isSelectionSimple` Branch 1 (*empty_selection*) @ line 996:
  `if (!s->numels()) return 0;` — the selection list is empty (no triangles
  are marked as selected). An empty region is not topologically simple;
  the function immediately returns false (0).

The fixture models a valid 2-triangle strip mesh where the selection set
is empty: no triangle is marked IS_VISITED. The BFS never starts.
`s->numels() == 0` → Branch 1 fires.

Geometry: two adjacent triangles sharing edge (v1, v2) — a simple manifold
strip. All edges are boundary except the shared interior edge (n=2). The
selection is empty (no IS_VISITED marks set before the call). The Euler
characteristic confirms the mesh is a topological disk.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me370",
    title="isSelectionSimple_empty_selection: no triangles marked selected, numels==0, return 0 (Branch 1)",
    defect_class="selection_empty",
)

# Two adjacent triangles forming a quadrilateral strip.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 1.0, 0.0)  # 2
v3 = m.vertex(0.0, 1.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)  # 0: lower-right triangle
t1 = m.triangle(v0, v2, v3)  # 1: upper-left triangle

# Shared interior edge (v0, v2) is incident on both triangles.
m.assert_edge_shared(v0, v2, 2)

# All other edges are boundary (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (topological disk — open strip).
m.assert_euler_characteristic(4, 5, 2, 1)
