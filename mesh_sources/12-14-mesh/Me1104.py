"""Me1104 — CreateTriangleFromVertices_unlinked_e2: e2 orphan after failed creation; Branch 5 frees e2.

MeshFix `Basic_TMesh.CreateTriangleFromVertices` Branch 5 (*UNLINKED_EDGE*) @ line 279:
  `if (e2->t1 == NULL && e2->t2 == NULL) { E.freeNode(e2); ... }`
  After CreateUnorientedTriangle returns NULL (Branch 4 null-guard), the code
  checks each edge in reverse order. Branch 5 fires when e2 has no incident
  triangles — meaning e2 was freshly created for this triangle attempt and was
  never assigned to any triangle. E.freeNode reclaims the edge object and any
  vertex edge-list references to it are nulled out.

In this fixture e3 is linked (it is shared with an existing triangle), so
Branch 4's free-e3 sub-step is skipped. But e2 was newly created and has no
incident triangles — Branch 5 fires to free it. e1 is also newly created and
unlinked, so Branch 6 fires next.

Structural distinction from Me1103: here e3=(v0,v2) is pre-existing (shared with
tc), whereas in Me1103 all three edges are unlinked. The presence of a linked e3
forces Branch 4 to skip its free, but e2 remains orphaned — Branch 5 is the first
cleanup that actually reclaims an edge.

Defect carrier: degenerate collinear triangle td=(v0,v1,v2) where the closing
edge e3=(v0,v2) is already shared with a valid triangle tc=(v0,va,v2). The two
collinear edges e1=(v0,v1) and e2=(v1,v2) are freshly created and unlinked.
Branch 4 null-guard fires (NULL return from CreateUnorientedTriangle), skips
the linked e3, then Branch 5 frees e2.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — collinear on X axis
  va=(1,1,0) — off-axis apex for valid triangle
  tc=(v0,va,v2) — valid control triangle sharing edge (v0,v2) with td
  td=(v0,v1,v2) — zero-area; e1=(v0,v1) and e2=(v1,v2) are unlinked orphans;
                   e3=(v0,v2) is linked via tc → Branch 4 skips e3 free
                   Branch 5 fires: e2->t1==NULL && e2->t2==NULL → freeNode(e2)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1104",
    title="CreateTriangleFromVertices_unlinked_e2: degenerate td collinear; e3 linked via tc; e2=(v1,v2) orphan freed by Branch 5 freeNode",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — collinear left / shared edge endpoint
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — collinear middle (td only)
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — collinear right / shared edge endpoint
va = m.vertex(1.0, 1.0, 0.0)   # 3 — off-axis apex (tc only)

# Valid control triangle sharing edge (v0,v2) with td — this links e3 of td.
tc = m.triangle(v0, va, v2)   # 0 — valid triangle; occupies one slot of (v0,v2)

# Degenerate triangle: v0, v1, v2 collinear on Y=Z=0.
# e3=(v0,v2) is shared with tc (linked, n=2) → Branch 4 skips free-e3.
# e1=(v0,v1) and e2=(v1,v2) are unlinked → Branch 5 frees e2; Branch 6 frees e1.
td = m.triangle(v0, v1, v2)   # 1 — zero-area degenerate

# Core defect: td has zero area.
m.assert_triangle_area_lt(1, 1e-12)

# e3=(v0,v2): linked — shared by tc and td (n=2).
# Linked e3 means Branch 4's free-e3 sub-step is SKIPPED.
m.assert_edge_shared(v0, v2, 2)   # e3 of td: linked → Branch 4 does NOT free it

# e2=(v1,v2): unlinked orphan — Branch 5 fires and frees it.
m.assert_edge_shared(v1, v2, 1)   # e2 of td: unlinked → Branch 5 freeNode(e2)

# e1=(v0,v1): unlinked orphan — Branch 6 fires after Branch 5.
m.assert_edge_shared(v0, v1, 1)   # e1 of td: unlinked → Branch 6 freeNode(e1)

# tc boundary edges.
m.assert_edge_shared(v0, va, 1)
m.assert_edge_shared(va, v2, 1)
