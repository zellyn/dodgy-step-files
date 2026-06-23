"""Me364 — remove_isolated_points_removal_count_check: no isolated vertices; removed_points_n==0 early return.

CGAL PMP `remove_isolated_points_in_polygon_soup` Branch 5 (*removal_count_check*) @ line 462:
  'if(removed_points_n == 0) return 0;' — after the detection loop, if no isolated
  points were found, the function skips the erase and remap steps and returns 0.
  This branch fires whenever the soup is clean (all vertices referenced).

Defect pattern: a closed tetrahedron — 4 vertices, 4 triangles, all fully manifold
  and closed. Every vertex is referenced by 3 triangles; no isolated vertices exist.
  The removal_count_check fires and the function returns immediately.

Geometry: regular tetrahedron with vertices at unit positions.
  V=4, E=6, F=4, chi=2 (closed manifold, genus 0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me364",
             title="remove_isolated_points_removal_count_check: closed tetrahedron; removed_points_n==0 triggers early return",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0,  0.0,  0.0)
v1 = m.vertex(1.0,  0.0,  0.0)
v2 = m.vertex(0.5,  1.0,  0.0)
v3 = m.vertex(0.5,  0.333, 1.0)

# Four faces of the tetrahedron (consistent outward winding).
t0 = m.triangle(v0, v2, v1)   # bottom (CW from below = outward)
t1 = m.triangle(v0, v1, v3)   # front
t2 = m.triangle(v1, v2, v3)   # right
t3 = m.triangle(v0, v3, v2)   # left

# Every edge is shared by exactly 2 triangles (closed manifold).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler: V=4, E=6, F=4, chi=2.
m.assert_euler_characteristic(4, 6, 4, 2)
