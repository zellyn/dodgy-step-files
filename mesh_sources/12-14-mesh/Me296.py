"""Me296 — connected_components null_face_check: BFS stops at open mesh boundary.

Catalog claim: CGAL PMP.connected_components Branch 7 @ line 242
(*Null_face_check*): `if (fqo != GT::null_face())` — when BFS traverses a
halfedge that lies on the mesh boundary (an open hole), the opposite
halfedge's face is GT::null_face(). Branch 7 catches this and skips the
null face, preventing a null-pointer dereference. Without this guard, BFS
over an open mesh would crash when it reaches a boundary halfedge.

Geometric signature: an open triangulated patch with one boundary hole.
Three triangles share edges forming a partial ring — the inner edges are
interior (shared by 2 triangles), while the outer edges are boundary
(each incident on exactly 1 triangle, their opposite halfedge has no face).
BFS over this patch hits boundary halfedges on every triangle and must
invoke Branch 7 to skip GT::null_face() opposites.

Source: CGAL PMP.connected_components Branch 7 @ line 242
(*Null_face_check*) — `if (fqo != GT::null_face())` skip guard for
boundary halfedges where the opposite face does not exist.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me296",
             title="connected_components null_face_check: open triangulated patch — BFS hits boundary halfedges with no opposite face",
             defect_class="disconnected_components")

# Open patch: 4 triangles forming a partial surface with a boundary hole.
# Layout: a 2x2 square subdivided into 4 triangles; the center vertex v4
# is shared by all 4 triangles. Outer edges are all boundary (degree 1).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — corner
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — corner
v2 = m.vertex(2.0, 2.0, 0.0)   # 2 — corner
v3 = m.vertex(0.0, 2.0, 0.0)   # 3 — corner
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — center

# 4 triangles around the center — inner edges shared, outer edges boundary.
t0 = m.triangle(v0, v1, v4)   # face 0: bottom; shares (v0,v4) with t3, (v1,v4) with t1
t1 = m.triangle(v1, v2, v4)   # face 1: right;  shares (v1,v4) with t0, (v2,v4) with t2
t2 = m.triangle(v2, v3, v4)   # face 2: top;    shares (v2,v4) with t1, (v3,v4) with t3
t3 = m.triangle(v3, v0, v4)   # face 3: left;   shares (v3,v4) with t2, (v0,v4) with t0

# Interior edges (each shared by 2 triangles) — BFS crosses these.
m.assert_edge_shared(v0, v4, 2)   # t0 and t3
m.assert_edge_shared(v1, v4, 2)   # t0 and t1
m.assert_edge_shared(v2, v4, 2)   # t1 and t2
m.assert_edge_shared(v3, v4, 2)   # t2 and t3

# Outer boundary edges (each on exactly 1 triangle) — BFS hits null_face here.
m.assert_edge_shared(v0, v1, 1)   # t0 outer edge — boundary
m.assert_edge_shared(v1, v2, 1)   # t1 outer edge — boundary
m.assert_edge_shared(v2, v3, 1)   # t2 outer edge — boundary
m.assert_edge_shared(v3, v0, 1)   # t3 outer edge — boundary

# All 4 faces are connected (same CC) — BFS starting from t0 reaches t1-t3.
# Also add an isolated face to confirm the disconnected_components defect class.
w0 = m.vertex(10.0, 0.0, 0.0)   # 5
w1 = m.vertex(11.0, 0.0, 0.0)   # 6
w2 = m.vertex(10.5, 1.0, 0.0)   # 7
iso = m.triangle(w0, w1, w2)   # face 4: isolated second CC

m.assert_triangle_not_reachable_from(iso, t0)
