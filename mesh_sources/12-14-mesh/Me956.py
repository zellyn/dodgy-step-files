"""Me956 — Basic_TMesh.checkGeometry dihedral_angle_180: adjacent coplanar triangles with 180° dihedral (Branch 7).

MeshFix `Basic_TMesh.checkGeometry` Branch 7 (*dihedral_angle_180*) @ line 247:
  'getDAngle(e->t2) == M_PI' — for each interior edge, the dihedral angle between
  the two adjacent triangles is computed. If it equals exactly π (180°), the two
  triangles are coplanar AND face the same direction (normals parallel). This means
  they overlap when projected orthogonally. checkGeometry returns edge->v1 as the
  defective vertex immediately.

Defect pattern: two triangles sharing an interior edge where both triangles lie in
the same plane and their normals point in the same direction. The dihedral angle
(measured by getDAngle) is π — this is distinct from anti-parallel normals
(dihedral = 0°, inverted triangle) or a proper fold (dihedral ∈ (0°, π)).

Geometry: four vertices forming a planar quad in the XY plane.
  t0=(v0,v1,v2): counter-clockwise, normal = +Z.
  t1=(v2,v1,v3): counter-clockwise, normal = +Z (same as t0).
  Shared interior edge: (v1,v2). Dihedral angle = π because both normals are +Z.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me956",
    title="Basic_TMesh.checkGeometry dihedral_angle_180: adjacent coplanar triangles sharing edge (v1,v2), dihedral = PI (Branch 7)",
    defect_class="overlapping_triangles",
)

# Four vertices of a planar quad in z=0.
v0 = m.vertex(0.0, 0.0, 0.0)    # 0
v1 = m.vertex(1.0, 0.0, 0.0)    # 1
v2 = m.vertex(0.0, 1.0, 0.0)    # 2
v3 = m.vertex(1.0, 1.0, 0.0)    # 3

# Triangle 0: (v0,v1,v2) — counter-clockwise in XY plane, normal = +Z.
t0 = m.triangle(v0, v1, v2)     # 0

# Triangle 1: (v2,v1,v3) — counter-clockwise in XY plane, normal = +Z.
# Shared edge (v1,v2) is interior. Dihedral angle between t0 and t1 = π
# because both lie in z=0 and normals are parallel (+Z, same direction).
t1 = m.triangle(v2, v1, v3)     # 1

# Assert: the shared edge (v1,v2) is shared by exactly 2 triangles (manifold edge).
m.assert_edge_shared(v1, v2, 2)

# Assert: the two adjacent triangles have nearly parallel normals (dot ≈ +1.0).
# This confirms the 180° dihedral / coplanar-same-direction condition.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, threshold=0.99)
