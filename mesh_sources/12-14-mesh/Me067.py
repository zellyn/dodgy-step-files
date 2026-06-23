"""Me067 — pinch_split_boundary: prev_id located deep in polygon — tests the lookup.

Catalog claim: Branch 6 (*pinch_split_boundary*) fires when the repeated vertex is
found at a large `i`. The algorithm must look up `prev_id = is_insert_successful.first->second`
from the map to find the earlier occurrence. This fixture places the pinch at position 6
(latest first occurrence at position 1) to stress the map lookup at maximum distance.

Polygon: (v0, v1, v2, v3, v4, v5, v1, v6) — v1 at positions 1 and 6.
  prev_id = 1, i = 6
  split_polygon_1 = polygon[1..6] = (v1, v2, v3, v4, v5, v1) → simplify → (v1, v2, v3, v4, v5) [pentagon]
  split_polygon_2 = polygon[6..7] + polygon[0..1] = (v1, v6) + (v0, v1)
                  = (v1, v6, v0, v1) → simplify → (v1, v6, v0) [triangle]

Result: pentagon (v1,v2,v3,v4,v5) → 3 triangles + triangle (v1,v6,v0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me067",
             title="pinch_split_boundary: 8-gon with pinch at positions 1 and 6 → pentagon + triangle",
             defect_class="pinched_polygon")

# Octagon: (v0, v1, v2, v3, v4, v5, v1, v6) — v1 at positions 1 and 6.
# split_polygon_1 = pentagon (v1, v2, v3, v4, v5) → 3 triangles via fan
# split_polygon_2 = triangle (v1, v6, v0)
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — pinch vertex (prev_id=1, i=6)
v2 = m.vertex(2.0, 0.5, 0.0)   # 2
v3 = m.vertex(2.0, 1.5, 0.0)   # 3
v4 = m.vertex(1.0, 2.0, 0.0)   # 4
v5 = m.vertex(0.0, 1.5, 0.0)   # 5
v6 = m.vertex(0.5, -1.0, 0.0)  # 6

# Sub-polygon 1 (split_polygon_1): pentagon (v1,v2,v3,v4,v5) → fan-triangulated from v1
t0 = m.triangle(v1, v2, v3)   # fan from v1
t1 = m.triangle(v1, v3, v4)
t2 = m.triangle(v1, v4, v5)

# Sub-polygon 2 (split_polygon_2): triangle (v1, v6, v0)
t3 = m.triangle(v1, v6, v0)

# Pentagon triangles (t0,t1,t2) are connected to each other via shared edges.
m.assert_edge_shared(v1, v3, 2)   # shared by t0 and t1
m.assert_edge_shared(v1, v4, 2)   # shared by t1 and t2

# v1 (pinch vertex) links the two sub-polygons; fan is disconnected.
m.assert_vertex_fan_disconnected(v1)

# t3 (split_polygon_2 triangle) not reachable from t0 (split_polygon_1).
m.assert_triangle_not_reachable_from(target=t3, source=t0)
