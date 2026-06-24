"""Me1194 — is_polygon_soup_a_polygon_mesh non_manifold_edge:
  edge shared by more than 2 polygons triggers non-manifold marking (Branch 2).

CGAL PMP `PMP.is_polygon_soup_a_polygon_mesh` Branch 2 (*non_manifold_edge*)
  @ line 220:
  'if (marked_edges.count(e) != 0) return false; else marked_edges.insert(e)' —
  Each directed edge (i0,i1) is inserted into a set. For a manifold soup, each
  directed edge appears in exactly one polygon. Branch 2 fires when a directed
  edge is encountered for the second time (i.e. it was already in marked_edges),
  meaning two polygons claim the same directed half-edge — the edge is shared by
  more than 2 polygons overall, which is non-manifold.

Defect pattern: three triangles all claiming the same directed edge v0→v1.
  When the second triangle with directed edge v0→v1 is processed, marked_edges
  already contains (0,1). Branch 2 fires and the function returns false.
  V=5, E=7, F=3.

Geometry:
  v0=(0,0,0), v1=(1,0,0): shared base
  v2=(0.5,1,0), v3=(0.5,-1,0), v4=(0.5,0,1) — three fan vertices
  t0=(v0,v1,v2), t1=(v0,v1,v3), t2=(v0,v1,v4) — three tris same directed edge
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1194",
    title="is_polygon_soup_a_polygon_mesh non_manifold_edge: three triangles claim directed edge v0→v1; second encounter fires marked_edges guard; returns false (Branch 2)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — shared base left
v1 = m.vertex(1.0,  0.0, 0.0)   # 1 — shared base right
v2 = m.vertex(0.5,  1.0, 0.0)   # 2 — fan vertex above
v3 = m.vertex(0.5, -1.0, 0.0)   # 3 — fan vertex below
v4 = m.vertex(0.5,  0.0, 1.0)   # 4 — fan vertex in front

# All three triangles share directed edge v0→v1
t0 = m.triangle(v0, v1, v2)    # 0
t1 = m.triangle(v0, v1, v3)    # 1
t2 = m.triangle(v0, v1, v4)    # 2

# Non-manifold edge: shared by 3 triangles (all same directed edge v0→v1)
m.assert_edge_shared(v0, v1, 3)

# Fan edges (each belongs to exactly one triangle)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# V=5, E=7, F=3, chi=1
m.assert_euler_characteristic(5, 7, 3, 1)
