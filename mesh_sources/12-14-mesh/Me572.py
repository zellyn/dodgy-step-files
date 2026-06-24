"""Me572 — Basic_TMesh.invertSelection branch 3: neighbor_t1_same_state — t1 of seed in same selection state; toggle via t1 path.

MeshFix `Basic_TMesh.invertSelection` Branch 3 (*neighbor_t1_same_state*) @ line 752:
  'if (s->t1() != NULL && ((IS_VISITED(s) && unmark) || (!IS_VISITED(s) && !unmark)))'
  — during BFS, for each dequeued triangle s, the algorithm checks whether the t1
  neighbor is in the same toggle-state. When the condition is true, t1 is inverted
  and enqueued. Branch 3 fires when the t1 neighbor of s matches the toggle direction.

Defect pattern: two triangles sharing edge (v0,v1) where t1 of the seed triangle
  is the adjacent triangle. The seed (t0=index 0) is dequeued; its t1 neighbor
  (index 1, adjacent via edge v0-v1) is also unmarked (same state as seed).
  Condition fires: !IS_VISITED(t1_neighbor) && !unmark → Branch 3 enqueues it.

Geometry (two triangles sharing edge v0-v1, "butterfly" shape):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,-1,0)
  t0=(v0,v2,v1): seed triangle; its t1 edge is the shared edge (v0,v1) → neighbor is t1
  t1=(v0,v1,v3): neighbor reached via t1 path of t0
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me572",
    title="Basic_TMesh.invertSelection neighbor_t1_same_state: t1 of seed is unmarked neighbor; BFS enqueues via t1 edge path (Branch 3)",
    defect_class="mesh_selection_toggle",
)

v0 = m.vertex(0.0,  0.0, 0.0)  # 0
v1 = m.vertex(1.0,  0.0, 0.0)  # 1
v2 = m.vertex(0.5,  1.0, 0.0)  # 2 — above shared edge
v3 = m.vertex(0.5, -1.0, 0.0)  # 3 — below shared edge

# Two triangles sharing edge (v0,v1): t0 and t1 neighbors in same state.
t0 = m.triangle(v0, v2, v1)  # 0: seed; its t1 (e1=v0-v1) neighbor is t1
t1 = m.triangle(v0, v1, v3)  # 1: reached via t1 path

# Shared edge (v0,v1) — the t1 edge of t0; n=2 confirms adjacency.
m.assert_edge_shared(v0, v1, 2)

# Outer boundary edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v2, v1, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# v2 and v3 have no shared triangle: they are on opposite sides of the shared edge.
m.assert_vertex_pair_no_shared_triangle(v2, v3)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
