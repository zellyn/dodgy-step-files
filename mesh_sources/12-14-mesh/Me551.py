"""Me551 — checkAndRepair::rebuildConnectivity VERTEX_GEOMETRIC_EQUALITY: two sorted vertices geometrically identical; v->info = pv (Branch 2).

MeshFix `checkAndRepair::rebuildConnectivity` Branch 2 (*VERTEX_GEOMETRIC_EQUALITY*) @ line 336:
  'if ((*v) != (*pv)) { pv = v; } else { v->info = pv; }'
  — after sorting all vertices by coordinate, the algorithm walks through
  the sorted array. Whenever the current vertex v has the same 3D position
  as the previous vertex pv, v's info pointer is set to pv (v->info = pv),
  unifying both as the same canonical representative → Branch 2 fires.

Defect pattern: two triangles sharing interior edge (v0,v2). Boundary vertices
  v1 and v3 are at identical coordinates (1.0,0.0,0.0) but are distinct mesh
  vertices (different indices, different info pointers). After the sort pass,
  they appear adjacent in the sorted array. The coordinate comparison fails
  (they ARE equal), so v3->info = v1 → Branch 2 fires. The two triangles
  together form an open disk.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1,0,0) [coincident with v1]
  t0=(v0,v1,v2), t1=(v0,v2,v3) sharing interior edge (v0,v2).
  Boundary cycle: v0 → v1 → v2 → v3 → v0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me551",
    title="checkAndRepair::rebuildConnectivity VERTEX_GEOMETRIC_EQUALITY: v1 and v3 both at (1,0,0); v3->info set to v1 during sorted-walk (Branch 2)",
    defect_class="near_coincident_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left corner
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — boundary at (1,0,0); canonical representative
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — apex
v3 = m.vertex(1.0, 0.0, 0.0)  # 3 — boundary at (1,0,0); coincident with v1

# Two triangles sharing interior edge (v0, v2).
t0 = m.triangle(v0, v1, v2)  # 0: left triangle
t1 = m.triangle(v0, v2, v3)  # 1: right triangle

# Interior shared edge (v0, v2) — n=2.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# v1 and v3 are geometrically identical — triggers v3->info = v1 (Branch 2).
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(v1, v3)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
