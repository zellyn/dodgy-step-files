"""Me1156 — PMP.orient nesting_depth_parity: two concentric closed components;
  inner component depth=1 (odd) gets inward orientation (Branch 2).

CGAL PMP `PMP.orient` Branch 2 (*nesting_depth_parity*) @ line 395:
  'if(depth % 2 == 1) orient_inward(cc); else orient_outward(cc);' —
  after computing nesting depth for each connected component, orient assigns
  outward normals to even-depth components (outside shells) and inward normals
  to odd-depth components (interior cavities). Branch 2 fires when the parity
  check is evaluated.

Defect pattern: two concentric closed tetrahedra (inner and outer). The outer
  tetrahedron (depth=0) should have outward normals; the inner tetrahedron
  (depth=1, nested inside the outer) should have inward normals to form a
  void/cavity. orient computes nesting depth via ray casting and applies the
  parity rule to each CC.

Geometry:
  Outer tetrahedron: a0=(0,0,0), a1=(4,0,0), a2=(2,3.46,0), a3=(2,1.15,3.27)
  Inner tetrahedron: b0=(1.5,0.5,0.5), b1=(2.5,0.5,0.5), b2=(2,1.87,0.5), b3=(2,1.07,1.5)
  The inner tetrahedron is completely inside the outer. Two separate CCs.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1156",
    title="PMP.orient nesting_depth_parity: inner CC depth=1 receives inward orientation; outer CC depth=0 outward (Branch 2)",
    defect_class="inverted_normals",
)

# Outer (large) closed tetrahedron.
a0 = m.vertex(0.0,  0.0,    0.0)    # 0
a1 = m.vertex(4.0,  0.0,    0.0)    # 1
a2 = m.vertex(2.0,  3.46,   0.0)    # 2
a3 = m.vertex(2.0,  1.15,   3.27)   # 3

# CCW-wound outer faces (outward normals).
t0 = m.triangle(a0, a1, a2)  # 0: outer base
t1 = m.triangle(a0, a3, a1)  # 1: outer front face
t2 = m.triangle(a1, a3, a2)  # 2: outer right face
t3 = m.triangle(a2, a3, a0)  # 3: outer left face

# Inner (small) closed tetrahedron — nestled inside the outer.
b0 = m.vertex(1.5,  0.5,    0.5)    # 4
b1 = m.vertex(2.5,  0.5,    0.5)    # 5
b2 = m.vertex(2.0,  1.87,   0.5)    # 6
b3 = m.vertex(2.0,  1.07,   1.5)    # 7

# CCW-wound inner faces (currently outward; orient will flip to inward for depth=1).
t4 = m.triangle(b0, b1, b2)  # 4: inner base
t5 = m.triangle(b0, b3, b1)  # 5: inner front face
t6 = m.triangle(b1, b3, b2)  # 6: inner right face
t7 = m.triangle(b2, b3, b0)  # 7: inner left face

# Outer tetrahedron: all 6 edges shared by exactly 2 faces.
m.assert_edge_shared(a0, a1, 2)
m.assert_edge_shared(a1, a2, 2)
m.assert_edge_shared(a0, a2, 2)
m.assert_edge_shared(a0, a3, 2)
m.assert_edge_shared(a1, a3, 2)
m.assert_edge_shared(a2, a3, 2)

# Inner tetrahedron: all 6 edges shared by exactly 2 faces.
m.assert_edge_shared(b0, b1, 2)
m.assert_edge_shared(b1, b2, 2)
m.assert_edge_shared(b0, b2, 2)
m.assert_edge_shared(b0, b3, 2)
m.assert_edge_shared(b1, b3, 2)
m.assert_edge_shared(b2, b3, 2)

# Two disconnected closed CCs — no shared edges.
m.assert_triangle_not_reachable_from(t4, t0)

# Combined Euler: V=8, E=12, F=8, chi=4 (two closed manifolds each chi=2).
m.assert_euler_characteristic(8, 12, 8, 4)
