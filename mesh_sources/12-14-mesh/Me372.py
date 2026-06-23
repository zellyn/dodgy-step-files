"""Me372 — isSelectionSimple_boundary_neighbor: NULL neighbor at mesh boundary, edge added to boundary list (Branch 3).

MeshFix `Basic_TMesh.isSelectionSimple` Branch 3 (*boundary_neighbor*) @ line 1009:
  `else { if (ta == NULL) break; top.appendHead(e); }` — when walking the
  three neighbors of a selected triangle, a neighbor is either NULL (mesh
  boundary edge) or an unselected triangle. If NULL, the loop breaks (null
  neighbor means the selection touches the mesh boundary). Otherwise the
  shared edge is appended to the boundary topology list `top`.

The fixture models a single selected triangle at the mesh boundary: all
three of its edges are boundary (n=1), so all neighbor slots are NULL.
When the BFS processes this triangle, Branch 3 fires three times (once per
edge). The `break` path fires on the first NULL neighbor; this triangle's
outer loop terminates early, and eventually `top.numels() > 0` (from the
appended edge before the break) causes Branch 4 to return 0.

Geometry: a single isolated triangle — all three edges are boundary (n=1),
all three neighbor triangles are NULL.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me372",
    title="isSelectionSimple_boundary_neighbor: single selected triangle at mesh boundary, NULL neighbor → break (Branch 3)",
    defect_class="selection_touches_boundary",
)

# Single triangle, all edges boundary.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.5, 1.0, 0.0)  # 2

t0 = m.triangle(v0, v1, v2)  # 0: the single selected triangle

# All edges are boundary (n=1): all three neighbors are NULL.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Euler: V=3, E=3, F=1, chi=1 (single open triangle — disk chi=1).
m.assert_euler_characteristic(3, 3, 1, 1)
