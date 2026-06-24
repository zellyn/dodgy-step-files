"""Me1123 — SI near near-orthogonal crease edge (constraint-preservation-mode branch).

CGAL PMP.remove_self_intersections Branch 9 @ line 2196 — *constraint-preservation-mode*:
  'if (constrain_sharp_edges) { smooth(..., strong_dihedral_angle); }'
  — during the smoothing repair phase, if constrain_sharp_edges=true the smoother locks
  edges whose dihedral angle exceeds strong_dihedral_angle (default ≈150°). This prevents
  smoothing from relaxing across feature creases. The branch fires when the SI repair
  region includes at least one such high-dihedral edge.

Defect pattern: triangles 0 and 1 share edge (v1,v2) at a near-90° dihedral — a strong
  crease feature (the two triangles meet at a right angle, like a corner of a box). Their
  shared edge has dihedral angle ≈90°, well above the strong_dihedral_angle threshold.
  Triangle 2 is an intruder that self-intersects tri 0 by piercing the z=0 face.
  The constrain_sharp_edges branch must keep (v1,v2) fixed during smoothing so the
  90° corner geometry is preserved while resolving the SI.

  Tri 0: in the XY plane (z=0) — the "floor" face.
  Tri 1: in the YZ plane (x=1) — the "wall" face. Shares edge (v1,v2) with tri 0.
  Dihedral angle at shared edge ≈ 90° (strong crease).
  Tri 2: intruder with apex at z=-0.4 crossing the floor face.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me1123",
             title="SI adjacent to 90-degree crease edge: constrain_sharp_edges preserves right-angle feature",
             defect_class="self_intersection_sharp_crease")

# Shared crease edge: v1=(1,0,0) to v2=(1,1,0).
# Tri 0 (floor): lies in z=0 plane.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — free apex of floor triangle
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — crease edge start
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — crease edge end

# Tri 0: floor (z=0 plane).
m.triangle(v0, v1, v2)   # tri 0

# Tri 1: wall (x=1 plane, perpendicular to z=0).
# Apex at (1, 0.5, 1.0) — directly above the crease midpoint.
v3 = m.vertex(1.0, 0.5, 1.0)   # 3 — wall apex (above z=0)
m.triangle(v1, v2, v3)   # tri 1 — shares (v1,v2) with tri 0 at 90°

# Tri 2: intruder that self-intersects the floor (tri 0) by crossing z=0.
# v4 is below z=0 (the defect), v5 and v6 are above z=0.
v4 = m.vertex(0.4, 0.4, -0.4)  # 4 — below floor (defect)
v5 = m.vertex(0.2, 0.1,  0.5)  # 5 — above floor
v6 = m.vertex(0.6, 0.1,  0.5)  # 6 — above floor
m.triangle(v4, v5, v6)   # tri 2 — intruder, crosses tri 0

# Assert: intruder self-intersects the floor face.
m.assert_triangles_self_intersect(0, 2)

# Assert: crease edge (v1,v2) is shared by exactly 2 triangles (manifold).
m.assert_edge_shared(v1, v2, 2)

# Assert: outer edges of floor and wall are boundary (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)
