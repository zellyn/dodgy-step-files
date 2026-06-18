"""N112 — CheckOverlapping with-tolerance-zero.

Catalog claim: "ShapeAnalysis_Edge.CheckOverlapping called with absolute
tolerance 0; algorithm uses internal epsilon but reports as 'no tolerance'."

Demonstration: Two overlapping edges (line1 and line2 overlapping) with
1.0E-8 vertical offset; UNCERTAINTY_MEASURE set to 0.0. CheckOverlapping
should reject them as non-overlapping due to the offset, but the zero
tolerance makes the algorithm behave unexpectedly.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N112",
             defect="CheckOverlapping with absolute tolerance 0 behaves unpredictably")

# Two nearly-overlapping horizontal line edges with small vertical gap
p1_start = f.cartesian_point((0.0, 0.0, 0.0))
p1_end = f.cartesian_point((1.0, 0.0, 0.0))

p2_start = f.cartesian_point((0.0, 1.0e-8, 0.0))  # 1e-8 above p1_start
p2_end = f.cartesian_point((1.0, 1.0e-8, 0.0))    # 1e-8 above p1_end

v1_start = f.vertex_point(p1_start)
v1_end = f.vertex_point(p1_end)
v2_start = f.vertex_point(p2_start)
v2_end = f.vertex_point(p2_end)

# First line (y=0)
line1_dir = f.direction((1.0, 0.0, 0.0))
line1_vec = f.vector(line1_dir, 1.0)
line1 = f.line(p1_start, line1_vec)

# Second line (y=1e-8, parallel offset)
line2_dir = f.direction((1.0, 0.0, 0.0))
line2_vec = f.vector(line2_dir, 1.0)
line2 = f.line(p2_start, line2_vec)

edge1 = f.edge_curve(v1_start, v1_end, line1)
edge2 = f.edge_curve(v2_start, v2_end, line2)

oe1 = f.oriented_edge(edge1, True)
oe2 = f.oriented_edge(edge2, False)  # reversed
loop1 = f.edge_loop([oe1])
loop2 = f.edge_loop([oe2])

# Plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
z_dir = f.direction((0.0, 0.0, 1.0))
x_dir = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(ax_origin, z_dir, x_dir)
plane = f.plane(placement)

face1 = f.advanced_face([f.face_outer_bound(loop1)], plane)
face2 = f.advanced_face([f.face_outer_bound(loop2)], plane)

shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
