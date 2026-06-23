"""Me032 — collinear_cc_strip: connected component of adjacent collinear triangles (Branch 9).

Catalog claim: three collinear zero-area triangles are chained end-to-end
forming a strip along the X axis. All three share edges and form a single
connected component (cc_faces). The boundary of the component (boundary_hedges)
encloses a degenerate disk. CGAL PMP.remove_degenerate_faces collects the
connected component and attempts to remove it as a disk.

Source: CGAL PMP.remove_degenerate_faces Branch 9 @ line 2319 —
*connected-component-of-collinear-faces*: multiple adjacent degenerate
triangles share vertices; cc_faces collected; boundary_hedges defines the
removal boundary.

Defect carrier: four vertices along the X axis (x=0,1,2,3) and three
collinear triangles (tri 0: v0-v1-v2, tri 1: v1-v2-v3, tri 2: v0-v2-v3).
All three triangles have zero area and share internal edges, forming a
connected degenerate strip. A clean control triangle sits apart.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me032",
             title="connected component of collinear faces: 3-triangle degenerate strip",
             defect_class="degenerate_triangle")

# Four collinear vertices — all degenerate triangles built from these.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(3.0, 0.0, 0.0)   # 3

# Three collinear connected triangles.
t0 = m.triangle(v0, v1, v2)   # face 0: zero area
t1 = m.triangle(v1, v2, v3)   # face 1: zero area, shares edge (v1,v2) with t0
t2 = m.triangle(v0, v2, v3)   # face 2: zero area, shares edges with t0 and t1

# Clean control triangle (isolated, non-degenerate).
v4 = m.vertex(0.0, 2.0, 0.0)
v5 = m.vertex(1.0, 2.0, 0.0)
v6 = m.vertex(0.5, 3.0, 0.0)
t3 = m.triangle(v4, v5, v6)   # face 3: clean, non-degenerate

# Assert all three degenerate faces have zero area.
m.assert_triangle_area_lt(t0, 1e-12)
m.assert_triangle_area_lt(t1, 1e-12)
m.assert_triangle_area_lt(t2, 1e-12)

# Shared internal edges: each shared by 2 faces within the degenerate CC.
m.assert_edge_shared(v1, v2, 2)   # shared by t0 and t1
m.assert_edge_shared(v0, v2, 2)   # shared by t0 and t2
m.assert_edge_shared(v2, v3, 2)   # shared by t1 and t2
