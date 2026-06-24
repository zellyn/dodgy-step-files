"""Me650 — Basic_TMesh.removeEdges list_head_initialization: traversal starts at E.head() (Branch 1).

MeshFix `Basic_TMesh.removeEdges` Branch 1 (*list_head_initialization*) @ line 579:
  'n = E.head();' — the function initializes the edge-list traversal pointer
  by calling E.head(), the first element of the doubly-linked edge list. This
  branch fires for any non-empty mesh that has at least one edge, which makes
  the list head valid and starts the scan for orphaned edges (edges whose
  vertex pointer is NULL).

Defect pattern: a minimal well-formed 3-triangle fan sharing a common hub vertex.
  All edges are valid (no null vertices). E.head() returns the first edge in the
  list, initialising n and entering the traversal loop. The edge count is 6 (3
  interior + 3 boundary), providing a substantive list for the traversal to walk.

Geometry:
  v0 = (0, 0, 0)   — hub vertex (shared by all triangles)
  v1 = (2, 0, 0)
  v2 = (1, 2, 0)
  v3 = (-1, 2, 0)
  t0 = (v0, v1, v2)
  t1 = (v0, v2, v3)
  t2 = (v0, v1, v3) — closes the fan
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me650",
    title="removeEdges list_head_initialization: non-empty mesh; E.head() initialises traversal pointer at first edge (Branch 1)",
    defect_class="orphaned_edge",
)

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — hub (shared by all 3 triangles)
v1 = m.vertex(2.0,  0.0, 0.0)   # 1
v2 = m.vertex(1.0,  2.0, 0.0)   # 2
v3 = m.vertex(-1.0, 2.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)     # 0
t1 = m.triangle(v0, v2, v3)     # 1
t2 = m.triangle(v0, v3, v1)     # 2 — closes the fan

# Hub vertex v0 is shared by all three triangles; each edge from v0 is n=2.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)

# Outer rim edges are each shared by 1 triangle.
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v1, 1)

# Euler: V=4, E=6, F=3, chi=1 (topological disk).
m.assert_euler_characteristic(4, 6, 3, 1)
