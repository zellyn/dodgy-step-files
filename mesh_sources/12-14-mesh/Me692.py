"""Me692 — connected_component iteration_construct: for-loop iterates over face neighbors.

Catalog claim: CGAL PMP.connected_component Branch 3 @ line 146
(*Iteration_construct*): the inner `for` loop iterates over the neighbors
(adjacent faces via halfedges) of the current face in the BFS queue.
A triangle mesh face has up to 3 neighbors — this branch exercises the
for-loop that visits each adjacent face to expand the BFS.

Geometric signature: a T-junction of seven triangles where the central
triangle has three neighbors (f1, f2, f3), each of which has one additional
outer neighbor (f4, f5, f6). When BFS processes the center face, the
for-loop over its halfedges iterates three times, discovering f1, f2, f3.
Each of those faces then has the for-loop iterate again to discover f4, f5,
f6. An isolated triangle (f7) forms a second CC.

Layout:
     f4
     |
f5 - f1 - f0(center) - f2 - f6
             |
             f3
             |
             f7 (isolated)

Source: CGAL PMP.connected_component Branch 3 @ line 146
(*Iteration_construct*) — `for` over neighboring faces; the 3-neighbor
center face forces the for-loop to iterate 3 times per BFS expansion step.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me692",
             title="connected_component iteration_construct: center triangle has 3 neighbors discovered via for-loop over halfedges",
             defect_class="disconnected_components")

# Center triangle: c0, c1, c2.
c0 = m.vertex(0.0, 0.0, 0.0)   # 0
c1 = m.vertex(2.0, 0.0, 0.0)   # 1
c2 = m.vertex(1.0, 2.0, 0.0)   # 2
center = m.triangle(c0, c1, c2)   # face 0: seed; 3 halfedges → f1, f2, f3

# Three inner rim triangles — each shares one edge with the center.
r0 = m.vertex(1.0, -2.0, 0.0)   # 3 — below (c0,c1)
r1 = m.vertex(3.5, 1.0, 0.0)    # 4 — right of (c1,c2)
r2 = m.vertex(-1.5, 1.0, 0.0)   # 5 — left of (c0,c2)

f1 = m.triangle(c0, r0, c1)   # face 1: shares edge (c0,c1)=(0,1) with center
f2 = m.triangle(c1, r1, c2)   # face 2: shares edge (c1,c2)=(1,2) with center
f3 = m.triangle(c2, r2, c0)   # face 3: shares edge (c0,c2)=(0,2) with center

# Three outer triangles — each adjacent to one rim triangle.
o0 = m.vertex(-0.5, -3.0, 0.0)  # 6
o1 = m.vertex(5.0, 0.0, 0.0)    # 7
o2 = m.vertex(-3.0, 2.0, 0.0)   # 8

f4 = m.triangle(c0, o0, r0)   # face 4: shares edge (c0,r0)=(0,3) with f1
f5 = m.triangle(c1, r1, o1)   # face 5: shares edge (c1,r1)=(1,4) with f2
f6 = m.triangle(c2, o2, r2)   # face 6: shares edge (c2,r2)=(2,5) with f3

# Center's three halfedge-edges each shared with one rim triangle.
m.assert_edge_shared(c0, c1, 2)   # center and f1
m.assert_edge_shared(c1, c2, 2)   # center and f2
m.assert_edge_shared(c0, c2, 2)   # center and f3

# Rim-to-outer shared edges.
m.assert_edge_shared(c0, r0, 2)   # f1 and f4
m.assert_edge_shared(c1, r1, 2)   # f2 and f5
m.assert_edge_shared(c2, r2, 2)   # f3 and f6

# Isolated triangle — forms a second CC (satisfies defect_class).
n0 = m.vertex(20.0, 0.0, 0.0)   # 9
n1 = m.vertex(21.0, 0.0, 0.0)   # 10
n2 = m.vertex(20.5, 1.0, 0.0)   # 11
iso = m.triangle(n0, n1, n2)   # face 7: isolated; unreachable from center

m.assert_triangle_not_reachable_from(iso, center)
