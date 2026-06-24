"""Me1091 — isolated_degenerate_single_flip: one degenerate face, no degenerate neighbors, flip branch (Branch 8).

CGAL PMP.remove_degenerate_faces Branch 8 @ line 2244 — *single-isolated-degenerate-face*:
  'if (!detect_cc_of_degenerate_triangles) { // flip the longest edge }'
  — when exactly one degenerate face is present with NO adjacent degenerate faces,
  detect_cc_of_degenerate_triangles is set to false and CGAL attempts to flip the
  degenerate face's longest edge rather than collecting a connected component.

Defect pattern: a clean triangulated strip of 3 non-degenerate triangles with an
  isolated collinear degenerate triangle attached at one edge. Vertices:
    v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(1.5,1,0), v4=(2,0,0).
  Clean triangles t0=(v0,v1,v2), t1=(v1,v3,v2), t2=(v1,v4,v3) form a healthy strip.
  The degenerate triangle t3=(v4,v5,v0) where v5=(1,0,0) is collinear — but this
  would conflict. Instead, the degenerate triangle t3 is a separate collinear triangle
  v5=(3,0,0), v6=(4,0,0) collinear with v4=(2,0,0), all along X axis.
  t3=(v4,v5,v6) is zero-area and shares edge (v4,_) only with the boundary.
  It has no adjacent degenerate triangles, so detect_cc=false.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1091",
             title="single isolated degenerate face attached at strip boundary: flip-candidate branch",
             defect_class="degenerate_triangle")

# Clean triangulated strip.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2
v3 = m.vertex(1.5, 1.0, 0.0)   # 3
v4 = m.vertex(2.0, 0.0, 0.0)   # 4

t0 = m.triangle(v0, v1, v2)   # face 0: clean
t1 = m.triangle(v1, v3, v2)   # face 1: clean
t2 = m.triangle(v1, v4, v3)   # face 2: clean

# Degenerate triangle attached at boundary edge (v1,v4) of t2.
# v5 is on the X axis between v1=(1,0,0) and v4=(2,0,0): midpoint (1.5,0,0).
# t3=(v1, v5, v4): all three on Y=0, Z=0 line → zero area.
v5 = m.vertex(1.5, 0.0, 0.0)   # 5 — midpoint of v1..v4, collinear
t3 = m.triangle(v1, v5, v4)    # face 3: DEGENERATE — v1, v5, v4 collinear along X

# Assert isolated degenerate triangle has zero area.
m.assert_triangle_area_lt(t3, 1e-12)

# Edge (v1,v4) is shared by t2 and t3 (interior between clean and degenerate).
m.assert_edge_shared(v1, v4, 2)

# The degenerate triangle's other two edges are true boundary edges.
m.assert_edge_shared(v1, v5, 1)
m.assert_edge_shared(v4, v5, 1)
