"""Me022 — SI region with topological hole (non-disk CC, genus branch).

Catalog claim: the SI region is a ring (annular topology) rather than a disk.
Its Euler characteristic (V - E + F) equals 0, not 1 (disk = χ=1). The healer
must detect this via euler_characteristic_of_selection and route to the
complex-topology handler instead of the simple hole-fill path.

Source: CGAL PMP.remove_self_intersections Branch 11 @ line 2264 —
*topology-genus-classification*: whether selected CC is topologically a disk
(chi=1) or has higher genus/holes (chi≠1); routes to complex-topology handler.

Defect carrier: a ring of 6 triangles forming an annular (cylindrical) band.
The ring has two boundary loops (inner and outer), giving χ = V - E + F = 6 - 12 + 6 = 0
(not a disk). An intruding 7th triangle self-intersects the ring, triggering SI
removal. The expansion around the SI region includes the whole ring, whose
non-disk topology forces the complex handler.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(catalog_id="Me022",
             title="SI in annular ring (chi=0 topology): complex-topology handler branch",
             defect_class="self_intersection_ring_topology")

# Triangular inner/outer ring: inner at r=0.5, outer at r=1.5, all at z=0.
n = 3
inner = []
outer = []
for i in range(n):
    angle = 2 * math.pi * i / n
    inner.append(m.vertex(0.5 * math.cos(angle), 0.5 * math.sin(angle), 0.0))
    outer.append(m.vertex(1.5 * math.cos(angle), 1.5 * math.sin(angle), 0.0))

# 6 triangles forming an annular band (2 per sector).
for i in range(n):
    j = (i + 1) % n
    m.triangle(inner[i], outer[i], outer[j])   # lower tri
    m.triangle(inner[i], outer[j], inner[j])   # upper tri

# Intruder: a triangle that pierces tri 0.
# Tri 0 = (inner[0], outer[0], outer[1]) = ((0.5,0,0),(1.5,0,0),(-0.75,1.3,0)).
# Its centroid is at ((0.5+1.5-0.75)/3, 1.3/3, 0) ≈ (0.417, 0.433, 0).
# Place the intruder to pass through this centroid with z straddling 0.
cx = (0.5 + 1.5 - 0.75) / 3
cy = 1.3 / 3
v_up   = m.vertex(cx,       cy,  1.0)   # 6 — above tri 0
v_down = m.vertex(cx,       cy, -1.0)   # 7 — below tri 0
v_side = m.vertex(cx + 1.0, cy,  0.0)  # 8 — in z=0 plane, outside ring

# Tri 6: (v_up, v_down, v_side) — passes through (cx,cy,0) which is inside tri 0.
m.triangle(v_up, v_down, v_side)   # tri 6 — intruder pierces ring at tri 0's centroid

# Assert: intruder (tri 6) self-intersects tri 0 (the first lower sector).
m.assert_triangles_self_intersect(0, 6)

# Assert: one of the ring's shared interior edges is incident on exactly 2 triangles.
m.assert_edge_shared(inner[0], outer[1], 2)
