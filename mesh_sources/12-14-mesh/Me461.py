"""Me461 — selectConnectedComponent unvisited_triangle_check: skip already-marked triangles.

Catalog claim: Basic_TMesh.selectConnectedComponent Branch 2 @ line 1074
(*unvisited_triangle_check*): inside the BFS loop, each dequeued triangle is tested
with `if (!IS_VISITED(t))`. Already-visited triangles are skipped immediately; only
unvisited triangles are processed. This branch fires in any multi-triangle BFS where
a triangle can be enqueued more than once (via multiple neighbor paths).

In MeshFix's BFS, a triangle can be added to `todo` by each of its 3 neighbors. When
the triangle is eventually dequeued a second or third time, `IS_VISITED(t)` is true
and the branch body is skipped. The fixture must have a triangle reachable via more
than one path so the duplicate-enqueue scenario is triggered.

Geometric signature: four triangles in a diamond/rhombus configuration. The center
triangle t3 is adjacent to three perimeter triangles (t0, t1, t2), each sharing one
edge. The BFS seeded at t0 enqueues t3 via e1(t0), then t1 enqueues t3 again via its
shared edge — second pop finds t3 already marked, Branch 2 fires.

  v0 = top, v1 = left, v2 = right, v3 = bottom (center hub: v4)
  t0 = (v0, v4, v1)  — seed; shares (v0,v4) with t3? No — t4 is center.

Simpler layout: 4 outer + 1 center vertex:
  t0 = (v0, v1, vc)  — seed
  t1 = (v1, v2, vc)  — adjacent to t0 via (v1,vc); also adjacent to t3 via (v2,vc)
  t2 = (v2, v3, vc)  — adjacent to t1 via (v2,vc); also adjacent to t3 via (v3,vc)
  t3 = (v3, v0, vc)  — adjacent to t2 via (v3,vc) and to t0 via (v0,vc)

BFS from t0: enqueue t1 and t3 (both neighbors of t0). Pop t1 → enqueue t2 and re-enqueue
t3 (already in queue). Pop t3 → mark. Pop t2 → mark. Pop t3 again → IS_VISITED true → Branch 2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me461",
             title="selectConnectedComponent unvisited_triangle_check: BFS skips already-marked triangle on second dequeue",
             defect_class="disconnected_components")

# Center vertex and 4 outer vertices forming a wheel (pinwheel fan).
vc = m.vertex(0.0,  0.0, 0.0)   # center hub
v0 = m.vertex(0.0,  2.0, 0.0)   # top
v1 = m.vertex(-2.0, 0.0, 0.0)   # left
v2 = m.vertex(0.0, -2.0, 0.0)   # bottom
v3 = m.vertex(2.0,  0.0, 0.0)   # right

# Four fan triangles — each shares one spoke edge with the center.
t0 = m.triangle(v0, v1, vc)    # 0: seed; shares spokes (v0,vc) and (v1,vc)
t1 = m.triangle(v1, v2, vc)    # 1: shares (v1,vc) with t0; also shares (v2,vc) with t2
t2 = m.triangle(v2, v3, vc)    # 2: shares (v2,vc) with t1; also shares (v3,vc) with t3
t3 = m.triangle(v3, v0, vc)    # 3: shares (v3,vc) with t2 AND (v0,vc) with t0 → reachable via 2 paths

# All four spoke edges are interior (shared by exactly 2 triangles).
m.assert_edge_shared(v0, vc, 2)   # spoke shared by t0 and t3
m.assert_edge_shared(v1, vc, 2)   # spoke shared by t0 and t1
m.assert_edge_shared(v2, vc, 2)   # spoke shared by t1 and t2
m.assert_edge_shared(v3, vc, 2)   # spoke shared by t2 and t3

# All outer rim edges are boundary (shared by exactly 1 triangle each).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v0, 1)

# Single connected component: all 4 triangles reachable from t0.
# Euler: V=5, E=8 (4 interior spokes + 4 boundary rim), F=4, chi = 5 - 8 + 4 = 1.
m.assert_euler_characteristic(v=5, e=8, f=4, chi=1)
