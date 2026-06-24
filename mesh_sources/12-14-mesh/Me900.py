"""Me900 — orient_triangle_soup_with_reference_triangle_soup reference_degenerate_triangle: degenerate reference triangle skipped during orientation alignment (Branch 1).

CGAL PMP `PMP.orient_triangle_soup_with_reference_triangle_soup` Branch 1
(*reference_degenerate_triangle*) @ line 155:
  'if (is_degenerate(ref_triangle)) continue;'
  — for each reference triangle the algorithm checks is_degenerate(); if true it
  skips that triangle and does not use it to orient the soup. A reference triangle
  with collinear vertices (area=0) is the minimal trigger.

Defect pattern: a small triangle soup (two non-degenerate query triangles) paired
  with a reference soup that contains one degenerate triangle (three collinear
  vertices at y=0) plus one valid reference triangle. The degenerate reference
  triangle cannot supply a normal; Branch 1 fires and it is skipped. Only the
  valid reference triangle participates in orientation alignment.

Geometry (query mesh):
  q0=(0,0,0), q1=(2,0,0), q2=(1,1,0), q3=(0,2,0)
  t0=(q0,q1,q2) — lower triangle (CCW in XY, normal +Z)
  t1=(q0,q2,q3) — upper triangle (CCW in XY, normal +Z)
  Shared interior edge (q0,q2): n=2. Four boundary edges: n=1 each.

Reference soup:
  r0=(0,0,0), r1=(2,0,0), r2=(1,0,0) — degenerate: r2 lies on r0-r1 line (area=0)
  r3=(0,1,0), r4=(2,1,0), r5=(1,2,0)
  ref_t0=(r0,r1,r2) — degenerate (is_degenerate → Branch 1 skips it)
  ref_t1=(r3,r4,r5) — valid reference (CCW, normal +Z)

Assertion evidence:
  - triangle_area_lt(t_degen=2, 1e-9): reference triangle index 2 (0-based in
    the combined vertex list) has area < 1e-9.
  - adjacent_triangles_inconsistent_winding absent: query triangles are consistently
    wound (no winding conflict in the query soup itself).
  - edge_shared_by_n_triangles(q0,q2,2): confirms the two query triangles share
    an interior edge — mesh is connected.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me900",
    title="orient_triangle_soup_with_reference_triangle_soup reference_degenerate_triangle: collinear reference triangle (area=0) skipped by is_degenerate check; only valid reference face used (Branch 1)",
    defect_class="degenerate_triangle",
)

# --- Query mesh vertices ---
q0 = m.vertex(0.0, 0.0, 0.0)  # 0
q1 = m.vertex(2.0, 0.0, 0.0)  # 1
q2 = m.vertex(1.0, 1.0, 0.0)  # 2 — shared interior vertex
q3 = m.vertex(0.0, 2.0, 0.0)  # 3

# --- Reference soup vertices ---
r0 = m.vertex(0.0, 0.0, 0.0)  # 4 — degenerate ref vertex A
r1 = m.vertex(2.0, 0.0, 0.0)  # 5 — degenerate ref vertex B
r2 = m.vertex(1.0, 0.0, 0.0)  # 6 — degenerate ref vertex C: collinear on AB
r3 = m.vertex(0.0, 1.0, 0.0)  # 7 — valid ref vertex A
r4 = m.vertex(2.0, 1.0, 0.0)  # 8 — valid ref vertex B
r5 = m.vertex(1.0, 2.0, 0.0)  # 9 — valid ref vertex C

# --- Query triangles ---
t0 = m.triangle(q0, q1, q2)   # 0: lower CCW query triangle
t1 = m.triangle(q0, q2, q3)   # 1: upper CCW query triangle

# --- Reference triangles ---
t_degen = m.triangle(r0, r1, r2)   # 2: degenerate reference (r2 collinear on r0-r1)
t_valid = m.triangle(r3, r4, r5)   # 3: valid reference (CCW, normal +Z)

# Query interior edge: shared by both query triangles.
m.assert_edge_shared(q0, q2, 2)   # interior edge between t0 and t1

# Query boundary edges (n=1).
m.assert_edge_shared(q0, q1, 1)   # t0 bottom
m.assert_edge_shared(q1, q2, 1)   # t0 right
m.assert_edge_shared(q2, q3, 1)   # t1 right
m.assert_edge_shared(q0, q3, 1)   # t1 left

# The degenerate reference triangle (t_degen, index 2) has area=0:
# r2=(1,0,0) lies exactly on segment r0-r1, so cross product = 0.
m.assert_triangle_area_lt(t_degen, 1e-9)

# Euler for query mesh: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
