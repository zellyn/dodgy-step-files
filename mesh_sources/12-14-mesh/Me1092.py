"""Me1092 — degenerate_cc_disk_strip: connected component of collinear triangles forms removable disk (Branch 9).

CGAL PMP.remove_degenerate_faces Branch 9 @ line 2319 — *connected-component-of-collinear-faces*:
  'for (face_descriptor fd : cc_faces) { ... boundary_hedges ... }'
  — when multiple adjacent degenerate triangles share edges, CGAL collects them
  into cc_faces and walks boundary_hedges to attempt removal as a degenerate disk.

Defect pattern: five collinear vertices along the X axis at x=0,1,2,3,4. Three
  zero-area triangles form a connected strip: t0=(v0,v1,v2), t1=(v1,v3,v2),
  t2=(v2,v3,v4). Adjacent pairs share edges — t0 shares (v1,v2) with t1, and
  t1 shares (v2,v3) with t2. The strip forms a connected degenerate component
  (cc_faces = {t0,t1,t2}) whose boundary traversal encloses the outer hull
  (v0→v4) to form the disk boundary. Two clean healthy triangles anchor the
  outer boundary.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1092",
             title="connected component of collinear faces: 3-triangle cc strip for disk removal",
             defect_class="degenerate_triangle")

# Five collinear vertices along X — all degenerate triangles are built from these.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(3.0, 0.0, 0.0)   # 3
v4 = m.vertex(4.0, 0.0, 0.0)   # 4

# Three collinear connected triangles forming a strip CC.
t0 = m.triangle(v0, v1, v2)   # face 0: zero area; left segment
t1 = m.triangle(v1, v3, v2)   # face 1: zero area; shares (v1,v2) with t0
t2 = m.triangle(v2, v3, v4)   # face 2: zero area; shares (v2,v3) with t1

# Two clean anchor triangles (non-degenerate, not part of the CC).
v5 = m.vertex(2.0, 2.0, 0.0)   # 5 — above midpoint
v6 = m.vertex(2.0, -2.0, 0.0)  # 6 — below midpoint
t3 = m.triangle(v0, v4, v5)   # face 3: healthy, wide triangle above
t4 = m.triangle(v4, v0, v6)   # face 4: healthy, wide triangle below

# Assert all three degenerate faces have zero area.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)
m.assert_triangle_area_lt(t2, 1e-12)

# Internal edges of the degenerate CC (shared by 2 faces within the strip).
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v2, v3, 2)   # shared by t1 and t2

# Outer boundary edges of the strip (shared by degenerate + 0 or 1 healthy faces).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v3, v4, 1)
