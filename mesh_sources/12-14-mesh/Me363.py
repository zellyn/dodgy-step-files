"""Me363 — remove_isolated_points_early_termination: swap index exceeds first_unused_pos; inner loop breaks.

CGAL PMP `remove_isolated_points_in_polygon_soup` Branch 4 (*early_termination*) @ line 432:
  'if(i >= first_unused_pos) break;' — during the detection scan, when the current
  index i overtakes the swap_position boundary, the inner loop terminates early.
  This occurs when multiple consecutive trailing points are all isolated: after the
  first isolated point is swapped, swap_position retreats; if i then reaches
  swap_position, the loop exits without scanning further.

Defect pattern: two triangles (t0=(v0,v1,v2), t1=(v3,v4,v5)) sharing no vertices,
  plus two trailing isolated vertices v6 and v7 at the end of the point list.
  After the usage scan: visited[0..5]=true, visited[6]=false, visited[7]=false.
  The detection loop finds i=6 unvisited (swap with position 7), then i=7 which
  equals first_unused_pos (6), so break fires before any out-of-bounds scan.

Geometry: v0..v5 form two valid triangles; v6=(10,0,0) and v7=(10,1,0) are orphans.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me363",
             title="remove_isolated_points_early_termination: two trailing orphans; i>=first_unused_pos break fires",
             defect_class="isolated_vertex")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)

v3 = m.vertex(3.0, 0.0, 0.0)
v4 = m.vertex(4.0, 0.0, 0.0)
v5 = m.vertex(3.5, 1.0, 0.0)

v6 = m.vertex(10.0, 0.0, 0.0)   # isolated
v7 = m.vertex(10.0, 1.0, 0.0)   # isolated

t0 = m.triangle(v0, v1, v2)
t1 = m.triangle(v3, v4, v5)

# Both isolated vertices.
m.assert_isolated_vertex(v6)
m.assert_isolated_vertex(v7)

# The two triangles are disconnected.
m.assert_triangle_not_reachable_from(target=1, source=0)
