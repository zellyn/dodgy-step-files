"""Me1171 — fill_edge_map non_manifold_detection: three polygons sharing one
  directed edge → nb_edges > 2 → edge flagged non-manifold (Branch 2).

CGAL PMP `PMP.Polygon_soup_orienter.fill_edge_map` Branch 2 (*non_manifold_detection*)
  @ line 201:
  'if (nb_edges > 2) {' —
  After filling the edge map, fill_edge_map counts incoming+outgoing edges at
  each directed edge. If the count exceeds 2 (i.e. more than one polygon claims
  the same directed edge or the reverse), the edge is flagged as non-manifold.
  Branch 2 fires when this threshold is exceeded.

Defect pattern: three triangles all sharing the directed edge v0→v1. In a
  correct manifold polygon soup, each undirected edge appears in at most two
  polygons (once in each direction). Here, three polygons all have vertex pair
  (v0,v1) as a directed edge — so edges[0][1] contains polygon ids 0, 1, 2.
  nb_edges = 3 > 2, so Branch 2 fires and the edge is marked non-manifold.

Geometry:
  v0=(0,0,0), v1=(1,0,0): the shared base edge
  v2=(0.5,1,0), v3=(0.5,-1,0), v4=(0.5,0.5,0): three apex vertices
  t0=(v0,v1,v2), t1=(v0,v1,v3), t2=(v0,v1,v4)  — three polys sharing v0→v1
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1171",
    title="fill_edge_map non_manifold_detection: three polygons share directed edge v0→v1; nb_edges=3 > 2 fires Branch 2",
    defect_class="non_manifold_edge",
)

# Two base vertices + three apex vertices
v0 = m.vertex(0.0,   0.0,   0.0)   # 0 — shared edge start
v1 = m.vertex(1.0,   0.0,   0.0)   # 1 — shared edge end
v2 = m.vertex(0.5,   1.0,   0.0)   # 2 — apex above
v3 = m.vertex(0.5,  -1.0,   0.0)   # 3 — apex below
v4 = m.vertex(0.5,   0.5,   0.0)   # 4 — apex middle

# Three triangles all claiming the same directed edge v0→v1
t0 = m.triangle(v0, v1, v2)   # 0: above
t1 = m.triangle(v0, v1, v3)   # 1: below
t2 = m.triangle(v0, v1, v4)   # 2: middle

# Edge v0-v1 shared by all three triangles = non-manifold (n=3)
m.assert_edge_shared(v0, v1, 3)

# Other edges are each owned by exactly one triangle
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# V=5, E=7, F=3, chi=1
m.assert_euler_characteristic(5, 7, 3, 1)
