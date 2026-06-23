"""Me103 — unlink_triangle_v1_edge_ref_boundary: v1's reference edge must be
updated to a boundary edge after the triangle is unlinked.

MeshFix `Basic_TMesh.unlinkTriangle` Branch 4 (*edge_reference_update_v1*):
'if (e2->isOnBoundary())' — after unlinking the target triangle, one of v1's
remaining incident edges (e2, the edge connecting v1 to v3 in MeshFix's
notation) transitions from interior to boundary. The branch ensures that
v1->e0 (v1's canonical edge pointer) is updated to point at the newly-created
boundary edge rather than a now-orphaned interior edge.

Geometric signature: v1 sits on the boundary of a small fan. One of its two
edges in the target triangle (call it e2) is currently shared with exactly one
other triangle; once t0 is removed, that edge becomes fully isolated (orphaned)
and v1's only remaining connection is through e2's partner. The branch updates
v1->e0 accordingly.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)  — base row
  v3=(1,1,0)  — apex shared by t0 and t1

  t0 = (v0, v1, v3)   ← target triangle
  t1 = (v1, v2, v3)   ← shares edge (v1,v3) with t0

  Edge (v0,v1) is the e2 edge for v1 in t0: it is shared by t0 only → boundary.
  After unlinking t0, e2=(v0,v1) becomes part of the now-open boundary.
  Branch 4 fires: e2->isOnBoundary() is TRUE, so v1->e0 is set to e2.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me103",
             title="unlink_triangle_v1_edge_ref_boundary: v1 reference edge updated to boundary after unlink",
             defect_class="unlink_edge_ref_v1")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — v1 of target triangle
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3 — apex

# Target triangle t0; v1 is the first vertex.
t0 = m.triangle(v0, v1, v3)    # 0 — target

# Adjacent triangle sharing edge (v1,v3).
t1 = m.triangle(v1, v2, v3)    # 1 — shares (v1,v3) with t0

# e2 for v1 in t0 = edge (v0,v1) → boundary (in t0 only).
m.assert_edge_shared(v0, v1, 1)   # boundary — will be v1's new reference edge

# e1 for v1 in t0 = edge (v1,v3) → interior (shared with t1).
m.assert_edge_shared(v1, v3, 2)   # interior: shared by t0 and t1

# Remaining open boundary edges of the two-triangle strip.
m.assert_edge_shared(v0, v3, 1)   # boundary
m.assert_edge_shared(v2, v3, 1)   # boundary
m.assert_edge_shared(v1, v2, 1)   # boundary
