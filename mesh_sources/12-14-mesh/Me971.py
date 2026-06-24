"""Me971 — deselectConnectedComponent_visited_triangle_check: BFS skips unvisited triangles (Branch 2).

MeshFix `Basic_TMesh.deselectConnectedComponent` Branch 2 (*visited_triangle_check*) @ line 1102:
  'if (IS_VISITED(t)) { ... }'
  — each triangle dequeued from todo is checked: only triangles with the
  VISITED (selected) bit set are processed. Unvisited triangles are silently
  skipped. This branch controls whether the BFS expands through a given
  triangle.

Defect pattern: a 3-triangle connected strip where only the seed triangle
  and one neighbor are selected; the third triangle is NOT selected. When
  the BFS processes the seed (t0) and finds neighbor t2, t2 is unvisited
  (IS_VISITED==false) so the check fails and t2 is not added to todo.
  Only t0 and t1 are deselected (ns=2); t2 is left as-is.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(0.5,1,0), v4=(1.5,1,0)
  t0=(v0,v1,v3): selected (seed)
  t1=(v1,v4,v3): selected (neighbor — IS_VISITED=true, expanded)
  t2=(v1,v2,v4): NOT selected (IS_VISITED=false — visited_triangle_check fails)
  BFS: t0 enqueued → expands → t1 queued (selected) → t2 seen but NOT visited.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me971",
    title="deselectConnectedComponent_visited_triangle_check: IS_VISITED(t) guard skips unselected neighbor t2; only t0+t1 deselected (Branch 2)",
    defect_class="selection_partial",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(2.0, 0.0, 0.0)  # 2
v3 = m.vertex(0.5, 1.0, 0.0)  # 3
v4 = m.vertex(1.5, 1.0, 0.0)  # 4

t0 = m.triangle(v0, v1, v3)  # 0: selected seed
t1 = m.triangle(v1, v4, v3)  # 1: selected neighbor (IS_VISITED=true)
t2 = m.triangle(v1, v2, v4)  # 2: unselected neighbor (IS_VISITED=false — skipped)

# Interior shared edges.
m.assert_edge_shared(v1, v3, 2)  # t0 and t1 share this edge
m.assert_edge_shared(v1, v4, 2)  # t1 and t2 share this edge

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v1, v2, 1)

# t2 is reachable topologically from t0 (via t1) but IS_VISITED is false on t2,
# so the BFS visited_triangle_check gate prevents it from being deselected.
# The unselected triangle (t2) remains untouched.
# Euler: V=5, E=7, F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
