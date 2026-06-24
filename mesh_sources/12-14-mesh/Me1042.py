"""Me1042 — stitch_borders per-component-boundary-segregation: border_edges_per_cc append segregates boundary per CC.

CGAL PMP `PMP.stitch_borders (internal dispatcher)` Branch 3 (*per-component-boundary-segregation*) @ line 443:
  'border_edges_per_cc[cc_ids[face(h,mesh)]].push_back(h);'
  In per_cc mode, after confirming a halfedge is on the border, the dispatcher
  appends it to the sub-list for its connected component (keyed by cc_ids lookup).
  Branch 3 fires once for each boundary halfedge when per_cc=true, populating
  separate boundary lists per component.

Defect pattern: three disconnected triangular patches (A, B, C), each open and
  with distinct boundary halfedges. When stitch_borders runs with per_cc=true,
  each boundary halfedge is appended to its component's slot in border_edges_per_cc,
  producing three separate lists — one for each component.

Geometry:
  Component A: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0)  → t0=(v0,v1,v2)
  Component B: v3=(3,0,0), v4=(4,0,0), v5=(3.5,1,0)  → t1=(v3,v4,v5)
  Component C: v6=(6,0,0), v7=(7,0,0), v8=(6.5,1,0)  → t2=(v6,v7,v8)
  Three isolated triangles (no shared edges), each a separate CC.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1042",
    title="stitch_borders per-component-boundary-segregation: border_edges_per_cc appends boundary halfedge to per-CC slot; three disconnected open triangles",
    defect_class="boundary_gap_thin",
)

# Component A
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Component B
v3 = m.vertex(3.0, 0.0, 0.0)   # 3
v4 = m.vertex(4.0, 0.0, 0.0)   # 4
v5 = m.vertex(3.5, 1.0, 0.0)   # 5

# Component C
v6 = m.vertex(6.0, 0.0, 0.0)   # 6
v7 = m.vertex(7.0, 0.0, 0.0)   # 7
v8 = m.vertex(6.5, 1.0, 0.0)   # 8

t0 = m.triangle(v0, v1, v2)    # 0 — Component A
t1 = m.triangle(v3, v4, v5)    # 1 — Component B
t2 = m.triangle(v6, v7, v8)    # 2 — Component C

# All edges are boundary (n=1) — each triangle is its own CC
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)

m.assert_edge_shared(v6, v7, 1)
m.assert_edge_shared(v7, v8, 1)
m.assert_edge_shared(v6, v8, 1)

# Components are disconnected
m.assert_triangle_not_reachable_from(t1, t0)
m.assert_triangle_not_reachable_from(t2, t0)

# Euler: V=9, E=9, F=3, chi=3 (three isolated open disks)
m.assert_euler_characteristic(9, 9, 3, 3)
