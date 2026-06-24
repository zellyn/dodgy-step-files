"""Me961 — CreateUnorientedTriangle_e2_slot_check: e2's first free t-slot (t1 or t2) is assigned.

MeshFix `Basic_TMesh.CreateUnorientedTriangle` Branch 2 (*e2_slot_check*) @ line 396:
  `if (e2->t1 == NULL) at2 = &(e2->t1); else if (e2->t2 == NULL) at2 = &(e2->t2);`
  Analogous slot-first policy for the second bounding edge e2. The function picks
  t1 if free, otherwise t2. No orientation test.

Defect carrier: a rectangle split into two triangles, where the second edge (e2) of
the newly created triangle is the shared diagonal. The diagonal edge already has one
slot occupied when the second triangle is created, so Branch 2 falls through to the
`else if (e2->t2 == NULL)` path for that creation and uses the primary `t1` path for
the first.

Geometry:
  v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0)
  t0=(v0,v1,v2) — first triangle; diagonal e2=(v0,v2) gets t1 slot
  t1=(v0,v2,v3) — second triangle; diagonal e2=(v0,v2) already has t1 → uses t2

After both creations the diagonal (v0,v2) is interior (n=2), demonstrating that
Branch 2 found and filled both t1 (primary) and t2 (else-if) for e2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me961",
    title="CreateUnorientedTriangle_e2_slot_check: find e2's first free t-slot (t1 or t2) without orientation (Branch 2)",
    defect_class="create_unoriented_triangle_slot",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(2.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 2.0, 0.0)   # 3

# t0: diagonal (v0,v2) is e2; its t1 slot is filled (primary path of Branch 2).
t0 = m.triangle(v0, v1, v2)   # 0

# t1: diagonal (v0,v2) is e2 again; t1 occupied → else-if path fills t2.
t1 = m.triangle(v0, v2, v3)   # 1

# Diagonal (v0,v2): both slots filled — Branch 2 primary + else-if both exercised.
m.assert_edge_shared(v0, v2, 2)   # Branch 2: e2->t1 and e2->t2 used

# Boundary edges (single-triangle each).
m.assert_edge_shared(v0, v1, 1)   # t0 only
m.assert_edge_shared(v1, v2, 1)   # t0 only
m.assert_edge_shared(v2, v3, 1)   # t1 only
m.assert_edge_shared(v0, v3, 1)   # t1 only

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(v=4, e=5, f=2, chi=1)
