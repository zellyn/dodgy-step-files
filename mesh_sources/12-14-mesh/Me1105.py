"""Me1105 — CreateTriangleFromVertices_unlinked_e1: e1 orphan after failed creation; Branch 6 frees e1.

MeshFix `Basic_TMesh.CreateTriangleFromVertices` Branch 6 (*UNLINKED_EDGE*) @ line 286:
  `if (e1->t1 == NULL && e1->t2 == NULL) { E.freeNode(e1); ... }`
  After CreateUnorientedTriangle returns NULL (Branch 4 null-guard), the code
  checks e2 (Branch 5) then e1 (Branch 6). Branch 6 fires when e1 has no incident
  triangles — e1 was freshly created for this triangle attempt and was never
  linked to any triangle. E.freeNode reclaims the orphaned edge.

In this fixture both e3 and e2 are pre-existing linked edges (each shared with a
valid existing triangle). Only e1 is freshly created and unlinked. The cleanup
order: Branch 4 (null-guard) skips e3 free because e3 is linked; Branch 5 skips
e2 free because e2 is linked; Branch 6 fires and frees e1.

Structural distinction from Me1104: here both e2 AND e3 are linked (shared with
existing triangles), leaving only e1 orphaned. Branch 6 is the final cleanup step
and is the first (and only) one that actually reclaims an edge in this configuration.

Defect carrier: degenerate collinear triangle td=(v0,v1,v2) where:
  e3=(v0,v2) is already shared with tc_a=(v0,va,v2) → linked, Branch 4 skips
  e2=(v1,v2) is already shared with tc_b=(v1,vb,v2) → linked, Branch 5 skips
  e1=(v0,v1) is freshly created and unlinked → Branch 6 fires: freeNode(e1)

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — collinear on X axis
  va=(1,2,0)  — off-axis apex for tc_a (shares e3=(v0,v2) with td)
  vb=(1.5,2,0)— off-axis apex for tc_b (shares e2=(v1,v2) with td)
  tc_a=(v0,va,v2) — valid control sharing e3=(v0,v2) with td
  tc_b=(v1,vb,v2) — valid control sharing e2=(v1,v2) with td
  td=(v0,v1,v2) — zero-area degenerate; only e1=(v0,v1) is unlinked → Branch 6
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1105",
    title="CreateTriangleFromVertices_unlinked_e1: degenerate td collinear; e3 and e2 linked; e1=(v0,v1) orphan freed by Branch 6 freeNode",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — collinear left / shared with tc_a
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — collinear middle / shared with tc_b
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — collinear right / shared with tc_a, tc_b
va = m.vertex(1.0, 2.0, 0.0)   # 3 — off-axis apex of tc_a
vb = m.vertex(1.5, 2.0, 0.0)   # 4 — off-axis apex of tc_b

# Valid control triangle tc_a shares edge (v0,v2) = e3 of td.
tc_a = m.triangle(v0, va, v2)   # 0 — occupies one slot of edge (v0,v2)

# Valid control triangle tc_b shares edge (v1,v2) = e2 of td.
tc_b = m.triangle(v1, vb, v2)   # 1 — occupies one slot of edge (v1,v2)

# Degenerate triangle: v0, v1, v2 collinear on Y=Z=0.
# e3=(v0,v2) linked via tc_a → Branch 4 skips.
# e2=(v1,v2) linked via tc_b → Branch 5 skips.
# e1=(v0,v1) freshly created, unlinked → Branch 6 fires: freeNode(e1).
td = m.triangle(v0, v1, v2)   # 2 — zero-area degenerate

# Core defect: td has zero area.
m.assert_triangle_area_lt(2, 1e-12)

# e3=(v0,v2): linked — shared by tc_a and td (n=2) → Branch 4 skips free.
m.assert_edge_shared(v0, v2, 2)   # e3: linked; Branch 4 does NOT free it

# e2=(v1,v2): linked — shared by tc_b and td (n=2) → Branch 5 skips free.
m.assert_edge_shared(v1, v2, 2)   # e2: linked; Branch 5 does NOT free it

# e1=(v0,v1): unlinked orphan — Branch 6 fires and frees it.
m.assert_edge_shared(v0, v1, 1)   # e1: unlinked → Branch 6 freeNode(e1)

# tc_a boundary edges.
m.assert_edge_shared(v0, va, 1)
m.assert_edge_shared(va, v2, 1)

# tc_b boundary edges.
m.assert_edge_shared(v1, vb, 1)
m.assert_edge_shared(vb, v2, 1)
