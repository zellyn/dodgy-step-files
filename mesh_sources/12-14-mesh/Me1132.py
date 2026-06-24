"""Me1132 — SI in non-axis-aligned mesh: oriented-bounding-box (OBB) transform branch.

Catalog claim: the self-intersecting mesh is rotated 45 degrees about the Z axis
so its principal axes are not aligned with X/Y/Z. An axis-aligned bounding box
would be significantly larger than the tight OBB. When CGAL_PMP_REPAIR_SI_USE_OBB
is enabled, remove_self_intersections computes an oriented_bounding_box and the
corresponding Aff_transformation to align the mesh with its principal axes before
compactifying the SI region. This exercises Branch 13: the OBB path vs the
axis-aligned fallback.

Source: CGAL PMP.remove_self_intersections Branch 13 @ line 2069 —
*bounding-box-obb-transform-applicability*: whether oriented-bounding-box
compactification is enabled (CGAL_PMP_REPAIR_SI_USE_OBB); use OBB-based
selection vs axis-aligned-box selection.

Defect carrier: a diamond-shaped mesh (square rotated 45 degrees) consisting of
4 triangles lying roughly in the Z=0 plane, plus an intruder triangle that
crosses the diamond. The diamond is oriented at 45 degrees (vertices at the
cardinal diagonal points), making the axis-aligned bounding box suboptimal
relative to the OBB. The intruder pierces tri 0, triggering SI detection.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(catalog_id="Me1132",
             title="SI in 45-degree-rotated diamond mesh: OBB Aff_transformation branch",
             defect_class="self_intersection_obb_transform")

# Diamond mesh: center + 4 cardinal diagonal vertices.
# This is a square rotated 45 degrees — not axis-aligned.
s = math.sqrt(2.0)
v0 = m.vertex( 0.0,  0.0, 0.0)   # 0 — center
v1 = m.vertex( s,    0.0, 0.0)   # 1 — east (45-deg rotated x+)
v2 = m.vertex( 0.0,  s,   0.0)   # 2 — north
v3 = m.vertex(-s,    0.0, 0.0)   # 3 — west
v4 = m.vertex( 0.0, -s,   0.0)   # 4 — south

# 4 triangles forming the diamond (all sharing center v0).
t0 = m.triangle(v0, v1, v2)   # tri 0 — NE quadrant
t1 = m.triangle(v0, v2, v3)   # tri 1 — NW quadrant
t2 = m.triangle(v0, v3, v4)   # tri 2 — SW quadrant
t3 = m.triangle(v0, v4, v1)   # tri 3 — SE quadrant

# Intruder: a triangle that pierces tri 0 (NE quadrant).
# Tri 0 vertices: (0,0,0), (sqrt2, 0, 0), (0, sqrt2, 0)
# Centroid ≈ (0.471, 0.471, 0)
cx = (0.0 + s + 0.0) / 3
cy = (0.0 + 0.0 + s) / 3
v5 = m.vertex(cx, cy,  1.0)   # 5 — above NE centroid
v6 = m.vertex(cx, cy, -1.0)   # 6 — below NE centroid
v7 = m.vertex(cx + 1.0, cy, 0.0)  # 7 — in z=0 plane, outside diamond

# Intruder triangle passes through centroid of tri 0.
m.triangle(v5, v6, v7)   # tri 4 — intruder pierces diamond at tri 0

# Assert: intruder (tri 4) self-intersects tri 0.
m.assert_triangles_self_intersect(0, 4)

# Assert: interior edge between NE and NW quadrant shared by exactly 2 triangles.
m.assert_edge_shared(v0, v2, 2)
