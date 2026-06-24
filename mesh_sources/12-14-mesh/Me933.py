"""Me933 — PMP.orient orientation-assignment-by-nesting: inner component detected ON_BOUNDED_SIDE; inward orientation assigned (Branch 4).

CGAL PMP `PMP.orient (main dispatcher)` Branch 4 (*orientation-assignment-by-nesting*) @ line 1007:
  'if(side_of_cc(xtrm_vertices[cc_id]) == ON_BOUNDED_SIDE) { ... orient_to_bound_a_volume(...); }'
  — for each non-self-intersecting component the dispatcher calls side_of_cc() using
  the component's extremal vertex as a probe point against the reference component.
  ON_BOUNDED_SIDE means the probe is inside the reference shell → the component is
  nested inside another → it needs inward (reversed) orientation to correctly bound a
  volume. Branch 4 fires when side_of_cc returns ON_BOUNDED_SIDE.

Defect pattern: two nested closed tetrahedral shells. The outer shell (Component A) is a
  large tetrahedron; the inner shell (Component B) is a small tetrahedron geometrically
  contained inside A. When the dispatcher probes Component B's extremal vertex against
  Component A's volume, side_of_cc returns ON_BOUNDED_SIDE → Branch 4 fires →
  orient_to_bound_a_volume is called to assign inward orientation to Component B.

Geometry:
  Component A (outer): a0=(0,0,0), a1=(6,0,0), a2=(3,6,0), a3=(3,3,6) — large tetra.
  Component B (inner): b0=(2,1,1), b1=(4,1,1), b2=(3,3,1), b3=(3,2,2.5) — small tetra
    with all vertices strictly inside Component A's convex hull.
  Both components are closed manifold tetrahedra (V=4, E=6, F=4, χ=2 each).
  Component B's extremal vertex b3=(3,2,2.5) lies inside the volume of Component A.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me933",
    title="PMP.orient orientation-assignment-by-nesting: small inner tetrahedron ON_BOUNDED_SIDE of large outer tetrahedron; inward orientation assigned (Branch 4)",
    defect_class="inverted_normals",
)

# Component A — large outer tetrahedron.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(6.0, 0.0, 0.0)   # 1
a2 = m.vertex(3.0, 6.0, 0.0)   # 2
a3 = m.vertex(3.0, 3.0, 6.0)   # 3 — apex at Z=6

# Component B — small inner tetrahedron, all vertices inside Component A.
# Centroid of A ≈ (3, 2.25, 1.5). Place B near centroid, well inside.
b0 = m.vertex(2.0, 1.0, 1.0)   # 4
b1 = m.vertex(4.0, 1.0, 1.0)   # 5
b2 = m.vertex(3.0, 3.0, 1.0)   # 6
b3 = m.vertex(3.0, 2.0, 2.5)   # 7 — apex at Z=2.5, inside A

# Component A faces (outward CCW from outside).
t0 = m.triangle(a0, a1, a2)   # base
t1 = m.triangle(a0, a3, a1)   # front-side
t2 = m.triangle(a1, a3, a2)   # right-side
t3 = m.triangle(a0, a2, a3)   # left-side

# Component B faces (outward CCW — will be flipped by orient after nesting detected).
t4 = m.triangle(b0, b1, b2)   # base
t5 = m.triangle(b0, b3, b1)   # front-side
t6 = m.triangle(b1, b3, b2)   # right-side
t7 = m.triangle(b0, b2, b3)   # left-side

# Component A — all 6 edges closed (shared by 2 faces).
m.assert_edge_shared(a0, a1, 2)
m.assert_edge_shared(a0, a2, 2)
m.assert_edge_shared(a1, a2, 2)
m.assert_edge_shared(a0, a3, 2)
m.assert_edge_shared(a1, a3, 2)
m.assert_edge_shared(a2, a3, 2)

# Component B — all 6 edges closed (shared by 2 faces).
m.assert_edge_shared(b0, b1, 2)
m.assert_edge_shared(b0, b2, 2)
m.assert_edge_shared(b1, b2, 2)
m.assert_edge_shared(b0, b3, 2)
m.assert_edge_shared(b1, b3, 2)
m.assert_edge_shared(b2, b3, 2)

# Two disconnected components (no edge path from A to B).
m.assert_triangle_not_reachable_from(t4, t0)

# No self-intersections between the two components (B is fully inside A).
m.assert_triangles_do_not_intersect(t0, t4)

# Full mesh: V=8, E=12, F=8, χ=4 (two disjoint closed spheres).
m.assert_euler_characteristic(8, 12, 8, 4)
