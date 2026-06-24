"""Me753 — simplify_polygons_in_polygon_soup modification_count: ++simplified_polygons_n when simplify fires.

CGAL PMP `PMP.simplify_polygons_in_polygon_soup` Branch 4 (*modification_count*) @ line 172:
  'if(simplify_polygon(points, polygon, traits) != 0) ++simplified_polygons_n;'
  — after simplify_polygon() runs, its non-zero return value (number of vertices removed)
  causes the modification counter to increment. Branch 4 fires whenever at least one
  polygon in the soup is actually simplified (has consecutive duplicates removed).

Defect pattern: two triangles each carrying a consecutive-duplicate pair. Both polygons
  require simplification, so simplified_polygons_n increments twice. Using two
  consecutive-duplicate triangles ensures Branch 4 fires more than once, proving the
  counter is accumulated across the entire soup rather than latching on the first hit.

  Triangle A: [v0, v0, v1] — consecutive duplicate at positions 0-1; simplify removes
    one v0 → return value 1 → ++simplified_polygons_n (first increment).
  Triangle B: [v2, v3, v3] — consecutive duplicate at positions 1-2; simplify removes
    one v3 → return value 1 → ++simplified_polygons_n (second increment).

Geometry:
  v0=(0,0,0), v1=(1,0,0) — defect triangle A.
  v2=(3,0,0), v3=(4,0,0) — defect triangle B.
  Both t_a and t_b have zero area (degenerate).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me753",
    title="simplify_polygons_in_polygon_soup modification_count: two consecutive-duplicate triangles each fire simplify_polygon; simplified_polygons_n incremented twice (Branch 4)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — triangle A first vertex (repeated at position 0-1)
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — triangle A second distinct vertex

v2 = m.vertex(3.0, 0.0, 0.0)  # 2 — triangle B first vertex
v3 = m.vertex(4.0, 0.0, 0.0)  # 3 — triangle B second vertex (repeated at position 1-2)

# Triangle A: [v0, v0, v1] — consecutive duplicate at positions 0-1.
# simplify_polygon returns 1 → ++simplified_polygons_n (first increment of Branch 4).
t_a = m.triangle(v0, v0, v1)  # triangle 0

# Triangle B: [v2, v3, v3] — consecutive duplicate at positions 1-2.
# simplify_polygon returns 1 → ++simplified_polygons_n (second increment of Branch 4).
t_b = m.triangle(v2, v3, v3)  # triangle 1

# Both defect triangles have zero area.
m.assert_triangle_area_lt(t_a, 1e-12)
m.assert_triangle_area_lt(t_b, 1e-12)

# Defect edge pairs confirm which distinct vertices each triangle holds.
m.assert_edge_shared(v0, v1, 1)  # t_a: v0 and v1 are distinct consecutive pair after simplify
m.assert_edge_shared(v2, v3, 1)  # t_b: v2 and v3 are distinct consecutive pair after simplify
