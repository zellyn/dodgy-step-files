"""Me965 — CreateUnorientedTriangle_mesh_list_append: T.appendHead(tt) inserts triangle into list T.

MeshFix `Basic_TMesh.CreateUnorientedTriangle` Branch 6 (*mesh_list_append*) @ line 405:
  `T.appendHead(tt);`
  After the adjacency slots are set (*at1=*at2=*at3=tt), the new triangle tt is
  prepended to the mesh's triangle list T. Without this step the triangle object
  exists but is invisible to all mesh traversals and counts.

This branch is structurally identical to CreateTriangle Branch 6 (Me355) but is
reached through the unoriented creation path. Any well-formed mesh where multiple
triangles were created by CreateUnorientedTriangle exercises this branch for each
triangle, since each call ends with T.appendHead(tt).

Defect carrier: four triangles tiling a square, each added by a CreateUnoriented-
Triangle call's T.appendHead. All four appear in the mesh list (confirmed by Euler
count V=5, E=8, F=4, chi=1 — open disk with central vertex). Interior shared edges
(n=2) prove each triangle was fully registered in T and adjacency is correct.

Geometry:
  v0=(1,1,0) — center, v1=(0,0,0), v2=(2,0,0), v3=(2,2,0), v4=(0,2,0)
  t0=(v0,v1,v2), t1=(v0,v2,v3), t2=(v0,v3,v4), t3=(v0,v4,v1) — four fan triangles
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me965",
    title="CreateUnorientedTriangle_mesh_list_append: T.appendHead(tt) inserts triangle into list T (Branch 6)",
    defect_class="create_unoriented_triangle_list_append",
)

v0 = m.vertex(1.0, 1.0, 0.0)   # 0 — fan center
v1 = m.vertex(0.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(2.0, 2.0, 0.0)   # 3
v4 = m.vertex(0.0, 2.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v2)   # 0 — appended by T.appendHead(tt)
t1 = m.triangle(v0, v2, v3)   # 1 — appended by T.appendHead(tt)
t2 = m.triangle(v0, v3, v4)   # 2 — appended by T.appendHead(tt)
t3 = m.triangle(v0, v4, v1)   # 3 — appended by T.appendHead(tt)

# Interior fan edges (each shared by two adjacent fan triangles).
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t3
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2
m.assert_edge_shared(v0, v4, 2)   # shared by t2 and t3

# Outer rim boundary edges (each owned by exactly one triangle).
m.assert_edge_shared(v1, v2, 1)   # t0 only
m.assert_edge_shared(v2, v3, 1)   # t1 only
m.assert_edge_shared(v3, v4, 1)   # t2 only
m.assert_edge_shared(v1, v4, 1)   # t3 only

# Euler: V=5, E=8, F=4, chi=1 (open square fan disk).
m.assert_euler_characteristic(v=5, e=8, f=4, chi=1)
