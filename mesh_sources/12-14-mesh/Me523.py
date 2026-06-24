"""Me523 — iterativeEdgeSwaps swap_improves_angle: Delaunay flip accepted because min angle improved (Branch 4).

Basic_TMesh.iterativeEdgeSwaps branch 4: swap_improves_angle

MeshFix `Basic_TMesh.iterativeEdgeSwaps` Branch 4 (*swap_improves_angle*) @ line 1586:
  'if (e->swap() && ... delaunayMinAngle improved) swaps.appendHead(adjacent edges)'
  — the algorithm attempts a swap on a candidate edge. If the swap succeeds AND the
  minimum angle of the two resulting triangles is greater than the minimum angle of
  the two original triangles, the swap is accepted and adjacent edges are added to
  the candidate queue.

Defect pattern: a thin elongated quad (non-Delaunay triangulation) where the current
  diagonal creates two very obtuse/thin triangles. Flipping to the other diagonal
  would produce two better-balanced triangles with a larger minimum angle — the swap
  is accepted.

Geometry: a tall thin quad where the "wrong" diagonal (the long one) is currently
  used. The quad has vertices at:
    v0=(0,0,0), v1=(4,0,0), v2=(2,3,0), v3=(2,-3,0)
  Current diagonal: (v0,v1) — the long horizontal edge splitting into two obtuse
  triangles (t0 and t1) with very small minimum angles.
  Optimal diagonal: (v2,v3) — produces two isoceles triangles with much larger
  minimum angles (Delaunay condition satisfied after swap).

  t0=(v0,v2,v3) — left triangle (thin; min angle is small)
  t1=(v2,v1,v3) — right triangle (thin; min angle is small)
  Interior edge (v2,v3) = the long diagonal — non-Delaunay; swapping to (v0,v1)
  would produce two better-balanced triangles.

The triangle_aspect_ratio_gt assertion captures the "thin/elongated" pre-swap state.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me523",
    title="iterativeEdgeSwaps swap_improves_angle: thin non-Delaunay quad; flip of long diagonal (v2,v3) improves min angle (Branch 4)",
    defect_class="mesh_optimization",
)

# Thin elongated quad — the long diagonal (v2,v3) is currently the shared edge.
# v2 and v3 are far apart vertically; v0 and v1 are the left/right tips.
v0 = m.vertex(0.0,  0.0, 0.0)   # 0 — left tip
v1 = m.vertex(4.0,  0.0, 0.0)   # 1 — right tip
v2 = m.vertex(2.0,  3.0, 0.0)   # 2 — top center
v3 = m.vertex(2.0, -3.0, 0.0)   # 3 — bottom center

# Current triangulation: long vertical diagonal (v2,v3) splits the quad
# into two thin triangles. The min angle in each is very small (< 30°).
t0 = m.triangle(v0, v2, v3)    # 0: left thin triangle
t1 = m.triangle(v2, v1, v3)    # 1: right thin triangle

# The interior edge (v2,v3) is the long vertical diagonal — swap candidate.
# After swap to (v0,v1), each resulting triangle has a 90° base angle — much better.
m.assert_edge_shared(v2, v3, 2)

# Boundary edges.
m.assert_edge_shared(v0, v2, 1)
m.assert_edge_shared(v0, v3, 1)
m.assert_edge_shared(v1, v2, 1)
m.assert_edge_shared(v1, v3, 1)

# Both triangles are elongated — high aspect ratio confirms non-Delaunay pre-swap state.
m.assert_triangle_aspect_ratio_gt(t0, 2.0)
m.assert_triangle_aspect_ratio_gt(t1, 2.0)

# Euler: V=4, E=5, F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
