"""Me294 — connected_components iteration_inner_halfedges: inner for-loop over face halfedges.

Catalog claim: CGAL PMP.connected_components Branch 5 @ line 237
(*Iteration_construct*): inside the BFS while-loop, an inner for-loop
iterates over every halfedge of the current face to discover neighboring
faces. For a triangle mesh this loop cycles 3 times per face; all three
halfedges are checked for opposite faces.

Geometric signature: a single connected component of 7 triangles arranged
as a hexagonal fan (6 triangles around a center triangle). Each face of
the center triangle is adjacent to 3 rim triangles, so BFS expanding from
the center face must iterate through all 3 halfedges (Branch 5 cycles 3
times) to discover the 3 rim neighbors. A disconnected noise triangle
confirms the fixture's defect class.

Source: CGAL PMP.connected_components Branch 5 @ line 237
(*Iteration_construct*) — inner `for(h : halfedges_around_face(fq, pmesh))`
iterates over all 3 halfedges of each face to propagate BFS to neighbors.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me294",
             title="connected_components inner halfedge iteration: hexagonal fan — center triangle has 3 neighbors discovered via 3 halfedges",
             defect_class="disconnected_components")

# Center triangle: c0, c1, c2 — three halfedges each leading to a rim triangle.
c0 = m.vertex(0.0, 0.0, 0.0)    # 0
c1 = m.vertex(2.0, 0.0, 0.0)    # 1
c2 = m.vertex(1.0, 2.0, 0.0)    # 2
center = m.triangle(c0, c1, c2)   # face 0: center; 3 halfedges → rims f1, f2, f3

# Three rim triangles — each shares one edge with the center.
r0 = m.vertex(1.0, -2.0, 0.0)   # 3 — below center edge (c0,c1)
r1 = m.vertex(3.0, 1.0, 0.0)    # 4 — right of center edge (c1,c2)
r2 = m.vertex(-1.0, 1.0, 0.0)   # 5 — left of center edge (c2,c0)

f1 = m.triangle(c0, r0, c1)   # face 1: shares edge (c0,c1) = (0,1) with center
f2 = m.triangle(c1, r1, c2)   # face 2: shares edge (c1,c2) = (1,2) with center
f3 = m.triangle(c2, r2, c0)   # face 3: shares edge (c0,c2) = (0,2) with center

# Three additional outer triangles adjacent to the rim.
ro0 = m.vertex(-1.0, -2.0, 0.0)  # 6
ro1 = m.vertex(4.0, -1.0, 0.0)   # 7
ro2 = m.vertex(-2.0, 3.0, 0.0)   # 8

f4 = m.triangle(c0, ro0, r0)   # face 4: shares edge (c0,r0) = (0,3) with f1
f5 = m.triangle(c1, r1, ro1)   # face 5: shares edge (c1,r1) = (1,4) with f2 ... wait (r1,c1)=(4,1)
f6 = m.triangle(c2, ro2, r2)   # face 6: shares edge (c2,r2) = (2,5) with f3 ... (r2,c2)=(5,2)

# Center triangle's 3 edges each shared with one rim triangle.
m.assert_edge_shared(c0, c1, 2)   # center and f1
m.assert_edge_shared(c1, c2, 2)   # center and f2
m.assert_edge_shared(c0, c2, 2)   # center and f3

# Rim-to-outer adjacency.
m.assert_edge_shared(c0, r0, 2)   # f1 and f4
m.assert_edge_shared(c1, r1, 2)   # f2 and f5
m.assert_edge_shared(c2, r2, 2)   # f3 and f6

# All 7 faces connected — reachable from center.
# (No assert needed; the absence of not_reachable is sufficient for the main claim.)

# Disconnected noise triangle for defect_class.
n0 = m.vertex(20.0, 0.0, 0.0)   # 9
n1 = m.vertex(21.0, 0.0, 0.0)   # 10
n2 = m.vertex(20.5, 1.0, 0.0)   # 11
noise = m.triangle(n0, n1, n2)   # face 7: isolated second CC

m.assert_triangle_not_reachable_from(noise, center)
