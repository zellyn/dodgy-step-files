"""Me752 — simplify_polygons_in_polygon_soup consecutive_duplicate_removal: simplify_polygon erases repeated vertex.

CGAL PMP `PMP.simplify_polygons_in_polygon_soup` Branch 3 (*consecutive_duplicate_removal*) @ line 171:
  'simplify_polygon(points, polygon, traits)' — the inner function finds any pair of
  consecutive identical vertex indices in the polygon list and erases the duplicate,
  iterating until no consecutive duplicates remain. Branch 3 fires when a polygon in the
  soup has at least one consecutive-duplicate pair.

Defect pattern: a triangle whose polygon-soup entry has two consecutive identical vertex
  indices: [v0, v0, v1]. The first two indices are the same (consecutive duplicate at
  positions 0 and 1). simplify_polygon detects this pair and erases one copy, reducing
  the polygon to [v0, v1] (size 2 — a degenerate edge-polygon). After removal, the
  polygon has no further consecutive duplicates so the inner loop exits.

  A second clean triangle (v2, v3, v4) is also present to exercise Branch 1 on a
  non-degenerate polygon so the iteration fires on both entries.

Geometry:
  v0=(0,0,0), v1=(1,0,0) — the two distinct vertices of the degenerate polygon.
  Triangle t_defect stored as (v0, v0, v1): index list [0, 0, 1].
  Consecutive pair at positions 0-1 → simplify_polygon erases one v0.

  v2=(3,0,0), v3=(4,0,0), v4=(3.5,1,0) — clean triangle.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me752",
    title="simplify_polygons_in_polygon_soup consecutive_duplicate_removal: triangle (v0,v0,v1) has consecutive duplicate at index 0-1; simplify_polygon erases copy (Branch 3)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — repeated consecutively at positions 0 and 1
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — second distinct vertex of defect polygon

v2 = m.vertex(3.0, 0.0, 0.0)  # 2 — clean triangle
v3 = m.vertex(4.0, 0.0, 0.0)  # 3
v4 = m.vertex(3.5, 1.0, 0.0)  # 4

# Defect triangle: index list [0, 0, 1] — consecutive duplicate at positions 0-1.
# simplify_polygon fires and removes one copy of v0 → polygon becomes [v0, v1].
t_defect = m.triangle(v0, v0, v1)  # triangle 0

# Clean triangle: distinct consecutive indices.
t_clean = m.triangle(v2, v3, v4)   # triangle 1

# The defect triangle has zero area (two identical vertices collapse the face).
m.assert_triangle_area_lt(t_defect, 1e-12)

# The defect edge (v0, v1) appears once: only t_defect has distinct vertices v0 and v1.
m.assert_edge_shared(v0, v1, 1)

# Clean triangle boundary edges.
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v2, v4, 1)
