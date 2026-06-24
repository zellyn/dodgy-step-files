"""Me531 — holeFilling::joinBoundaryLoops branch 2: SAME_BOUNDARY_LOOP_NOJUSTCONNECT.

MeshFix `holeFilling::joinBoundaryLoops` Branch 2 (*SAME_BOUNDARY_LOOP_NOJUSTCONNECT*) @ line 737:
  'if (v == gw) return NULL'
  — gw is reachable from gv on the same boundary loop; with justconnect=false,
    return NULL (cannot bridge same loop).

Branch 2 fires when the algorithm walks from gv along the boundary and reaches gw
before exhausting the loop. Both gv and gw lie on one single boundary loop (a
single-boundary open disk). The method detects same-loop membership and returns
NULL since bridging would collapse the only hole.

Geometry: an open disk with a single hexagonal boundary loop.
Six triangles (fan from center) with 6 boundary edges forming one closed loop.
  c=(0,0,0) center; p0..p5 around the perimeter (hex ring).

Picking any two non-adjacent boundary vertices (e.g. p0 and p3) as gv/gw:
gv=p0 is boundary; walking the single loop reaches p3 → Branch 2 fires.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me531",
             title="joinBoundaryLoops_SAME_BOUNDARY_LOOP_NOJUSTCONNECT: gv and gw on same loop; Branch 2 returns NULL",
             defect_class="joinBoundaryLoops_same_boundary_loop")

import math

# Center vertex.
c = m.vertex(0.0, 0.0, 0.0)   # 0

# Six perimeter vertices (regular hexagon, unit radius).
p0 = m.vertex(1.0,  0.0,  0.0)    # 1
p1 = m.vertex(0.5,  0.866, 0.0)   # 2
p2 = m.vertex(-0.5, 0.866, 0.0)   # 3
p3 = m.vertex(-1.0, 0.0,  0.0)    # 4
p4 = m.vertex(-0.5, -0.866, 0.0)  # 5
p5 = m.vertex(0.5,  -0.866, 0.0)  # 6

# Six fan triangles from center.
t0 = m.triangle(c, p0, p1)   # 0
t1 = m.triangle(c, p1, p2)   # 1
t2 = m.triangle(c, p2, p3)   # 2
t3 = m.triangle(c, p3, p4)   # 3
t4 = m.triangle(c, p4, p5)   # 4
t5 = m.triangle(c, p5, p0)   # 5

# Six boundary edges (perimeter — each shared by exactly 1 triangle).
m.assert_edge_shared(p0, p1, 1)   # boundary
m.assert_edge_shared(p1, p2, 1)   # boundary
m.assert_edge_shared(p2, p3, 1)   # boundary
m.assert_edge_shared(p3, p4, 1)   # boundary
m.assert_edge_shared(p4, p5, 1)   # boundary
m.assert_edge_shared(p5, p0, 1)   # boundary

# Six interior edges (spoke — each shared by 2 triangles).
m.assert_edge_shared(c, p0, 2)
m.assert_edge_shared(c, p1, 2)
m.assert_edge_shared(c, p2, 2)
m.assert_edge_shared(c, p3, 2)
m.assert_edge_shared(c, p4, 2)
m.assert_edge_shared(c, p5, 2)

# Single boundary loop — all six perimeter vertices on one loop.
# p0 and p3 are on the same loop (distance 3 apart) — walking from p0 reaches p3.
m.assert_hole_boundary([p0, p1, p2, p3, p4, p5])

# Euler: V=7, E=12, F=6, chi=1 (open disk).
m.assert_euler_characteristic(7, 12, 6, 1)
