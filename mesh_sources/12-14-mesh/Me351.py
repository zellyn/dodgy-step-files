"""Me351 — CreateTriangle_e2_e3_orientation_check: e2 and e3 share v2, assign e2->t1.

MeshFix `Basic_TMesh.CreateTriangle` Branch 2 (*e2_e3_orientation_check*) @ line 368:
  `if (e2->commonVertex(e3) == e2->v2 && e2->t1 == NULL) at2 = &(e2->t1);`
  When e2 and e3 share e2's v2 endpoint and e2's t1 slot is free, the new triangle
  is assigned to e2->t1.

This is the analogous check for the second bounding edge e2. In the oriented
half-edge representation each edge has a "head" (v2) and "tail" (v1). If e2's head
vertex is the junction with e3, and e2->t1 is unoccupied, CreateTriangle sets
at2 = &(e2->t1) — the same pattern as Branch 1 but applied to e2.

Defect carrier: two triangles sharing edge (v1,v2). The reference triangle tref
occupies one slot of (v1,v2); the new triangle tf claims the other (e2->t1).
In tf, e2=(v1,v2) has its v2 head at v2, which is also the start of e3=(v2,v3).
Branch 2 fires because e2->commonVertex(e3)==e2->v2 and e2->t1 is free.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0)
  tref=(v0,v1,v2) — reference triangle (shares edge v1-v2 with tf)
  tf=(v3,v1,v2)   — new triangle; e2=(v1,v2) head=v2 = junction with e3=(v2,v3)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me351",
    title="CreateTriangle_e2_e3_orientation_check: e2->v2==commonVertex(e2,e3), assign e2->t1 (Branch 2)",
    defect_class="create_triangle_orientation_slot",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3

# Reference triangle: occupies one t-slot of edge (v1,v2).
tref = m.triangle(v0, v1, v2)   # 0

# New triangle tf: e2=(v1,v2) with head=v2 = junction with e3=(v2,v3).
# Branch 2 fires: e2->commonVertex(e3) == e2->v2 == v2; e2->t1 free → at2 = &(e2->t1).
tf = m.triangle(v3, v1, v2)   # 1

# e2 = (v1,v2): now shared by tref and tf — Branch 2 wrote tf into e2->t1.
m.assert_edge_shared(v1, v2, 2)   # Branch 2: e2->t1 assigned to tf

# e3 = (v2,v3): boundary edge (tf only).
m.assert_edge_shared(v2, v3, 1)

# Other boundary edges.
m.assert_edge_shared(v0, v1, 1)   # tref only
m.assert_edge_shared(v0, v2, 1)   # tref only
m.assert_edge_shared(v1, v3, 1)   # tf only (e_other boundary)
