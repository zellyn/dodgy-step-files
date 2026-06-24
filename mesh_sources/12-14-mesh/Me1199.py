"""Me1199 — keep_largest_connected_components output_iterator_presence:
  output_iterator records removed component IDs when provided (Branch 4).

CGAL PMP `PMP.keep_largest_connected_components` Branch 4 (*output_iterator_presence*)
  @ line 421:
  'if (out != emptyset_iterator()) *out++ = cc_id;' —
  When the caller provides an output iterator (not the default emptyset_iterator),
  Branch 4 fires for each removed component, writing its ID into the iterator.
  This allows the caller to track which components were deleted.

Defect pattern: a mesh with 2 connected components where the smaller is removed
  and its component ID is captured via an output iterator. The large component
  (3 triangles) is kept; the small component (1 triangle) is removed.
  Branch 4 fires for the small component, writing its ID to the output iterator.

Geometry:
  Component A (large, kept): 3-triangle fan around v0
  Component B (small, removed): 1-triangle far away
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1199",
    title="keep_largest_connected_components output_iterator_presence: output_iterator records removed component ID; 2-component mesh, small component removed and its ID captured (Branch 4)",
    defect_class="self_intersection",
)

# Component A (large, kept): 3-triangle fan
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — center
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v2, v3)    # 1
t2 = m.triangle(v0, v3, v1)    # 2

# Component B (small, removed): 1-triangle
v4 = m.vertex(10.0, 0.0, 0.0)  # 4
v5 = m.vertex(11.0, 0.0, 0.0)  # 5
v6 = m.vertex(10.5, 1.0, 0.0)  # 6

t3 = m.triangle(v4, v5, v6)    # 3: will be removed

# Components are disconnected
m.assert_triangle_not_reachable_from(t3, t0)

# Component B (small) is the isolated triangle to be removed
m.assert_isolated_vertex(v4)    # v4 unreachable from component A
# (using assert_isolated_vertex to encode that v4 is in a component not reachable from A)

# Component A interior edges (fan)
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
# Component A boundary
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v1, v3, 1)

# Component B edges
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v4, v6, 1)
m.assert_edge_shared(v5, v6, 1)

# V=7, E=9, F=4, chi=2 (two separate discs)
m.assert_euler_characteristic(7, 9, 4, 2)
