"""Me661 — merge_duplicate_points_in_polygon_soup point_dedup_scan: for each input point, insert into unique-point map; coincident pair triggers is_insert_successful check (Branch 2).

CGAL PMP `PMP.merge_duplicate_points_in_polygon_soup` Branch 2 (*point_dedup_scan*) @ line 547:
  'for(std::size_t i=0; i<ini_points_n; ++i)
   { auto [id, is_insert_successful] = point_to_id.insert(...); }'
  — The scan loop iterates over every input point, inserting each into a
  coordinate-keyed map. On the first occurrence the insert succeeds; on a
  duplicate coordinate the insert returns the existing id. The branch covers
  the per-point scan body including the `point_to_id.insert` call and the
  `is_insert_successful` test.

Defect pattern: two triangles sharing an interior edge, with two boundary
  vertices that have coincident coordinates. When the dedup scan processes
  these two identical-coordinate points, the second insert fails
  (is_insert_successful == false), establishing a merge mapping.

Geometry:
  p0=(0,0,0), p1=(1,0,0), p2=(0.5,1,0), p3=(1,0,0) [coincident with p1]
  t0=(p0,p1,p2), t1=(p0,p2,p3) sharing interior edge (p0,p2).
  p1 and p3 at identical coordinates (1,0,0) — the scan inserts p1
  successfully then fails to insert p3, firing the duplicate path.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me661",
    title="merge_duplicate_points_in_polygon_soup point_dedup_scan: coincident p1==p3 at (1,0,0); second insert into point_to_id fails (is_insert_successful==false) (Branch 2)",
    defect_class="near_coincident_vertex",
)

p0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left corner
p1 = m.vertex(1.0, 0.0, 0.0)  # 1 — boundary; coincident with p3
p2 = m.vertex(0.5, 1.0, 0.0)  # 2 — apex
p3 = m.vertex(1.0, 0.0, 0.0)  # 3 — boundary; coincident with p1

# Two triangles sharing interior edge (p0, p2).
t0 = m.triangle(p0, p1, p2)  # 0
t1 = m.triangle(p0, p2, p3)  # 1

# Interior shared edge (n=2): point_dedup_scan iterates both p1 and p3.
m.assert_edge_shared(p0, p2, 2)

# Boundary edges (n=1 each).
m.assert_edge_shared(p0, p1, 1)
m.assert_edge_shared(p1, p2, 1)
m.assert_edge_shared(p2, p3, 1)
m.assert_edge_shared(p0, p3, 1)

# p1 and p3 are geometrically identical — second insert fails, merge recorded.
m.assert_vertex_pair_distance_lt(p1, p3, 1e-9)
m.assert_vertex_pair_no_shared_triangle(p1, p3)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
