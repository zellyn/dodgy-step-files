"""Me104 — unlink_triangle_v2_edge_ref_boundary: v2's reference edge must be
updated to a boundary edge after the triangle is unlinked.

MeshFix `Basic_TMesh.unlinkTriangle` Branch 5 (*edge_reference_update_v2*):
'if (e3->isOnBoundary())' — after unlinking, the edge e3 (connecting v2 to v1
in MeshFix notation, i.e. the edge shared between v2 and the first vertex of
the target triangle) is or becomes a boundary edge. v2->e0 must be updated to
point at the newly-boundary e3.

Geometry — mirror of Me103 but for v2 (the second vertex of target t0):
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)
  v3=(1,1,0)  — apex

  t0 = (v0, v3, v2)   ← target; v2 is the THIRD position, but as the
                          second vertex in MeshFix's e3 sense (e3 connects v2→v1).
                          We arrange so that edge (v1,v2)=(v3,v2) in our notation
                          is interior and edge (v0,v2) is boundary.

  Simpler arrangement:
    t0 = (v0, v1, v2)   ← target
    t1 = (v0, v3, v1)   ← shares edge (v0,v1) with t0

  e3 for v2 in t0 = edge (v1,v2): in t0 only → BOUNDARY.
  After unlinking t0, v2 loses all its triangles; e3=(v1,v2) becomes the
  boundary edge v2->e0 must reference.

  Actually: use a 3-triangle fan at v2 so v2 remains connected after t0 is
  removed. Focus on the fact that e3 (the shared edge between v2 and v1 of t0
  in MeshFix) is the boundary edge that Branch 5 catches.

  Re-layout:
    v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0), v4=(2,0,0)
    t0 = (v0, v1, v2)   ← target (v2 = vertex 2)
    t1 = (v1, v4, v2)   ← shares edge (v1,v2) which is e3 for v2
                           → (v1,v2) shared by 2 → interior (not boundary)
    For Branch 5, we need e3 = edge (v2, <first-vertex-of-t0>) to be boundary.
    In MeshFix e3 connects v2 back to v1 of the triangle; if only t0 uses (v0,v2),
    that edge is boundary.

  Final layout:
    t0 = (v0, v1, v2)   — target
    t1 = (v0, v3, v1)   — shares (v0,v1) with t0; edge (v0,v2) boundary → Branch 5
    Edge (v0,v2) = e3 for v2 in t0: in t0 only → boundary → Branch 5 updates v2->e0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me104",
             title="unlink_triangle_v2_edge_ref_boundary: v2 reference edge updated to boundary after unlink",
             defect_class="unlink_edge_ref_v2")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2 — v2 of target triangle
v3 = m.vertex(-0.5, 1.0, 0.0)  # 3 — outer vertex in t1

# Target triangle t0.
t0 = m.triangle(v0, v1, v2)    # 0 — target

# Adjacent triangle sharing (v0,v1).
t1 = m.triangle(v0, v3, v1)    # 1 — shares edge (v0,v1) with t0

# e3 for v2 in t0 = edge (v0,v2): in t0 only → boundary.
# Branch 5 fires: e3->isOnBoundary() → update v2->e0 = e3.
m.assert_edge_shared(v0, v2, 1)   # boundary — will be v2's new e0 reference

# e2 for v2 in t0 = edge (v1,v2): in t0 only → also boundary.
m.assert_edge_shared(v1, v2, 1)   # boundary

# Shared edge between t0 and t1.
m.assert_edge_shared(v0, v1, 2)   # interior: shared by t0 and t1

# t1's remaining boundary edges.
m.assert_edge_shared(v0, v3, 1)   # boundary
m.assert_edge_shared(v1, v3, 1)   # boundary
