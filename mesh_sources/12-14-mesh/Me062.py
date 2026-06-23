"""Me062 — polygon_replacement + new_polygon_append: swap original / push second sub-polygon.

Catalog claim: after split_pinched_polygons detects a pinch and creates two sub-polygons,
Branch 9 (*polygon_replacement*) fires: std::swap(polygon, split_polygon_1) replaces the
current slot with the first sub-polygon. Branch 10 (*new_polygon_append*) fires immediately
after: polygons.push_back(split_polygon_2) appends the second sub-polygon to the list for
re-processing.

This fixture encodes a pentagon (v0, v1, v2, v0, v3) — v0 at positions 0 and 3:
  split_polygon_1 = polygon[0..3] = (v0, v1, v2, v0) → simplify → (v0, v1, v2) [triangle]
  split_polygon_2 = polygon[0..0] + polygon[3..4] = (v0) + (v0, v3) → (v0, v3) [degenerate: only 2 verts]

Hmm - for a pentagon with pinch at positions 0 and 3:
  split_polygon_1 = (v0, v1, v2, v0) → simplify consecutive → (v0, v1, v2) [triangle, ok]
  split_polygon_2 = polygon[i..end] + polygon[begin..prev_id]
    = polygon[3..4] + polygon[0..0]
    = (v0, v3) + (v0)  → (v0, v3, v0) → simplify → (v0, v3) [2 verts, skipped by small_polygon_skip]

Pentagon doesn't yield two useful sub-polygons. Use a heptagon (v0,v1,v2,v3,v0,v4,v5):
  v0 at positions 0 and 4. prev_id=0, i=4.
  split_polygon_1 = polygon[0..4] = (v0, v1, v2, v3, v0) → simplify → (v0, v1, v2, v3) [quad → 2 tris]
  split_polygon_2 = polygon[4..6] + polygon[0..0] = (v0, v4, v5) + (v0) = (v0, v4, v5, v0) → simplify → (v0, v4, v5) [triangle]

Both sub-polygons are valid! The quad is triangulated as 2 triangles.
This demonstrates:
  - polygon_replacement (Branch 9): original slot ← quad (v0,v1,v2,v3)
  - new_polygon_append (Branch 10): push triangle (v0,v4,v5)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me062",
             title="polygon_replacement+new_polygon_append: heptagon (v0..v3,v0,v4,v5) → quad+triangle",
             defect_class="pinched_polygon")

# Heptagon polygon: (v0, v1, v2, v3, v0, v4, v5)
# v0 at positions 0 and 4. After split:
#   slot replacement  → quad  (v0, v1, v2, v3) → triangles t0, t1
#   push_back         → triangle (v0, v4, v5) → triangle t2
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — pinch vertex (prev_id=0, i=4)
v1 = m.vertex(1.0, -0.5, 0.0)  # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(1.0, 0.5, 0.0)   # 3
v4 = m.vertex(-1.0, -0.5, 0.0) # 4
v5 = m.vertex(-1.0, 0.5, 0.0)  # 5

# Sub-polygon 1 (polygon_replacement → slot): quad (v0,v1,v2,v3)
t0 = m.triangle(v0, v1, v2)    # triangulated quad half 1
t1 = m.triangle(v0, v2, v3)    # triangulated quad half 2

# Sub-polygon 2 (new_polygon_append): triangle (v0,v4,v5)
t2 = m.triangle(v0, v4, v5)

# Pinch vertex v0 connects t0/t1 (sub-polygon 1) with t2 (sub-polygon 2).
# The fan at v0 is disconnected: t0,t1 form one fan cluster, t2 another.
m.assert_vertex_fan_disconnected(v0)

# t2 (pushed back polygon) is disconnected from t0 (replacement polygon).
m.assert_triangle_not_reachable_from(target=t2, source=t0)
