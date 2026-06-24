"""Me962 — CreateUnorientedTriangle_e3_slot_check: e3's first free t-slot (t1 or t2) is assigned.

MeshFix `Basic_TMesh.CreateUnorientedTriangle` Branch 3 (*e3_slot_check*) @ line 399:
  `if (e3->t1 == NULL) at3 = &(e3->t1); else if (e3->t2 == NULL) at3 = &(e3->t2);`
  Analogous slot-first policy for the third bounding edge e3. No orientation test.

Defect carrier: three triangles forming a fan around a central vertex. The third
bounding edge of each new fan triangle is a radial spoke from the center. For the
first triangle the spoke is a fresh boundary (t1 used). For the second triangle the
same spoke is shared (t2 used for the outer part), demonstrating that Branch 3
correctly traverses t1 → t2 for e3.

Geometry:
  v0=(1,1,0) — fan center
  v1=(0,0,0), v2=(2,0,0), v3=(2,2,0)
  t0=(v0,v1,v2) — e3=(v0,v1) is a fresh boundary; Branch 3 uses t1
  t1=(v0,v2,v3) — e3=(v0,v2) already has t1 from t0; Branch 3 uses t2
  t2=(v0,v3,v1) — closes the fan; e3=(v0,v3) fresh boundary → t1 used

All three radial spokes end up interior (n=2) after the fan is complete.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me962",
    title="CreateUnorientedTriangle_e3_slot_check: find e3's first free t-slot (t1 or t2) without orientation (Branch 3)",
    defect_class="create_unoriented_triangle_slot",
)

v0 = m.vertex(1.0, 1.0, 0.0)   # 0 — fan center
v1 = m.vertex(0.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(2.0, 2.0, 0.0)   # 3

# t0: e3=(v0,v1) fresh → Branch 3 primary path (t1 used).
t0 = m.triangle(v0, v1, v2)   # 0

# t1: e3=(v0,v2) already has t1 from t0 → Branch 3 else-if path (t2 used).
t1 = m.triangle(v0, v2, v3)   # 1

# t2: closes the fan; e3=(v0,v3) fresh → Branch 3 primary path (t1 used).
t2 = m.triangle(v0, v3, v1)   # 2

# Interior radial spokes — Branch 3 filled both t-slots on each.
m.assert_edge_shared(v0, v1, 2)   # shared by t0 and t2
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v3, 2)   # shared by t1 and t2

# Outer rim boundary edges.
m.assert_edge_shared(v1, v2, 1)   # t0 only
m.assert_edge_shared(v2, v3, 1)   # t1 only
m.assert_edge_shared(v1, v3, 1)   # t2 only

# Euler: V=4, E=6, F=3, chi=1 (open fan disk).
m.assert_euler_characteristic(v=4, e=6, f=3, chi=1)
