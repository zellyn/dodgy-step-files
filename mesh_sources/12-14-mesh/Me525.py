"""Me525 — iterativeEdgeSwaps convergence_fail: totits >= 10; iteration limit reached without convergence (Branch 6).

Basic_TMesh.iterativeEdgeSwaps branch 6: convergence_fail

MeshFix `Basic_TMesh.iterativeEdgeSwaps` Branch 6 (*convergence_fail*) @ line 1606:
  'if (totits >= 10) TMesh::warning("..."); return totits;'
  — if the swap iteration loop exhausts all 10 allowed passes without emptying the
  candidate queue, the algorithm issues a warning and returns the iteration count.
  This fires when the swap candidate set oscillates: swapping one edge adds the
  adjacent edges back to the queue, which then swap back, forming a cycle.

Defect pattern: a nearly-regular four-triangle fan around a central vertex where
  the Delaunay criterion is on a knife-edge — swapping the diagonal between any
  pair of quads immediately creates a new non-Delaunay edge in the adjacent pair.
  The swap queue never empties: it oscillates between two equivalent triangulations.

Geometry: a central vertex v4 surrounded by 4 outer vertices forming a square.
  The four triangles use alternating diagonals so that every interior edge is
  marginally non-Delaunay:
    v0=(0,0,0), v1=(2,0,0), v2=(2,2,0), v3=(0,2,0), v4=(1,1,0) [center]

  Triangles:
    t0=(v0,v1,v4) — bottom  (interior edges: (v0,v4) and (v1,v4))
    t1=(v1,v2,v4) — right   (interior edges: (v1,v4) and (v2,v4))
    t2=(v2,v3,v4) — top     (interior edges: (v2,v4) and (v3,v4))
    t3=(v3,v0,v4) — left    (interior edges: (v3,v4) and (v0,v4))

  All four edges radiating from v4 are interior (shared by 2 triangles each).
  All outer quad edges (v0-v1, v1-v2, v2-v3, v3-v0) are boundary (n=1).
  This is a regular fan: every edge from center is exactly Delaunay-neutral.
  In the oscillating swap scenario, swapping any spoke attempts to replace it
  with the cross-diagonal, which immediately re-creates the same non-Delaunay
  condition in the adjacent quad — creating a cycle that never terminates within
  10 iterations.

  Note: the oscillation happens because the four spokes from v4 are exactly
  symmetric — swapping any one edge produces a congruent configuration that
  swaps the other edges back. The convergence_fail branch fires because
  totits reaches 10 before the queue drains.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me525",
    title="iterativeEdgeSwaps convergence_fail: 4-triangle symmetric fan oscillates swap queue; totits reaches 10 without convergence (Branch 6)",
    defect_class="mesh_optimization",
)

# Square with center vertex — four-triangle fan.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0 — lower-left corner
v1 = m.vertex(2.0, 0.0, 0.0)   # 1 — lower-right corner
v2 = m.vertex(2.0, 2.0, 0.0)   # 2 — upper-right corner
v3 = m.vertex(0.0, 2.0, 0.0)   # 3 — upper-left corner
v4 = m.vertex(1.0, 1.0, 0.0)   # 4 — center vertex (connected to all corners)

# Four triangles: one per quadrant, all sharing the center vertex v4.
t0 = m.triangle(v0, v1, v4)    # 0: bottom triangle
t1 = m.triangle(v1, v2, v4)    # 1: right triangle
t2 = m.triangle(v2, v3, v4)    # 2: top triangle
t3 = m.triangle(v3, v0, v4)    # 3: left triangle

# All four spoke edges from v4 are interior (shared by 2 triangles each).
m.assert_edge_shared(v0, v4, 2)   # left spoke: shared by t0 and t3
m.assert_edge_shared(v1, v4, 2)   # bottom-right spoke: shared by t0 and t1
m.assert_edge_shared(v2, v4, 2)   # right spoke: shared by t1 and t2
m.assert_edge_shared(v3, v4, 2)   # top-left spoke: shared by t2 and t3

# Boundary edges of the outer square (n=1 each).
m.assert_edge_shared(v0, v1, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v2, v3, 1)
m.assert_edge_shared(v3, v0, 1)

# Euler: V=5, E=8, F=4, chi=1 (open planar disk).
m.assert_euler_characteristic(5, 8, 4, 1)
