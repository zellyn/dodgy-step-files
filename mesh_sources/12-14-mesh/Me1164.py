"""Me1164 — triangulate_and_refine_hole.main visitor_callback_optional:
  visitor parameter presence/absence; Default_visitor used when absent;
  start/end_refine_phase callbacks not invoked (Branch 4).

CGAL PMP `triangulate_and_refine_hole.main` Branch 4 (*visitor_callback_optional*)
  @ line 402:
  'GetVisitor::type visitor = choose_parameter(get_parameter(np, internal_np::visitor),
    Default_visitor());
   visitor.start_refine_phase(); ... refine(...); visitor.end_refine_phase();' —
  triangulate_and_refine_hole resolves the visitor named parameter. When
  absent, Default_visitor (a no-op implementation) is used so that
  start_refine_phase/end_refine_phase calls are harmless no-ops. Branch 4 fires
  when the visitor parameter lookup is evaluated.

Defect pattern: a hexagonal hole bordered by six hat-triangles. No caller-
  supplied visitor parameter: Default_visitor is substituted. The visitor
  callback phase-tracking is essentially a no-op. The 6-edge boundary forms
  a regular hexagonal hole.

Geometry:
  Hex corners: r0=(1,0,0), r1=(2,0,0), r2=(2.5,0.87,0), r3=(2,1.73,0),
               r4=(1,1.73,0), r5=(0.5,0.87,0)
  Hat outer: r6=(1.5,-0.87,0), r7=(3,0,0), r8=(3,1.73,0),
             r9=(1.5,2.6,0), r10=(0,1.73,0), r11=(0,0,0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1164",
    title="triangulate_and_refine_hole.main visitor_callback_optional: Default_visitor substituted; 6-edge hex hole; start/end_refine_phase no-ops (Branch 4)",
    defect_class="boundary_hole",
)

# Hexagonal hole boundary vertices.
r0 = m.vertex(1.0,   0.0,    0.0)   # 0
r1 = m.vertex(2.0,   0.0,    0.0)   # 1
r2 = m.vertex(2.5,   0.87,   0.0)   # 2
r3 = m.vertex(2.0,   1.73,   0.0)   # 3
r4 = m.vertex(1.0,   1.73,   0.0)   # 4
r5 = m.vertex(0.5,   0.87,   0.0)   # 5

# Hat outer vertices.
r6  = m.vertex(1.5,  -0.87,  0.0)   # 6 — south hat
r7  = m.vertex(3.0,   0.0,   0.0)   # 7 — SE hat
r8  = m.vertex(3.0,   1.73,  0.0)   # 8 — NE hat
r9  = m.vertex(1.5,   2.6,   0.0)   # 9 — north hat
r10 = m.vertex(0.0,   1.73,  0.0)   # 10 — NW hat
r11 = m.vertex(0.0,   0.0,   0.0)   # 11 — SW hat

# Six hat triangles.
t0 = m.triangle(r0, r6,  r1)   # 0: south hat
t1 = m.triangle(r1, r7,  r2)   # 1: SE hat
t2 = m.triangle(r2, r8,  r3)   # 2: NE hat
t3 = m.triangle(r3, r9,  r4)   # 3: north hat
t4 = m.triangle(r4, r10, r5)   # 4: NW hat
t5 = m.triangle(r5, r11, r0)   # 5: SW hat

# Hex hole boundary edges — each n=1.
m.assert_edge_shared(r0, r1, 1)
m.assert_edge_shared(r1, r2, 1)
m.assert_edge_shared(r2, r3, 1)
m.assert_edge_shared(r3, r4, 1)
m.assert_edge_shared(r4, r5, 1)
m.assert_edge_shared(r0, r5, 1)

# Outer hat edges.
m.assert_edge_shared(r0,  r6,  1)
m.assert_edge_shared(r1,  r6,  1)
m.assert_edge_shared(r1,  r7,  1)
m.assert_edge_shared(r2,  r7,  1)
m.assert_edge_shared(r2,  r8,  1)
m.assert_edge_shared(r3,  r8,  1)
m.assert_edge_shared(r3,  r9,  1)
m.assert_edge_shared(r4,  r9,  1)
m.assert_edge_shared(r4,  r10, 1)
m.assert_edge_shared(r5,  r10, 1)
m.assert_edge_shared(r5,  r11, 1)
m.assert_edge_shared(r0,  r11, 1)

# Hole boundary loop.
m.assert_hole_boundary([r0, r1, r2, r3, r4, r5])

# Open mesh with hexagonal hole: V=12, E=18, F=6, chi=0.
m.assert_euler_characteristic(12, 18, 6, 0)
