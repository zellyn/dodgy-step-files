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

# Common direction. Two VECTORs of different magnitudes ⇒ different
# parameterization speeds on the same 3D geometry.
line_dir = f.direction((1.0, 0.0, 0.0))
vec_slow = f.vector(line_dir, 1.0)   # speed 1 unit per param
vec_fast = f.vector(line_dir, 2.0)   # speed 2 units per param — 2x faster

# First edge: line at speed 1.0; param range covers [0, 1] for unit segment.
line1 = f.line(p_start, vec_slow)
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)
edge1 = f.edge_curve(v_start, v_end, line1)

# Second edge: line at speed 2.0; param range covers [0, 0.5] for the same
# unit segment. CheckOverlapping comparing raw params would see {0..1} vs
# {0..0.5} on identical 3D and (without normalization) declare no overlap.
line2 = f.line(p_start, vec_fast)
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
