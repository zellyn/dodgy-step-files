"""Me066 — point_uniqueness_check: unique_points map tracks all preceding vertices.

Catalog claim: as the inner scan advances through the polygon vertices (Branch 4:
*point_uniqueness_check*), each vertex is inserted into the unique_points map. For
every insert, is_insert_successful.second is checked. This fixture places the pinch
deep in the polygon so that Branch 4 fires multiple times building up the map before
Branch 5 (*pinch_detection*) finally triggers.

Polygon: (v0, v1, v2, v3, v4, v2, v5) — v2 at positions 2 and 5.
The map is built through positions 0 (v0), 1 (v1), 2 (v2 — inserted OK), 3 (v3), 4 (v4).
At position 5, v2 is re-inserted → insert fails → pinch detected.
  prev_id = 2, i = 5
  split_polygon_1 = polygon[2..5] = (v2, v3, v4, v2) → simplify → (v2, v3, v4) [triangle]
  split_polygon_2 = polygon[5..6] + polygon[0..2] = (v2,v5) + (v0,v1,v2)
                  = (v2, v5, v0, v1, v2) → simplify → (v2, v5, v0, v1) [quad]

Result: triangle (v2,v3,v4) + quad (v2,v5,v0,v1) → 3 triangles total.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me066",
             title="point_uniqueness_check: 7-gon (v0..v4,v2,v5) — pinch found at map position 5",
             defect_class="pinched_polygon")

# Heptagon: (v0, v1, v2, v3, v4, v2, v5) — v2 repeated at positions 2 and 5.
# After split:
#   split_polygon_1 = (v2, v3, v4)        [triangle]
#   split_polygon_2 = (v2, v5, v0, v1)    [quad → 2 triangles]
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — pinch vertex (positions 2 and 5)
v3 = m.vertex(2.5, 1.0, 0.0)   # 3
v4 = m.vertex(1.5, 1.5, 0.0)   # 4
v5 = m.vertex(1.0, -1.0, 0.0)  # 5

# Sub-polygon 1 (split_polygon_1): triangle (v2, v3, v4)
t0 = m.triangle(v2, v3, v4)

# Sub-polygon 2 (split_polygon_2): quad (v2, v5, v0, v1)
t1 = m.triangle(v2, v5, v0)
t2 = m.triangle(v2, v0, v1)

# v2 (pinch vertex) connects the two sub-polygon groups.
# Fan at v2 should be disconnected (t0 shares no edge with t1/t2).
m.assert_vertex_fan_disconnected(v2)

# t0 (triangle from split_polygon_1) not reachable from t1 (quad sub-polygon).
m.assert_triangle_not_reachable_from(target=t0, source=t1)
