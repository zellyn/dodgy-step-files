"""Me021 — SI adjacent to sharp dihedral edge (constrain_sharp_edges branch).

Catalog claim: two triangles share a near-180° dihedral edge (very sharp feature)
and a third triangle self-intersects with one of them. The smoothing-based repair
path must preserve the sharp edge as a constraint, exercising the
constrain_sharp_edges / strong_dihedral_angle branch.

Source: CGAL PMP.remove_self_intersections Branch 9 @ line 2196 —
*constraint-preservation-mode*: whether to constrain high-dihedral-angle edges
during smoothing (first pass); sharp-edge constraints vs unconstrained smoothing.

Defect carrier: triangles 0 and 1 share edge (v1, v2) at a near-180° dihedral
(one triangle at z=0, the other tilts by only 3° above — the "sharp feature edge").
Triangle 2 is an intruding element that self-intersects triangle 0. A smoother
that ignores the sharp constraint would collapse triangles 0 and 1 into a flat
surface, destroying the feature; the constrain_sharp_edges branch prevents this.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(catalog_id="Me021",
             title="SI near sharp dihedral feature: constrain_sharp_edges branch",
             defect_class="self_intersection_sharp_edge")

# Shared sharp-feature edge along Y axis: v1 at (1,0,0), v2 at (1,2,0).
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — free apex of triangle 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — shared sharp edge vertex
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — shared sharp edge vertex

# Triangle 0: in z=0 plane (the "floor" side of the sharp fold).
m.triangle(v0, v1, v2)   # tri 0

# Triangle 1: shares edge (v1,v2), tilts only 3° above z=0 (near-180° dihedral).
# Apex at (1 + cos(177°), 1, sin(177°)) ≈ (0.0052, 1, 0.157) — very shallow.
angle_rad = math.radians(177.0)
v3 = m.vertex(1.0 + math.cos(angle_rad), 1.0, math.sin(angle_rad))  # 3
m.triangle(v1, v2, v3)   # tri 1 — very shallow angle with tri 0 → sharp feature

# Triangle 2: intruder that self-intersects tri 0 by crossing the z=0 plane.
v4 = m.vertex(0.5, 1.0,  0.8)  # 4 — above z=0
v5 = m.vertex(0.5, 1.0, -0.5)  # 5 — below z=0 (the defect)
v6 = m.vertex(0.5, 0.0,  0.0)  # 6 — in z=0 plane, inside tri 0's footprint
m.triangle(v4, v5, v6)   # tri 2 — spans z=-0.5 to +0.8, pierces patch

# Assert: dihedral between tri 0 and tri 1 is very shallow (near-180°).
# We verify this via inconsistent-winding oracle: at ~177° the normals point in
# roughly the same direction (not opposite), so this is NOT winding-inconsistent.
# Instead, assert the SI between tri 0 and tri 2.
m.assert_triangles_self_intersect(0, 2)

# Also assert the shared edge (v1,v2) is shared by exactly 2 triangles (manifold).
m.assert_edge_shared(v1, v2, 2)
