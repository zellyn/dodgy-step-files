"""Me371 — isSelectionSimple_visited_neighbor: BFS marks adjacent selected triangle (Branch 2).

MeshFix `Basic_TMesh.isSelectionSimple` Branch 2 (*visited_neighbor*) @ line 1008:
  `if (IS_VISITED(ta) && !IS_VISITED2(ta)) { MARK_VISIT2(ta); nv++; ... }` —
  during the BFS over selected triangles, a selected neighbor `ta` that has
  not yet been visited2 is discovered: it is marked IS_VISITED2 and added to
  the BFS queue (nv incremented). This is the core expansion step of the
  BFS connectivity check.

The fixture models a connected 3-triangle fan all in the selection. BFS
starts at the first triangle; the second and third are each discovered via
Branch 2's neighbor test. After BFS, nv == 3 == s->numels() → selection is
connected; no boundary edges crossing a null neighbor → passes Branch 4
and Branch 7; returns true.

Geometry: three triangles sharing a common hub vertex v0 — a fan.
The outer edges are boundary (n=1); the inner spoke edges (v0,v1),
(v0,v2), (v0,v3) are shared between adjacent fan triangles (n=2).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me371",
    title="isSelectionSimple_visited_neighbor: 3-triangle fan selection, BFS discovers each via IS_VISITED+!IS_VISITED2 (Branch 2)",
    defect_class="selection_simple",
)

# Hub vertex.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0: hub

# Rim vertices.
v1 = m.vertex(1.0,  0.0, 0.0)  # 1
v2 = m.vertex(0.5,  1.0, 0.0)  # 2
v3 = m.vertex(-0.5, 1.0, 0.0)  # 3
v4 = m.vertex(-1.0, 0.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v2)  # 0: right-sector
t1 = m.triangle(v0, v2, v3)  # 1: center-sector
t2 = m.triangle(v0, v3, v4)  # 2: left-sector

# Inner spoke edges shared by adjacent fan triangles (interior, n=2).
m.assert_edge_shared(v0, v2, 2)  # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)  # shared by t1 and t2

# Outer and end-spoke edges are boundary (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v4, 1)

# Euler: V=5, E=7, F=3, chi=1 (topological disk — open fan).
m.assert_euler_characteristic(5, 7, 3, 1)
