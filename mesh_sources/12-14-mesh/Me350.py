"""Me350 — CreateTriangle_e1_e2_orientation_check: e1 and e2 share v2, assign e1->t1.

MeshFix `Basic_TMesh.CreateTriangle` Branch 1 (*e1_e2_orientation_check*) @ line 365:
  `if (e1->commonVertex(e2) == e1->v2 && e1->t1 == NULL) at1 = &(e1->t1);`
  When e1 and e2 share e1's v2 endpoint and e1's t1 slot is free, the new triangle
  is assigned to e1->t1.

In the half-edge mesh, edges have two triangle slots (t1, t2). CreateTriangle
determines which slot to use for each of the three bounding edges. Branch 1 fires
when e1's "head" vertex (v2 in MeshFix) is the shared junction with e2, and t1 is
still available — meaning this is the first triangle incident on that edge side.

Defect carrier: a mesh with a boundary slot waiting to be filled. Two triangles
t0=(v0,v1,v2) and t1=(v1,v3,v2) share edge (v1,v2). A third fill triangle
tf=(v0,v2,v3) is created by CreateTriangle using e1=(v0,v2), e2=(v2,v3),
e3=(v3,v0). Edge e1 shares v2 with e2, so Branch 1 sets at1=&(e1->t1).

Geometry (flat XY plane):
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(3,2,0)
  t0=(v0,v1,v2), t1=(v1,v3,v2) — existing triangles
  tf=(v0,v2,v3) — newly created triangle (result of CreateTriangle)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me350",
    title="CreateTriangle_e1_e2_orientation_check: e1->v2==commonVertex(e1,e2), assign e1->t1 (Branch 1)",
    defect_class="create_triangle_orientation_slot",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
v3 = m.vertex(3.0, 2.0, 0.0)   # 3

# Existing triangles before CreateTriangle fires.
t0 = m.triangle(v0, v1, v2)   # 0
t1 = m.triangle(v1, v3, v2)   # 1

# New triangle created by CreateTriangle: tf uses edges e1=(v0,v2), e2=(v2,v3), e3=(v3,v0).
# Branch 1 fires: e1->commonVertex(e2) == e1->v2 == v2; e1->t1 slot is free.
tf = m.triangle(v0, v2, v3)   # 2

# The e1 edge (v0,v2) is now interior: shared by t0 and tf.
m.assert_edge_shared(v0, v2, 2)   # Branch 1: e1->t1 assigned to tf

# The e2 edge (v2,v3) is now interior: shared by t1 and tf.
m.assert_edge_shared(v2, v3, 2)

# The e3 edge (v0,v3) is a boundary (only tf).
m.assert_edge_shared(v0, v3, 1)

# (v1,v2) and (v0,v1) and (v1,v3) remain as expected.
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v1, 1)   # boundary
m.assert_edge_shared(v1, v3, 1)   # boundary
