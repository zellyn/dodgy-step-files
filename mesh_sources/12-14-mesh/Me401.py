"""Me401 — detect_identical_mergeable_vertices identical_point_detection: target point of current halfedge equals previous (Branch 2).

CGAL PMP `PMP.internal.detect_identical_mergeable_vertices` Branch 2 (*identical_point_detection*) @ line 169:
  'if(get(vpm, target(cycle_hedges[i], mesh)) == get(vpm, target(cycle_hedges[i-1], mesh)))'
  — after sorting, the algorithm iterates the sorted halfedge array comparing each
  halfedge's target point to the previous one. When they match, Branch 2 fires and
  the pair is flagged for candidate-group creation.

Defect pattern: two triangles sharing one interior edge, with two boundary vertices
  sharing identical coordinates. The minimal pair (i-1, i) that satisfies the equality
  check is the identical_point_detection branch. Distinct from Branch 1 (which covers
  the sort call itself) and Branch 3 (which covers the group-creation resize).

Geometry:
  v0=(0,0,0), v1=(3,0,0), v2=(1.5,2,0), v3=(3,0,0) [coincident with v1]
  t0=(v0,v1,v2), t1=(v0,v2,v3) sharing interior edge (v0,v2).
  Boundary cycle: v0 → v1 → v2 → v3 → v0.
  After sort, halfedges targeting v1 and v3 (both at (3,0,0)) are adjacent;
  the equality comparison fires → Branch 2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me401",
    title="detect_identical_mergeable_vertices identical_point_detection: sorted boundary halfedge i-1 and i target same point (3,0,0); equality fires (Branch 2)",
    defect_class="near_coincident_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(3.0, 0.0, 0.0)  # 1 — boundary; coincident with v3
v2 = m.vertex(1.5, 2.0, 0.0)  # 2 — apex
v3 = m.vertex(3.0, 0.0, 0.0)  # 3 — boundary; coincident with v1

# Two triangles sharing interior edge (v0, v2).
t0 = m.triangle(v0, v1, v2)  # 0
t1 = m.triangle(v0, v2, v3)  # 1

# Interior shared edge.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Coincident pair on boundary — triggers identical_point_detection after sort.
m.assert_vertex_pair_distance_lt(v1, v3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(v1, v3)

# Euler: V=4, E=5, F=2, chi=1.
m.assert_euler_characteristic(4, 5, 2, 1)
