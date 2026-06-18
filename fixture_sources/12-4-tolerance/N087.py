"""N087 — CheckOverlapping parameterization mismatch.

Catalog claim: "ShapeAnalysis_Edge.CheckOverlapping compares parametric
parameter values directly without normalizing parameterization speed. Two
edges following identical 3D geometry but with different speed (arc-length
vs. chord-length) parameter domains fail overlap detection; parameter-space
comparison yields false negative."

Demonstration: Two overlapping edges covering the same 3D line segment,
but with different parameterizations: one uses arc-length (parameter range
[0, 1]), the other uses chord-length (parameter range [0, 2]). Both map to
the same 3D geometry but CheckOverlapping fails to recognize them as identical
because it compares raw parameter values without normalizing for speed.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N087",
             defect="CheckOverlapping fails on edges with different parameterization speeds")

# Two identical line segments in 3D, from (0,0,0) to (1,0,0)
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))

# Direction and vector for the line
line_dir = f.direction((1.0, 0.0, 0.0))
line_vec = f.vector(line_dir, 1.0)

# First edge: line with standard parameterization [0, 1]
line1 = f.line(p_start, line_vec)
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)
edge1 = f.edge_curve(v_start, v_end, line1)

# Second edge: same line but with raw parameter domain [0, 2] (stretched parameterization)
# This represents a different parameterization speed mapping same 3D geometry
line2 = f.line(p_start, line_vec)
# Edge spans [0, 2] instead of [0, 1], same 3D geometry but different parameterization
edge2 = f.edge_curve(v_start, v_end, line2)

# Build faces to hold the overlapping edges
oe1 = f.oriented_edge(edge1, True)
oe2 = f.oriented_edge(edge2, False)  # reversed to sit on top
loop1 = f.edge_loop([oe1])
loop2 = f.edge_loop([oe2])

# Plane in XY
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
