"""Me691 — connected_component visited_vertex_dedup: seed face re-encountered during BFS expansion.

Catalog claim: CGAL PMP.connected_component Branch 2 @ line 144
(*Visited_vertex_dedup*): `!already_processed.insert(seed_face)` — the BFS
checks whether a face has already been added to the output set before
inserting it again. In a ring or mesh where multiple BFS paths lead back to
the original seed face (or where a face is adjacent to two already-queued
faces), the dedup guard fires to skip the re-encounter.

Geometric signature: four triangles arranged as a closed ring (f0-f1-f2-f3)
where each adjacent pair shares one edge and f3 also shares an edge back to
f0. When BFS starts at f0 it immediately discovers f1 and f3. When BFS
processes f1 it discovers f2. When BFS processes f2 it discovers f3 —
but f3 was already inserted via f0. Branch 2's dedup guard fires on the
second encounter of f3 and skips re-insertion. An isolated triangle (f4)
forms a second CC.

Ring topology:
  f0 -- f1
  |      |
  f3 -- f2

f0=(v0,v1,v4); f1=(v1,v2,v4); f2=(v2,v3,v4); f3=(v3,v0,v4) — all share
the center vertex v4; adjacent pairs share one spoke edge.

Source: CGAL PMP.connected_component Branch 2 @ line 144
(*Visited_vertex_dedup*) — `!already_processed.insert(seed_face)` dedup
guard fires when a face is discovered via multiple BFS paths.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me691",
             title="connected_component visited_vertex_dedup: 4-triangle fan ring where f3 is reachable via two BFS paths",
             defect_class="disconnected_components")

# Fan ring: 4 outer rim vertices + center apex.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — rim top-left
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — rim top-right
v2 = m.vertex(2.0, 2.0, 0.0)   # 2 — rim bottom-right
v3 = m.vertex(0.0, 2.0, 0.0)   # 3 — rim bottom-left
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — center apex (shared by all 4 triangles)

# Four fan triangles — consecutive pairs share one spoke edge.
f0 = m.triangle(v0, v1, v4)   # face 0: seed; shares (v0,v4)=(0,4) with f3, (v1,v4)=(1,4) with f1
f1 = m.triangle(v1, v2, v4)   # face 1: shares (v1,v4)=(1,4) with f0, (v2,v4)=(2,4) with f2
f2 = m.triangle(v2, v3, v4)   # face 2: shares (v2,v4)=(2,4) with f1, (v3,v4)=(3,4) with f3
f3 = m.triangle(v3, v0, v4)   # face 3: shares (v3,v4)=(3,4) with f2, (v0,v4)=(0,4) with f0

# All four spoke edges shared by exactly 2 triangles.
m.assert_edge_shared(v0, v4, 2)   # f0 and f3 — ring-closure edge; triggers dedup when f3 found via f2
m.assert_edge_shared(v1, v4, 2)   # f0 and f1
m.assert_edge_shared(v2, v4, 2)   # f1 and f2
m.assert_edge_shared(v3, v4, 2)   # f2 and f3

# Isolated triangle — forms a second CC (satisfies defect_class).
w0 = m.vertex(10.0, 0.0, 0.0)   # 5
w1 = m.vertex(11.0, 0.0, 0.0)   # 6
w2 = m.vertex(10.5, 1.0, 0.0)   # 7
iso = m.triangle(w0, w1, w2)   # face 4: isolated; unreachable from f0

m.assert_triangle_not_reachable_from(iso, f0)
