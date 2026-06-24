"""Me414 — refineSelectedHolePatches_vertex_split_density_check: sparse triangle triggers centroid vertex insertion.

MeshFix `holeFilling::refineSelectedHolePatches` Branch 5 (*VERTEX_SPLIT_DENSITY_CHECK*) @ line 654:
  'if (dv1>sigma && dv1>sv1 && dv2>sigma && dv2>sv2 && dv3>sigma && dv3>sv3)
   { splitTriangle(t, centroid); nnt++; }'
  For each triangle in the region, the algorithm computes the distance from each
  vertex to the triangle's centroid (dv1, dv2, dv3) and compares against sigma
  (average boundary-edge length) and against each vertex's own average local edge
  length (sv1, sv2, sv3). When ALL three distances exceed both thresholds, a new
  vertex is inserted at the centroid to split the triangle — Branch 5 fires.

Defect pattern: a single large equilateral-ish triangle with vertices far apart.
  The centroid is significantly more distant from each vertex than any plausible
  sigma (average boundary-edge length of ~1.0). This models a hole-fill patch
  triangle that is too coarse and requires centroid subdivision.

  With v0=(0,0,0), v1=(6,0,0), v2=(3,5,0):
    centroid = (3, 5/3, 0) ≈ (3, 1.667, 0)
    dv1 = |(0,0)-(3,1.667)| = sqrt(9 + 2.778) ≈ 3.43
    dv2 = |(6,0)-(3,1.667)| = sqrt(9 + 2.778) ≈ 3.43
    dv3 = |(3,5)-(3,1.667)| = 3.333

  All dv > 3.3 >> sigma ≈ 1.0 → Branch 5 fires.
  The high aspect ratio confirms the triangle is "too large" relative to the
  local mesh density (sigma), satisfying the density check.

  The fixture models the pre-split state; after Branch 5 a centroid vertex is
  inserted and nnt is incremented.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me414",
             title="refineSelectedHolePatches_vertex_split_density_check: large sparse triangle triggers centroid insertion (Branch 5)",
             defect_class="hole_in_hull")

# Large hole-fill triangle — all vertices far from centroid (>> sigma).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — bottom-left
v1 = m.vertex(6.0, 0.0, 0.0)   # 1 — bottom-right (edge length 6.0)
v2 = m.vertex(3.0, 5.0, 0.0)   # 2 — apex

# The single large triangle t0 is the density-check candidate.
# centroid = (3, 5/3, 0); dv0≈3.43, dv1≈3.43, dv2≈3.33 >> sigma
t0 = m.triangle(v0, v1, v2)   # 0 — large; all dv >> sigma → Branch 5 fires

# All three edges are boundary (no sharing — single-triangle fixture).
m.assert_edge_shared(v0, v1, 1)   # bottom edge, length 6.0
m.assert_edge_shared(v1, v2, 1)   # right edge, length ≈ 5.83
m.assert_edge_shared(v0, v2, 1)   # left edge, length ≈ 5.83

# High aspect ratio confirms the triangle is too sparse relative to sigma=1.0.
# aspect_ratio = longest * perimeter / (4 * area)
# longest=6, perimeter≈17.66, area=0.5*base*height=0.5*6*5=15
# ratio = 6 * 17.66 / (4 * 15) ≈ 106 / 60 ≈ 1.77 > 1.5
m.assert_triangle_aspect_ratio_gt(t0, 1.5)

# Euler: V=3, E=3, F=1, chi=1 (single triangle, open disk with one face).
m.assert_euler_characteristic(3, 3, 1, 1)
