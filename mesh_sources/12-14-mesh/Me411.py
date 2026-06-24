"""Me411 — refineSelectedHolePatches_edge_first_occurrence: edge e1 not yet visited; marked.

MeshFix `holeFilling::refineSelectedHolePatches` Branch 2 (*EDGE_FIRST_OCCURRENCE*) @ line 607:
  'if (!IS_BIT(e, 5)) { MARK_BIT(e, 5); all_edges.appendHead(e); }'
  As the algorithm traverses the edges of each triangle in the region, it checks
  each edge e1. If BIT 5 is not yet set, Branch 2 fires: the edge is seen for the
  first time, marked with BIT 5, and added to the all_edges list for later
  classification (interior vs boundary).

Defect pattern: a 4-triangle patch where each edge is encountered in order.
  The first time each edge is traversed, BIT 5 is clear → Branch 2 fires. On the
  second traversal of a shared edge, BIT 5 is set → the edge goes to Branch 3
  (interior detection). Boundary edges (only traversed once) fire Branch 2 and
  stay in all_edges without a second hit.

Geometry: a 2x1 strip of 4 triangles in a 3x2 grid.
  v0=(0,0,0), v1=(1,0,0), v2=(2,0,0), v3=(0,1,0), v4=(1,1,0), v5=(2,1,0)
  t0=(v0,v1,v3), t1=(v1,v4,v3), t2=(v1,v2,v4), t3=(v2,v5,v4)

  Interior edges (traversed twice; BIT 5 set on second → Branch 3):
    (v1,v3): t0 ↔ t1   (v1,v4): t1 ↔ t2   (v2,v4): t2 ↔ t3
  Boundary edges (traversed once; BIT 5 clear → Branch 2):
    (v0,v1),(v0,v3),(v3,v4),(v1,v2),(v4,v5),(v2,v5)

Each boundary edge triggers Branch 2 exactly once. Three interior edges each
trigger Branch 2 on first pass, then Branch 3 on second pass.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me411",
             title="refineSelectedHolePatches_edge_first_occurrence: first-seen edge marked with BIT5, added to all_edges (Branch 2)",
             defect_class="hole_in_hull")

# 3x2 grid: 6 vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(1.0, 0.0, 0.0)   # 1
v2 = m.vertex(2.0, 0.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3
v4 = m.vertex(1.0, 1.0, 0.0)   # 4
v5 = m.vertex(2.0, 1.0, 0.0)   # 5

# 4-triangle strip.
t0 = m.triangle(v0, v1, v3)   # 0
t1 = m.triangle(v1, v4, v3)   # 1 — shares (v1,v3) with t0
t2 = m.triangle(v1, v2, v4)   # 2 — shares (v1,v4) with t1
t3 = m.triangle(v2, v5, v4)   # 3 — shares (v2,v4) with t2

# Interior edges — first occurrence (Branch 2) then second (Branch 3).
m.assert_edge_shared(v1, v3, 2)   # t0 ↔ t1: first pass → Branch 2, second → Branch 3
m.assert_edge_shared(v1, v4, 2)   # t1 ↔ t2: same
m.assert_edge_shared(v2, v4, 2)   # t2 ↔ t3: same

# Boundary edges — first occurrence only → Branch 2, never revisited.
m.assert_edge_shared(v0, v1, 1)   # t0 outer
m.assert_edge_shared(v0, v3, 1)   # t0 outer
m.assert_edge_shared(v3, v4, 1)   # t1 outer
m.assert_edge_shared(v1, v2, 1)   # t2 outer
m.assert_edge_shared(v4, v5, 1)   # t3 outer
m.assert_edge_shared(v2, v5, 1)   # t3 outer

# Euler: V=6, E=9 (3 interior + 6 boundary), F=4, chi=1 (open disk).
m.assert_euler_characteristic(6, 9, 4, 1)
