"""Me631 — Basic_TMesh.growSelection branch 2: vertex_marking.

MeshFix `Basic_TMesh.growSelection` Branch 2 (*vertex_marking*) @ line 700:
  'MARK_VISIT(v1); MARK_VISIT(v2); MARK_VISIT(v3);'
  — within the IS_VISITED(t) block, all three vertex pointers of the
  selected triangle are individually marked. Branch 2 emphasizes that
  three separate MARK_VISIT calls execute — one per vertex — creating
  the vertex frontier for the upcoming neighbor-check pass.

Defect pattern: a 5-triangle mesh with a shared interior vertex (v0)
  and a pre-selected triangle t0 that contributes all three of its
  vertices (v0, v1, v2) to the marking frontier. The other triangles
  share edges with t0 via the vertex-marked boundary: after the marking
  pass the vertices v0, v1, v2 carry VISITED flags that will trigger
  selection of t1, t2 in the second pass.
  Shared edges demonstrate that the topology is connected; boundary
  edges confirm the open surface.

Geometry:
  v0=(0,0,0) interior shared vertex
  v1=(2,0,0), v2=(0,2,0) — two vertices of pre-selected t0
  v3=(-1,0,0), v4=(0,-1,0) — outer rim for unselected neighbors
  v5=(2,2,0) — second neighbor of v1-v2 edge
  t0=(v0,v1,v2) pre-selected; MARK_VISIT on v0, v1, v2 → Branch 2
  t1=(v0,v2,v3) shares edge (v0,v2) — unselected neighbor
  t2=(v0,v3,v4) shares edge (v0,v3) — further unselected
  t3=(v0,v4,v1) shares edges (v0,v4) and (v0,v1) — closes fan
  t4=(v1,v2,v5) shares edge (v1,v2) with t0 — unselected boundary neighbor
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me631",
    title="growSelection vertex_marking: MARK_VISIT(v1); MARK_VISIT(v2); MARK_VISIT(v3) on t0's three vertices; 5-triangle fan (Branch 2)",
    defect_class="non_manifold_edge",
)

v0 = m.vertex(0.0,  0.0, 0.0)  # 0 — interior shared vertex
v1 = m.vertex(2.0,  0.0, 0.0)  # 1 — outer rim; vertex of t0 and t3,t4
v2 = m.vertex(0.0,  2.0, 0.0)  # 2 — outer rim; vertex of t0 and t1,t4
v3 = m.vertex(-1.0, 0.0, 0.0)  # 3 — outer rim W
v4 = m.vertex(0.0, -1.0, 0.0)  # 4 — outer rim S
v5 = m.vertex(2.0,  2.0, 0.0)  # 5 — apex for t4

# Pre-selected triangle; Branch 2 marks v0, v1, v2 individually.
t0 = m.triangle(v0, v1, v2)  # 0: pre-selected

# Unselected neighbors in the fan around v0.
t1 = m.triangle(v0, v2, v3)  # 1: shares edge (v0,v2) with t0
t2 = m.triangle(v0, v3, v4)  # 2: shares edge (v0,v3) with t1
t3 = m.triangle(v0, v4, v1)  # 3: shares (v0,v4) with t2; (v0,v1) with t0

# Unselected neighbor sharing the (v1,v2) edge of t0.
t4 = m.triangle(v1, v2, v5)  # 4: shares edge (v1,v2) with t0

# Fan interior edges (shared by 2 triangles).
m.assert_edge_shared(v0, v1, 2)  # t0, t3
m.assert_edge_shared(v0, v2, 2)  # t0, t1
m.assert_edge_shared(v0, v3, 2)  # t1, t2
m.assert_edge_shared(v0, v4, 2)  # t2, t3

# Edge (v1,v2) shared by t0 and t4 — key edge demonstrating vertex-marking
# propagation will reach t4 via both v1 and v2 being marked.
m.assert_edge_shared(v1, v2, 2)  # t0, t4

# Boundary edges (each owned by exactly 1 triangle).
m.assert_edge_shared(v1, v4, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v5, 1)
m.assert_edge_shared(v2, v5, 1)

# Euler: V=6, E=10, F=5, chi=1 (open disk).
m.assert_euler_characteristic(6, 10, 5, 1)
