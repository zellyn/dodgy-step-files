"""Me278 — autorefine_triangle_soup: duplicate-point-detection-in-dedup (Branch 9).

CGAL PMP `autorefine_impl::autorefine_triangle_soup` Branch 9 @ line 1224:
  'points[indices[i]] == points[indices[i+1]]' — during the deduplication sweep
  over the sorted intersection-point list, adjacent entries are compared. When two
  adjacent entries have exactly the same coordinates, they are collapsed to a single
  id via id_map, preventing downstream triangle-insertion from inserting two
  identical refinement points.

The input pattern: two different triangle pairs that produce the same intersection
point. After collection, the sorted point list contains a geometric duplicate — two
entries at the exact same coordinates. Branch 9 detects the duplicate (equal adjacent
entries) and maps the second to the first via id_map.

Geometry: three triangles. Triangle t0 is a horizontal panel. Triangles t1 and t2
each cross t0 in a way that one of their intersection segment endpoints coincides
at the same 3D location. This shared endpoint is the near-coincident vertex pair
that gets collapsed via id_map.

In this fixture, t1 and t2 both have one vertex at (0,0,0) which sits exactly on
the boundary of t0. Each pair (t0,t1) and (t0,t2) would independently compute this
boundary point as an intersection contribution, generating duplicate entries.

Keywords: points[indices[i]]==points[indices[i+1]], id_map, duplicate point collapse.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me278",
             title="autorefine_triangle_soup dedup duplicate-point: coincident insertion points → id_map",
             defect_class="autorefine_dedup_duplicate_point")

# Triangle 0: horizontal base in z=0.
v0 = m.vertex(-2.0,  0.0, 0.0)  # 0
v1 = m.vertex( 2.0,  0.0, 0.0)  # 1
v2 = m.vertex( 0.0,  2.0, 0.0)  # 2

# Triangle 1: tilted, crossing t0.
# v3 is below t0, v4 is above t0, v5 is at (0,0,0) on t0's boundary edge v0-v1.
v3 = m.vertex(-1.0,  0.0, -1.0)  # 3 — below z=0
v4 = m.vertex(-1.0,  0.0,  1.0)  # 4 — above z=0
v5 = m.vertex( 0.0,  0.0,  0.0)  # 5 — on t0's edge v0-v1 (y=0, z=0, x=0)

# Triangle 2: tilted differently, also crossing t0.
# v6 is above, v7 is below, v8 is at (0,0,0) = same as v5 (duplicate insertion pt).
v6 = m.vertex( 0.5,  1.0,  1.0)  # 6 — above z=0
v7 = m.vertex( 0.5,  1.0, -1.0)  # 7 — below z=0
v8 = m.vertex( 0.0,  0.0,  0.0)  # 8 — same position as v5 (DUPLICATE)

t0 = m.triangle(v0, v1, v2)   # 0 — horizontal base
t1 = m.triangle(v3, v4, v5)   # 1 — crosses t0
t2 = m.triangle(v6, v7, v8)   # 2 — crosses t0 at same point

# t0 and t1 cross each other.
m.assert_triangles_self_intersect(t0, t1)

# t0 and t2 cross each other.
m.assert_triangles_self_intersect(t0, t2)

# v5 and v8 are at the same position — this is the duplicate insertion point
# that Branch 9 collapses via id_map.
m.assert_vertex_pair_distance_lt(v5, v8, 1e-12)

# v5 lies on edge v0-v1 of t0 (midpoint of the base edge).
m.assert_vertex_on_edge(v5, v0, v1)
