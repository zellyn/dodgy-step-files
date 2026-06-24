"""Me430 — checkAndRepair::forceNormalConsistence branch 1: ADJACENT_NORMAL_T1_INCONSISTENT.

MeshFix `checkAndRepair::forceNormalConsistence` Branch 1 @ line 944:
  '!t->checkAdjNor(t1)' — triangle t1 (adjacent across edge e1 of triangle t)
  has a flipped normal relative to t; the algorithm inverts t1 and sets r=1.

The orientation propagator walks every triangle t and checks each of its three
neighbour triangles (t1, t2, t3 across edges e1, e2, e3). When checkAdjNor(t1)
returns false, t1's winding is inconsistent with t; Branch 1 fires t1->invert().

Input pattern: two triangles sharing edge (v0, v1) where BOTH triangles list the
shared edge in the SAME direction (both ascending, e.g. v0→v1 in both), rather
than the correct pattern where one says v0→v1 and the other says v1→v0. This
gives antiparallel normals; the dot product of their normals is < 0.

Geometry: three-triangle strip. t0 is the reference orientation triangle (z+
normal). t1 shares edge (v0,v1) with t0 but has the same-sense vertex order,
meaning its normal points in the −z direction (inconsistent with t0). t2 is a
second correctly-oriented neighbor for breadth: it shares edge (v1,v2) with t0
in the correct (opposite) direction, so its normal is +z.

    v0=(0,0,0), v1=(1,0,0), v2=(0.5,1,0), v3=(0.5,-1,0)
    t0 = (v0, v1, v2)   normal +z  [reference]
    t1 = (v0, v1, v3)   normal -z  [shares (v0,v1) in same sense → INCONSISTENT]
    t2 = (v1, v0, v3)   would be consistent across (v0,v1) but below plane
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me430",
             title="forceNormalConsistence t1-inconsistent: adjacent triangle flipped across shared edge e1 (Branch 1)",
             defect_class="inconsistent_face_orientation")

# Reference triangle t0 — counter-clockwise in xy-plane → normal +z.
v0 = m.vertex(0.0,  0.0, 0.0)   # 0
v1 = m.vertex(1.0,  0.0, 0.0)   # 1
v2 = m.vertex(0.5,  1.0, 0.0)   # 2 — above edge (v0,v1)

# Flipped neighbor — listed with the same (v0→v1) sense, so normal is −z.
v3 = m.vertex(0.5, -1.0, 0.0)   # 3 — below edge (v0,v1)

# t0: CCW in XY → normal (0,0,+1)
t0 = m.triangle(v0, v1, v2)   # 0 — reference

# t1: lists (v0, v1) in the same direction (not reversed). CCW would require
# (v1, v0, v3) across this shared edge. Instead (v0, v1, v3) gives CW from
# the +z viewpoint → normal (0,0,−1). This is the ADJACENT_NORMAL_T1_INCONSISTENT case.
t1 = m.triangle(v0, v1, v3)   # 1 — same-direction shared edge → antiparallel normal

# Shared edge (v0,v1): both t0 and t1 list it in the same sense.
# Edge is shared by 2 triangles (manifold), but orientation is inconsistent.
m.assert_edge_shared(v0, v1, 2)

# The key defect: normals of t0 and t1 are antiparallel (dot < 0).
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)

# Boundary edges (each on exactly 1 triangle).
m.assert_edge_shared(v1, v2, 1)   # t0 outer
m.assert_edge_shared(v0, v2, 1)   # t0 outer
m.assert_edge_shared(v1, v3, 1)   # t1 outer
m.assert_edge_shared(v0, v3, 1)   # t1 outer
