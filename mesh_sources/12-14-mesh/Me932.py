"""Me932 — PMP.orient self-intersecting-pair-detection: self-intersecting component marked; nesting test skipped (Branch 3).

CGAL PMP `PMP.orient (main dispatcher)` Branch 3 (*self-intersecting-pair-detection*) @ line 1001:
  'if(does_self_intersect(faces_of_cc[ccs_to_test_i], tm, params)) self_intersecting_cc.insert(cc_id);'
  — the dispatcher calls does_self_intersect() for each component in cc_to_handle.
  When a self-intersecting component is detected, its ID is inserted into
  self_intersecting_cc. The orientation-by-nesting logic (side_of_cc check) is
  then skipped for that component. Branch 3 fires for any component that returns
  true from does_self_intersect.

Defect pattern: two closed components. Component A is a clean closed tetrahedron.
  Component B is a closed orientable shell (8 triangles, 6 vertices, χ=2) where
  two faces genuinely pierce each other in 3D: face t4=(b0,b1,b2) in the Y=0 plane
  crosses face t5=(b3,b4,b5) which straddles Y=0 (b3 at Y=-1, b4 at Y=+1, b5 at Y=2).
  The dispatcher detects Component B as self-intersecting → inserts it into
  self_intersecting_cc → skips nesting test for Component B.

Geometry:
  Component A: a0=(0,0,0), a1=(2,0,0), a2=(1,2,0), a3=(1,1,1) — clean tetrahedron.
  Component B (8 faces, 6 vertices):
    b0=(5,0,0), b1=(7,0,0), b2=(6,0,2) — face t4 in Y=0 plane
    b3=(6,-1,0), b4=(6,1,0), b5=(5,0,2) — face t5 slanted across Y=0
  Cross face t4=(b0,b1,b2) lies in plane Y=0.
  Cross face t5=(b3,b4,b5) straddles plane Y=0 (b3 at Y=-1, b4 at Y=1).
  t5 intersects plane Y=0 along a segment that passes through the interior of t4 → SI.
  Six sealing faces complete the closed shell: s1=(b0,b1,b4), s2=(b0,b4,b3),
  s3=(b1,b2,b5), s4=(b1,b5,b4), s5=(b0,b5,b2), s6=(b0,b3,b5).
  All 12 edges of Component B are shared by exactly 2 faces.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me932",
    title="PMP.orient self-intersecting-pair-detection: Component B closed shell where t4 (Y=0 plane) is pierced by t5 (straddles Y=0); self_intersecting_cc.insert() fires (Branch 3)",
    defect_class="self_intersection",
)

# Component A — clean closed tetrahedron.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(2.0, 0.0, 0.0)   # 1
a2 = m.vertex(1.0, 2.0, 0.0)   # 2
a3 = m.vertex(1.0, 1.0, 1.0)   # 3

# Component B — self-intersecting closed shell.
b0 = m.vertex(5.0,  0.0, 0.0)  # 4 — cross face A base-left
b1 = m.vertex(7.0,  0.0, 0.0)  # 5 — cross face A base-right
b2 = m.vertex(6.0,  0.0, 2.0)  # 6 — cross face A apex (in Y=0 plane)
b3 = m.vertex(6.0, -1.0, 0.0)  # 7 — cross face B base-back (Y<0)
b4 = m.vertex(6.0,  1.0, 0.0)  # 8 — cross face B base-front (Y>0)
b5 = m.vertex(5.0,  0.0, 2.0)  # 9 — cross face B apex (in Y=0 plane)

# Component A faces (outward CCW).
t0 = m.triangle(a0, a1, a2)
t1 = m.triangle(a0, a3, a1)
t2 = m.triangle(a1, a3, a2)
t3 = m.triangle(a0, a2, a3)

# Component B: cross faces.
t4 = m.triangle(b0, b1, b2)   # cross face A — in Y=0 plane
t5 = m.triangle(b3, b4, b5)   # cross face B — straddles Y=0; pierces t4

# Component B: 6 sealing faces completing the closed shell.
t6 = m.triangle(b0, b1, b4)   # side — shares (b0,b1) with t4
t7 = m.triangle(b0, b4, b3)   # side
t8 = m.triangle(b1, b2, b5)   # side — shares (b1,b2) with t4
t9 = m.triangle(b1, b5, b4)   # side
t10 = m.triangle(b0, b5, b2)  # side — shares (b0,b2) with t4
t11 = m.triangle(b0, b3, b5)  # side

# Component A — all 6 edges closed.
m.assert_edge_shared(a0, a1, 2)
m.assert_edge_shared(a0, a2, 2)
m.assert_edge_shared(a1, a2, 2)
m.assert_edge_shared(a0, a3, 2)
m.assert_edge_shared(a1, a3, 2)
m.assert_edge_shared(a2, a3, 2)

# Component B — all 12 edges shared by exactly 2 faces.
m.assert_edge_shared(b0, b1, 2)  # t4 and t6
m.assert_edge_shared(b0, b2, 2)  # t4 and t10
m.assert_edge_shared(b1, b2, 2)  # t4 and t8
m.assert_edge_shared(b3, b4, 2)  # t5 and t7
m.assert_edge_shared(b3, b5, 2)  # t5 and t11
m.assert_edge_shared(b4, b5, 2)  # t5 and t9
m.assert_edge_shared(b0, b4, 2)  # t6 and t7
m.assert_edge_shared(b1, b4, 2)  # t6 and t9  (b1=idx5, b4=idx8 → canonical (5,8))
m.assert_edge_shared(b1, b5, 2)  # t8 and t9
m.assert_edge_shared(b2, b5, 2)  # t8 and t10
m.assert_edge_shared(b0, b5, 2)  # t10 and t11
m.assert_edge_shared(b0, b3, 2)  # t7 and t11

# Two disconnected components (no edge path between A and B).
m.assert_triangle_not_reachable_from(t4, t0)

# Component B self-intersection: t4 (in Y=0 plane) is pierced by t5 (straddles Y=0).
m.assert_triangles_self_intersect(t4, t5)

# Full mesh Euler: Component A (V=4,E=6,F=4,chi=2) + Component B (V=6,E=12,F=8,chi=2).
m.assert_euler_characteristic(10, 18, 12, 4)
