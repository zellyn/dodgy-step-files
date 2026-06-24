"""Me992 — orient_triangle_soup_with_reference_triangle_mesh triangle_degeneracy: is_degenerate_triangle_face check skips collinear reference triangle (Branch 3).

CGAL PMP `PMP.orient_triangle_soup_with_reference_triangle_mesh` Branch 3 (*triangle_degeneracy*) @ line 315:
  'if(PMP::is_degenerate_triangle_face(fd, tmesh, parameters::all_default())) continue;'
  — for each face of the reference mesh, before adding it to the AABB
  tree (or before using it for closest-face queries), the algorithm tests
  whether the face is degenerate (collinear vertices, zero area). A
  degenerate reference face is silently skipped. Branch 3 fires when the
  reference mesh contains ≥1 degenerate triangle.

Defect pattern: a reference mesh with one valid (non-degenerate) triangle
  and one degenerate collinear triangle. The degenerate reference triangle
  has its three vertices all on the X-axis — zero area, zero normal.
  Branch 3 fires when the algorithm processes the degenerate face and
  calls is_degenerate_triangle_face → true → continue (skip).

  The soup contains two triangles to be oriented against the valid
  reference triangle.

Geometry (reference mesh):
  Valid reference:
    r0=(0,0,0), r1=(2,0,0), r2=(1,2,0)
    ref_t0=(r0,r1,r2): CCW, normal +Z (area = 2.0).

  Degenerate reference (collinear — all three vertices on X-axis, zero area):
    d0=(0,0,0), d1=(1,0,0), d2=(2,0,0)
    ref_degen=(d0,d1,d2): collinear, area=0, is_degenerate → true → SKIPPED.

Geometry (soup):
  s0=(0,0,0), s1=(2,0,0), s2=(1,2,0)
  soup_t0=(s0,s1,s2): CCW, normal +Z (correct).

  s3=(0,0,0), s4=(1,2,0), s5=(2,0,0)
  soup_t1=(s3,s4,s5): CW, normal -Z (misoriented — the defect).

The algorithm skips ref_degen (Branch 3) and uses ref_t0 to orient the
soup. soup_t1 is detected as having a negative dot product with the
closest reference face normal and gets flipped.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me992",
    title="orient_triangle_soup_with_reference_triangle_mesh triangle_degeneracy: collinear degenerate reference triangle skipped by is_degenerate_triangle_face (Branch 3)",
    defect_class="soup_orientation_degenerate_reference",
)

# ---- reference mesh: one valid + one degenerate triangle ----
r0 = m.vertex(0.0, 0.0, 0.0)   # 0 — valid reference
r1 = m.vertex(2.0, 0.0, 0.0)   # 1
r2 = m.vertex(1.0, 2.0, 0.0)   # 2

d0 = m.vertex(0.0, 0.0, 0.0)   # 3 — degenerate reference (collinear, on X-axis)
d1 = m.vertex(1.0, 0.0, 0.0)   # 4
d2 = m.vertex(2.0, 0.0, 0.0)   # 5

ref_t0   = m.triangle(r0, r1, r2)  # 0: valid, CCW, normal +Z, area=2.0
ref_degen = m.triangle(d0, d1, d2) # 1: DEGENERATE — collinear on X-axis, area=0

# ---- soup triangles (subject mesh to orient) ----
s0 = m.vertex(0.0, 0.0, 0.0)   # 6
s1 = m.vertex(2.0, 0.0, 0.0)   # 7
s2 = m.vertex(1.0, 2.0, 0.0)   # 8

s3 = m.vertex(0.0, 0.0, 0.0)   # 9
s4 = m.vertex(1.0, 2.0, 0.0)   # 10
s5 = m.vertex(2.0, 0.0, 0.0)   # 11

soup_t0 = m.triangle(s0, s1, s2)   # 2: CCW, normal +Z (correct)
soup_t1 = m.triangle(s3, s4, s5)   # 3: CW, normal -Z  (misoriented — defect)

# ---- assertions ----

# The degenerate reference triangle has zero area (all three vertices collinear
# on the X-axis: d0=(0,0,0), d1=(1,0,0), d2=(2,0,0)).
# is_degenerate_triangle_face returns true → Branch 3 fires (continue/skip).
m.assert_triangle_area_lt(ref_degen, 1e-9)

# The valid reference triangle has positive area (non-degenerate).
# soup_t1 is wound CW — normal -Z, opposite to reference (+Z).
m.assert_triangle_normal_z_negative(soup_t1)

# Degenerate triangle vertices d0, d1, d2 are collinear on X-axis.
# d0 lies exactly on segment d1→d2 (collinearity witness).
m.assert_vertex_on_edge(d1, d0, d2)
