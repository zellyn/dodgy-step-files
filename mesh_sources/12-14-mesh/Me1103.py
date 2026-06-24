"""Me1103 — CreateTriangleFromVertices_degenerate_triangle: e3 unlinked; Branch 4 null-guard frees e3.

MeshFix `Basic_TMesh.CreateTriangleFromVertices` Branch 4 (*DEGENERATE_TRIANGLE*) @ line 270:
  `if ((t=CreateUnorientedTriangle(e1,e2,e3)) == NULL) { ... }`
  When the three vertices are collinear, CreateUnorientedTriangle returns NULL.
  Branch 4 fires the primary null-check guard. It then checks whether e3 is
  unlinked (e3->t1==NULL && e3->t2==NULL). When both slots of e3 are empty,
  Branch 4 frees e3 via freeNode.

In this fixture e3 is freshly created for the degenerate triangle and has no
incident triangles. Edges e1 and e2 are also unlinked (no prior triangle sharing
them), so all three cleanup branches (4, 5, 6) execute in sequence. Branch 4 is
the entry point that triggers the cascade; the distinguishing defect is
e3->t1==NULL && e3->t2==NULL (both slots vacant).

Defect carrier: three collinear vertices forming a degenerate triangle. No prior
triangles share any of the three edges, so all of e1, e2, e3 are unlinked after
the failed CreateUnorientedTriangle call. Branch 4 detects the NULL return and
frees e3 first.

Geometry:
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0) — collinear on X axis
  va=(1,1,0) — off-axis apex for a valid context triangle
  tc=(v0,va,v2) — valid control triangle (no edge shared with td)
  td=(v0,v1,v2) — zero-area; all edges unlinked; Branch 4 frees e3=(v0,v2)
  Note: tc uses edge (v0,v2) = e3-equivalent of td. To keep e3 unlinked for
  the target branch we use a rotated winding so tc's edges don't overlap td's.
  Instead, va is placed off-axis and tc=(v0,va,v2) shares no edges with td.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1103",
    title="CreateTriangleFromVertices_degenerate_triangle: collinear v0-v1-v2; all edges unlinked; Branch 4 null-guard frees e3=(v1→v2→v0)",
    defect_class="degenerate_triangle",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — collinear left
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — collinear middle
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — collinear right
va = m.vertex(1.0, 2.0, 0.0)   # 3 — off-axis apex (control only)
vb = m.vertex(3.0, 1.0, 0.0)   # 4 — second off-axis apex (control only)

# Two valid control triangles that share no edges with the degenerate triangle.
# They establish mesh context but keep e1, e2, e3 of td unlinked.
tc0 = m.triangle(va, v0, vb)   # 0 — control (uses va-v0, v0-vb, va-vb)
tc1 = m.triangle(va, vb, v2)   # 1 — control (uses va-vb, vb-v2, va-v2)

# Degenerate triangle: v0, v1, v2 are collinear on Y=Z=0.
# All three edges e1=(v0,v1), e2=(v1,v2), e3=(v2,v0) are unlinked (no shared triangles).
# CreateUnorientedTriangle returns NULL → Branch 4 fires; e3 freed first.
td = m.triangle(v0, v1, v2)   # 2 — zero-area degenerate

# Core defect: td has zero area.
m.assert_triangle_area_lt(2, 1e-12)

# Degenerate triangle edges — all boundary/unlinked (n=1 each); e3=(v0,v2).
m.assert_edge_shared(v0, v1, 1)   # e1 of td: unlinked orphan
m.assert_edge_shared(v1, v2, 1)   # e2 of td: unlinked orphan
m.assert_edge_shared(v0, v2, 1)   # e3 of td: unlinked orphan — Branch 4 frees this

# Control triangle edges (boundary).
m.assert_edge_shared(va, v0, 1)
m.assert_edge_shared(v0, vb, 1)
m.assert_edge_shared(va, vb, 2)   # shared interior between tc0 and tc1
m.assert_edge_shared(vb, v2, 1)
m.assert_edge_shared(va, v2, 1)
