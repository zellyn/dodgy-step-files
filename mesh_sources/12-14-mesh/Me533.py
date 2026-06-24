"""Me533 — holeFilling::joinBoundaryLoops branch 4: BOUNDARY_LOOP_LENGTH_ACCUMULATION.

MeshFix `holeFilling::joinBoundaryLoops` Branch 4 (*BOUNDARY_LOOP_LENGTH_ACCUMULATION*) @ line 766:
  'tl1 += e->length(); tl2 += e->length();'
  — traversal accumulates total perimeter of each boundary loop before bridging.

Branch 4 fires during the pre-bridging perimeter measurement phase: for each
boundary loop (loop1 starting at gv, loop2 starting at gw), the algorithm walks
the entire loop summing edge lengths (tl1, tl2). The accumulated lengths control
balanced triangulation in Branch 5.

Geometry: an open annular ring with TWO distinct closed boundary loops.
  Inner triangle hole: i0, i1, i2 (inner boundary — 3 edges, short perimeter ~3 units).
  Outer triangle:     o0, o1, o2 (outer boundary — 3 edges, long perimeter ~6 units).
  6 annulus triangles fill between the two loops.

gv on inner loop, gw on outer loop: Branch 4 walks inner loop summing 3 edge
lengths (tl1) and outer loop summing 3 edge lengths (tl2).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me533",
             title="joinBoundaryLoops_BOUNDARY_LOOP_LENGTH_ACCUMULATION: two-loop annulus; perimeters tl1+tl2 accumulated before bridging (Branch 4)",
             defect_class="joinBoundaryLoops_boundary_loop_length_accumulation")

# Inner triangle hole vertices (unit triangle, short perimeter).
i0 = m.vertex(0.0, 0.0, 0.0)    # 0 — inner loop (gv)
i1 = m.vertex(1.0, 0.0, 0.0)    # 1 — inner loop
i2 = m.vertex(0.5, 0.87, 0.0)   # 2 — inner loop

# Outer triangle vertices (scaled 2x, long perimeter).
o0 = m.vertex(-0.5, -0.87, 0.0)  # 3 — outer loop (gw)
o1 = m.vertex(1.5,  -0.87, 0.0)  # 4 — outer loop
o2 = m.vertex(0.5,   1.73, 0.0)  # 5 — outer loop

# 6 annulus triangles bridging inner and outer loops.
# Bottom side: o0-o1 outer, i0-i1 inner.
t0 = m.triangle(o0, i0, i1)   # 0
t1 = m.triangle(o0, i1, o1)   # 1
# Right side: o1-o2 outer, i1-i2 inner.
t2 = m.triangle(o1, i1, i2)   # 2
t3 = m.triangle(o1, i2, o2)   # 3
# Left side: o2-o0 outer, i2-i0 inner.
t4 = m.triangle(o2, i2, i0)   # 4
t5 = m.triangle(o2, i0, o0)   # 5

# Inner boundary edges (3 edges — each on exactly 1 triangle).
m.assert_edge_shared(i0, i1, 1)   # inner boundary
m.assert_edge_shared(i1, i2, 1)   # inner boundary
m.assert_edge_shared(i0, i2, 1)   # inner boundary

# Outer boundary edges (3 edges — each on exactly 1 triangle).
m.assert_edge_shared(o0, o1, 1)   # outer boundary
m.assert_edge_shared(o1, o2, 1)   # outer boundary
m.assert_edge_shared(o0, o2, 1)   # outer boundary

# Interior edges (6 bridge edges — each on 2 triangles).
m.assert_edge_shared(o0, i0, 2)
m.assert_edge_shared(o0, i1, 2)
m.assert_edge_shared(o1, i1, 2)
m.assert_edge_shared(o1, i2, 2)
m.assert_edge_shared(o2, i2, 2)
m.assert_edge_shared(o2, i0, 2)

# Two distinct closed boundary loops.
m.assert_hole_boundary([i0, i1, i2])         # inner loop (gv side)
m.assert_hole_boundary([o0, o2, o1])         # outer loop (gw side)
