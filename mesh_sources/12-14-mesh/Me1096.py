"""Me1096 — border_face_null_opposite: degenerate boundary face has no opposite, direct remove_face (Branch 13).

CGAL PMP.remove_degenerate_faces Branch 13 @ line 2292 — *border-face-removal*:
  'if (opposite_face == GT::null_face()) { Euler::remove_face(h, tmesh); }'
  — when the degenerate face is on the boundary, the opposite face across its longest
  edge is a null face (GT::null_face()). A flip is impossible on a boundary edge, so
  CGAL removes the face directly via Euler::remove_face.

Defect pattern: an open triangulated strip (boundary mesh) with one degenerate triangle
  attached at the open boundary. Vertices v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0) form
  a clean base triangle t0. Vertex v3=(0,0,0) is the same position as v0 but separate
  — midpoint v4=(0.5,0,0) lies between v0 and v1. Degenerate face t1=(v0,v4,v1) is
  collinear along the X axis and attached to the boundary edge (v0,v1) of the base
  triangle. v4 is the midpoint of v0..v1 (all at y=0, z=0).

  t1's longest edge is (v0,v1). The opposite face across (v0,v1) from t1's perspective
  is t0. But the edges (v0,v4) and (v4,v1) are true boundary edges with no opposite face
  (null_face). CGAL identifies the open boundary condition and removes t1 via remove_face.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1096",
             title="border face removal: degenerate collinear triangle on open boundary — direct remove_face",
             defect_class="degenerate_triangle")

# Clean base triangle.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.5, 1.0, 0.0)   # 2

t0 = m.triangle(v0, v1, v2)   # face 0: clean non-degenerate base

# Additional clean triangles to form an open-boundary strip.
v3 = m.vertex(1.5, 0.5, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4
t1 = m.triangle(v1, v3, v4)   # face 1: clean
t2 = m.triangle(v1, v4, v2)   # face 2: clean

# Degenerate triangle on boundary: collinear vertices along Y=0 plane.
# v5 is the midpoint of v2=(0.5,1,0) and v4=(1,1,0) shifted down to be on y=1 line.
# Instead: attach a collinear triangle at the right boundary edge (v3,v4) which is open.
# v3=(1.5,0.5,0), v4=(1,1,0) — midpoint = (1.25, 0.75, 0).
v5 = m.vertex(1.25, 0.75, 0.0)   # 5 — midpoint of v3..v4 (collinear with v3 and v4)
t3 = m.triangle(v3, v5, v4)      # face 3: DEGENERATE — v3, v5, v4 are collinear

# Assert the degenerate triangle has zero area.
m.assert_triangle_area_lt(t3, 1e-12)

# Edge (v3,v4) is shared by t1 and t3 (interior between clean and degenerate).
m.assert_edge_shared(v3, v4, 2)

# The degenerate triangle's other edges are true boundary edges (shared by 1 face only).
m.assert_edge_shared(v3, v5, 1)
m.assert_edge_shared(v4, v5, 1)
