"""Me1152 — keep_connected_components by_id: CC-id guard on halfedge(v, pmesh).

CGAL PMP `PMP.keep_connected_components` Branch 1 (*by_id*) @ line 308:
  'halfedge_descriptor h = halfedge(v, pmesh)' — when components are
  selected by integer CC-id the function iterates vertices, obtains a
  representative halfedge for each vertex and checks whether its face belongs
  to a kept component. This branch fires whenever the by-id overload is used.

Defect pattern: a mesh with two topologically disconnected triangle components.
  Component A (faces 0-1) is a two-triangle fan and Component B (face 2) is an
  isolated triangle far away. When keep_connected_components is called with the
  id of component A, the halfedge(v, pmesh) guard fires for every vertex in
  component B, identifies them as belonging to a discarded CC, and removes them.

Geometry:
  Component A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0,1,0)
    t0=(v0,v1,v2), t1=(v0,v2,v3) sharing edge (v0,v2).
  Component B: v4=(50,0,0), v5=(51,0,0), v6=(50.5,1,0)
    t2=(v4,v5,v6) — isolated, no shared edges with A.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1152",
    title="keep_connected_components by_id: halfedge(v,pmesh) guard fires; two-component mesh selected by CC id",
    defect_class="disconnected_components",
)

# Component A: two-triangle fan sharing edge (v0,v2).
v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — shared apex
v3 = m.vertex(0.0, 1.0, 0.0)  # 3

t0 = m.triangle(v0, v1, v2)   # 0: component A left
t1 = m.triangle(v0, v2, v3)   # 1: component A right

# Component B: isolated triangle far from A.
v4 = m.vertex(50.0, 0.0, 0.0)  # 4
v5 = m.vertex(51.0, 0.0, 0.0)  # 5
v6 = m.vertex(50.5, 1.0, 0.0)  # 6

t2 = m.triangle(v4, v5, v6)    # 2: component B — isolated

# Interior edge of component A shared by t0 and t1.
m.assert_edge_shared(v0, v2, 2)

# Component B is unreachable from component A.
m.assert_triangle_not_reachable_from(t2, t0)

# Euler: V=7, E=9, F=3, chi=1 (two open-disk components: 1+1=2... wait)
# Two disconnected open disks: component A (V=4,E=5,F=2,chi=1) + component B (V=3,E=3,F=1,chi=1)
# Combined: V=7, E=8, F=3, chi=7-8+3=2.
m.assert_euler_characteristic(7, 8, 3, 2)
