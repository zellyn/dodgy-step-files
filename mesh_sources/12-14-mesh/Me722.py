"""Me722 — Basic_TMesh.safeCoordBackApproximation branch 3: Jitter escape condition.

Basic_TMesh.safeCoordBackApproximation Branch 3 (*jitter escape condition*) @ line 288:
  'for(a = -1; a <= 1; a++) for(b = -1; b <= 1; b++) for(c = -1; c <= 1; c++) {
     if(a == 0 && b == 0 && c == 0) continue;
     ov->x += a*delta; ov->y += b*delta; ov->z += c*delta;
     if(!e->overlaps()) { resolved = 1; break; } else { undo; }
   }'
  — for each of the 26 direction-vectors (a,b,c) in {-1,0,1}^3 minus {0,0,0}, MeshFix tries
  perturbing the chosen opposite vertex by `delta`. When `a=b=c=2` (loop exhausted without
  finding a non-overlapping jitter), the overlap was not resolved; the algorithm continues.

Defect pattern: a pair of coplanar triangles sharing an edge where the overlapping apex
  vertex (ov) cannot escape the overlap by simple ±delta jitter in any of the 26 directions
  — it is geometrically "trapped". The fixture demonstrates the scenario that exercises the
  full 26-direction scan: t0 is a large outer triangle and t1 is a very small inner triangle
  whose apex is deep inside t0's area.

Geometry (3-triangle fan around a central vertex):
  v0=(0,0,0), v1=(6,0,0), v2=(3,5,0), v3=(3,1,0)
  t0=(v0,v1,v2): large outer triangle, area=15
  t1=(v0,v1,v3): tiny inner triangle, area=3; v3 trapped deep inside t0
  t2=(v1,v2,v3): adjacency triangle completing the fan, area varies
  Multiple overlapping triangles → jitter loop iterates all 26 directions.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me722",
    title="safeCoordBackApproximation jitter escape condition: overlapping apex trapped inside large triangle; 26-direction jitter scan exercised (Branch 3)",
    defect_class="self_intersection_coplanar_overlap",
)

# Outer triangle vertices.
v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — shared edge start
v1 = m.vertex(6.0, 0.0, 0.0)  # 1 — shared edge end
v2 = m.vertex(3.0, 5.0, 0.0)  # 2 — apex of large outer triangle t0

# Inner apex — deep inside t0's area, shared by t1 and t2.
v3 = m.vertex(3.0, 1.0, 0.0)  # 3 — ov: trapped apex; t1 area = 3.0

t0 = m.triangle(v0, v1, v2)   # 0: large outer triangle (area=15)
t1 = m.triangle(v0, v1, v3)   # 1: small inner triangle (area=3); overlaps t0
t2 = m.triangle(v1, v2, v3)   # 2: right adjacency triangle

# Shared edge (v0,v1) between t0 and t1.
m.assert_edge_shared(v0, v1, 2)
# Shared edge (v1,v2) between t0 and t2.
m.assert_edge_shared(v1, v2, 2)
# Non-shared edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# t0 and t1 are coplanar with overlapping interiors (t1 inside t0).
m.assert_triangles_self_intersect(t0, t1)

# t1 has small area (3.0) — its apex v3 is the jitter target.
m.assert_triangle_area_lt(t1, 4.0)
