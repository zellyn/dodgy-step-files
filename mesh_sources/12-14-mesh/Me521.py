"""Me521 — iterativeEdgeSwaps swap_candidate_filter: interior non-sharp non-boundary edge qualifies as swap candidate (Branch 2).

Basic_TMesh.iterativeEdgeSwaps branch 2: swap_candidate_filter

MeshFix `Basic_TMesh.iterativeEdgeSwaps` Branch 2 (*swap_candidate_filter*) @ line 1567:
  'if (!IS_SHARPEDGE(e) && !e->isOnBoundary()) swaps.appendHead(e);'
  — for each triangle edge, the algorithm checks whether the edge is interior
  (shared by exactly 2 triangles), non-sharp (not flagged IS_SHARPEDGE), and
  not on the mesh boundary. Only such edges are added to the swap candidate list.

Defect pattern: a minimal interior-edge mesh where a clear interior edge exists
  between two adjacent triangles. The edge is interior (n=2), not marked as a
  sharp feature, and not on the boundary — it satisfies all three filter conditions
  and enters the swap candidate queue.

Geometry: four vertices forming a planar quad, split along the diagonal (v1,v2).
  The shared edge (v1,v2) is interior. All four outer edges are boundary (n=1).
  This is the simplest possible interior-edge configuration.

  v0=(0,0,0), v1=(1,0,0), v2=(0,1,0), v3=(1,1,0)
  t0=(v0,v1,v2) — lower-left triangle
  t1=(v1,v3,v2) — upper-right triangle
  Interior edge: (v1,v2) — shared by t0 and t1, non-boundary, non-sharp.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me521",
    title="iterativeEdgeSwaps swap_candidate_filter: interior edge (v1,v2) is non-sharp and non-boundary, qualifies for swap queue (Branch 2)",
    defect_class="mesh_optimization",
)

v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — lower-left
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — lower-right
v2 = m.vertex(0.0, 1.0, 0.0)   # 2 — upper-left
v3 = m.vertex(1.0, 1.0, 0.0)   # 3 — upper-right

# Two triangles sharing the interior diagonal edge (v1,v2).
t0 = m.triangle(v0, v1, v2)    # 0: lower-left
t1 = m.triangle(v1, v3, v2)    # 1: upper-right

# Interior edge (v1,v2) — shared by exactly 2 triangles (non-boundary, non-sharp).
m.assert_edge_shared(v1, v2, 2)

# Boundary edges — n=1 each.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v1, v3, 1)
m.assert_edge_shared(v2, v3, 1)

# Euler: V=4, E=5, F=2, chi=1 (open planar disk).
m.assert_euler_characteristic(4, 5, 2, 1)
