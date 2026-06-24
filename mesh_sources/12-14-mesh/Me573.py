"""Me573 — Basic_TMesh.invertSelection branch 4: neighbor_t2_same_state — t2 of seed in same selection state; toggle via t2 path.

MeshFix `Basic_TMesh.invertSelection` Branch 4 (*neighbor_t2_same_state*) @ line 754:
  'if (s->t2() != NULL && ((IS_VISITED(s) && unmark) || (!IS_VISITED(s) && !unmark)))'
  — during BFS, after processing t1, the algorithm checks whether the t2 neighbor
  is in the same toggle-state. Branch 4 fires when the t2 neighbor of dequeued
  triangle s matches the toggle direction.

Defect pattern: three triangles where the seed has a t2 neighbor (same toggle state)
  but no t1 neighbor (so only the t2 path fires for the seed). A strip where the
  seed triangle connects to t1_neighbor via e2 (t2's edge) while e1 is a boundary.

Geometry (three coplanar triangles, strip):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(3,1,0), v4=(4,0,0)
  t0=(v0,v1,v2): seed; its t2 edge (e2 = v1-v2) is shared with t1
  t1=(v1,v3,v2): reached via t2 path of t0 (shares v1-v2)
  t2=(v1,v4,v3): shares edge (v1,v3) with t1
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me573",
    title="Basic_TMesh.invertSelection neighbor_t2_same_state: t2 of seed is unmarked neighbor; BFS enqueues via t2 edge path (Branch 4)",
    defect_class="mesh_selection_toggle",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(2.0, 0.0, 0.0)  # 1 — shared hub
v2 = m.vertex(1.0, 1.0, 0.0)  # 2 — above left
v3 = m.vertex(3.0, 1.0, 0.0)  # 3 — above right
v4 = m.vertex(4.0, 0.0, 0.0)  # 4 — far right

# Seed t0 — its e2 edge (v1,v2) is shared with t1 (t2 path).
t0 = m.triangle(v0, v1, v2)  # 0: seed; t2 neighbor shares (v1,v2)
t1 = m.triangle(v1, v3, v2)  # 1: reached via t2 path of t0
t2 = m.triangle(v1, v4, v3)  # 2: reached via t1 path of t1

# t2 edge of t0 = e2 = (v1,v2): shared with t1.
m.assert_edge_shared(v1, v2, 2)  # t0-t1 via t2 path
# t1 edge of t1 = (v1,v3): shared with t2.
m.assert_edge_shared(v1, v3, 2)  # t1-t2 via t1 path

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# v0 and v3 have no shared triangle (opposite ends of strip).
m.assert_vertex_pair_no_shared_triangle(v0, v3)
m.assert_vertex_pair_no_shared_triangle(v0, v4)

# Euler: V=5, E=7, F=3, chi=1.
m.assert_euler_characteristic(5, 7, 3, 1)
