"""Me534 — holeFilling::joinBoundaryLoops branch 5: BALANCED_TRIANGULATION_CRITERION.

MeshFix `holeFilling::joinBoundaryLoops` Branch 5 (*BALANCED_TRIANGULATION_CRITERION*) @ line 779:
  'if (c1 < c2) { EulerEdgeTriangle(…, gve, …); pl1 -= gve->length(); gve = gve->next; }'
  — compare cost c1 (triangle from loop1) vs c2 (triangle from loop2); pick
    lower-cost side, insert triangle, advance that loop pointer.

Branch 5 fires inside the main triangulation loop when both loops still have
remaining length. The algorithm selects the cheaper side (c1 vs c2), inserts a
bridge triangle from that side, reduces the accumulated loop-length by the new
edge length, and advances the loop pointer. This interleaves triangles from both
loops to produce a balanced fill patch.

Geometry: two-loop annular ring (square inner hole, square outer boundary).
  Inner square: i0..i3 (unit square, inner boundary — 4 edges).
  Outer square: o0..o3 (3x larger, outer boundary — 4 edges).
  8 annulus triangles (2 per side) bridging the two square loops.

Both loops have equal perimeter so the criterion alternates between c1 and c2
choices, exercising the balanced branch repeatedly. gv on inner loop (i0), gw
on outer loop (o0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me534",
             title="joinBoundaryLoops_BALANCED_TRIANGULATION_CRITERION: two-loop square annulus; c1 vs c2 cost alternates between loops (Branch 5)",
             defect_class="joinBoundaryLoops_balanced_triangulation_criterion")

# Inner square boundary (unit square).
i0 = m.vertex(0.0, 0.0, 0.0)   # 0 — inner loop (gv)
i1 = m.vertex(1.0, 0.0, 0.0)   # 1
i2 = m.vertex(1.0, 1.0, 0.0)   # 2
i3 = m.vertex(0.0, 1.0, 0.0)   # 3

# Outer square boundary (3x, centered around inner).
o0 = m.vertex(-1.0, -1.0, 0.0)  # 4 — outer loop (gw)
o1 = m.vertex(2.0,  -1.0, 0.0)  # 5
o2 = m.vertex(2.0,   2.0, 0.0)  # 6
o3 = m.vertex(-1.0,  2.0, 0.0)  # 7

# 8 annulus triangles (2 triangles per side of the square annulus).
# Bottom side: i0-i1 inner, o0-o1 outer.
t0 = m.triangle(o0, i0, i1)   # 0
t1 = m.triangle(o0, i1, o1)   # 1
# Right side: i1-i2 inner, o1-o2 outer.
t2 = m.triangle(o1, i1, i2)   # 2
t3 = m.triangle(o1, i2, o2)   # 3
# Top side: i2-i3 inner, o2-o3 outer.
t4 = m.triangle(o2, i2, i3)   # 4
t5 = m.triangle(o2, i3, o3)   # 5
# Left side: i3-i0 inner, o3-o0 outer.
t6 = m.triangle(o3, i3, i0)   # 6
t7 = m.triangle(o3, i0, o0)   # 7

# Inner boundary edges (4 edges — n=1 each).
m.assert_edge_shared(i0, i1, 1)   # inner boundary
m.assert_edge_shared(i1, i2, 1)   # inner boundary
m.assert_edge_shared(i2, i3, 1)   # inner boundary
m.assert_edge_shared(i0, i3, 1)   # inner boundary

# Outer boundary edges (4 edges — n=1 each).
m.assert_edge_shared(o0, o1, 1)   # outer boundary
m.assert_edge_shared(o1, o2, 1)   # outer boundary
m.assert_edge_shared(o2, o3, 1)   # outer boundary
m.assert_edge_shared(o0, o3, 1)   # outer boundary

# Interior bridge edges (8 diagonal edges — n=2 each).
m.assert_edge_shared(o0, i0, 2)
m.assert_edge_shared(o0, i1, 2)
m.assert_edge_shared(o1, i1, 2)
m.assert_edge_shared(o1, i2, 2)
m.assert_edge_shared(o2, i2, 2)
m.assert_edge_shared(o2, i3, 2)
m.assert_edge_shared(o3, i3, 2)
m.assert_edge_shared(o3, i0, 2)

# Two distinct boundary loops.
m.assert_hole_boundary([i0, i1, i2, i3])         # inner square loop (gv=i0)
m.assert_hole_boundary([o0, o3, o2, o1])         # outer square loop (gw=o0)
