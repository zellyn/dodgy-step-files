"""Me432 — checkAndRepair::forceNormalConsistence branch 3: ADJACENT_NORMAL_T3_INCONSISTENT.

MeshFix `checkAndRepair::forceNormalConsistence` Branch 3 @ line 946:
  '!t->checkAdjNor(t3)' — triangle t3 (adjacent across edge e3 of triangle t)
  has a flipped normal relative to t; the algorithm inverts t3.

The propagator checks t1 (e1), t2 (e2), then t3 (e3) in sequence. Branch 3
fires when the THIRD neighbour (t3 across e3) has antiparallel normal to t.

Input pattern: four triangles. t0 is the reference (+z normal). t1 and t2 share
edges e1 and e2 of t0 in the correct opposite sense (consistent +z normals).
t3 shares edge e3 of t0 in the SAME sense (listing e3 in the same direction),
giving t3 a −z normal — the ADJACENT_NORMAL_T3_INCONSISTENT case (Branch 3).

Geometry:
    v0=(0,0,0), v1=(2,0,0), v2=(1,2,0) — t0 reference
    t0 = (v0,v1,v2): edges e1=(v0,v1), e2=(v1,v2), e3=(v2,v0). Normal +z.

    v3=(3,-1,0): t1=(v1,v0,v3) — shares (v0,v1) opposite → normal +z (consistent).
    v4=(2,3,0):  t2=(v2,v1,v4) — shares (v1,v2) opposite → normal +z (consistent).
    v5=(-1,1,0): t3=(v2,v0,v5) — shares (v2,v0) in SAME sense → normal −z (INCONSISTENT).

Normal verification:
    t3=(v2,v0,v5): v2=(1,2,0), v0=(0,0,0), v5=(-1,1,0).
    (v0-v2)=(-1,-2,0), (v5-v2)=(-2,-1,0).
    n = (-1,-2,0)×(-2,-1,0) = ((-2)·0-0·(-1), 0·(-2)-(-1)·0, (-1)·(-1)-(-2)·(-2)) = (0,0,1-4)=(0,0,-3) → −z ✓

    t0 e3=(v2,v0): t0 lists (v2→v0) as the third edge.
    t3=(v2,v0,v5) lists the edge also as (v2→v0) — SAME direction → inconsistent.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me432",
             title="forceNormalConsistence t3-inconsistent: adjacent triangle flipped across shared edge e3 (Branch 3)",
             defect_class="inconsistent_face_orientation")

v0 = m.vertex( 0.0, 0.0, 0.0)   # 0
v1 = m.vertex( 2.0, 0.0, 0.0)   # 1
v2 = m.vertex( 1.0, 2.0, 0.0)   # 2
v3 = m.vertex( 3.0, -1.0, 0.0)  # 3 — t1 outer vertex
v4 = m.vertex( 2.0, 3.0, 0.0)   # 4 — t2 outer vertex
v5 = m.vertex(-1.0, 1.0, 0.0)   # 5 — t3 outer vertex (flipped triangle)

# t0: CCW → normal +z. Edges: e1=(v0,v1), e2=(v1,v2), e3=(v2,v0).
t0 = m.triangle(v0, v1, v2)   # 0 — reference; normal +z

# t1: shares e1=(v0,v1) in opposite sense (v1→v0); normal +z (consistent).
t1 = m.triangle(v1, v0, v3)   # 1 — consistent

# t2: shares e2=(v1,v2) in opposite sense (v2→v1); normal +z (consistent).
t2 = m.triangle(v2, v1, v4)   # 2 — consistent

# t3: shares e3=(v2,v0) in SAME sense (v2→v0 appears in t0 AND t3) → normal -z.
# t0 lists e3 as v2→v0 (its third edge). t3=(v2,v0,v5) lists it the same way.
t3 = m.triangle(v2, v0, v5)   # 3 — ADJACENT_NORMAL_T3_INCONSISTENT: normal -z

# Shared interior edges (each on exactly 2 triangles).
m.assert_edge_shared(v0, v1, 2)   # t0 ↔ t1
m.assert_edge_shared(v1, v2, 2)   # t0 ↔ t2
m.assert_edge_shared(v0, v2, 2)   # t0 ↔ t3 (canonical of v2,v0)

# Key defect: t0 and t3 have antiparallel normals.
m.assert_adjacent_triangles_inconsistent_winding(t0, t3)

# Boundary edges (each on exactly 1 triangle).
m.assert_edge_shared(v0, v3, 1)   # t1 outer
m.assert_edge_shared(v1, v3, 1)   # t1 outer
m.assert_edge_shared(v1, v4, 1)   # t2 outer
m.assert_edge_shared(v2, v4, 1)   # t2 outer
m.assert_edge_shared(v0, v5, 1)   # t3 outer
m.assert_edge_shared(v2, v5, 1)   # t3 outer
