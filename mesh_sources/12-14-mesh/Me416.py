"""Me416 — refineSelectedHolePatches_vertex_insertion_convergence: no new vertices inserted (pnnt==nnt); gits++.

MeshFix `holeFilling::refineSelectedHolePatches` Branch 7 (*VERTEX_INSERTION_CONVERGENCE*) @ line 699:
  'if (pnnt == nnt) gits++; if (gits >= 10) break;'
  At the end of each refinement iteration, pnnt (previous iteration's triangle
  count) is compared with nnt (current count). If no new vertices were inserted
  (pnnt == nnt), the iteration was "empty" and gits is incremented. After 10
  consecutive empty iterations, the refinement loop breaks — convergence is
  declared. Branch 7 fires when a complete pass over the region triangles
  adds no new centroid vertices.

Defect pattern: a well-refined triangulation where all vertices are already
  close to their centroid (all dv < sigma or dv < sv). No triangle passes the
  Branch 5 density check, so nnt == pnnt → Branch 7. The mesh is compact and
  uniform: vertices are close to their triangles' centroids.

  With 4 small equilateral-ish triangles, each vertex is within 0.5 units of
  its triangle's centroid, and sigma ≈ 1.0. So dv < sigma for all → Branch 5
  never fires → pnnt == nnt after each pass → Branch 7 fires, gits++.

Geometry: 4 small right-isoceles triangles sharing a hub — each with short edges.
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(0,1,0), v4=(0.5,0.5,0) — center hub.
  t0=(v0,v1,v4), t1=(v1,v2,v4), t2=(v2,v3,v4), t3=(v3,v0,v4)

  Edge lengths: outer ≈ 1.0; hub spokes ≈ sqrt(0.5) ≈ 0.707.
  Centroid of t0=(v0,v1,v4): ((0+1+0.5)/3,(0+0+0.5)/3) = (0.5, 0.167).
  dv0 = |(0,0)-(0.5,0.167)| = sqrt(0.25+0.028) ≈ 0.527.
  sigma ≈ (4*1.0 + 4*0.707) / 8 ≈ 0.854 (avg of outer and hub edges) — but
  the boundary edges only (non-interior) contribute to sigma:
    boundary edges: (v0,v1),(v1,v2),(v2,v3),(v3,v0) each length 1.0 → sigma = 1.0.
  dv0 ≈ 0.527 < sigma = 1.0 → density check does NOT fire → pnnt==nnt → Branch 7.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me416",
             title="refineSelectedHolePatches_vertex_insertion_convergence: no new vertices inserted, gits incremented (Branch 7)",
             defect_class="hole_in_hull")

# Well-refined 4-triangle fan — vertices close to centroids, no splitting needed.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — bottom-left
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — bottom-right
v2 = m.vertex(1.0, 1.0, 0.0)   # 2 — top-right
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — top-left
v4 = m.vertex(0.5, 0.5, 0.0)   # 4 — center hub

# 4-triangle fan around hub.
t0 = m.triangle(v0, v1, v4)   # 0 — centroid (0.5, 0.167); dv0≈0.527 < sigma=1.0
t1 = m.triangle(v1, v2, v4)   # 1 — centroid (0.833, 0.5); dv1≈0.527 < sigma=1.0
t2 = m.triangle(v2, v3, v4)   # 2 — centroid (0.5, 0.833); dv2≈0.527 < sigma=1.0
t3 = m.triangle(v3, v0, v4)   # 3 — centroid (0.167, 0.5); dv3≈0.527 < sigma=1.0

# Hub (interior) edges — shared by 2 triangles each.
m.assert_edge_shared(v0, v4, 2)   # t0 ↔ t3
m.assert_edge_shared(v1, v4, 2)   # t0 ↔ t1
m.assert_edge_shared(v2, v4, 2)   # t1 ↔ t2
m.assert_edge_shared(v3, v4, 2)   # t2 ↔ t3

# Outer boundary edges — contribute to sigma ≈ 1.0.
m.assert_edge_shared(v0, v1, 1)   # length 1.0 → sigma += 1.0
m.assert_edge_shared(v1, v2, 1)   # length 1.0 → sigma += 1.0
m.assert_edge_shared(v2, v3, 1)   # length 1.0 → sigma += 1.0
m.assert_edge_shared(v3, v0, 1)   # length 1.0 → sigma += 1.0
# sigma = 4.0 / 4 = 1.0.

# Hub-spoke edges (v0,v4) etc. have length sqrt(0.5) ≈ 0.707; each vertex's
# average local edge length sv ≈ 0.707 < 1.0 = sigma for the hub. For outer
# vertices: sv = avg of 2 outer edges (1.0) + 1 hub edge (0.707) ≈ 0.902.
# All dv ≈ 0.527 < sigma=1.0 → density check does NOT fire → pnnt==nnt → Branch 7.

# Hub-spoke distance < sigma confirms "already close enough" — no split needed.
m.assert_vertex_pair_distance_lt(v0, v4, 0.8)   # |v0,v4| = sqrt(0.5) ≈ 0.707 < 0.8
m.assert_vertex_pair_distance_lt(v1, v4, 0.8)   # same
m.assert_vertex_pair_distance_lt(v2, v4, 0.8)   # same
m.assert_vertex_pair_distance_lt(v3, v4, 0.8)   # same

# Euler: V=5, E=8 (4 interior + 4 boundary), F=4, chi=1 (open disk).
m.assert_euler_characteristic(5, 8, 4, 1)
