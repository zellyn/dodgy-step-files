"""Me723 — Basic_TMesh.safeCoordBackApproximation branch 4: Convergence check.

Basic_TMesh.safeCoordBackApproximation Branch 4 (*convergence check*) @ line 295:
  'pnos = nos; nos = 0; ... if(nos >= pnos) break;'
  — after each repair iteration the new overlap count `nos` is compared to the previous
  count `pnos`. If `nos < pnos` the algorithm continues (progress was made); otherwise it
  breaks. The fixture demonstrates a multi-iteration repair scenario with two independent
  overlapping pairs — pair A and pair B — so that one pair can be resolved per iteration,
  demonstrating monotone decrease: iteration 1: nos=2; after repair iteration: nos=1; nos<pnos.

Defect pattern: four triangles in the XY plane forming two independent overlapping pairs:
  - Pair A: large t0 and small t1 share edge (v0,v1); t1 overlaps t0.
  - Pair B: large t2 and small t3 share edge (v4,v5); t3 overlaps t2.
  These two pairs are spatially separated so they do not interact. Pair A resolves in the
  first jitter step; pair B may still overlap → `nos` decreases from 2 to 1 → `nos < pnos`
  → Branch 4 fires and the algorithm continues.

Geometry:
  Pair A: v0=(0,0,0), v1=(4,0,0), v2=(2,4,0), v3=(2,1,0); t0 large (area=8), t1 small (area=2)
  Pair B: v4=(10,0,0), v5=(14,0,0), v6=(12,4,0), v7=(12,1,0); t2 large (area=8), t3 small (area=2)
  The two pairs are offset by 10 units in X to keep them spatially independent.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me723",
    title="safeCoordBackApproximation convergence check: two independent overlapping pairs; nos decreases across iterations confirming nos<pnos progress (Branch 4)",
    defect_class="self_intersection_coplanar_overlap",
)

# Pair A: offset at x=0
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(4.0, 0.0, 0.0)   # 1 — shared edge A
v2 = m.vertex(2.0, 4.0, 0.0)   # 2 — apex of large t0 (area=8)
v3 = m.vertex(2.0, 1.0, 0.0)   # 3 — apex of small t1 (area=2); inside t0

# Pair B: offset at x=10
v4 = m.vertex(10.0, 0.0, 0.0)  # 4
v5 = m.vertex(14.0, 0.0, 0.0)  # 5 — shared edge B
v6 = m.vertex(12.0, 4.0, 0.0)  # 6 — apex of large t2 (area=8)
v7 = m.vertex(12.0, 1.0, 0.0)  # 7 — apex of small t3 (area=2); inside t2

t0 = m.triangle(v0, v1, v2)    # 0: pair-A large triangle
t1 = m.triangle(v0, v1, v3)    # 1: pair-A small triangle; overlaps t0
t2 = m.triangle(v4, v5, v6)    # 2: pair-B large triangle
t3 = m.triangle(v4, v5, v7)    # 3: pair-B small triangle; overlaps t2

# Pair A shared edge.
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v3, 1)

# Pair B shared edge.
m.assert_edge_shared(v4, v5, 2)
m.assert_edge_shared(v5, v6, 1)
m.assert_edge_shared(v4, v6, 1)
m.assert_edge_shared(v5, v7, 1)
m.assert_edge_shared(v4, v7, 1)

# Both pairs have overlapping coplanar interiors.
m.assert_triangles_self_intersect(t0, t1)   # pair A
m.assert_triangles_self_intersect(t2, t3)   # pair B

# Both small triangles have area 2.0 < 3.0 — ov selection fires for each.
m.assert_triangle_area_lt(t1, 3.0)
m.assert_triangle_area_lt(t3, 3.0)
