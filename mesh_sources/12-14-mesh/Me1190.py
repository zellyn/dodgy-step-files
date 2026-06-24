"""Me1190 — does_polygon_soup_self_intersect duplicate_point_presence:
  merge_duplicate_points_in_polygon_soup fires before intersection test (Branch 1).

CGAL PMP `PMP.does_polygon_soup_self_intersect` Branch 1 (*duplicate_point_presence*)
  @ line 40:
  'merge_duplicate_points_in_polygon_soup(points, polygons, np)' —
  Before running the pairwise triangle test, the function merges near-coincident
  point entries so the soup is in canonical form. Branch 1 fires for any soup
  whose point list contains duplicate or near-duplicate coordinates.

Defect pattern: two triangles that share a vertex described by two separate but
  geometrically identical point entries (v2 and v2b both at (0.5,1,0)). The soup
  has a duplicate point: the same spatial location is indexed twice. Branch 1
  (merge_duplicate_points) must run before the self-intersection test can proceed.
  After merging, the two triangles share a manifold edge and do not self-intersect.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0) [original apex]
  v2b=(0.5,1,0) [duplicate — same coordinates as v2, different index]
  t0=(v0,v1,v2), t1=(v2b,v1,v3) where v3=(1.5,1,0)
  Raw edges: (0,1) n=1, (0,2) n=1, (1,2) n=1, (1,3) n=1, (1,4) n=1, (3,4) n=1 — 6 distinct raw edges
  V=5 (pre-merge), E=6 raw, F=2; chi=5-6+2=1
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1190",
    title="does_polygon_soup_self_intersect duplicate_point_presence: two coincident point entries trigger merge_duplicate_points before intersection test (Branch 1)",
    defect_class="near_coincident_vertex",
)

v0  = m.vertex(0.0,  0.0, 0.0)   # 0 — base left
v1  = m.vertex(1.0,  0.0, 0.0)   # 1 — base right
v2  = m.vertex(0.5,  1.0, 0.0)   # 2 — apex (original)
v2b = m.vertex(0.5,  1.0, 0.0)   # 3 — apex duplicate (same coords as v2)
v3  = m.vertex(1.5,  1.0, 0.0)   # 4 — right outer

# t0 uses original apex; t1 uses duplicate apex index
t0 = m.triangle(v0, v1, v2)   # 0: left triangle
t1 = m.triangle(v2b, v1, v3)  # 1: right triangle (v2b == v2 geometrically)

# The two apex indices are a duplicate vertex pair (distance == 0)
m.assert_vertex_pair_distance_lt(v2, v2b, 1e-9)

# Raw edge counts before merge (each triangle has 3 distinct edges)
m.assert_edge_shared(v0, v1, 1)    # edge [0,1]: only in t0
m.assert_edge_shared(v0, v2, 1)    # edge [0,2]: only in t0
m.assert_edge_shared(v1, v2, 1)    # edge [1,2]: only in t0 (raw)
m.assert_edge_shared(v1, v2b, 1)   # edge [1,3]: only in t1 (raw duplicate apex)
m.assert_edge_shared(v1, v3, 1)    # edge [1,4]: only in t1
m.assert_edge_shared(v2b, v3, 1)   # edge [3,4]: only in t1

# V=5, E=6 raw edges, F=2; chi=5-6+2=1
m.assert_euler_characteristic(5, 6, 2, 1)
