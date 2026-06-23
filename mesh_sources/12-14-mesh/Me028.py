"""Me028 — border_degenerate_face: degenerate triangle on mesh boundary (Branch 5).

Catalog claim: triangle 1 is a zero-area collinear triangle whose three
edges are all boundary edges (each incident on only one face). It represents
a dangling degenerate face at the mesh border — the is_border(opposite) /
border_deg_faces branch in CGAL PMP.remove_degenerate_faces.

Source: CGAL PMP.remove_degenerate_faces Branch 5 @ line 2118 —
*border-degenerate-face*: degenerate triangle on mesh boundary, handled
separately from interior degenerate faces via the border_deg_faces queue.

Defect carrier: triangle 0 is a clean manifold triangle; triangle 1 is a
degenerate collinear triangle at the far side that shares no edges with
triangle 0, so all its edges are open boundary edges (incident count = 1).
A healer invoking remove_degenerate_faces encounters the is_border branch
for this isolated boundary degenerate face.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me028",
             title="border degenerate face: collinear zero-area triangle on open boundary",
             defect_class="degenerate_triangle")

# Clean interior triangle (non-degenerate, open mesh).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
t0 = m.triangle(v0, v1, v2)   # face 0: clean control triangle

# Degenerate border triangle — collinear, isolated (no shared edges with face 0).
# All three edges of this triangle are boundary edges (incident on 1 face only).
v3 = m.vertex(3.0, 0.0, 0.0)
v4 = m.vertex(4.0, 0.0, 0.0)
v5 = m.vertex(5.0, 0.0, 0.0)
t1 = m.triangle(v3, v4, v5)   # face 1: zero area, collinear, all edges are boundary

# Assert degenerate triangle has zero area.
m.assert_triangle_area_lt(t1, 1e-12)

# Assert each of the degenerate triangle's edges is on the boundary (shared by 1 triangle only).
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v4, v5, 1)
m.assert_edge_shared(v3, v5, 1)
