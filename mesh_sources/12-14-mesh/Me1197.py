"""Me1197 — keep_largest_connected_components component_size_criterion:
  component with fewer faces than threshold is marked for removal (Branch 2).

CGAL PMP `PMP.keep_largest_connected_components` Branch 2 (*component_size_criterion*)
  @ line 410:
  'if (face_size_pmap[cc] < threshold) components_to_remove.insert(cc)' —
  After sorting components by face count, Branch 2 compares each component's
  size (number of faces) against the computed threshold. Components with fewer
  faces than the threshold are scheduled for removal (i.e. are not among the
  largest N). Branch 2 is the core keep/discard decision loop.

Defect pattern: a mesh with three connected components of different sizes:
  Large: 4-triangle fan (component A, largest)
  Medium: 2-triangle strip (component B, medium)
  Small: 1-triangle isolated (component C, smallest)
  When keep_largest_connected_components(mesh, 1) is called, component C
  (size=1) and component B (size=2) fall below the threshold; Branch 2 fires
  twice marking them for removal.

Geometry: three separate triangulated patches at different positions.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1197",
    title="keep_largest_connected_components component_size_criterion: three components (4-tri, 2-tri, 1-tri); small/medium components marked for removal via face_size_pmap < threshold (Branch 2)",
    defect_class="self_intersection",
)

# Component A: 4-triangle fan (largest) — fan around center v0
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — center
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3
v4 = m.vertex(0.0, -1.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v2)    # 0: fan Q1
t1 = m.triangle(v0, v2, v3)    # 1: fan Q2
t2 = m.triangle(v0, v3, v4)    # 2: fan Q3
t3 = m.triangle(v0, v4, v1)    # 3: fan Q4

# Component B: 2-triangle strip (medium) — far from A
v5 = m.vertex(10.0, 0.0, 0.0)  # 5
v6 = m.vertex(11.0, 0.0, 0.0)  # 6
v7 = m.vertex(10.5, 1.0, 0.0)  # 7
v8 = m.vertex(11.5, 1.0, 0.0)  # 8

t4 = m.triangle(v5, v6, v7)    # 4: strip left
t5 = m.triangle(v6, v8, v7)    # 5: strip right

# Component C: 1-triangle (smallest) — further away
v9  = m.vertex(20.0, 0.0, 0.0)  # 9
v10 = m.vertex(21.0, 0.0, 0.0)  # 10
v11 = m.vertex(20.5, 1.0, 0.0)  # 11

t6 = m.triangle(v9, v10, v11)   # 6: isolated triangle

# Components are disconnected
m.assert_triangle_not_reachable_from(t4, t0)   # B unreachable from A
m.assert_triangle_not_reachable_from(t6, t0)   # C unreachable from A
m.assert_triangle_not_reachable_from(t6, t4)   # C unreachable from B

# Component A interior edges (fan center)
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v0, v4, 2)
# Component A boundary
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# Component B edges
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v5, v7, 1)
m.assert_edge_shared(v6, v7, 2)
m.assert_edge_shared(v6, v8, 1)
m.assert_edge_shared(v7, v8, 1)

# Component C edges
m.assert_edge_shared(v9, v10, 1)
m.assert_edge_shared(v9, v11, 1)
m.assert_edge_shared(v10, v11, 1)

# V=12, E=16, F=7, chi=3 (three separate discs)
m.assert_euler_characteristic(12, 16, 7, 3)
