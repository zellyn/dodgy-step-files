"""Me662 — merge_duplicate_points_in_polygon_soup new_unique_point: id==unique_points.size(); every vertex is first-seen; unique_points.push_back fires for each (Branch 3).

CGAL PMP `PMP.merge_duplicate_points_in_polygon_soup` Branch 3 (*new_unique_point*) @ line 558:
  'if(id == unique_points.size()) { unique_points.push_back(points[i]); }'
  — When the insert succeeds (point not previously seen), the returned id
  equals the current size of unique_points. The algorithm appends the point
  to unique_points and increments the unique counter. This branch fires once
  per distinct coordinate during the scan.

Defect pattern: a clean triangle fan with three distinct vertices — no
  coincident coordinates anywhere. Every point insert succeeds; Branch 3
  fires for every vertex (id==unique_points.size() each time). After the
  scan, unique_points.size()==ini_points_n so no remapping is performed.

Geometry:
  q0=(0,0,0), q1=(2,0,0), q2=(1,2,0), q3=(0,2,0) — four distinct vertices.
  t0=(q0,q1,q2), t1=(q0,q2,q3) sharing interior edge (q0,q2).
  All vertex coordinates are unique; every insert into point_to_id succeeds.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me662",
    title="merge_duplicate_points_in_polygon_soup new_unique_point: all four vertices distinct; every insert succeeds and id==unique_points.size() fires for each (Branch 3)",
    defect_class="near_coincident_vertex",
)

q0 = m.vertex(0.0, 0.0, 0.0)  # 0 — distinct
q1 = m.vertex(2.0, 0.0, 0.0)  # 1 — distinct
q2 = m.vertex(1.0, 2.0, 0.0)  # 2 — distinct
q3 = m.vertex(0.0, 2.0, 0.0)  # 3 — distinct

# Two triangles sharing interior edge (q0, q2).
t0 = m.triangle(q0, q1, q2)  # 0
t1 = m.triangle(q0, q2, q3)  # 1

# Interior shared edge (n=2).
m.assert_edge_shared(q0, q2, 2)

# Boundary edges (n=1 each).
m.assert_edge_shared(q0, q1, 1)
m.assert_edge_shared(q1, q2, 1)
m.assert_edge_shared(q2, q3, 1)
m.assert_edge_shared(q0, q3, 1)

# All vertices are at distinct coordinates — no duplicate inserts.
# After scan: unique_points.size()==4==ini_points_n; no remap needed.
# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
