"""Tfa171 — ShapeFix_Face.FixLoopWire complex-self-intersection

Catalog claim: "Face with inner wire containing triple-point self-intersection.
FixLoopWire's merge logic handles double-points but not triples, where three
edges meet at a single point. The fixture exercises the pathological case where
self-intersection detection fails and merge creates degenerate sub-faces."

Demonstration: construct a face with an inner wire (hole) where three edges
meet at a single point (triple-point intersection). This is a self-touching
wire where the topology is more complex than a simple double-point (two edges
crossing or touching).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa171",
             defect="Face with inner wire containing triple-point self-intersection")

# Outer boundary: 10×10 square from (0,0,0) to (10,10,0)
p_out_0 = f.cartesian_point((0.0, 0.0, 0.0))
p_out_1 = f.cartesian_point((10.0, 0.0, 0.0))
p_out_2 = f.cartesian_point((10.0, 10.0, 0.0))
p_out_3 = f.cartesian_point((0.0, 10.0, 0.0))

v_out_0 = f.vertex_point(p_out_0)
v_out_1 = f.vertex_point(p_out_1)
v_out_2 = f.vertex_point(p_out_2)
v_out_3 = f.vertex_point(p_out_3)

# Outer loop edges
directions_dist = [
    ((1.0, 0.0, 0.0), (v_out_0, v_out_1), (p_out_0, p_out_1), 10.0),
    ((0.0, 1.0, 0.0), (v_out_1, v_out_2), (p_out_1, p_out_2), 10.0),
    ((-1.0, 0.0, 0.0), (v_out_2, v_out_3), (p_out_2, p_out_3), 10.0),
    ((0.0, -1.0, 0.0), (v_out_3, v_out_0), (p_out_3, p_out_0), 10.0),
]

edges_out = []
for (dx, dy, dz), (va, vb), (pa, pb), dist in directions_dist:
    d = f.direction((dx, dy, dz))
    vec = f.vector(d, dist)
    line = f.line(pa, vec)
    edges_out.append(f.edge_curve(va, vb, line))

loop_out = f.edge_loop([f.oriented_edge(e) for e in edges_out])

# Inner wire (hole) with triple-point self-intersection.
# The wire forms a shape like a triangle, but one vertex is a "triple point"
# where three edges meet.
#
# Topology:
#   P0 (2, 2, 0) --(edge1)-- P1 (4, 2, 0)
#   P1 (4, 2, 0) --(edge2)-- P2 (4, 4, 0)  [P2 is the triple point]
#   P2 (4, 4, 0) --(edge3)-- P3 (3, 3, 0)  [back toward center]
#   P3 (3, 3, 0) --(edge4)-- P2 (4, 4, 0)  [back to triple point again!]
#   P2 (4, 4, 0) --(edge5)-- P0 (2, 2, 0)  [closing the loop]
#
# This creates a self-intersecting polygon where vertex P2 is visited by
# three edges (edge2 end, edge3 start, edge4 end, edge5 start).

p_in_0 = f.cartesian_point((2.0, 2.0, 0.0))
p_in_1 = f.cartesian_point((4.0, 2.0, 0.0))
p_in_2 = f.cartesian_point((4.0, 4.0, 0.0))  # Triple point
p_in_3 = f.cartesian_point((3.0, 3.0, 0.0))

v_in_0 = f.vertex_point(p_in_0)
v_in_1 = f.vertex_point(p_in_1)
v_in_2 = f.vertex_point(p_in_2)
v_in_3 = f.vertex_point(p_in_3)

# Build 5 edges for the self-intersecting loop
# Edge 1: P0 -> P1
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 2.0)
line = f.line(p_in_0, vec)
e_in_1 = f.edge_curve(v_in_0, v_in_1, line)

# Edge 2: P1 -> P2
d = f.direction((0.0, 1.0, 0.0))
vec = f.vector(d, 2.0)
line = f.line(p_in_1, vec)
e_in_2 = f.edge_curve(v_in_1, v_in_2, line)

# Edge 3: P2 -> P3
d = f.direction((-0.707, -0.707, 0.0))  # diagonal down-left
vec = f.vector(d, 1.414)
line = f.line(p_in_2, vec)
e_in_3 = f.edge_curve(v_in_2, v_in_3, line)

# Edge 4: P3 -> P2 (back to triple point)
d = f.direction((0.707, 0.707, 0.0))  # diagonal up-right
vec = f.vector(d, 1.414)
line = f.line(p_in_3, vec)
e_in_4 = f.edge_curve(v_in_3, v_in_2, line)

# Edge 5: P2 -> P0 (close the loop)
d = f.direction((-0.707, -0.707, 0.0))
vec = f.vector(d, 2.828)  # sqrt(2^2 + 2^2)
line = f.line(p_in_2, vec)
e_in_5 = f.edge_curve(v_in_2, v_in_0, line)

loop_in = f.edge_loop([
    f.oriented_edge(e_in_1),
    f.oriented_edge(e_in_2),
    f.oriented_edge(e_in_3),
    f.oriented_edge(e_in_4),
    f.oriented_edge(e_in_5),
])

# Create plane and face
ax_origin = f.cartesian_point((5.0, 5.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

# Face with outer bound and one inner bound (the self-intersecting hole)
face = f.advanced_face([
    f.face_outer_bound(loop_out),
    f.face_bound(loop_in),  # Inner bound with triple-point self-intersection
], plane)

# Wrap in shell and surface model
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
