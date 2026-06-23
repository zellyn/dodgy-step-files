"""Me373 — isSelectionSimple_mesh_boundary_in_selection: selection touches mesh boundary, top.numels()>0, return 0 (Branch 4).

MeshFix `Basic_TMesh.isSelectionSimple` Branch 4 (*mesh_boundary_in_selection*) @ line 1017:
  `if (top.numels()) { ...; return 0; }` — after the BFS finishes, the
  `top` list (edges at the selection boundary that are not shared with
  another selected triangle) is non-empty. This means at least one edge of
  the selected region touches the mesh boundary (a real boundary edge, not
  just a selection boundary). `isSelectionSimple` returns 0 (false).

The fixture models a selected region that is a connected strip of 2 adjacent
triangles. One outer edge is a true mesh boundary edge (n=1), so it gets
added to `top` during BFS. After BFS, top.numels() > 0 → Branch 4 fires.

The key distinction from Branch 3 (which fires per-edge per-triangle during
BFS inner loop) is that Branch 4 is the post-BFS check on the accumulated
`top` list. The fixture has a connected 2-triangle strip with open mesh
boundary edges, so `top` is populated and Branch 4 terminates the function.

Geometry: two adjacent triangles sharing one interior edge. Three outer
boundary edges exist (n=1), which are appended to `top` during BFS.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me373",
    title="isSelectionSimple_mesh_boundary_in_selection: 2-triangle connected strip with open boundary edges, top.numels()>0 → return 0 (Branch 4)",
    defect_class="selection_touches_boundary",
)

# Two adjacent triangles sharing edge (v1, v2).
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1
v2 = m.vertex(1.0, 1.0, 0.0)  # 2
v3 = m.vertex(3.0, 1.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)  # 0: left triangle
t1 = m.triangle(v1, v3, v2)  # 1: right triangle

# Shared interior edge — both triangles selected, so this is a selection
# interior edge (NOT added to top). The two triangles are in the same
# selection; BFS from t0 discovers t1 via Branch 2 (IS_VISITED neighbor).
m.assert_edge_shared(v1, v2, 2)

# Outer boundary edges (n=1): each added to `top` during BFS → Branch 4 fires.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
