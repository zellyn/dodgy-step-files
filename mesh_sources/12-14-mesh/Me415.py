"""Me415 — refineSelectedHolePatches_edge_swap_delaunay_improvement: edge swap reduces length, kept.

MeshFix `holeFilling::refineSelectedHolePatches` Branch 6 (*EDGE_SWAP_DELAUNAY_IMPROVEMENT*) @ line 683:
  'if (e->squaredLength() >= l*0.999999) { e->swap(1); ... }'
  After vertex insertion, each candidate edge in the swap list is compared
  against the lengths of the two alternative edges formed by swapping the
  diagonal. If the current edge length squared is >= l * 0.999999 (where l is
  the squared length of the longer alternative diagonal), the swap does NOT
  improve quality — the swap is KEPT (i.e., the branch body executes to add
  edge neighbors and proceed). Branch 6 fires when the existing edge is at
  least as long as what it would become after a swap, meaning the swap is
  beneficial and accepted.

Defect pattern: a quadrilateral split into two triangles along a long diagonal.
  The current diagonal is longer than the alternative diagonal — swapping would
  improve the triangulation (more equilateral). Branch 6 detects this and keeps
  the swap.

  Quadrilateral: v0=(0,0,0), v1=(2,0,0), v2=(2,1,0), v3=(0,1,0).
  Current diagonal: (v0,v2) = length sqrt(4+1) = sqrt(5) ≈ 2.236.
  Alternative diagonal: (v1,v3) = length sqrt(4+1) = sqrt(5) ≈ 2.236.
  Hmm — symmetric rectangle gives equal diagonals. Use a non-symmetric quad:

  v0=(0,0,0), v1=(3,0,0), v2=(2,2,0), v3=(0,2,0)
  Current diagonal: (v0,v2) = sqrt(4+4) = sqrt(8) ≈ 2.828.
  Alternative diagonal: (v1,v3) = sqrt(9+4) = sqrt(13) ≈ 3.606.
  Here current (v0,v2) is shorter — swapping to (v1,v3) would be WORSE.
  We need current diagonal LONGER than alternative.

  v0=(0,0,0), v1=(3,0,0), v2=(1,2,0), v3=(0,1,0)
  Current diagonal: (v1,v3) = sqrt(9+1) = sqrt(10) ≈ 3.162.
  t0=(v0,v1,v3), t1=(v1,v2,v3)
  Alternative diagonal: (v0,v2) = sqrt(1+4) = sqrt(5) ≈ 2.236.
  squaredLength(current) = 10, l = squaredLength(v0,v2) = 5.
  10 >= 5 * 0.999999 → TRUE → Branch 6 fires, swap kept.

Geometry: two triangles forming a non-convex-ish quad where (v1,v3) diagonal is long.
  t0=(v0,v1,v3): the longer diagonal (v1,v3) is shared with t1.
  t1=(v1,v2,v3): same shared diagonal (v1,v3).
  After swap: diagonal becomes (v0,v2), which is shorter — improvement accepted.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me415",
             title="refineSelectedHolePatches_edge_swap_delaunay_improvement: long diagonal satisfies swap condition, swap accepted (Branch 6)",
             defect_class="hole_in_hull")

# Quadrilateral vertices.
v0 = m.vertex(0.0, 0.0, 0.0)   # 0
v1 = m.vertex(3.0, 0.0, 0.0)   # 1
v2 = m.vertex(1.0, 2.0, 0.0)   # 2
v3 = m.vertex(0.0, 1.0, 0.0)   # 3

# Current triangulation uses long diagonal (v1,v3).
# squaredLength(v1,v3) = (3-0)^2 + (0-1)^2 = 9+1 = 10.
# Alternative diagonal (v0,v2): squaredLength = (0-1)^2 + (0-2)^2 = 1+4 = 5.
# 10 >= 5 * 0.999999 → TRUE → Branch 6: swap is beneficial, kept.
t0 = m.triangle(v0, v1, v3)   # 0 — uses long diagonal (v1,v3)
t1 = m.triangle(v1, v2, v3)   # 1 — uses long diagonal (v1,v3)

# The current (long) diagonal — shared interior edge.
m.assert_edge_shared(v1, v3, 2)   # interior: long diagonal; swap reduces to (v0,v2)

# Boundary edges.
m.assert_edge_shared(v0, v1, 1)   # t0 outer
m.assert_edge_shared(v0, v3, 1)   # t0 outer
m.assert_edge_shared(v2, v3, 1)   # t1 outer
m.assert_edge_shared(v1, v2, 1)   # t1 outer

# The long diagonal is longer than the alternative — confirms Branch 6 condition.
# We verify this via vertex_pair_distance_lt: (v0,v2) < (v1,v3) in squared length.
# |v1,v3| ≈ 3.162, |v0,v2| ≈ 2.236 — the CURRENT diagonal is longer.
# Assert that the current diagonal (v1,v3) is longer than the alternative (v0,v2)
# by checking v0-v2 distance is less than v1-v3 distance.
m.assert_vertex_pair_distance_lt(v0, v2, 2.5)   # |v0,v2| = sqrt(5) ≈ 2.236 < 2.5

# Euler: V=4, E=5 (1 interior + 4 boundary), F=2, chi=1 (open disk).
m.assert_euler_characteristic(4, 5, 2, 1)
