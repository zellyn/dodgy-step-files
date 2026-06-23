"""Me065 — dynamic_polygon_iteration: split pushes new polygon that is also pinched.

Catalog claim: the outer loop in split_pinched_polygons iterates using polygons.size()
re-evaluated every pass (Branch 1: *dynamic_polygon_iteration*). A first polygon splits
into a clean triangle and a *new* pinched polygon that is immediately appended with
push_back. On the next outer iteration, polygons.size() has grown, so the loop continues
and processes the newly appended pinched polygon.

Polygon list (initial):
  - Polygon 0: (v0,v1,v2,v0,v3,v4,v0,v5,v6) — two pinches at v0 (positions 0,3 and 0,6)
    But the inner loop breaks at the FIRST pinch (Branch 11: loop_break):
      First split: split_polygon_1=(v0,v1,v2), split_polygon_2=(v0,v3,v4,v0,v5,v6)
    split_polygon_2 is pushed back → dynamic size triggers another outer iteration.
    split_polygon_2 is also pinched at v0 (positions 0 and 3):
      Second split: split_polygon_1=(v0,v3,v4), split_polygon_2=(v0,v5,v6)

Final triangles: (v0,v1,v2), (v0,v3,v4), (v0,v5,v6).
All three meet at pinch vertex v0 with a three-way disconnected fan.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me065",
             title="dynamic_polygon_iteration: double-pinched 9-gon grows polygon list via push_back cascade",
             defect_class="pinched_polygon")

# Pinch vertex v0 — appears THREE times in the original polygon:
# positions 0, 3, and 6.  Inner loop breaks at first (position 3).
# push_back of split_polygon_2=(v0,v3,v4,v0,v5,v6) forces outer loop to grow.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — triple pinch vertex

# Fan cluster A: (v0, v1, v2)
v1 = m.vertex(1.0,  0.0, 0.0)  # 1
v2 = m.vertex(0.7,  0.7, 0.0)  # 2

# Fan cluster B: (v0, v3, v4)
v3 = m.vertex(0.0,  1.0, 0.0)  # 3
v4 = m.vertex(-0.7, 0.7, 0.0)  # 4

# Fan cluster C: (v0, v5, v6)
v5 = m.vertex(-1.0, 0.0, 0.0)  # 5
v6 = m.vertex(-0.7,-0.7, 0.0)  # 6

t0 = m.triangle(v0, v1, v2)   # from first split_polygon_1
t1 = m.triangle(v0, v3, v4)   # from second split_polygon_1
t2 = m.triangle(v0, v5, v6)   # from second split_polygon_2

# All three triangles share only the pinch vertex v0.
# The fan at v0 is three-way disconnected.
m.assert_vertex_fan_disconnected(v0)

# t0 cannot reach t1 by edge walk.
m.assert_triangle_not_reachable_from(target=t1, source=t0)

# t0 cannot reach t2 by edge walk.
m.assert_triangle_not_reachable_from(target=t2, source=t0)
