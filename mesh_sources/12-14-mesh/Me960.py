"""Me960 — CreateUnorientedTriangle_e1_slot_check: e1's first free t-slot (t1 or t2) is assigned.

MeshFix `Basic_TMesh.CreateUnorientedTriangle` Branch 1 (*e1_slot_check*) @ line 393:
  `if (e1->t1 == NULL) at1 = &(e1->t1); else if (e1->t2 == NULL) at1 = &(e1->t2);`
  Unlike CreateTriangle, no orientation test is performed. The function simply finds
  the first free slot on e1. If t1 is NULL it uses t1; otherwise it falls through to
  t2. This branch fires whenever a triangle is being created on a boundary edge.

Key difference from CreateTriangle (Me350-352): orientation (commonVertex check) is
absent. Any triangle adjacent to a boundary edge exercises this branch — the slot
assignment depends only on availability, not on which endpoint is shared.

Defect carrier: a single isolated boundary triangle plus a second triangle that
shares one of its edges. Edge e_shared starts as a boundary (t1 slot occupied by
t0, t2 slot NULL). When t1 is created on the same edge, Branch 1 falls through
to the `else if (e1->t2 == NULL)` path. A fresh triangle tf then exercises the
primary path (e1->t1 NULL → uses t1 immediately).

Geometry (flat XY plane):
  v0=(0,0,0), v1=(2,0,0), v2=(1,2,0), v3=(3,2,0)
  t0=(v0,v1,v2) — existing triangle; its edge (v1,v2) has t1 occupied
  t1=(v1,v3,v2) — second triangle sharing (v1,v2); e1->t2 slot used here
  tf=(v0,v2,v3) — third triangle; e1=(v0,v2) is a fresh boundary → t1 used
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me960",
    title="CreateUnorientedTriangle_e1_slot_check: find e1's first free t-slot (t1 or t2) without orientation (Branch 1)",
    defect_class="create_unoriented_triangle_slot",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
v3 = m.vertex(3.0, 2.0, 0.0)   # 3

# t0 occupies t1 slot of edge (v1,v2).
t0 = m.triangle(v0, v1, v2)   # 0

# t1 exercises the else-if path: e1=(v1,v2) has t1 occupied, so t2 is used.
t1 = m.triangle(v1, v3, v2)   # 1

# tf creates a fresh triangle; e1=(v0,v2) is a clean boundary, t1 slot is free.
tf = m.triangle(v0, v2, v3)   # 2

# Edge (v1,v2): occupied by t0 and t1 — both slots filled (n=2).
m.assert_edge_shared(v1, v2, 2)   # Branch 1 else-if path: e1->t2 used for t1

# Edge (v0,v2): shared by t0 and tf — Branch 1 primary path: e1->t1 used for tf.
m.assert_edge_shared(v0, v2, 2)   # Branch 1: e1->t1 assigned to tf

# Edge (v2,v3): shared by t1 and tf (interior).
m.assert_edge_shared(v2, v3, 2)

# Boundary edges (single-triangle).
m.assert_edge_shared(v0, v1, 1)   # t0 only
m.assert_edge_shared(v0, v3, 1)   # tf only
m.assert_edge_shared(v1, v3, 1)   # t1 only
