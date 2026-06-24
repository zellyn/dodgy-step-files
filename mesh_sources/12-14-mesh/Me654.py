"""Me654 — Basic_TMesh.removeEdges topology_invalidation: d_boundaries=d_handles=d_shells=1 (Branch 5).

MeshFix `Basic_TMesh.removeEdges` Branch 5 (*topology_invalidation*) @ line 592:
  'd_boundaries = d_handles = d_shells = 1;' — after the edge-removal loop has
  deleted at least one orphaned edge, the cached topology metrics (boundary count,
  handle/genus count, shell count) are marked dirty. Any prior computed values are
  now stale and must be recomputed on next access.

Geometric proxy: a mesh with TWO disconnected open shells is the canonical pattern
  that maximises non-trivial d_shells and d_boundaries values. After orphaned-edge
  cleanup, all three topology caches must be invalidated. The fixture has one
  degenerate triangle (with a coincident-vertex edge) in Shell A, and a clean
  triangle pair in Shell B — the degenerate triangle's edge is the orphan that
  triggers the dirty-flag path.

Geometry (Shell A — left, with orphaned edge):
  a0 = (0, 0, 0), a1 = (0, 0, 0) [=a0], a2 = (2, 1, 0)
  ta0 = (a0, a1, a2)   — degenerate; a0==a1 is the orphaned edge

Geometry (Shell B — right, clean, disconnected):
  b0 = (6, 0, 0), b1 = (8, 0, 0), b2 = (7, 2, 0), b3 = (6, 2, 0)
  tb0 = (b0, b1, b2)
  tb1 = (b0, b2, b3)

Two disconnected open shells → d_shells > 1. Orphaned edge in Shell A triggers
removal → d_boundaries = d_handles = d_shells = 1 (dirty flags set).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me654",
    title="removeEdges topology_invalidation: two disconnected shells; orphaned edge (a0==a1) triggers d_boundaries=d_handles=d_shells=1 (Branch 5)",
    defect_class="orphaned_edge",
)

# Shell A — degenerate triangle with orphaned zero-length edge.
a0 = m.vertex(0.0, 0.0, 0.0)   # 0 — coincident with a1 (orphaned-edge endpoint a)
a1 = m.vertex(0.0, 0.0, 0.0)   # 1 — coincident with a0 (orphaned-edge endpoint b)
a2 = m.vertex(2.0, 1.0, 0.0)   # 2

ta0 = m.triangle(a0, a1, a2)   # 0 — degenerate (a0==a1); orphaned edge a0-a1

# Shell B — clean disconnected pair of triangles (well-separated from Shell A).
b0 = m.vertex(6.0, 0.0, 0.0)   # 3
b1 = m.vertex(8.0, 0.0, 0.0)   # 4
b2 = m.vertex(7.0, 2.0, 0.0)   # 5
b3 = m.vertex(6.0, 2.0, 0.0)   # 6

tb0 = m.triangle(b0, b1, b2)   # 1 — well-formed
tb1 = m.triangle(b0, b2, b3)   # 2 — well-formed

# a0 and a1 are coincident: the orphaned edge that drives topology_invalidation.
m.assert_vertex_pair_distance_lt(a0, a1, 1e-9)

# Degenerate triangle ta0 has zero area.
m.assert_triangle_area_lt(ta0, 1e-9)

# Orphaned collapsed edge in Shell A (boundary, n=1).
m.assert_edge_shared(a0, a1, 1)

# Shell B interior shared edge (n=2).
m.assert_edge_shared(b0, b2, 2)

# Shell A and Shell B are disconnected — no shared vertices between them.
m.assert_vertex_pair_no_shared_triangle(a2, b0)
