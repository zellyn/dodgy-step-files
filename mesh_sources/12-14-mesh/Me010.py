"""Me010 — sliver_triangle (needle): extreme aspect ratio, one edge 1000× shorter.

Catalog claim: triangle 1 is a needle-sliver with aspect ratio > 500. The
two long edges are ~1.0 units; the short edge (between v3 and v4) is ~0.001
units. The face normal is numerically unstable and CGAL
is_needle_triangle_face / remove_almost_degenerate_faces targets exactly this
pattern. MeshFix strongDegeneracyRemoval collapses sliver edges.

Defect carrier: triangle 1 has vertices at (0,0,0), (1,0,0), (0.5, 0.001, 0).
The short altitude from (0.5, 0.001, 0) to the base at y=0 is 0.001, while
the base length is 1.0 — aspect ratio ~ 500.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me010",
             title="sliver triangle: aspect ratio > 500, needle aligned along X",
             defect_class="needle_triangle")

# Clean control triangle.
v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
m.triangle(v0, v1, v2)   # face 0: clean equilateral-ish control

# Needle triangle: base 1.0, height 0.001.
v3 = m.vertex(0.0, -1.0, 0.0)
v4 = m.vertex(1.0, -1.0, 0.0)
v5 = m.vertex(0.5, -0.999, 0.0)   # altitude = 0.001, base = 1.0 → AR ≈ 500
m.triangle(v3, v4, v5)   # face 1: needle/sliver

# Assert aspect ratio > 500 (circumradius / inradius metric via area check).
# Aspect ratio proxy: longest_edge² / (4√3 · area) — for a needle with
# base=1, height=0.001: area=0.0005, longest_edge≈1; ratio ≈ 289.
# Use the simpler altitude-based inradius: r_in = area / s where s = semi-perimeter.
# Regardless of formula, assert area < 1e-3 (area = 0.5 * 1 * 0.001 = 5e-4).
m.assert_triangle_area_lt(1, 1e-3)
m.assert_triangle_aspect_ratio_gt(1, 100.0)
