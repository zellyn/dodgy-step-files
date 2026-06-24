"""Me902 — orient_triangle_soup_with_reference_triangle_soup orientation_flip_decision: dot product of normals negative; query triangle flipped to match reference (Branch 3).

CGAL PMP `PMP.orient_triangle_soup_with_reference_triangle_soup` Branch 3
(*orientation_flip_decision*) @ line 200:
  'if (dot_product(query_normal, ref_normal) < 0) flip(query_triangle);'
  — after finding the closest reference face the algorithm computes the dot product
  of the query triangle's normal with the reference triangle's normal. If the dot
  product is negative (normals point opposite directions), the query triangle is
  flipped. Branch 3 fires for any query triangle whose normal opposes the nearest
  reference normal.

Defect pattern: two adjacent query triangles sharing an interior edge, where one
  triangle (t1) has reversed winding (CW) relative to its neighbour (t0) and to
  the reference soup. The reference contains a matching pair of CCW triangles.
  The dot product of t1's normal (−Z) against the nearest reference normal (+Z)
  is −1 → Branch 3 fires and t1 is flipped.

Geometry (query mesh):
  p0=(0,0,0), p1=(2,0,0), p2=(1,1,0), p3=(0,2,0)
  t0=(p0,p1,p2) — CCW (normal +Z) — correctly wound
  t1=(p2,p0,p3) — CW  (normal −Z) — reversed vs reference; Branch 3 target

  Interior edge (p0,p2) shared by t0 and t1: both contain vertices p0 and p2.
  t0=(p0,p1,p2): edges (p0,p1),(p1,p2),(p0,p2)[interior].
  t1=(p2,p0,p3): edges (p2,p0)=(p0,p2)[interior],(p2,p3),(p0,p3).
  Boundary: (p0,p1),(p1,p2),(p2,p3),(p0,p3).

Reference soup:
  r0=(0,0,-1), r1=(2,0,-1), r2=(1,1,-1), r3=(0,2,-1)
  ref_t0=(r0,r1,r2) — CCW (normal +Z); closest to query t0
  ref_t1=(r0,r2,r3) — CCW (normal +Z); closest to query t1

  Query t1 has normal −Z; ref_t1 has normal +Z; dot product = −1 < 0 → flip.

Assertion evidence:
  - adjacent_triangles_inconsistent_winding(t0=0, t1=1): t0 normal is +Z,
    t1 normal is −Z; they share edge (p0,p2); inconsistent winding confirmed.
  - triangle_normal_z_negative(t1=1): t1=(p2,p0,p3) is CW in XY plane;
    cross product (p0−p2)×(p3−p2) points −Z.
  - edge_shared_by_n_triangles(p0,p2, n=2): interior shared edge confirms
    adjacency of t0 and t1.
  - Euler: V=4, E=5, F=2, chi=1 (open disk).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me902",
    title="orient_triangle_soup_with_reference_triangle_soup orientation_flip_decision: t1 CW winding gives normal -Z; dot product with reference normal +Z is negative; t1 flipped (Branch 3)",
    defect_class="inverted_normal",
)

# --- Query mesh vertices ---
p0 = m.vertex(0.0, 0.0, 0.0)  # 0
p1 = m.vertex(2.0, 0.0, 0.0)  # 1
p2 = m.vertex(1.0, 1.0, 0.0)  # 2 — shared interior vertex
p3 = m.vertex(0.0, 2.0, 0.0)  # 3

# --- Reference soup vertices (z=-1 plane) ---
r0 = m.vertex(0.0, 0.0, -1.0)  # 4
r1 = m.vertex(2.0, 0.0, -1.0)  # 5
r2 = m.vertex(1.0, 1.0, -1.0)  # 6
r3 = m.vertex(0.0, 2.0, -1.0)  # 7

# --- Query triangles ---
t0 = m.triangle(p0, p1, p2)   # 0: CCW (normal +Z) — correctly wound
t1 = m.triangle(p2, p0, p3)   # 1: CW  (normal −Z) — reversed; Branch 3 target

# --- Reference triangles (both CCW, normal +Z) ---
ref_t0 = m.triangle(r0, r1, r2)   # 2: closest to query t0
ref_t1 = m.triangle(r0, r2, r3)   # 3: closest to query t1

# t0 and t1 share interior edge (p0, p2).
m.assert_edge_shared(p0, p2, 2)   # interior edge: t0 and t1

# Boundary edges (n=1 each).
m.assert_edge_shared(p0, p1, 1)   # t0 bottom
m.assert_edge_shared(p1, p2, 1)   # t0 right
m.assert_edge_shared(p2, p3, 1)   # t1 upper-right
m.assert_edge_shared(p0, p3, 1)   # t1 left

# t1 has reversed winding: normal is −Z.
m.assert_triangle_normal_z_negative(t1)

# t0 and t1 share an edge but have antiparallel normals.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Euler for query mesh: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
