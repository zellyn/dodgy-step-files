"""Me480 — removeTriangles list_head_initialization: BFS init from triangle list head.

Basic_TMesh.removeTriangles branch 1: list_head_initialization —
  `Node *n = T.head(); while (n != NULL) { ... n = n->next(); }`

The traversal of the orphan-triangle list always begins at T.head(). Any
non-empty mesh exercises this initialization step: the algorithm enters the
while-loop because n is not NULL. Two valid triangles sharing a vertex
demonstrate the minimal mesh where removeTriangles would begin list traversal.
Neither triangle has a nulled edge pointer (both are intact), so the null-edge
removal branches are not taken, but the list-head initialization at Branch 1 is
unconditionally exercised on any non-empty mesh.

Geometry (z = 0):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(2,0,0)
  t0 = (v0, v1, v2) — healthy triangle, area=0.5
  t1 = (v1, v3, v2) — healthy triangle, area=0.5
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me480",
             title="removeTriangles list_head_initialization: BFS init from T.head() on 2-triangle mesh (Branch 1)",
             defect_class="open_boundary")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(2.0, 0.0, 0.0)   # 3

t0 = m.triangle(v0, v1, v2)    # 0 — healthy
t1 = m.triangle(v1, v3, v2)    # 1 — healthy

# Both triangles are valid; T.head() is non-NULL — list-head init fires.
# Interior shared-vertex edge between t0 and t1.
m.assert_edge_shared(v1, v2, 2)

# Boundary edges each incident on one triangle.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Euler: V=4, E=5, F=2, chi=4-5+2=1 (open disk)
m.assert_euler_characteristic(4, 5, 2, 1)
