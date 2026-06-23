"""Me064 — small_polygon_skip: a triangle polygon alongside a pinched hexagon.

Catalog claim: the polygon soup contains both a clean triangle (3 points, which cannot
be pinched) and a pinched hexagon. CGAL PMP.split_pinched_polygons_in_polygon_soup
Branch 2 (*small_polygon_skip*) fires for the triangle: the condition
`if(ini_polygon_size <= 3)` is true, so the polygon is skipped with `continue`.
Only the hexagon is scanned for pinches.

Polygon list:
  - Polygon 0: (v0, v1, v2) — 3 vertices, cannot be pinched → Branch 2 (small_polygon_skip)
  - Polygon 1: (v3, v4, v5, v3, v6, v7) — 6 vertices, v3 at positions 0 and 3 → pinched

The clean triangle remains as-is. The hexagon splits into:
  split_polygon_1 = (v3, v4, v5) [triangle]
  split_polygon_2 = (v3, v6, v7) [triangle]

Defect: the mixed soup forces Branch 2 to fire on the 3-vertex polygon before
Branch 4 (point_uniqueness_check) scans for pinches in the hexagon.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me064",
             title="small_polygon_skip: triangle (<=3 verts) skipped; adjacent hexagon is pinched",
             defect_class="pinched_polygon")

# Polygon 0: clean triangle (Branch 2 fires — skip because size <= 3)
v0 = m.vertex(5.0, 0.0, 0.0)   # 0
v1 = m.vertex(6.0, 0.0, 0.0)   # 1
v2 = m.vertex(5.5, 1.0, 0.0)   # 2

t_control = m.triangle(v0, v1, v2)   # triangle 0 — control (clean, not pinched)

# Polygon 1: hexagon (v3,v4,v5,v3,v6,v7) — v3 repeated at positions 0 and 3
v3 = m.vertex(0.0, 0.0, 0.0)   # 3 — pinch vertex
v4 = m.vertex(1.0, 0.0, 0.0)   # 4
v5 = m.vertex(0.5, 1.0, 0.0)   # 5
v6 = m.vertex(-1.0, 0.0, 0.0)  # 6
v7 = m.vertex(-0.5, 1.0, 0.0)  # 7

# After split: sub-polygon 1 = (v3,v4,v5), sub-polygon 2 = (v3,v6,v7)
t1 = m.triangle(v3, v4, v5)   # triangle 1 — split_polygon_1
t2 = m.triangle(v3, v6, v7)   # triangle 2 — split_polygon_2 (push_back'd)

# The clean control triangle (t_control) has no connectivity with t1/t2.
m.assert_triangle_not_reachable_from(target=t_control, source=t1)

# v3 (pinch vertex) has a disconnected fan: t1 and t2 share only v3, no edge.
m.assert_vertex_fan_disconnected(v3)
