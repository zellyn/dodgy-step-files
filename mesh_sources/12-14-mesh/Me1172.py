"""Me1172 — fill_edge_map non_manifold_visitor_callback: the non-manifold edge
  fires visitor.non_manifold_edge(i0, i1, nb_edges) callback (Branch 3).

CGAL PMP `PMP.Polygon_soup_orienter.fill_edge_map` Branch 3 (*non_manifold_visitor_callback*)
  @ line 209:
  'visitor.non_manifold_edge(i0, i1, nb_edges)' —
  After Branch 2 detects a non-manifold edge (nb_edges > 2), Branch 3 invokes
  the visitor callback with the edge endpoints and the polygon count. This lets
  the caller track which edges are non-manifold. Branch 3 fires immediately
  after Branch 2 for every detected non-manifold edge.

Defect pattern: four triangles sharing one undirected edge — two claim directed
  (v0→v1) and two claim directed (v1→v0). The fill_edge_map records all four
  polygons. At the non-manifold check step, the combined count for this edge
  exceeds 2, triggering both Branch 2 (detection) and Branch 3 (callback).
  Separate from Me1171 (which has three polys in one direction); here we have
  two polys per direction, still nb_edges=4 > 2.

Geometry:
  v0=(0,0,0), v1=(1,0,0): shared base edge
  v2=(0.5, 1,0), v3=(0.5,-1,0): CCW pair (t0,t1)
  v4=(0.5, 2,0), v5=(0.5,-2,0): CW pair (t2,t3)
  t0=(v0,v1,v2), t1=(v0,v1,v3): two CCW polys using v0→v1
  t2=(v1,v0,v4), t3=(v1,v0,v5): two CW polys using v1→v0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1172",
    title="fill_edge_map non_manifold_visitor_callback: four polys share one edge; visitor.non_manifold_edge fired (Branch 3)",
    defect_class="non_manifold_edge",
)

# Two base vertices + four apex vertices
v0 = m.vertex(0.0,   0.0,   0.0)   # 0 — shared edge start
v1 = m.vertex(1.0,   0.0,   0.0)   # 1 — shared edge end
v2 = m.vertex(0.5,   1.0,   0.0)   # 2 — above CCW apex 1
v3 = m.vertex(0.5,  -1.0,   0.0)   # 3 — below CCW apex 1
v4 = m.vertex(0.5,   2.0,   0.0)   # 4 — above CCW apex 2
v5 = m.vertex(0.5,  -2.0,   0.0)   # 5 — below CCW apex 2

# Four triangles sharing edge v0-v1 (non-manifold: 4 incidents)
t0 = m.triangle(v0, v1, v2)   # 0: uses directed v0→v1
t1 = m.triangle(v0, v1, v3)   # 1: uses directed v0→v1
t2 = m.triangle(v1, v0, v4)   # 2: uses directed v1→v0
t3 = m.triangle(v1, v0, v5)   # 3: uses directed v1→v0

# Edge v0-v1 shared by all four triangles = non-manifold (n=4)
m.assert_edge_shared(v0, v1, 4)

# Other edges owned by exactly one triangle
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v0, v5, 1)
m.assert_edge_shared(v1, v5, 1)

# V=6, E=9, F=4, chi=1
m.assert_euler_characteristic(6, 9, 4, 1)
