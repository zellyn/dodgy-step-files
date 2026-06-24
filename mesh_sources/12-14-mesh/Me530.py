"""Me530 — holeFilling::joinBoundaryLoops branch 1: NULL_VERTEX_INPUT.

MeshFix `holeFilling::joinBoundaryLoops` Branch 1 (*NULL_VERTEX_INPUT*) @ line 729:
  'if (gv == NULL || gw == NULL || !gv->isOnBoundary() || !gw->isOnBoundary()) return NULL'
  — input vertex is not on boundary; method returns NULL immediately.

Branch 1 fires when either gv or gw is an interior vertex (all incident edges
shared by 2 triangles — never on the mesh boundary). The algorithm cannot bridge
boundary loops if the supplied vertex is interior, so it returns NULL.

Geometry: a closed tetrahedron-like cap where every vertex is interior
(all incident edges n=2). The interior vertex has no boundary edges at all.
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(1,1,1)
  4 triangles forming a closed (fully bounded) surface cap — no open boundary.

All edges are shared by exactly 2 triangles. Every vertex is interior; passing
any vertex as gv to joinBoundaryLoops triggers Branch 1.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me530",
             title="joinBoundaryLoops_NULL_VERTEX_INPUT: all vertices interior; no boundary; Branch 1 returns NULL",
             defect_class="joinBoundaryLoops_null_vertex_input")

# Four vertices forming a closed triangulated cap.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 1.0)   # 3 — apex (interior)

# 4 triangles forming a closed surface (no boundary edges).
t0 = m.triangle(v0, v1, v2)   # 0 — base
t1 = m.triangle(v0, v1, v3)   # 1 — front face
t2 = m.triangle(v1, v2, v3)   # 2 — right face
t3 = m.triangle(v0, v2, v3)   # 3 — left face (closes the surface)

# All edges shared by exactly 2 triangles — no boundary edges exist.
# Every vertex is interior (all incident edges n=2).
m.assert_edge_shared(v0, v1, 2)   # base-front
m.assert_edge_shared(v1, v2, 2)   # base-right
m.assert_edge_shared(v0, v2, 2)   # base-left
m.assert_edge_shared(v0, v3, 2)   # front-left
m.assert_edge_shared(v1, v3, 2)   # front-right
m.assert_edge_shared(v2, v3, 2)   # right-left

# Euler: V=4, E=6, F=4, chi=2 (closed surface: sphere-like).
m.assert_euler_characteristic(4, 6, 4, 2)
