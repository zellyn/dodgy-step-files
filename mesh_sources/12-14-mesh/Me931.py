"""Me931 — PMP.orient self-intersection-component-skip: cc_to_handle exhausted; loop exits (Branch 2).

CGAL PMP `PMP.orient (main dispatcher)` Branch 2 (*self-intersection-component-skip*) @ line 985:
  'if(!any) break;'
  — after each iteration the dispatcher checks whether the cc_to_handle set still
  contains any unprocessed component. When all components have been handled (oriented or
  skipped), the set becomes empty: any=false and the loop terminates via break.
  Branch 2 fires on the loop iteration that finds cc_to_handle exhausted.

Defect pattern: a minimal two-component mesh where both closed components are
  non-self-intersecting. The dispatcher processes Component A first (it becomes the
  reference component), then Component B (oriented relative to A). After both are
  handled, cc_to_handle is empty → any=false → Branch 2 fires and the outer loop
  terminates.

Geometry:
  Component A: small closed tetrahedron at origin (4 faces, vertices at Z 0–1).
  Component B: small closed tetrahedron offset in X by 5 (4 faces, same Z range).
  Both wound outward-CCW. No self-intersections between or within components.
  After both components are oriented, cc_to_handle = {} → break.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me931",
    title="PMP.orient self-intersection-component-skip: all components processed; cc_to_handle becomes empty → loop-break fires (Branch 2)",
    defect_class="disconnected_components",
)

# Component A — tetrahedron at X=0..2
a0 = m.vertex(0.0, 0.0, 0.0)   # 0
a1 = m.vertex(2.0, 0.0, 0.0)   # 1
a2 = m.vertex(1.0, 2.0, 0.0)   # 2
a3 = m.vertex(1.0, 1.0, 1.0)   # 3

# Component B — tetrahedron at X=5..7 (clearly separated, no SI)
b0 = m.vertex(5.0, 0.0, 0.0)   # 4
b1 = m.vertex(7.0, 0.0, 0.0)   # 5
b2 = m.vertex(6.0, 2.0, 0.0)   # 6
b3 = m.vertex(6.0, 1.0, 1.0)   # 7

# Component A faces (outward CCW).
t0 = m.triangle(a0, a1, a2)   # base
t1 = m.triangle(a0, a3, a1)   # side
t2 = m.triangle(a1, a3, a2)   # side
t3 = m.triangle(a0, a2, a3)   # side

# Component B faces (outward CCW).
t4 = m.triangle(b0, b1, b2)   # base
t5 = m.triangle(b0, b3, b1)   # side
t6 = m.triangle(b1, b3, b2)   # side
t7 = m.triangle(b0, b2, b3)   # side

# Component A — all 6 edges shared by 2 faces (closed).
m.assert_edge_shared(a0, a1, 2)
m.assert_edge_shared(a0, a2, 2)
m.assert_edge_shared(a1, a2, 2)
m.assert_edge_shared(a0, a3, 2)
m.assert_edge_shared(a1, a3, 2)
m.assert_edge_shared(a2, a3, 2)

# Component B — all 6 edges shared by 2 faces (closed).
m.assert_edge_shared(b0, b1, 2)
m.assert_edge_shared(b0, b2, 2)
m.assert_edge_shared(b1, b2, 2)
m.assert_edge_shared(b0, b3, 2)
m.assert_edge_shared(b1, b3, 2)
m.assert_edge_shared(b2, b3, 2)

# Components are disconnected (no shared-edge path from A to B).
m.assert_triangle_not_reachable_from(t4, t0)

# No self-intersections between the two separated tetrahedra.
m.assert_triangles_do_not_intersect(t0, t4)

# Full mesh: V=8, E=12, F=8, χ=4 (two disjoint closed spheres).
m.assert_euler_characteristic(8, 12, 8, 4)
