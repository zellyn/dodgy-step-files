"""Me1130 — SI in open mesh with hole (chi != 1 topology): complex-topology handler.

Catalog claim: the SI region spans an open strip with a topological hole —
two boundary loops instead of one — giving Euler characteristic chi = V - E + F = 0
(not 1; not a disk). CGAL's remove_self_intersections calls
euler_characteristic_of_selection on the face selection around the SI and
detects chi != 1, routing to handle_CC_with_complex_topology rather than the
simple disk hole-fill path.

Source: CGAL PMP.remove_self_intersections Branch 11 @ line 2264 —
*topology-genus-classification*: whether selected CC is topologically a disk
(chi=1) or has higher genus/holes (chi != 1); routes to complex-topology handler.

Defect carrier: an annular strip of 8 triangles (4 sectors x 2 triangles each)
forming a band with inner boundary (r=0.5) and outer boundary (r=1.5). The strip
has two distinct boundary loops, making chi = V - E + F = 8 - 16 + 8 = 0. An
intruder triangle pierces one sector of the strip, triggering SI detection. The
expansion around the SI region includes the full annular strip, whose non-disk
topology (chi=0) forces the complex-topology handler branch.
"""
from step_corpus.mesh_builder import MeshFile
import math

m = MeshFile(catalog_id="Me1130",
             title="SI in annular strip (chi=0): euler_characteristic != 1 complex-topology branch",
             defect_class="self_intersection_ring_topology")

# 4-sector annular strip: inner at r=0.5, outer at r=1.5, all at z=0.
n = 4
inner = []
outer = []
for i in range(n):
    angle = 2 * math.pi * i / n
    inner.append(m.vertex(0.5 * math.cos(angle), 0.5 * math.sin(angle), 0.0))
    outer.append(m.vertex(1.5 * math.cos(angle), 1.5 * math.sin(angle), 0.0))

# 8 triangles forming the annular band (2 per sector).
for i in range(n):
    j = (i + 1) % n
    m.triangle(inner[i], outer[i], outer[j])   # lower tri of sector i
    m.triangle(inner[i], outer[j], inner[j])   # upper tri of sector i

# Intruder: a triangle that pierces sector 0.
# Sector 0 lower = (inner[0], outer[0], outer[1])
#   inner[0] = (0.5, 0, 0), outer[0] = (1.5, 0, 0), outer[1] = (0, 1.5, 0)
# Centroid of sector 0 lower tri ≈ (0.667, 0.5, 0)
cx = (0.5 + 1.5 + 0.0) / 3
cy = (0.0 + 0.0 + 1.5) / 3
v_up   = m.vertex(cx,       cy,  1.0)   # above sector 0
v_down = m.vertex(cx,       cy, -1.0)   # below sector 0
v_side = m.vertex(cx + 1.2, cy,  0.0)  # in z=0 plane, outside strip

# Intruder triangle passes through centroid of sector 0 lower tri.
m.triangle(v_up, v_down, v_side)   # tri 8 — intruder pierces strip at sector 0

# Assert: intruder (tri 8) self-intersects tri 0 (sector 0 lower).
m.assert_triangles_self_intersect(0, 8)

# Assert: an interior edge of the strip is shared by exactly 2 triangles.
m.assert_edge_shared(inner[0], outer[1], 2)
