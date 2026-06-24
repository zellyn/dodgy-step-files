"""Me574 — Basic_TMesh.invertSelection branch 5: neighbor_t3_same_state — t3 of seed in same selection state; toggle via t3 path.

MeshFix `Basic_TMesh.invertSelection` Branch 5 (*neighbor_t3_same_state*) @ line 756:
  'if (s->t3() != NULL && ((IS_VISITED(s) && unmark) || (!IS_VISITED(s) && !unmark)))'
  — during BFS, after processing t1 and t2, the algorithm checks whether the t3
  neighbor is in the same toggle-state. Branch 5 fires when the t3 neighbor of
  dequeued triangle s matches the toggle direction.

Defect pattern: a triangle strip where the seed's e3 edge (third edge, v2-v0) is
  shared with a neighbor that is in the same toggle state. e1 and e2 are boundary
  edges on the seed, so only the t3 path fires for the seed.

Geometry (three-triangle strip):
  v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(-1,1,0), v4=(-2,0,0)
  t0=(v0,v1,v2): seed; its e3 edge (v2,v0) is shared with t1 (t3 path)
  t1=(v3,v0,v2): reached via t3 path of t0 (shares v0-v2)
  t2=(v3,v4,v0): shares edge (v3,v0) with t1
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me574",
    title="Basic_TMesh.invertSelection neighbor_t3_same_state: t3 of seed is unmarked neighbor; BFS enqueues via t3 edge path (Branch 5)",
    defect_class="mesh_selection_toggle",
)

v0 = m.vertex( 0.0, 0.0, 0.0)  # 0 — center base
v1 = m.vertex( 2.0, 0.0, 0.0)  # 1 — right base
v2 = m.vertex( 1.0, 1.0, 0.0)  # 2 — right apex
v3 = m.vertex(-1.0, 1.0, 0.0)  # 3 — left apex
v4 = m.vertex(-2.0, 0.0, 0.0)  # 4 — left base

# Seed t0 — its e3 edge (v2,v0) is shared with t1 (t3 path).
t0 = m.triangle(v0, v1, v2)  # 0: seed; t3 neighbor shares (v2,v0)
t1 = m.triangle(v3, v0, v2)  # 1: reached via t3 path of t0
t2 = m.triangle(v3, v4, v0)  # 2: reached via t1/t2/t3 path of t1

# t3 edge of t0 = e3 = (v2,v0): shared with t1.
m.assert_edge_shared(v0, v2, 2)  # t0-t1 via t3 path
# Shared edge t1-t2.
m.assert_edge_shared(v0, v3, 2)  # t1-t2

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v4, 1)

# v1 and v4 share no triangle (opposite ends of strip).
m.assert_vertex_pair_no_shared_triangle(v1, v4)
m.assert_vertex_pair_no_shared_triangle(v1, v3)

# Euler: V=5, E=7, F=3, chi=1.
m.assert_euler_characteristic(5, 7, 3, 1)
