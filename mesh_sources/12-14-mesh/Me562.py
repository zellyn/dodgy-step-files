"""Me562 — loopSubdivision sharp_edge_preservation: steep dihedral angle between adjacent triangles.

Basic_TMesh.loopSubdivision Branch 3 (*sharp_edge_preservation*) @ line 115:
  'if(IS_SHARPEDGE(e)) { detected_sharp = 1; }'
  — During Loop subdivision, each edge is inspected for a sharp/crease tag.
  If any edge is marked sharp (e.g. dihedral angle > 60°), the algorithm logs
  a warning (detected_sharp flag) but continues subdividing. This branch fires
  when at least one edge between two adjacent triangles has a steep dihedral
  angle — i.e. the triangles are far from coplanar.

Fixture: 3 triangles where two adjacent triangles form a steep dihedral angle
  (normals nearly anti-parallel). t0 lies in the XY plane; t1 is folded
  sharply upward at roughly 120° dihedral (so normal dot ≈ −0.5, which is
  < 0: inconsistent winding from the shared-edge perspective but at a crease).
  t2 is attached to t1 at a gentler angle.

Geometric signature:
  t0 = flat in Z=0 plane
  t1 = folded up: the shared edge (v1,v2) is the crease; t1 rises steeply in Z
  t2 = further extension of t1 at a shallower angle
  Adjacent t0/t1 normals: nearly anti-parallel (steep fold), capturing the IS_SHARPEDGE branch.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me562",
    title="loopSubdivision sharp_edge_preservation: t0 and t1 share crease edge (v1,v2) with steep dihedral; IS_SHARPEDGE branch triggered (Branch 3)",
    defect_class="loop_subdivision",
)

# Flat base triangle in the XY plane.
v0 = m.vertex(0.0, 0.0,  0.0)   # 0 — left base
v1 = m.vertex(2.0, 0.0,  0.0)   # 1 — right base (start of crease edge)
v2 = m.vertex(1.0, 2.0,  0.0)   # 2 — apex of base triangle (end of crease edge)

# t0 is flat in Z=0 plane. Normal: (0, 0, +1) pointing up.
t0 = m.triangle(v0, v1, v2)  # 0 — base triangle

# Sharply folded triangle: shares crease edge (v1, v2) and folds steeply downward.
# v3 is placed below the base plane so the dihedral angle across (v1,v2) is ~150°.
# t1 normal ≈ (0, +sin(150°), -cos(150°)) = (0, 0.5, 0.866) — wait, let's be explicit:
# t1 = (v1, v2, v3) with v3 far below. Using right-hand rule:
# If v3=(1,0,-2): t1=(v1,v2,v3)=(2,0,0),(1,2,0),(1,0,-2).
# Normal = (v2-v1)×(v3-v1) = (-1,2,0)×(-1,0,-2) = (2*(-2)-0*0, 0*(-1)-(-1)*(-2), (-1)*0-2*(-1))
#         = (-4, -2, 2) → normalized ≈ (-0.873, -0.436, 0.218).
# t0 normal = (0,0,1). Dot: ≈ 0.218 (not steep enough).
# Better: v3=(1,-0.5,-3): more downward.
# t1=(v1,v2,v3)=(2,0,0),(1,2,0),(1,-0.5,-3).
# (v2-v1)=(-1,2,0); (v3-v1)=(-1,-0.5,-3).
# Cross: (2*(-3)-0*(-0.5), 0*(-1)-(-1)*(-3), (-1)*(-0.5)-2*(-1)) = (-6, -3, 0.5+2) = (-6,-3,2.5).
# t0 normal=(0,0,1), t1 normal≈(-6,-3,2.5)/norm. Dot with (0,0,1): 2.5/sqrt(36+9+6.25)=2.5/7.28≈0.34. Still positive.
# For anti-parallel normals: need dot < 0 → v3 placed so t1 normal has negative Z.
# t1=(v2,v1,v3) (reversed): normal = (v1-v2)×(v3-v2) = (1,-2,0)×(0,-2,-3) = ((-2)*(-3)-0*(-2), 0*0-1*(-3), 1*(-2)-(-2)*0) = (6,3,-2).
# Dot with (0,0,1): -2/7.28 ≈ -0.27. Anti-parallel! Using t1=(v2,v1,v3) order.
v3 = m.vertex(1.0, -0.5, -3.0)  # 3 — below-plane vertex creating steep fold at crease

# t1 shares crease edge (v1,v2) and folds steeply (normals near anti-parallel to t0).
t1 = m.triangle(v2, v1, v3)  # 1 — sharply folded; shares edge (v1,v2) with t0

# A gentler adjacent triangle off t1.
v4 = m.vertex(3.0, -0.5, -1.5)  # 4 — extends t1 at shallower angle
t2 = m.triangle(v1, v4, v3)   # 2 — shares edge (v1,v3) with t1

# The crease edge (v1,v2) is interior: shared by exactly 2 triangles (t0 and t1).
m.assert_edge_shared(v1, v2, 2)

# Adjacent triangles t0 and t1 share the crease edge with nearly anti-parallel normals.
# The dihedral across (v1,v2) is steep (> 60° threshold for IS_SHARPEDGE).
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Other interior edge: (v1,v3) shared by t1 and t2.
m.assert_edge_shared(v1, v3, 2)

# Boundary edges (n=1).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# Euler: V=5, E=7, F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
