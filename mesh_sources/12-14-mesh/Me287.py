"""Me287 — checkGeometry_overlapping_triangles_dihedral: adjacent coplanar triangles with 180° dihedral (Branch 8).

MeshFix `checkAndRepair::checkGeometry` Branch 8 (*OVERLAPPING_TRIANGLES_DIHEDRAL*) @ line 247:
  `getDAngle(e->t2) == M_PI` — two triangles sharing an edge have a dihedral angle of
  exactly π (180°). This means both triangles lie in the same plane and fold flat in
  the SAME direction (normals parallel, not anti-parallel). The triangles overlap when
  projected orthogonally. checkGeometry returns the edge's v1 vertex as defective.

Geometry: four vertices forming a planar quad in the XY plane. Two triangles share
the diagonal edge (v1,v2). Both triangles have the same outward normal (+Z direction),
forming a flat fold: dihedral angle = 180°. This is distinct from inverted normals
(dihedral = 0°) or a proper convex fold (dihedral ∈ (0°, 180°)).

Triangle t0 (index 0): v0=(0,0,0), v1=(1,0,0), v2=(0,1,0) — normal = +Z.
Triangle t1 (index 1): v2=(0,1,0), v1=(1,0,0), v3=(1,1,0) — normal = +Z (same).
Shared edge: (v1, v2). Both in z=0 plane → dihedral = 180°.

Sources: MeshFix `checkAndRepair::checkGeometry` lines 244–252; MESH_HEAL_COVERAGE.md.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me287",
    title="checkGeometry_overlapping_triangles_dihedral: adjacent coplanar triangles, dihedral = 180° (Branch 8)",
    defect_class="overlapping_triangles",
)

# Four vertices of a planar quad in z=0.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(1.0, 1.0, 0.0)   # 3

# Triangle 0: (v0, v1, v2) — counter-clockwise in XY plane, normal = +Z.
t0 = m.triangle(v0, v1, v2)    # 0

# Triangle 1: (v2, v1, v3) — also counter-clockwise in XY plane, normal = +Z.
# Shared edge (v1, v2) is interior. Dihedral angle between t0 and t1 = 180°
# because both lie in z=0 and normals are parallel (+Z, same direction).
t1 = m.triangle(v2, v1, v3)    # 1

# Assert: the shared edge (v1,v2) is shared by exactly 2 triangles (manifold edge).
m.assert_edge_shared(v1, v2, 2)

# Assert: the two adjacent triangles have nearly parallel normals (dot ≈ +1.0).
# This confirms the 180° dihedral / coplanar-same-direction condition.
m.assert_adjacent_triangles_normal_dot_gt(t0, t1, threshold=0.99)
