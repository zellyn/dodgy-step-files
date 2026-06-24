"""Me412 — refineSelectedHolePatches_edge_interior_detection: edge appears twice; classified as interior.

MeshFix `holeFilling::refineSelectedHolePatches` Branch 3 (*EDGE_INTERIOR_DETECTION*) @ line 615:
  'else { UNMARK_BIT(e, 5); interior_edges.appendHead(e); }'
  When an edge is encountered a second time (BIT 5 already set from the first
  traversal in Branch 2), Branch 3 fires: BIT 5 is cleared and the edge is added
  to the interior_edges list. Interior edges are excluded from the boundary-length
  averaging in Branch 4. Any edge shared by exactly 2 triangles in the selected
  region triggers Branch 3 on its second traversal.

Defect pattern: three triangles in an L-shape with two interior edges. The central
  edge (v1,v2) is shared by triangles t0 and t1. On first traversal of t0's edges,
  (v1,v2) is seen for the first time → Branch 2. On traversal of t1's edges,
  (v1,v2) is seen again with BIT 5 set → Branch 3. Similarly for (v2,v4) between
  t1 and t2.

Geometry: three triangles forming an L-shape.
  v0=(0,0,0), v1=(1,0,0), v2=(1,1,0), v3=(2,0,0), v4=(2,1,0)
  t0=(v0,v1,v2)  — left triangle
  t1=(v1,v3,v2)  — middle; (v1,v2) interior with t0
  t2=(v2,v3,v4)  — right; (v2,v3) interior with t1

Interior edges (Branch 3 fires on second traversal):
  (v1,v2): t0 ↔ t1
  (v2,v3): t1 ↔ t2

Boundary edges (Branch 2 only — first occurrence):
  (v0,v1),(v0,v2),(v1,v3),(v3,v4),(v2,v4)
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me412",
             title="refineSelectedHolePatches_edge_interior_detection: shared edge seen twice cleared from BIT5, added to interior_edges (Branch 3)",
             defect_class="hole_in_hull")

# 5 vertices — all used in triangles.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 1.0, 0.0)   # 2
v3 = m.vertex(2.0, 0.0, 0.0)   # 3
v4 = m.vertex(2.0, 1.0, 0.0)   # 4

# Three-triangle L-shape with two interior edges.
t0 = m.triangle(v0, v1, v2)   # 0 — left triangle
t1 = m.triangle(v1, v3, v2)   # 1 — middle; (v1,v2) interior with t0
t2 = m.triangle(v2, v3, v4)   # 2 — right; (v2,v3) interior with t1

# Interior edges — Branch 3 fires on second traversal of each.
m.assert_edge_shared(v1, v2, 2)   # t0 ↔ t1: first pass Branch 2, second Branch 3
m.assert_edge_shared(v2, v3, 2)   # t1 ↔ t2: same

# Boundary edges — Branch 2 only (first occurrence, BIT5 never set again).
m.assert_edge_shared(v0, v1, 1)   # t0 outer
m.assert_edge_shared(v0, v2, 1)   # t0 outer
m.assert_edge_shared(v1, v3, 1)   # t1 outer
m.assert_edge_shared(v3, v4, 1)   # t2 outer
m.assert_edge_shared(v2, v4, 1)   # t2 outer

# Euler: V=5, E=7 (2 interior + 5 boundary), F=3, chi=1 (open disk).
m.assert_euler_characteristic(5, 7, 3, 1)
