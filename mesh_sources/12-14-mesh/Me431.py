"""Me431 — checkAndRepair::forceNormalConsistence branch 2: ADJACENT_NORMAL_T2_INCONSISTENT.

MeshFix `checkAndRepair::forceNormalConsistence` Branch 2 @ line 945:
  '!t->checkAdjNor(t2)' — triangle t2 (adjacent across edge e2 of triangle t)
  has a flipped normal relative to t; the algorithm inverts t2 and marks the fix.

After checking t1 across e1 (Branch 1), the propagator checks t2 across e2.
When checkAdjNor(t2) returns false, t2 has the wrong winding relative to t.
Branch 2 fires t2->invert().

Input pattern: three triangles where t0 is the reference (+z normal). t1 shares
edge (v0,v1) with t0 in the correct opposite sense (+z consistent). t2 shares
edge (v1,v2) with t0 in the SAME sense (listing v1→v2, not v2→v1), giving t2
a −z normal inconsistent with t0. The inconsistency is on the SECOND edge (e2),
triggering Branch 2.

Geometry:
    v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(1,-1,0), v4=(0.5,2,0)

    t0 = (v0, v1, v2)         edge e1=(v0,v1), e2=(v1,v2), e3=(v2,v0); normal +z
    t1 = (v1, v0, v3)         shares e1 in opposite sense (v1→v0) vs t0 (v0→v1) → consistent +z
    t2 = (v1, v2, v4)         shares e2 in SAME sense (v1→v2) → normal −z: INCONSISTENT

Normal computation for t2=(v1,v2,v4):
    v1=(1,0,0), v2=(0,1,0), v4=(0.5,2,0)
    (v2-v1)=(-1,1,0), (v4-v1)=(-0.5,2,0)
    n = (-1,1,0)×(-0.5,2,0) = (1·0-0·2, 0·(-0.5)-(-1)·0, (-1)·2-1·(-0.5)) = (0,0,-1.5) → −z ✓
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me431",
             title="forceNormalConsistence t2-inconsistent: adjacent triangle flipped across shared edge e2 (Branch 2)",
             defect_class="inconsistent_face_orientation")

v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(0.0, 1.0, 0.0)   # 2
v3 = m.vertex(1.0, -1.0, 0.0)  # 3 — neighbor of t1 (correctly oriented, below x-axis)
v4 = m.vertex(0.5, 2.0, 0.0)   # 4 — neighbor of t2 (flipped orientation)

# t0: CCW in XY → normal (0,0,+1). Reference triangle.
t0 = m.triangle(v0, v1, v2)   # 0

# t1: shares edge (v0,v1) with t0 in OPPOSITE sense (v1→v0 in t1) → consistent +z normal.
# v3=(1,-1,0): normal of (v1,v0,v3) = (0,0,+1). Dot with t0 = +1: consistent.
t1 = m.triangle(v1, v0, v3)   # 1 — consistent +z normal

# t2: shares edge (v1,v2) with t0 in SAME sense (v1→v2 in t2) → normal −z: INCONSISTENT.
t2 = m.triangle(v1, v2, v4)   # 2 — normal -z: ADJACENT_NORMAL_T2_INCONSISTENT

# Shared edge (v0,v1): t0 and t1 — correctly oriented manifold.
m.assert_edge_shared(v0, v1, 2)
# Shared edge (v1,v2): t0 and t2 — inconsistently oriented.
m.assert_edge_shared(v1, v2, 2)

# Key defect: t0 and t2 have antiparallel normals (dot < 0).
m.assert_adjacent_triangles_inconsistent_winding(t0, t2)

# Boundary edges (each incident on exactly 1 triangle).
m.assert_edge_shared(v0, v2, 1)   # t0 outer
m.assert_edge_shared(v0, v3, 1)   # t1 outer: (v0,v3) in t1=(v1,v0,v3)
m.assert_edge_shared(v1, v3, 1)   # t1 outer: (v3,v1) in t1=(v1,v0,v3)
m.assert_edge_shared(v2, v4, 1)   # t2 outer: (v2,v4) in t2=(v1,v2,v4)
m.assert_edge_shared(v1, v4, 1)   # t2 outer: (v4,v1) → canonical (v1,v4)
