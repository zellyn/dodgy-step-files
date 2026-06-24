"""Me1160 — PMP.orient_to_bound_a_volume parent_child_orientation_rule: inner CC
  oriented opposite to parent; child depth=1 flipped inward (Branch 3).

CGAL PMP `PMP.orient_to_bound_a_volume` Branch 3 (*parent_child_orientation_rule*) @ line 1005:
  'if(is_on_bounded_side(parent_cc, cc)) flip_orientation(cc);' —
  after computing nesting depths, orient_to_bound_a_volume assigns orientation
  based on parent-child relationships: a component nested inside another (its
  child) must face the opposite direction. Branch 3 fires when the function
  applies this parent-child flip to the inner (child) component.

Defect pattern: two concentric closed tetrahedra (parent outer + child inner).
  orient_to_bound_a_volume first orients the outer shell with outward normals
  (depth=0), then detects the inner shell is nested inside the outer (depth=1)
  and flips it so its normals point inward — Branch 3 fires on the parent-child
  orientation assignment.

Geometry:
  Outer: c0=(0,0,0), c1=(8,0,0), c2=(4,6.93,0), c3=(4,2.31,6.53)
  Inner: d0=(2.5,1,0.7), d1=(5.5,1,0.7), d2=(4,4.5,0.7), d3=(4,2.2,3.5)
  The inner tetrahedron is completely enclosed by the outer.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1160",
    title="PMP.orient_to_bound_a_volume parent_child_orientation_rule: inner CC depth=1 flipped opposite to outer parent shell (Branch 3)",
    defect_class="inverted_normals",
)

# Outer (parent) closed tetrahedron.
c0 = m.vertex(0.0,  0.0,    0.0)    # 0
c1 = m.vertex(8.0,  0.0,    0.0)    # 1
c2 = m.vertex(4.0,  6.93,   0.0)    # 2
c3 = m.vertex(4.0,  2.31,   6.53)   # 3

t0 = m.triangle(c0, c1, c2)  # 0: outer base (CCW from above)
t1 = m.triangle(c0, c3, c1)  # 1: outer front
t2 = m.triangle(c1, c3, c2)  # 2: outer right
t3 = m.triangle(c2, c3, c0)  # 3: outer left

# Inner (child) closed tetrahedron — nested inside the outer.
d0 = m.vertex(2.5,  1.0,    0.7)    # 4
d1 = m.vertex(5.5,  1.0,    0.7)    # 5
d2 = m.vertex(4.0,  4.5,    0.7)    # 6
d3 = m.vertex(4.0,  2.2,    3.5)    # 7

# CCW-wound inner faces — currently with outward normals;
# orient_to_bound_a_volume will flip to inward (Branch 3).
t4 = m.triangle(d0, d1, d2)  # 4: inner base
t5 = m.triangle(d0, d3, d1)  # 5: inner front
t6 = m.triangle(d1, d3, d2)  # 6: inner right
t7 = m.triangle(d2, d3, d0)  # 7: inner left

# Outer shell: all 6 edges shared by 2 faces.
m.assert_edge_shared(c0, c1, 2)
m.assert_edge_shared(c1, c2, 2)
m.assert_edge_shared(c0, c2, 2)
m.assert_edge_shared(c0, c3, 2)
m.assert_edge_shared(c1, c3, 2)
m.assert_edge_shared(c2, c3, 2)

# Inner shell: all 6 edges shared by 2 faces.
m.assert_edge_shared(d0, d1, 2)
m.assert_edge_shared(d1, d2, 2)
m.assert_edge_shared(d0, d2, 2)
m.assert_edge_shared(d0, d3, 2)
m.assert_edge_shared(d1, d3, 2)
m.assert_edge_shared(d2, d3, 2)

# Two separate CCs — no path between them.
m.assert_triangle_not_reachable_from(t4, t0)

# Combined Euler: V=8, E=12, F=8, chi=4 (two closed manifolds).
m.assert_euler_characteristic(8, 12, 8, 4)
