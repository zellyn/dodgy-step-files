"""Me410 — refineSelectedHolePatches_region_initialization: t0 pre-selected; BFS builds visited region.

MeshFix `holeFilling::refineSelectedHolePatches` Branch 1 (*REGION_INITIALIZATION*) @ line 590:
  'if (IS_VISITED(t0)) { UNMARK_VISIT(t0); ... }' — the algorithm marks t0 as visited
  (pre-selected) then BFS-expands over all visited triangles to collect the refinement
  region. Branch 1 fires immediately: t0 is already marked, so it is unmarked and used
  as the BFS seed from which the region of hole-fill triangles is assembled.

Defect pattern: five triangles forming a connected hole-fill patch. The central
  triangle t0 is the BFS seed (IS_VISITED). BFS propagates via shared interior edges
  to the four surrounding triangles t1-t4, assembling the full region.

Geometry: five triangles sharing a common hub vertex v0 at (1,1,0).
  Outer ring: v1=(0,1,0), v2=(1,2,0), v3=(2,1,0), v4=(1,0,0).
  Extra outer vertex: v5=(0,0,0) to give t1 a distinct outer triangle.

  t0=(v0,v1,v2)  — BFS seed (pre-selected)
  t1=(v0,v2,v3)  — adjacent to t0 via (v0,v2)
  t2=(v0,v3,v4)  — adjacent to t1 via (v0,v3)
  t3=(v0,v4,v1)  — adjacent to t2 via (v0,v4) and to t0 via (v0,v1)
  t4=(v1,v5,v4)  — adjacent to t3 via (v1,v4)

Interior edges (shared by 2 triangles): (v0,v1), (v0,v2), (v0,v3), (v0,v4), (v1,v4)
Boundary edges (shared by 1 triangle): v1-v2, v2-v3, v3-v4, v0-v5 is unused —
  outer: (v1,v2),(v2,v3),(v3,v4),(v1,v5),(v5,v4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me410",
             title="refineSelectedHolePatches_region_initialization: BFS builds hole-fill region from pre-selected t0 (Branch 1)",
             defect_class="hole_in_hull")

# Hub + outer ring.
v0 = m.vertex(1.0, 1.0, 0.0)   # 0 — hub
v1 = m.vertex(0.0, 1.0, 0.0)   # 1 — left
v2 = m.vertex(1.0, 2.0, 0.0)   # 2 — top
v3 = m.vertex(2.0, 1.0, 0.0)   # 3 — right
v4 = m.vertex(1.0, 0.0, 0.0)   # 4 — bottom
v5 = m.vertex(0.0, 0.0, 0.0)   # 5 — extra outer

# Five-triangle fan: t0 is the BFS seed (pre-selected/IS_VISITED).
t0 = m.triangle(v0, v1, v2)   # 0 — BFS seed; Branch 1: IS_VISITED, unmark, start BFS
t1 = m.triangle(v0, v2, v3)   # 1 — BFS reaches via (v0,v2)
t2 = m.triangle(v0, v3, v4)   # 2 — BFS reaches via (v0,v3)
t3 = m.triangle(v0, v4, v1)   # 3 — BFS reaches via (v0,v4)
t4 = m.triangle(v1, v5, v4)   # 4 — BFS reaches via (v1,v4)

# Interior edges — BFS propagation links between region triangles.
m.assert_edge_shared(v0, v1, 2)   # t0 ↔ t3
m.assert_edge_shared(v0, v2, 2)   # t0 ↔ t1
m.assert_edge_shared(v0, v3, 2)   # t1 ↔ t2
m.assert_edge_shared(v0, v4, 2)   # t2 ↔ t3
m.assert_edge_shared(v1, v4, 2)   # t3 ↔ t4

# Boundary edges — delimiting the hole-fill patch (each on exactly 1 triangle).
m.assert_edge_shared(v1, v2, 1)   # t0 outer
m.assert_edge_shared(v2, v3, 1)   # t1 outer
m.assert_edge_shared(v3, v4, 1)   # t2 outer
m.assert_edge_shared(v1, v5, 1)   # t4 outer
m.assert_edge_shared(v5, v4, 1)   # t4 outer

# Euler: V=6, E=10 (5 interior + 5 boundary), F=5, chi=1 (open disk).
m.assert_euler_characteristic(6, 10, 5, 1)
