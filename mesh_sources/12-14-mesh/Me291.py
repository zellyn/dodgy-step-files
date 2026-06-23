"""Me291 — connected_components visited_face_dedup_outer: already-handled faces skipped in outer loop.

Catalog claim: CGAL PMP.connected_components Branch 2 @ line 226
(*Visited_vertex_dedup*): `if (!handled[get(fimap,f)])` — the outer
for-loop skips any face already marked handled in a previous BFS.
A mesh with a large connected component followed by a tiny second
component demonstrates this: after BFS labels all faces in component A,
the outer loop encounters component B as the next unhandled face.

Geometric signature: four triangles share edges forming one connected
patch (component A, faces 0-3); a fifth isolated triangle (component B,
face 4) is disconnected. After BFS marks faces 0-3 as handled with CC
label 0, the outer loop reaches face 4 (Branch 2 checks `!handled[face]`
and finds it unhandled), seeds a second BFS, and assigns label 1.

Source: CGAL PMP.connected_components Branch 2 @ line 226
(*Visited_vertex_dedup*) — outer `if (!handled[...])` skip guard prevents
re-processing already-labelled faces in subsequent outer-loop iterations.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me291",
             title="connected_components visited_face_dedup_outer: multi-face CC followed by isolated face exercises handled[] skip",
             defect_class="disconnected_components")

# Component A: connected patch of 4 triangles (fan around apex v4).
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(1.0, 1.0, 0.0)
v3 = m.vertex(0.0, 1.0, 0.0)
v4 = m.vertex(0.5, 0.5, 1.0)   # apex
t0 = m.triangle(v0, v1, v4)   # face 0: shares edges with t1 and t3
t1 = m.triangle(v1, v2, v4)   # face 1: shares edges with t0 and t2
t2 = m.triangle(v2, v3, v4)   # face 2: shares edges with t1 and t3
t3 = m.triangle(v3, v0, v4)   # face 3: shares edges with t2 and t0

# Component B: single isolated triangle far away.
v5 = m.vertex(20.0, 0.0, 0.0)
v6 = m.vertex(21.0, 0.0, 0.0)
v7 = m.vertex(20.5, 1.0, 0.0)
t4 = m.triangle(v5, v6, v7)   # face 4: isolated, handled[] skip fires when outer loop arrives

# Component A is fully internally connected — faces 0-3 reachable from each other.
m.assert_edge_shared(v0, v4, 2)   # shared by t0 and t3
m.assert_edge_shared(v1, v4, 2)   # shared by t0 and t1
m.assert_edge_shared(v2, v4, 2)   # shared by t1 and t2
m.assert_edge_shared(v3, v4, 2)   # shared by t2 and t3

# Component B is disconnected from component A.
m.assert_triangle_not_reachable_from(t4, t0)
