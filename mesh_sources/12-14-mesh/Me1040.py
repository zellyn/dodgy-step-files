"""Me1040 — stitch_borders border-component-independence: per_cc routing dispatches per-component vs global border collection.

CGAL PMP `PMP.stitch_borders (internal dispatcher)` Branch 1 (*border-component-independence*) @ line 426:
  'if (per_cc) { ... border_edges_per_cc ... } else { border_edges ... }'
  When per_cc=true, the dispatcher routes to per-component border-edge collection
  rather than a single global pass. This branch fires when the mesh has multiple
  connected components so that each component's boundary halfedges are collected
  independently.

Defect pattern: two disconnected triangular patches, each with an open boundary.
  Component A (triangles 0-1) has an open boundary on the right side.
  Component B (triangles 2-3) has an open boundary on the right side.
  The two patches are not connected topologically; each forms its own connected
  component. per_cc=true routes the dispatcher to enumerate boundary halfedges
  separately per connected component rather than globally.

Geometry:
  Component A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0)
    t0=(v0,v1,v2), t1=(v1,v3,v2) sharing interior edge (v1,v2)
    open boundary: v0-v1, v0-v2, v1-v3, v2-v3
  Component B: v4=(3,0,0), v5=(4,0,0), v6=(3.5,1,0), v7=(4.5,1,0)
    t2=(v4,v5,v6), t3=(v5,v7,v6) sharing interior edge (v5,v6)
    open boundary: v4-v5, v4-v6, v5-v7, v6-v7
  Components are disconnected: no shared edge or vertex.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1040",
    title="stitch_borders border-component-independence: per_cc routing dispatches per-component vs global; two disconnected open patches",
    defect_class="boundary_gap_thin",
)

# Component A — left patch
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3

# Component B — right patch (disconnected)
v4 = m.vertex(3.0, 0.0, 0.0)   # 4
v5 = m.vertex(4.0, 0.0, 0.0)   # 5
v6 = m.vertex(3.5, 1.0, 0.0)   # 6
v7 = m.vertex(4.5, 1.0, 0.0)   # 7

# Component A triangles
t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v1, v3, v2)    # 1 — shares (v1,v2) with t0

# Component B triangles
t2 = m.triangle(v4, v5, v6)    # 2
t3 = m.triangle(v5, v7, v6)    # 3 — shares (v5,v6) with t2

# Interior edges (shared by 2 triangles)
m.assert_edge_shared(v1, v2, 2)  # Component A interior
m.assert_edge_shared(v5, v6, 2)  # Component B interior

# Open boundary edges of Component A (n=1)
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Open boundary edges of Component B (n=1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v4, v6, 1)
m.assert_edge_shared(v5, v7, 1)
m.assert_edge_shared(v6, v7, 1)

# Components are disconnected: t0 and t2 are not reachable from each other
m.assert_triangle_not_reachable_from(t2, t0)

# Euler per component: each 2-triangle strip is an open disk chi=1
# Combined: V=8, E=10, F=4, chi=2 (two disks)
m.assert_euler_characteristic(8, 10, 4, 2)
