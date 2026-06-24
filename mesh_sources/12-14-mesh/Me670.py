"""Me670 — checkAndRepair::mergeCoincidentEdges branch 1: BOUNDARY_VERTEX_CLASSIFICATION.

MeshFix `checkAndRepair::mergeCoincidentEdges` Branch 1 (*BOUNDARY_VERTEX_CLASSIFICATION*) @ line 266:
  'MARK_BIT(e->v1, 5);' — while scanning every edge in the mesh, each
  boundary edge (shared by exactly one triangle, n == 1) causes both its
  endpoint vertices to be tagged with BIT 5 via MARK_BIT. Vertices so
  tagged are later tested with 'isOnBoundary' to decide whether merging
  is legal. This branch fires once per boundary edge found in the scan.

Defect pattern: an open triangulated strip with a clear perimeter boundary.
  Five vertices arranged as two adjacent triangles sharing one interior edge
  (n=2). The remaining four outer edges are each on the boundary (n=1). Each
  boundary edge triggers Branch 1, marking its two endpoint vertices with
  BIT 5. The interior shared edge does NOT trigger this branch.

Geometry:
  v0 = (0, 0, 0)  — left-bottom corner
  v1 = (1, 0, 0)  — bottom-middle
  v2 = (2, 0, 0)  — right-bottom corner
  v3 = (0, 1, 0)  — left-top corner
  v4 = (2, 1, 0)  — right-top corner
  t0 = (v0, v1, v3)  — left triangle
  t1 = (v1, v2, v4)  — right triangle (separate patch; shares no edge with t0)
  Boundary edges: (v0,v1), (v1,v3), (v0,v3), (v1,v2), (v2,v4), (v1,v4) — all n=1.
  No shared interior edge (n=2) exists since the two triangles don't touch.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me670",
    title="mergeCoincidentEdges BOUNDARY_VERTEX_CLASSIFICATION: open mesh; every edge n=1 triggers MARK_BIT(v,5) on both endpoints (Branch 1)",
    defect_class="open_boundary",
)

v0 = m.vertex(0.0, 0.0, 0.0)  # 0 — left-bottom
v1 = m.vertex(1.0, 0.0, 0.0)  # 1 — bottom-middle (shared vertex between patches)
v2 = m.vertex(2.0, 0.0, 0.0)  # 2 — right-bottom
v3 = m.vertex(0.0, 1.0, 0.0)  # 3 — left-top
v4 = m.vertex(2.0, 1.0, 0.0)  # 4 — right-top

t0 = m.triangle(v0, v1, v3)   # 0 — left triangle
t1 = m.triangle(v1, v2, v4)   # 1 — right triangle

# All six edges are boundary edges (n=1): each one fires Branch 1,
# marking both endpoints with MARK_BIT(v, 5) for isOnBoundary lookup.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v4, 1)
m.assert_edge_shared(v1, v4, 1)

# Euler: V=5, E=6, F=2, chi=1 (two disjoint disks share only vertex v1;
# chi = V - E + F = 5 - 6 + 2 = 1).
m.assert_euler_characteristic(5, 6, 2, 1)
