"""Me1159 — PMP.orient_to_bound_a_volume nesting_depth_calculation: two nested closed
  components; ray-casting parity determines inner CC depth (Branch 2).

CGAL PMP `PMP.orient_to_bound_a_volume` Branch 2 (*nesting_depth_calculation*) @ line 990:
  'nesting_level = count_intersections_along_ray(cc, all_ccs);' —
  for meshes with >1 connected component, orient_to_bound_a_volume shoots a
  ray from each component to count how many other components enclose it. The
  parity of the intersection count determines nesting depth. Branch 2 fires
  during the ray-casting loop to compute nesting level.

Defect pattern: two concentric closed tetrahedra. The outer tetrahedron encloses
  the inner one. orient_to_bound_a_volume fires Branch 2 when computing the
  nesting depth of the inner tetrahedron by ray casting against the outer shell.

Geometry:
  Outer: a0=(0,0,0), a1=(6,0,0), a2=(3,5.2,0), a3=(3,1.73,4.9)
  Inner: b0=(2,1,0.5), b1=(4,1,0.5), b2=(3,3,0.5), b3=(3,1.5,2.5)
  The inner tetrahedron is fully inside the outer.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1159",
    title="PMP.orient_to_bound_a_volume nesting_depth_calculation: ray casting counts intersection parity for inner CC nested inside outer (Branch 2)",
    defect_class="inverted_normals",
)

# Outer large closed tetrahedron.
a0 = m.vertex(0.0,  0.0,    0.0)    # 0
a1 = m.vertex(6.0,  0.0,    0.0)    # 1
a2 = m.vertex(3.0,  5.2,    0.0)    # 2
a3 = m.vertex(3.0,  1.73,   4.9)    # 3

t0 = m.triangle(a0, a1, a2)  # 0: outer base (CCW)
t1 = m.triangle(a0, a3, a1)  # 1: outer front
t2 = m.triangle(a1, a3, a2)  # 2: outer right
t3 = m.triangle(a2, a3, a0)  # 3: outer left

# Inner small closed tetrahedron — inside the outer.
b0 = m.vertex(2.0,  1.0,    0.5)    # 4
b1 = m.vertex(4.0,  1.0,    0.5)    # 5
b2 = m.vertex(3.0,  3.0,    0.5)    # 6
b3 = m.vertex(3.0,  1.5,    2.5)    # 7

t4 = m.triangle(b0, b1, b2)  # 4: inner base (CCW)
t5 = m.triangle(b0, b3, b1)  # 5: inner front
t6 = m.triangle(b1, b3, b2)  # 6: inner right
t7 = m.triangle(b2, b3, b0)  # 7: inner left

# Outer shell: all 6 edges shared by exactly 2 faces.
m.assert_edge_shared(a0, a1, 2)
m.assert_edge_shared(a1, a2, 2)
m.assert_edge_shared(a0, a2, 2)
m.assert_edge_shared(a0, a3, 2)
m.assert_edge_shared(a1, a3, 2)
m.assert_edge_shared(a2, a3, 2)

# Inner shell: all 6 edges shared by exactly 2 faces.
m.assert_edge_shared(b0, b1, 2)
m.assert_edge_shared(b1, b2, 2)
m.assert_edge_shared(b0, b2, 2)
m.assert_edge_shared(b0, b3, 2)
m.assert_edge_shared(b1, b3, 2)
m.assert_edge_shared(b2, b3, 2)

# Two disconnected CCs — no path from inner to outer.
m.assert_triangle_not_reachable_from(t4, t0)

# Combined Euler: V=8, E=12, F=8, chi=4 (two separate closed manifolds).
m.assert_euler_characteristic(8, 12, 8, 4)
