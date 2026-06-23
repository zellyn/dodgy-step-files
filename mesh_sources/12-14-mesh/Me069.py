"""Me069 — new_polygon_append cascade: multiple polygons in soup, each independently pinched.

Catalog claim: the polygon soup contains two independently pinched polygons. Each is
processed in its own outer-loop iteration. For each, Branch 10 (*new_polygon_append*)
fires: polygons.push_back(split_polygon_2) appends a new polygon to the list. After
both outer iterations run, the list grows from 2 to 4 (then the two appended clean
triangles are processed but pass the small-polygon-skip harmlessly if they have 3 verts).

Polygon list (initial, 2 entries):
  - Polygon 0: (v0, v1, v2, v0, v3, v4) — v0 repeated → split into (v0,v1,v2) + (v0,v3,v4)
  - Polygon 1: (v5, v6, v7, v5, v8, v9) — v5 repeated → split into (v5,v6,v7) + (v5,v8,v9)

Each push_back fires Branch 10 independently. The outer loop continues because
polygons.size() grew. The two appended triangles are then iterated (Branch 2: skipped).

Final triangles: 4 distinct non-overlapping triangles with two pinch-vertex hubs.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me069",
             title="new_polygon_append cascade: two independently pinched hexagons each trigger push_back",
             defect_class="pinched_polygon")

# Polygon 0: (v0, v1, v2, v0, v3, v4) — v0 pinch vertex
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — first pinch hub
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3
v4 = m.vertex(-0.5, 1.0, 0.0)  # 4

# Polygon 1: (v5, v6, v7, v5, v8, v9) — v5 pinch vertex (offset by 5 units in X)
v5 = m.vertex(5.0, 0.0, 0.0)   # 5 — second pinch hub
v6 = m.vertex(6.0, 0.0, 0.0)   # 6
v7 = m.vertex(5.5, 1.0, 0.0)   # 7
v8 = m.vertex(4.0, 0.0, 0.0)   # 8
v9 = m.vertex(4.5, 1.0, 0.0)   # 9

# Results from Polygon 0:
t0 = m.triangle(v0, v1, v2)   # split_polygon_1 (replaces polygon 0 slot)
t1 = m.triangle(v0, v3, v4)   # split_polygon_2 (push_back'd — Branch 10 for polygon 0)

# Results from Polygon 1:
t2 = m.triangle(v5, v6, v7)   # split_polygon_1 (replaces polygon 1 slot)
t3 = m.triangle(v5, v8, v9)   # split_polygon_2 (push_back'd — Branch 10 for polygon 1)

# Pinch hub v0: fan disconnected (t0 and t1 share only v0).
m.assert_vertex_fan_disconnected(v0)

# Pinch hub v5: fan disconnected (t2 and t3 share only v5).
m.assert_vertex_fan_disconnected(v5)

# t0 not reachable from t1 (same hub, no shared edge).
m.assert_triangle_not_reachable_from(target=t1, source=t0)

# t2 not reachable from t3 (same hub, no shared edge).
m.assert_triangle_not_reachable_from(target=t3, source=t2)

# The two polygon groups are completely disconnected from each other.
m.assert_triangle_not_reachable_from(target=t2, source=t0)
