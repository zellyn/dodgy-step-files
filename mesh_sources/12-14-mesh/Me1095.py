"""Me1095 — flip_impossible_shared_diagonal: pre-existing diagonal blocks edge flip (Branch 12).

CGAL PMP.remove_degenerate_faces Branch 12 @ line 2256 — *edge-flip-impossible*:
  'if (!CGAL::Euler::can_flip_edge(h, tmesh)) { /* flip is not possible */ all_removed = false; }'
  — when the degenerate face is isolated (no adjacent degenerate neighbors) and CGAL
  attempts a longest-edge flip, the flip fails because the would-be new edge already
  exists in the mesh. The face is removed via remove_face instead; all_removed is set false.

Defect pattern: a quad formed by vertices v0=(0,0,0), v1=(2,0,0), v2=(1,1,0), v3=(1,-1,0).
  Two healthy triangles t0=(v0,v2,v1) and t1=(v0,v1,v3) share the interior diagonal
  (v0,v1). A degenerate collinear triangle t2=(v0,v3,v1) also contains edge (v0,v1)
  — so (v0,v1) is shared by 3 faces. The degenerate face t2's longest edge is (v0,v1).
  Attempting to flip (v0,v1) fails because the flip would produce an edge identical to
  an already-existing diagonal: CGAL detects 'flip is not possible' and removes t2
  directly, setting all_removed=false.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1095",
             title="flip-impossible degenerate: longest-edge diagonal already 3-way shared — removal fallback",
             defect_class="degenerate_triangle")

# Quad diamond: left, right, top, bottom.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — left vertex
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — right vertex
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — top vertex
v3 = m.vertex(1.0,-1.0, 0.0)   # 3 — bottom vertex

# Two healthy triangles sharing the horizontal diagonal (v0, v1).
t0 = m.triangle(v0, v2, v1)   # face 0: upper triangle; edges (v0,v2),(v2,v1),(v0,v1)
t1 = m.triangle(v0, v1, v3)   # face 1: lower triangle; edges (v0,v1),(v1,v3),(v0,v3)

# Degenerate collinear triangle using the same diagonal (v0, v1).
# v4 is the midpoint of v0..v1 on the X axis — collinear with v0 and v1.
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — midpoint of v0..v1; collinear
t2 = m.triangle(v0, v4, v1)   # face 2: DEGENERATE; v0=(0,0,0), v4=(1,0,0), v1=(2,0,0) collinear

# Assert the degenerate triangle has zero area.
m.assert_triangle_area_lt(t2, 1e-12)

# The diagonal (v0, v1) is shared by all 3 faces — flip is impossible.
m.assert_edge_shared(v0, v1, 3)

# Outer boundary edges of the healthy triangles (each shared by 1 face).
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v3, 1)
