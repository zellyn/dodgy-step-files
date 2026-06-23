"""Me220 — eulerUpdate_component_discovery: BFS discovers second disconnected shell (Branch 1).

MeshFix `Basic_TMesh.eulerUpdate` Branch 1 (*component_discovery*) @ line 1747:
  '!IS_BIT(t, 5)' — triangle not yet visited by connected-component BFS.
  'n_shells++' — new shell found, increment shell count.

When eulerUpdate walks all triangles and finds one with bit 5 unset (unvisited),
it seeds a new connected-component BFS from that triangle. Each such seed
increments n_shells. This fixture has two completely disconnected triangles so
eulerUpdate must seed twice: once for each component.

Geometry: two non-adjacent triangles with no shared edge.
  T0 = (v0, v1, v2) — first shell at z=0
  T1 = (v3, v4, v5) — second shell at z=5 (far away, definitely separate)

Shell count after eulerUpdate: 2 (two separate connected components).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me220",
             title="eulerUpdate_component_discovery: two disconnected shells force n_shells++ twice",
             defect_class="disconnected_shell")

# Shell 1: triangle at z=0
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

# Shell 2: triangle at z=5 — completely separate
v3 = m.vertex(0.0, 0.0, 5.0)   # 3
v4 = m.vertex(1.0, 0.0, 5.0)   # 4
v5 = m.vertex(0.5, 1.0, 5.0)   # 5

t0 = m.triangle(v0, v1, v2)   # 0 — shell 1
t1 = m.triangle(v3, v4, v5)   # 1 — shell 2

# Shell 1 cannot reach shell 2 through shared edges.
m.assert_triangle_not_reachable_from(target=t1, source=t0)

# All edges are boundary (each triangle has 3 boundary edges).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)
