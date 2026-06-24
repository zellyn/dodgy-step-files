"""Me522 — iterativeEdgeSwaps convergence_iteration: totits++ < 10; iteration loop progresses through multiple swap passes (Branch 3).

Basic_TMesh.iterativeEdgeSwaps branch 3: convergence_iteration

MeshFix `Basic_TMesh.iterativeEdgeSwaps` Branch 3 (*convergence_iteration*) @ line 1573:
  'while (swaps && totits++ < 10) { ... }'
  — the outer iteration loop repeats swap passes as long as (a) there are edges in
  the swap queue and (b) the total iteration count is under 10. Branch 3 fires each
  time the condition holds and the loop body executes at least once (i.e. convergence
  required more than one pass).

Defect pattern: a multi-triangle mesh with several non-Delaunay interior edges
  that each require at least one swap pass to stabilize. The chain of edges is long
  enough that a second pass is needed after the first round of swaps propagates.

Geometry: six triangles in a 2×2 grid of quads, each split along the same diagonal.
  The interior edges are sub-optimal (non-Delaunay) and require at least two swap
  iterations to converge to the Delaunay triangulation.

  Grid vertices (3×2 + extra):
    v0=(0,0,0), v1=(1,0,0), v2=(2,0,0)
    v3=(0,1,0), v4=(1,1,0), v5=(2,1,0)
    v6=(0.5,2,0) [apex bridging top]

  Triangles:
    t0=(v0,v1,v3) — lower-left quad, lower triangle
    t1=(v1,v4,v3) — lower-left quad, upper triangle; interior edge (v1,v3) is sub-optimal
    t2=(v1,v2,v4) — lower-right quad, lower triangle
    t3=(v2,v5,v4) — lower-right quad, upper triangle; interior edge (v2,v4) is sub-optimal
    t4=(v3,v4,v6) — upper-left
    t5=(v4,v5,v6) — upper-right (creates more interior edges)

  Interior edges: (v1,v3) in left quad, (v2,v4) in right quad, (v3,v4) top row, (v4,v6) top apex.
  After swap of (v1,v3) to (v0,v4), the queue gains adjacent edges which then require
  a second pass — triggering totits > 1 and exercising the convergence_iteration branch.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me522",
    title="iterativeEdgeSwaps convergence_iteration: multi-pass swap loop (totits++ < 10) across 6-triangle grid requiring multiple iterations (Branch 3)",
    defect_class="mesh_optimization",
)

# 3×2 grid plus apex
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — lower-left
v1 = m.vertex(1.0, 0.0, 0.0)   # 1 — lower-center
v2 = m.vertex(2.0, 0.0, 0.0)   # 2 — lower-right
v3 = m.vertex(0.0, 1.0, 0.0)   # 3 — mid-left
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — center
v5 = m.vertex(2.0, 1.0, 0.0)   # 5 — mid-right
v6 = m.vertex(1.0, 2.0, 0.0)   # 6 — apex

# Lower-left quad split along (v1,v3) diagonal — sub-optimal for Delaunay
t0 = m.triangle(v0, v1, v3)    # 0
t1 = m.triangle(v1, v4, v3)    # 1  interior edge (v1,v3) between t0,t1

# Lower-right quad split along (v2,v4) diagonal — sub-optimal for Delaunay
t2 = m.triangle(v1, v2, v4)    # 2
t3 = m.triangle(v2, v5, v4)    # 3  interior edge (v2,v4) between t2,t3

# Upper row
t4 = m.triangle(v3, v4, v6)    # 4
t5 = m.triangle(v4, v5, v6)    # 5

# Interior edges (swap candidates): each shared by exactly 2 triangles.
m.assert_edge_shared(v1, v3, 2)   # sub-optimal diagonal in left quad
m.assert_edge_shared(v2, v4, 2)   # sub-optimal diagonal in right quad
m.assert_edge_shared(v3, v4, 2)   # horizontal center strip edge
m.assert_edge_shared(v4, v5, 2)   # right strip

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v2, v5, 1)
m.assert_edge_shared(v3, v6, 1)
m.assert_edge_shared(v5, v6, 1)

# Euler: V=7, E=12, F=6, chi=1 (open planar disk).
m.assert_euler_characteristic(7, 12, 6, 1)
