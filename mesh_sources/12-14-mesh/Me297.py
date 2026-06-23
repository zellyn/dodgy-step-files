"""Me297 — connected_components visited_face_dedup_cross_halfedge: BFS skips already-visited opposite face.

Catalog claim: CGAL PMP.connected_components Branch 8 @ line 244
(*Visited_vertex_dedup*): `if (!handled[get(fimap,fqo)])` — before
pushing an opposite face onto the BFS queue, the algorithm checks whether
that face is already handled. This prevents redundant re-queuing of faces
that were already discovered and labelled via a different halfedge path.

Geometric signature: a T-shaped mesh where every non-boundary face shares
at least two edges with other faces. The central "hub" triangle (t0) is
adjacent to three rim triangles (t1, t2, t3). When BFS processes t0, all
three opposite faces are pushed. When BFS then processes t1, it checks
halfedges of t1: the halfedge back toward t0 leads to an already-handled
face — Branch 8 fires and skips it. Each of t1, t2, t3 also shares an
edge with its outer neighbor (t4, t5, t6), pushing those neighbors only
once each (no duplicates because they haven't been handled yet at that
point). A disconnected component (t7) confirms the fixture's defect class.

Source: CGAL PMP.connected_components Branch 8 @ line 244
(*Visited_vertex_dedup*) — `if (!handled[get(fimap,fqo)])` prevents
re-queuing faces already labelled in a previous BFS expansion step.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me297",
             title="connected_components visited_face_dedup_cross_halfedge: hub-and-spoke mesh — BFS skips already-handled opposite faces",
             defect_class="disconnected_components")

# Hub-and-spoke: center triangle t0 with 3 rim triangles, each with 1 outer triangle.
# Total: 7 faces in one CC.

# Center triangle vertices.
c0 = m.vertex(0.0, 0.0, 0.0)    # 0
c1 = m.vertex(2.0, 0.0, 0.0)    # 1
c2 = m.vertex(1.0, 2.0, 0.0)    # 2
t0 = m.triangle(c0, c1, c2)    # face 0: hub; shared edges (c0,c1),(c1,c2),(c0,c2)

# Three inner rim triangles — each adjacent to the center.
r0 = m.vertex(1.0, -2.0, 0.0)  # 3
r1 = m.vertex(3.5, 1.0, 0.0)   # 4
r2 = m.vertex(-1.5, 1.0, 0.0)  # 5

t1 = m.triangle(c0, r0, c1)    # face 1: shares (c0,c1) with t0
t2 = m.triangle(c1, r1, c2)    # face 2: shares (c1,c2) with t0
t3 = m.triangle(c2, r2, c0)    # face 3: shares (c0,c2) with t0

# Three outer triangles — each adjacent to one rim triangle.
o0 = m.vertex(0.0, -3.5, 0.0)  # 6
o1 = m.vertex(4.5, -1.0, 0.0)  # 7
o2 = m.vertex(-3.0, 2.0, 0.0)  # 8

t4 = m.triangle(c0, o0, r0)    # face 4: shares (c0,r0) = (0,3) with t1
t5 = m.triangle(c1, r1, o1)    # face 5: shares (c1,r1) = (1,4) with t2
t6 = m.triangle(c2, o2, r2)    # face 6: shares (c2,r2) = (2,5) with t3

# Hub edges — each shared by center (t0) and one rim triangle.
m.assert_edge_shared(c0, c1, 2)   # t0 and t1
m.assert_edge_shared(c1, c2, 2)   # t0 and t2
m.assert_edge_shared(c0, c2, 2)   # t0 and t3

# Rim-to-outer edges.
m.assert_edge_shared(c0, r0, 2)   # t1 and t4
m.assert_edge_shared(c1, r1, 2)   # t2 and t5
m.assert_edge_shared(c2, r2, 2)   # t3 and t6

# Disconnected component — second CC for the defect_class claim.
d0 = m.vertex(20.0, 0.0, 0.0)   # 9
d1 = m.vertex(21.0, 0.0, 0.0)   # 10
d2 = m.vertex(20.5, 1.0, 0.0)   # 11
iso = m.triangle(d0, d1, d2)   # face 7: isolated CC 1

m.assert_triangle_not_reachable_from(iso, t0)
