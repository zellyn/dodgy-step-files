"""Me694 — connected_component null_face_check: BFS stops at mesh boundary (null opposite face).

Catalog claim: CGAL PMP.connected_component Branch 5 @ line 151
(*Null_face_check*): `neighbor != boost::graph_traits<PolygonMesh>::null_face()`
— when the BFS traverses a halfedge whose opposite halfedge has no adjacent
face (a boundary halfedge), `opposite(hd, pmesh)` returns `null_face`. The
null-face check guards against following that null reference — the BFS simply
does not enqueue null_face and stops at the mesh boundary edge.

Geometric signature: three triangles forming a partial disk open at one side
(t0, t1, t2 sharing edges but not forming a closed surface). Each boundary
edge of the partial disk produces a null_face neighbor. When BFS expands
from t0 it discovers t1 and t2 via shared interior edges, and also encounters
boundary halfedges on the outer rim — for those, the null_face check fires
and prevents following. A disconnected isolated triangle (t3) forms a
second CC.

Strip of 3 triangles sharing edges along the base:
  p0      p1
  /\\t0  t1/\\
 /  \\   /  \\t2
b0   b1   b2   b3

t0=(b0,b1,p0); t1=(b1,b2,p1) — NOT sharing an edge with t0.
Use fan: t0=(b0,b1,p0); t1=(b1,p1,p0) shares (b1,p0); t2=(b1,b2,p1) shares (b1,p1).
Outer edges (b0,b1), (b0,p0), (p0,p1), (p1,b2), (b2,b1) are boundary edges
whose opposite faces are null_face — Branch 5 fires for each.

Source: CGAL PMP.connected_component Branch 5 @ line 151
(*Null_face_check*) — `neighbor != null_face` guards boundary halfedges;
fires for every outer boundary edge of the open mesh.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me694",
             title="connected_component null_face_check: open-boundary mesh; BFS encounters null_face at every boundary halfedge",
             defect_class="disconnected_components")

# Open strip of 3 triangles (no closed surface) with boundary edges.
b0 = m.vertex(0.0, 0.0, 0.0)   # 0 — base left
b1 = m.vertex(1.0, 0.0, 0.0)   # 1 — base mid
b2 = m.vertex(2.0, 0.0, 0.0)   # 2 — base right

p0 = m.vertex(0.5, 1.0, 0.0)   # 3 — apex above (b0,b1)
p1 = m.vertex(1.5, 1.0, 0.0)   # 4 — apex above (b1,b2)

# Three triangles: t0 and t1 share edge (b1,p0); t1 and t2 share edge (b1,p1).
t0 = m.triangle(b0, b1, p0)   # face 0: seed; boundary edges: (b0,p0),(b0,b1)
t1 = m.triangle(b1, p1, p0)   # face 1: shares (b1,p0)=(1,3) with t0; boundary: (p0,p1)
t2 = m.triangle(b1, b2, p1)   # face 2: shares (b1,p1)=(1,4) with t1; boundary: (b1,b2),(b2,p1)

# Interior shared edges (each shared by exactly 2 triangles).
m.assert_edge_shared(b1, p0, 2)   # t0 and t1
m.assert_edge_shared(b1, p1, 2)   # t1 and t2

# Boundary edges are shared by exactly 1 triangle (null_face on opposite side).
# These are the edges where the null_face_check Branch 5 fires during BFS.
m.assert_edge_shared(b0, p0, 1)   # t0 boundary — opposite is null_face
m.assert_edge_shared(b0, b1, 1)   # t0 boundary — opposite is null_face
m.assert_edge_shared(p0, p1, 1)   # t1 boundary — opposite is null_face
m.assert_edge_shared(b2, p1, 1)   # t2 boundary — opposite is null_face
m.assert_edge_shared(b1, b2, 1)   # t2 boundary — opposite is null_face

# Isolated triangle — forms a second CC.
q0 = m.vertex(10.0, 0.0, 0.0)   # 5
q1 = m.vertex(11.0, 0.0, 0.0)   # 6
q2 = m.vertex(10.5, 1.0, 0.0)   # 7
iso = m.triangle(q0, q1, q2)   # face 3: isolated; unreachable from t0

m.assert_triangle_not_reachable_from(iso, t0)
