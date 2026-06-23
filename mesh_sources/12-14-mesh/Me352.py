"""Me352 — CreateTriangle_e3_e1_orientation_check: e3 and e1 share v2, assign e3->t1.

MeshFix `Basic_TMesh.CreateTriangle` Branch 3 (*e3_e1_orientation_check*) @ line 371:
  `if (e3->commonVertex(e1) == e3->v2 && e3->t1 == NULL) at3 = &(e3->t1);`
  When e3 and e1 share e3's v2 endpoint and e3's t1 slot is free, the new triangle
  is assigned to e3->t1.

This is the symmetric check for the third bounding edge e3. The junction between
e3 and e1 is where e3's "head" (v2 in MeshFix) meets e1's tail, exactly matching
the Branch 3 guard. With e3->t1 free the new triangle claims that slot.

Defect carrier: two existing triangles and a gap triangle to be filled.
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(1,1,0)
  tA=(v0,v1,v3) and tB=(v1,v2,v3) — existing triangles
  tf=(v0,v3,v2) — the new triangle filling the remaining gap
  e3=(v0,v3) from tf's perspective; its head v3 is also the junction with e1=(v3,v2).
  Branch 3: e3->commonVertex(e1) == e3->v2 == v3; e3->t1 free → at3 = &(e3->t1).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me352",
    title="CreateTriangle_e3_e1_orientation_check: e3->v2==commonVertex(e3,e1), assign e3->t1 (Branch 3)",
    defect_class="create_triangle_orientation_slot",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3

# Existing triangles.
tA = m.triangle(v0, v1, v3)   # 0
tB = m.triangle(v1, v2, v3)   # 1

# New triangle tf filling the remaining sector.
# e3=(v0,v3): head=v3, which is also junction with e1=(v3,v2). Branch 3 fires.
tf = m.triangle(v0, v3, v2)   # 2

# e3=(v0,v3): now shared by tA and tf (tA already occupied t2, tf gets t1).
m.assert_edge_shared(v0, v3, 2)   # Branch 3: e3->t1 assigned to tf

# e1=(v2,v3): now shared by tB and tf.
m.assert_edge_shared(v2, v3, 2)

# (v0,v1): shared by tA only (boundary).
m.assert_edge_shared(v0, v1, 1)

# (v1,v3): shared by tA and tB — interior.
m.assert_edge_shared(v1, v3, 2)

# (v1,v2): shared by tB only.
m.assert_edge_shared(v1, v2, 1)

# (v0,v2): shared by tf only (the gap-closing edge, boundary).
m.assert_edge_shared(v0, v2, 1)
