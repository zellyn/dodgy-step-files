"""Me750 — simplify_polygons_in_polygon_soup polygon_iteration: loop body entered for each polygon.

CGAL PMP `PMP.simplify_polygons_in_polygon_soup` Branch 1 (*polygon_iteration*) @ line 165:
  'for(P_ID polygon_index = 0; polygon_index < polygons.size(); ++polygon_index)
   { auto& polygon = polygons[polygon_index]; ... }' — the outer for-loop body is entered
  once per polygon in the soup. Branch 1 fires for any polygon soup that contains at
  least one polygon.

Defect pattern: two clean triangles forming a simple 4-vertex open mesh. The polygon
  soup iteration visits polygon 0 (t0) and polygon 1 (t1) in sequence — Branch 1 fires
  twice, once for each triangle. Both triangles have distinct vertex indices, so
  simplify_polygon() returns 0 (no consecutive duplicates removed).

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(2,0,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3) sharing interior edge (v0,v2).
  All polygon entries have size 3 and distinct consecutive indices.
  simplify_polygon returns 0 for both; simplified_polygons_n stays 0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me750",
    title="simplify_polygons_in_polygon_soup polygon_iteration: for-loop body entered for each of 2 polygons in soup (Branch 1)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — shared left corner
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — bottom-right of t0
v2 = m.vertex(0.5, 1.0, 0.0)  # 2 — shared apex
v3 = m.vertex(2.0, 0.0, 0.0)  # 3 — right corner of t1

# Polygon soup with 2 entries (triangles); loop body fires for each.
t0 = m.triangle(v0, v1, v2)  # polygon_index=0; distinct indices → simplify returns 0
t1 = m.triangle(v0, v2, v3)  # polygon_index=1; distinct indices → simplify returns 0

# Interior shared edge (v0, v2) — manifold.
m.assert_edge_shared(v0, v2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
