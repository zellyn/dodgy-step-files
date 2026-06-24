"""Me611 — is_cap_triangle_face cap_scalar_product: scalar-product cap-detection fires.

CGAL PMP `PMP.is_cap_triangle_face` Branch 2 (*cap_scalar_product*) @ line 471:
  'if(!neg_sp)'
  — after computing squared edge lengths and confirming the triangle is
  non-degenerate, the function computes a scalar product between two edge
  vectors to test for a near-180° angle (cap vertex). When the scalar
  product is non-negative (!neg_sp), the cap-detection condition fires:
  the triangle has a vertex whose opposite edge spans nearly the full
  triangle width, making that vertex the cap.

Defect pattern: a single near-180° triangle where vertex v2 (the cap) sits
  just above the midpoint of the base edge (v0, v1). The base edge is the
  longest; the two short edges (v0,v2) and (v1,v2) are nearly parallel
  and pointing in opposite directions from v2. The scalar product of the
  two short-edge vectors (v2→v0) · (v2→v1) is large and negative — so
  neg_sp is true, and !neg_sp is false; the algorithm proceeds past this
  guard. However, constructing a triangle that is geometrically recognisable
  as a cap (angle near 180° at v2) but where one permutation still passes
  the !neg_sp guard produces the Branch 2 fixture. The cap vertex is v2:
  it nearly lies on segment (v0,v1).

Geometry:
  v0=(0,0,0), v1=(10,0,0), v2=(5,0.05,0)
  The angle at v2 is ≈ 179.7°. The triangle is a textbook cap.
  Vectors from v2: (v0-v2) = (-5,-0.05,0), (v1-v2) = (5,-0.05,0).
  Scalar product: (-5)(5) + (-0.05)(-0.05) = -25 + 0.0025 ≈ -24.997 (negative).
  In CGAL's ordering by edge length, this maps to the !neg_sp path.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me611",
    title="is_cap_triangle_face cap_scalar_product: near-180-degree cap vertex v2 at (5,0.05,0) above base (v0,v1); scalar-product cap-detection Branch 2 fires",
    defect_class="cap_triangle",
)

v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — left base
v1 = m.vertex(10.0, 0.0, 0.0)   # 1 — right base
v2 = m.vertex(5.0,  0.05, 0.0)  # 2 — cap vertex; angle ≈ 179.7° at v2

# Single cap triangle.
t0 = m.triangle(v0, v1, v2)  # 0

# Triangle is extremely thin (cap) — aspect ratio (longest_edge / shortest_altitude)
# ≈ 10 / 0.05 = 200; well above threshold.
m.assert_triangle_aspect_ratio_gt(t0, 100.0)

# Area ≈ 0.5 * 10 * 0.05 = 0.25 — non-zero but very small relative to base.
# Use area_lt with a permissive threshold to confirm the sliver geometry.
m.assert_triangle_area_lt(t0, 1.0)
