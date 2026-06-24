"""Me543 — checkAndRepair::removeDegenerateTriangles branch 4: CAP_VERTEX_ORDER_DISTANCE

MeshFix `checkAndRepair::removeDegenerateTriangles` Branch 4 (*CAP_VERTEX_ORDER_DISTANCE*) @ line 484:
  'if (squaredDistance(splitvs[0], e->v1) > squaredDistance(splitvs[1], e->v1)) swap(splitvs);'
  When nov==2 (two cap vertices found), MeshFix orders them by their squared distance
  to the first edge endpoint e->v1.  If ov1 is farther from v1 than ov2, the cap
  vertices are swapped so the nearer one is processed first.

Geometric signature: a degenerate (zero-area) triangle has two adjacent cap triangles.
  Cap vertex ov1 is farther from e->v1 (= v0 here) than ov2, so the swap fires.

Geometry (z = 0):
  v0=(0,0,0)  — degenerate triangle anchor / e->v1 reference vertex
  v1=(6,0,0)  — degenerate triangle anchor opposite
  v2=(3,0,0)  — degenerate triangle midpoint on v0-v1 (area=0)
  v3=(5,2,0)  — ov1 (far cap vertex): dist²(v3, v0) = 25+4 = 29  [farther from v0]
  v4=(1,2,0)  — ov2 (near cap vertex): dist²(v4, v0) = 1+4  =  5  [nearer to v0]

  e->v1 = v0 = (0,0,0).  dist²(ov1=v3, v0) = 29 > dist²(ov2=v4, v0) = 5 → swap.

  t0 = (v0, v1, v2) — degenerate (area=0; collinear)
  t1 = (v0, v2, v3) — cap 1: opposite vertex v3 (far from v0)
  t2 = (v2, v1, v4) — cap 2: opposite vertex v4 (near to v0)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me543",
    title="checkAndRepair::removeDegenerateTriangles CAP_VERTEX_ORDER_DISTANCE: two caps; ov1 farther from e->v1 than ov2 causing swap of splitvs order",
    defect_class="degenerate_triangle_cap_vertex_order_distance",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — e->v1 reference vertex (anchor)
v1 = m.vertex(6.0, 0.0, 0.0)   # 1 — far anchor
v2 = m.vertex(3.0, 0.0, 0.0)   # 2 — midpoint on v0-v1; makes t0 degenerate
v3 = m.vertex(5.0, 2.0, 0.0)   # 3 — ov1: far cap vertex; dist²(v3,v0)=29
v4 = m.vertex(1.0, 2.0, 0.0)   # 4 — ov2: near cap vertex; dist²(v4,v0)=5

# t0: degenerate triangle (collinear, area=0).
t0 = m.triangle(v0, v1, v2)    # 0 — degenerate: v2 on v0-v1
# t1: first cap triangle; opposite vertex v3 is FAR from v0.
t1 = m.triangle(v0, v2, v3)    # 1 — cap 1 (far ov1=v3)
# t2: second cap triangle; opposite vertex v4 is NEAR v0.
t2 = m.triangle(v2, v1, v4)    # 2 — cap 2 (near ov2=v4)

# t0 is exactly degenerate.
m.assert_triangle_area_lt(0, 1e-9)

# v2 lies on segment v0-v1 (the degenerate edge).
m.assert_vertex_on_edge(v2, v0, v1)

# Distance ordering: v3 farther from v0=(0,0,0) than v4.
# dist²(v3, v0) = 5²+2² = 29; dist²(v4, v0) = 1²+2² = 5; 29 > 5 → swap fires.
# We verify via vertex_pair_distance_lt comparisons:
# |v3 - v0| = sqrt(29) ≈ 5.385; |v4 - v0| = sqrt(5) ≈ 2.236.
m.assert_vertex_pair_distance_lt(v0, v4, 3.0)   # v4 close to v0 (sqrt(5)≈2.24 < 3)
# v3 is NOT close to v0 at threshold 3: sqrt(29)≈5.39; so no assert needed.

# Cap edge (v0, v2) shared by t0 and t1.
m.assert_edge_shared(v0, v2, 2)
# Cap edge (v2, v1) shared by t0 and t2.
m.assert_edge_shared(v1, v2, 2)

# Healthy cap areas.
m.assert_triangle_area_lt(1, 7.0)   # t1: area=|(v2-v0)×(v3-v0)|/2 = |(3,0)×(5,2)|/2 = 3
m.assert_triangle_area_lt(2, 7.0)   # t2: area=|(v1-v2)×(v4-v2)|/2 = |(3,0)×(-2,2)|/2 = 3
