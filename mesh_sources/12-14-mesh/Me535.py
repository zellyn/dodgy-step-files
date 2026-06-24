"""Me535 — holeFilling::joinBoundaryLoops branch 6: PATCH_REFINEMENT.

MeshFix `holeFilling::joinBoundaryLoops` Branch 6 (*PATCH_REFINEMENT*) @ line 792:
  'if (refine) refineSelectedHolePatches();'
  — after bridging the two boundary loops, if refine=true the patch is passed
    to refineSelectedHolePatches() to improve triangle quality.

Branch 6 fires at the end of joinBoundaryLoops when the caller requests mesh
refinement of the newly created bridge patch. The hole-fill triangles are marked
as a selected patch and refineSelectedHolePatches() subdivides or improves them
for higher-quality output.

Geometry: two-loop pentagon annulus (5-sided inner hole, 5-sided outer rim).
  Inner pentagon: i0..i4 (inner boundary — 5 edges).
  Outer pentagon: o0..o4 (2x larger, outer boundary — 5 edges).
  10 annulus triangles (2 per side) bridging the two loops.

With refine=true, after the 10 bridge triangles are inserted, Branch 6 fires and
refineSelectedHolePatches() refines the patch. The two distinct boundary loops
(pentagon-shaped) ensure the annular topology required for joinBoundaryLoops.
gv on inner loop (i0), gw on outer loop (o0).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me535",
             title="joinBoundaryLoops_PATCH_REFINEMENT: two-loop pentagon annulus; refine=true triggers refineSelectedHolePatches (Branch 6)",
             defect_class="joinBoundaryLoops_patch_refinement")

import math

# Inner pentagon boundary vertices (unit pentagon).
# angles: 90, 162, 234, 306, 18 degrees (starting top, CCW)
r_in = 1.0
r_out = 2.0
angles = [math.radians(90 + k * 72) for k in range(5)]

i0 = m.vertex(r_in * math.cos(angles[0]), r_in * math.sin(angles[0]), 0.0)   # 0 — inner (gv)
i1 = m.vertex(r_in * math.cos(angles[1]), r_in * math.sin(angles[1]), 0.0)   # 1
i2 = m.vertex(r_in * math.cos(angles[2]), r_in * math.sin(angles[2]), 0.0)   # 2
i3 = m.vertex(r_in * math.cos(angles[3]), r_in * math.sin(angles[3]), 0.0)   # 3
i4 = m.vertex(r_in * math.cos(angles[4]), r_in * math.sin(angles[4]), 0.0)   # 4

# Outer pentagon boundary vertices (2x radius).
o0 = m.vertex(r_out * math.cos(angles[0]), r_out * math.sin(angles[0]), 0.0)  # 5 — outer (gw)
o1 = m.vertex(r_out * math.cos(angles[1]), r_out * math.sin(angles[1]), 0.0)  # 6
o2 = m.vertex(r_out * math.cos(angles[2]), r_out * math.sin(angles[2]), 0.0)  # 7
o3 = m.vertex(r_out * math.cos(angles[3]), r_out * math.sin(angles[3]), 0.0)  # 8
o4 = m.vertex(r_out * math.cos(angles[4]), r_out * math.sin(angles[4]), 0.0)  # 9

# 10 annulus triangles (2 per side of pentagon annulus).
# Side 0: i0-i1 inner, o0-o1 outer.
t0 = m.triangle(o0, i0, i1)   # 0
t1 = m.triangle(o0, i1, o1)   # 1  (corrected winding)
# Side 1: i1-i2 inner, o1-o2 outer.
t2 = m.triangle(o1, i1, i2)   # 2
t3 = m.triangle(o1, i2, o2)   # 3
# Side 2: i2-i3 inner, o2-o3 outer.
t4 = m.triangle(o2, i2, i3)   # 4
t5 = m.triangle(o2, i3, o3)   # 5
# Side 3: i3-i4 inner, o3-o4 outer.
t6 = m.triangle(o3, i3, i4)   # 6
t7 = m.triangle(o3, i4, o4)   # 7
# Side 4: i4-i0 inner, o4-o0 outer.
t8 = m.triangle(o4, i4, i0)   # 8
t9 = m.triangle(o4, i0, o0)   # 9

# Inner boundary edges (5 edges — n=1 each).
m.assert_edge_shared(i0, i1, 1)   # inner boundary
m.assert_edge_shared(i1, i2, 1)   # inner boundary
m.assert_edge_shared(i2, i3, 1)   # inner boundary
m.assert_edge_shared(i3, i4, 1)   # inner boundary
m.assert_edge_shared(i4, i0, 1)   # inner boundary

# Outer boundary edges (5 edges — n=1 each).
m.assert_edge_shared(o0, o1, 1)   # outer boundary
m.assert_edge_shared(o1, o2, 1)   # outer boundary
m.assert_edge_shared(o2, o3, 1)   # outer boundary
m.assert_edge_shared(o3, o4, 1)   # outer boundary
m.assert_edge_shared(o4, o0, 1)   # outer boundary

# Interior bridge edges (10 diagonal edges — n=2 each).
m.assert_edge_shared(o0, i0, 2)
m.assert_edge_shared(o0, i1, 2)
m.assert_edge_shared(o1, i1, 2)
m.assert_edge_shared(o1, i2, 2)
m.assert_edge_shared(o2, i2, 2)
m.assert_edge_shared(o2, i3, 2)
m.assert_edge_shared(o3, i3, 2)
m.assert_edge_shared(o3, i4, 2)
m.assert_edge_shared(o4, i4, 2)
m.assert_edge_shared(o4, i0, 2)

# Two distinct closed boundary loops.
m.assert_hole_boundary([i0, i1, i2, i3, i4])         # inner pentagon (gv=i0)
m.assert_hole_boundary([o0, o4, o3, o2, o1])         # outer pentagon (gw=o0)
