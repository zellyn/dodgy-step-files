"""Me107 — unlink_triangle_isolated_edge_pair_v2: both edges e2 and e3 incident
on v2 in the target triangle become isolated after the triangle is unlinked,
making v2 an orphaned (isolated) vertex.

MeshFix `Basic_TMesh.unlinkTriangle` Branch 8 (*isolated_edge_pair_v2*):
'if (e2->isIsolated() && e3->isIsolated())' — e2 and e3 are the two edges of
the target triangle incident on v2. If both become isolated after the unlink,
v2->e0 is set to NULL.

For Branch 8: the SECOND vertex (v2) of the target triangle appears only in
that one triangle. Its two edges (v1v2 and v2v3 in MeshFix notation) have
no other incident triangles.

Geometry — a 4-triangle mesh where the second vertex of the target triangle
is unique:
  v0=(0,0,0), v1=(1,0,0) [unique v2], v2=(2,0,0), v3=(1,1,0), v4=(0,1,0), v5=(2,1,0)

  t0 = (v0, v1, v2)   ← target; v1=(1,0,0) is second vertex, in t0 only
  t1 = (v0, v3, v4)   — unrelated upper-left triangle
  t2 = (v0, v2, v3)   — shares (v0,v2) but not (v0,v1) or (v1,v2)

  Edges at v1 in t0:
    (v0,v1) — in t0 only → isolated after unlink
    (v1,v2) — in t0 only → isolated after unlink
  → Branch 8 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me107",
             title="unlink_triangle_isolated_edge_pair_v2: v2's both incident edges isolated, v2 becomes orphan",
             defect_class="unlink_isolated_edge_pair_v2")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — v2 in MeshFix target; in t0 only
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3
v4 = m.vertex(0.0, 1.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5

# Target triangle; v1 is the second vertex (in t0 only).
t0 = m.triangle(v0, v1, v2)    # 0 — target

# Adjacent triangles NOT sharing any edge with v1.
t1 = m.triangle(v0, v3, v4)    # 1
t2 = m.triangle(v0, v2, v3)    # 2 — shares (v0,v2) with t0's third edge but not v1
t3 = m.triangle(v2, v5, v3)    # 3

# Both edges of t0 at v1 are boundary (in t0 only).
m.assert_edge_shared(v0, v1, 1)   # boundary: only t0 uses this edge
m.assert_edge_shared(v1, v2, 1)   # boundary: only t0 uses this edge

# t0's third edge (v0,v2) is shared with t2.
m.assert_edge_shared(v0, v2, 2)   # interior: shared by t0 and t2

# Other mesh boundary edges.
m.assert_edge_shared(v0, v4, 1)   # boundary
m.assert_edge_shared(v3, v4, 1)   # boundary
