"""Me712 — Basic_TMesh.removeVertices branch 3: vertex_removal.

MeshFix `Basic_TMesh.removeVertices` Branch 3 (*vertex_removal*) @ line 614:
  'n = V.removeCell(v); delete v;' — after an orphan vertex is identified (e0==NULL),
  it is unlinked from the doubly-linked vertex list via V.removeCell and its memory
  is freed. This branch fires for every orphan vertex that is actually deleted.

Defect pattern: single triangle plus two isolated vertices (v3 at (3,3,0) and
  v4 at (4,4,0)). Each isolated vertex is encountered by the while-loop, passes
  the e0==NULL check, and is removed via V.removeCell + delete. The removal step
  executes twice — once per orphan — covering the vertex_removal branch.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0) — one triangle t0=(v0,v1,v2).
  v3=(3,3,0) and v4=(4,4,0) are isolated (not referenced by any triangle).
  Three boundary edges; Euler ignoring isolated vertices: V=5, E=3, F=1, chi=-1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me712",
    title="Basic_TMesh.removeVertices vertex_removal: V.removeCell+delete fires for each of 2 isolated vertices v3,v4 (Branch 3)",
    defect_class="isolated_vertex",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(3.0, 3.0, 0.0)   # 3 — isolated; will be removed
v4 = m.vertex(4.0, 4.0, 0.0)   # 4 — isolated; will be removed

t0 = m.triangle(v0, v1, v2)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)

# Both isolated vertices — V.removeCell + delete fires for each.
m.assert_isolated_vertex(v3)
m.assert_isolated_vertex(v4)
