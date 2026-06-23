"""Me362 — remove_isolated_points_unused_detection: unvisited point found; swap to end-of-keep region.

CGAL PMP `remove_isolated_points_in_polygon_soup` Branch 3 (*unused_point_detection*) @ line 430:
  'if(!visited[i]) { std::swap(points[swap_position], points[i]); ... }' — after the
  usage scan, the function iterates visited[] and swaps each unvisited point toward the
  tail of the array, accumulating removed_points_n.

Defect pattern: a single triangle (v0,v1,v2) plus one isolated vertex v3 at (5,5,5).
  After the scan, visited[0..2]=true but visited[3]=false. The detection loop finds i=3
  unvisited, swaps points[swap_position] with points[3], and increments removed_points_n.

Geometry: v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(5,5,5) — orphan.
  Triangle t0=(v0,v1,v2); v3 not referenced.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me362",
             title="remove_isolated_points_unused_detection: isolated v3 found by !visited[i] and swapped toward tail",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(5.0, 5.0, 5.0)   # isolated — no triangle references this

m.triangle(v0, v1, v2)

# v3 is isolated.
m.assert_isolated_vertex(v3)

# All triangle edges are boundary.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
