"""Me355 — CreateTriangle_mesh_list_append: T.appendHead(tt) inserts triangle into mesh list.

MeshFix `Basic_TMesh.CreateTriangle` Branch 6 (*mesh_list_append*) @ line 377:
  `T.appendHead(tt);`
  After the adjacency slots are set, the new triangle tt is prepended to the mesh's
  triangle list T. This is the list-membership step: without it the triangle exists
  as an object but is invisible to all mesh traversals (iterators, counts, etc.).

Defect carrier: a mesh with three triangles forming a fan around a central vertex.
All three were added via CreateTriangle's T.appendHead(tt), so they all appear in
the mesh list and share interior edges — only possible if each was properly appended.
A mesh with a missing T.appendHead would lose count (e.g. n_triangles mismatch).

Geometry (fan around apex):
  Center v0=(1,1,0), outer ring v1=(0,0,0), v2=(2,0,0), v3=(2,2,0), v4=(0,2,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4) — three fan triangles
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me355",
    title="CreateTriangle_mesh_list_append: T.appendHead(tt) inserts triangle into list T (Branch 6)",
    defect_class="create_triangle_list_append",
)

v0 = m.vertex(1.0, 1.0, 0.0)   # 0 — fan apex
v1 = m.vertex(0.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(2.0, 2.0, 0.0)   # 3
v4 = m.vertex(0.0, 2.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v2)   # 0 — appended by T.appendHead(tt)
t1 = m.triangle(v0, v2, v3)   # 1 — appended by T.appendHead(tt)
t2 = m.triangle(v0, v3, v4)   # 2 — appended by T.appendHead(tt)

# Interior fan edges (each shared by two adjacent fan triangles).
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2

# Boundary edges (each owned by exactly one triangle).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v0, v4, 1)

# Euler: V=5, E=7, F=3, chi=1 (open fan disk).
m.assert_euler_characteristic(v=5, e=7, f=3, chi=1)
