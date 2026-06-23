"""Me105 — unlink_triangle_v3_edge_ref_boundary: v3's reference edge must be
updated to a boundary edge after the triangle is unlinked.

MeshFix `Basic_TMesh.unlinkTriangle` Branch 6 (*edge_reference_update_v3*):
'if (e1->isOnBoundary())' — after unlinking, e1 (the base edge connecting v1
to v2 in MeshFix notation, i.e. the edge of the target triangle opposite the
third vertex v3) is or becomes a boundary edge. v3->e0 must be updated to
reference the newly-boundary e1.

In MeshFix: for target triangle t=(v1,v2,v3), edge e1=(v1,v2), e2=(v2,v3),
e3=(v3,v1). Branch 6 tests e1->isOnBoundary() and sets v3->e0 = e1.

Geometry:
  A three-triangle fan with a shared apex (v3), where the base edge of the
  target triangle (e1 = (v0,v1)) is shared with exactly one other triangle
  (making it interior = shared by 2). After target t0 is unlinked, e1 becomes
  a boundary edge and Branch 6 updates v3->e0 to e1.

  Wait — if e1 is shared by t0 and t1, after t0 is removed e1 is on t1 alone →
  now boundary. Branch 6 condition: e1->isOnBoundary() AFTER the unlink.

  Layout:
    v0=(0,0,0), v1=(2,0,0)  — base
    v2=(1,1,0)  — apex (v3 in MeshFix)
    v3=(1,2,0)  — upper vertex in t1 (which shares base with t0)

    t0 = (v0, v1, v2)   ← target
    t1 = (v0, v3, v1)   ← shares edge (v0,v1) = e1 with t0

  After t0 is unlinked, (v0,v1) is in t1 only → becomes boundary.
  Branch 6: e1->isOnBoundary() → set v2->e0 = e1.
  Note: v2=(1,1,0) is the "v3" (third vertex / apex) in MeshFix's convention.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me105",
             title="unlink_triangle_v3_edge_ref_boundary: apex v3 reference edge updated to newly-boundary base edge",
             defect_class="unlink_edge_ref_v3")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — base left
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — base right
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — apex = "v3" in MeshFix notation
v3 = m.vertex(1.0, 2.0, 0.0)   # 3 — upper vertex in the adjacent triangle

# Target triangle t0; v2 is the apex (third vertex in MeshFix).
t0 = m.triangle(v0, v1, v2)    # 0 — target

# Adjacent triangle sharing the base edge (v0,v1).
t1 = m.triangle(v0, v3, v1)    # 1 — shares (v0,v1) with t0

# Base edge e1=(v0,v1) shared by t0 and t1 → interior now, boundary after unlink.
m.assert_edge_shared(v0, v1, 2)   # interior: shared by t0 and t1

# Lateral edges of t0 at apex v2: both boundary (in t0 only).
m.assert_edge_shared(v0, v2, 1)   # boundary
m.assert_edge_shared(v1, v2, 1)   # boundary

# Remaining edges of t1: all boundary.
m.assert_edge_shared(v0, v3, 1)   # boundary
m.assert_edge_shared(v1, v3, 1)   # boundary
