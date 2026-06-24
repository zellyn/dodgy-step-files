"""Me930 — PMP.orient z-extremum-selection: highest-Z component promoted as orientation reference (Branch 1).

CGAL PMP `PMP.orient (main dispatcher)` Branch 1 (*z-extremum-selection*) @ line 979:
  'if(z(xtrm_vertices[cc_id]) > z(xtrm_vertices[ref_cc_id])) ref_cc_id = cc_id;'
  — the main loop iterates over non-self-intersecting connected components and
  compares the Z coordinate of each component's extremal (highest-Z) vertex against
  the current reference component. The component with the globally highest Z vertex
  becomes the reference for outward orientation. Branch 1 fires when a later component
  has a higher extremal Z than the current best, causing ref_cc_id to be updated.

Defect pattern: two closed tetrahedral components at different Z heights. Component A
  (low tetrahedron, Z range 0–1) is processed first; Component B (high tetrahedron,
  Z range 10–11) has a higher extremal Z. When the loop reaches Component B its
  extremal vertex Z (11.0) exceeds the reference Z (1.0) → Branch 1 fires, ref_cc_id
  updated to Component B.

Geometry:
  Component A (low): a0=(0,0,0), a1=(2,0,0), a2=(1,2,0), a3=(1,1,1) — apex at Z=1.
  Component B (high): b0=(5,0,10), b1=(7,0,10), b2=(6,2,10), b3=(6,1,11) — apex at Z=11.
  Both are closed manifold tetrahedra wound outward-CCW.
  Two disconnected components: t0–t3 (Component A) and t4–t7 (Component B).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me930",
    title="PMP.orient z-extremum-selection: two-component mesh; high-Z tetra (apex Z=11) updates ref_cc_id over low-Z tetra (apex Z=1) (Branch 1)",
    defect_class="inverted_normals",
)

# Component A — low tetrahedron, Z range 0..1
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(2.0, 0.0, 0.0)   # 1
a2 = m.vertex(1.0, 2.0, 0.0)   # 2
a3 = m.vertex(1.0, 1.0, 1.0)   # 3 — extremal Z=1

# Component B — high tetrahedron, Z range 10..11
b0 = m.vertex(5.0, 0.0, 10.0)  # 4
b1 = m.vertex(7.0, 0.0, 10.0)  # 5
b2 = m.vertex(6.0, 2.0, 10.0)  # 6
b3 = m.vertex(6.0, 1.0, 11.0)  # 7 — extremal Z=11

# Component A: tetrahedron wound outward (CCW from outside).
t0 = m.triangle(a0, a1, a2)   # base face (a0,a1,a2): normal points -Z (outward down)
t1 = m.triangle(a0, a3, a1)   # side: normal points outward
t2 = m.triangle(a1, a3, a2)   # side: normal points outward
t3 = m.triangle(a0, a2, a3)   # side: normal points outward

# Component B: tetrahedron wound outward (CCW from outside).
t4 = m.triangle(b0, b1, b2)   # base face: normal points -Z (outward down)
t5 = m.triangle(b0, b3, b1)   # side: normal points outward
t6 = m.triangle(b1, b3, b2)   # side: normal points outward
t7 = m.triangle(b0, b2, b3)   # side: normal points outward

# Component A — all edges shared by exactly 2 faces (closed manifold).
m.assert_edge_shared(a0, a1, 2)
m.assert_edge_shared(a0, a2, 2)
m.assert_edge_shared(a1, a2, 2)
m.assert_edge_shared(a0, a3, 2)
m.assert_edge_shared(a1, a3, 2)
m.assert_edge_shared(a2, a3, 2)

# Component B — all edges shared by exactly 2 faces (closed manifold).
m.assert_edge_shared(b0, b1, 2)
m.assert_edge_shared(b0, b2, 2)
m.assert_edge_shared(b1, b2, 2)
m.assert_edge_shared(b0, b3, 2)
m.assert_edge_shared(b1, b3, 2)
m.assert_edge_shared(b2, b3, 2)

# Two disconnected components: no path from Component A to Component B.
m.assert_triangle_not_reachable_from(t4, t0)

# Two disjoint closed spheres: χ = χ_A + χ_B = 2 + 2 = 4.
# Full mesh: V=8, E=12, F=8, χ=4.
m.assert_euler_characteristic(8, 12, 8, 4)
