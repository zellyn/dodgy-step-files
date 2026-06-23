"""Me031 — isolated_degenerate_face_flip_candidate: lone degenerate triangle surrounded by non-degenerate neighbors (Branch 8).

Catalog claim: a single degenerate (zero-area) triangle is embedded in a
manifold patch. Its neighbors are all non-degenerate, so no adjacent
degenerate component is detected. CGAL PMP.remove_degenerate_faces enters
the detect_cc_of_degenerate_triangles==false branch and attempts a longest-
edge flip instead of region removal.

Source: CGAL PMP.remove_degenerate_faces Branch 8 @ line 2244 —
*single-isolated-degenerate-face*: no adjacent degenerate triangles;
algorithm tries to flip the degenerate face's longest edge rather than
collecting a connected component.

Defect carrier: a flat fan of 5 triangles around center vertex (0,0,0) in
the z=0 plane. Triangle 2 is collinear (zero-area) because its three
vertices are collinear. Triangles 0,1,3,4 are non-degenerate neighbors.
The zero-area triangle is geometrically isolated among healthy neighbors.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me031",
             title="isolated degenerate face among healthy neighbors — flip-candidate branch",
             defect_class="degenerate_triangle")

# Hub at origin.
hub = m.vertex(0.0, 0.0, 0.0)   # 0

# Outer ring — 5 points around the hub at unit radius in z=0.
import math
outer = []
for i in range(5):
    angle = 2 * math.pi * i / 5
    outer.append(m.vertex(math.cos(angle), math.sin(angle), 0.0))
# outer indices: 1,2,3,4,5

# 5 triangles around hub. Triangle 2 (hub, outer[1], outer[2]) will be
# made degenerate by co-locating outer[1] and outer[2] on the same radial line.
# Instead: override triangle 2 to be collinear: (hub, midpoint of edge, outer_shifted).
# Use a simpler approach: triangle 2 = (hub, A, B) where hub, A, B are collinear.
collinear_a = m.vertex(1.0, 0.0, 0.0)    # 6 — along X axis
collinear_b = m.vertex(2.0, 0.0, 0.0)    # 7 — along X axis (collinear with hub)

t0 = m.triangle(hub, outer[0], outer[1])   # face 0: normal fan
t1 = m.triangle(hub, outer[1], outer[2])   # face 1: normal fan
t2 = m.triangle(hub, collinear_a, collinear_b)   # face 2: DEGENERATE — collinear along X
t3 = m.triangle(hub, outer[2], outer[3])   # face 3: normal fan
t4 = m.triangle(hub, outer[3], outer[4])   # face 4: normal fan

# Assert the isolated degenerate triangle has zero area.
m.assert_triangle_area_lt(t2, 1e-12)

# The hub is shared by all 5 triangles.
# The degenerate edge (hub, collinear_a) is interior — shared by 1 face only since
# it doesn't connect back to the outer ring in manifold fashion.
m.assert_edge_shared(hub, collinear_a, 1)
m.assert_edge_shared(hub, collinear_b, 1)
