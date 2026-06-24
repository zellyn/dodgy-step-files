"""Me710 — Basic_TMesh.removeVertices branch 1: list_head_initialization.

MeshFix `Basic_TMesh.removeVertices` Branch 1 (*list_head_initialization*) @ line 606:
  'n = V.head();' — traversal of the vertex list begins by fetching the list head.
  This branch fires for any non-empty mesh; the pointer n is set to the first
  vertex in V so the while-loop can walk the linked list.

Defect pattern: a minimal valid triangle mesh (one triangle, three vertices).
  No isolated vertices — the list head is simply initialized and the loop
  walks all three vertices without removing any. The list_head_initialization
  branch fires as soon as the traversal begins.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0) — one triangle t0=(v0,v1,v2).
  Three boundary edges each shared by exactly 1 triangle.
  Euler: V=3, E=3, F=1, chi=1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me710",
    title="Basic_TMesh.removeVertices list_head_initialization: V.head() called on 3-vertex mesh; traversal begins (Branch 1)",
    defect_class="isolated_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0
v1 = m.vertex(1.0, 0.0, 0.0)  # 1
v2 = m.vertex(0.0, 1.0, 0.0)  # 2

t0 = m.triangle(v0, v1, v2)

# All three boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Euler: V=3, E=3, F=1, chi=1.
m.assert_euler_characteristic(3, 3, 1, 1)
