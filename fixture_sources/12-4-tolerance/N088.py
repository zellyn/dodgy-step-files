"""N088 — Vertex at cone apex zero tolerance.

Catalog claim: "BRepLib.UpdateInnerTolerances samples curve at parameter
points to compute vertex tolerance, but cone apex (singular point) has zero
radius. Computation returns 0.0 tolerance; edge touching apex incorrectly
marked as arbitrarily small tolerance constraint instead of recognizing
degeneracy."

Demonstration: A conical surface with apex at origin, and an edge starting
at the apex (singular point). The vertex at the apex has a very small
computed tolerance (should be 0.0 or degenerate), which triggers validators
expecting non-zero tolerance at non-degenerate vertices.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(catalog_id="N088",
             defect="Vertex at cone apex yields zero tolerance from UpdateInnerTolerances")

# Apex at origin
apex = f.cartesian_point((0.0, 0.0, 0.0))
v_apex = f.vertex_point(apex)

# Point on the cone edge at z=1, radius=0.5 (semi-angle = arctan(0.5/1) ≈ 26.57°)
edge_pt = f.cartesian_point((0.5, 0.0, 1.0))
v_edge = f.vertex_point(edge_pt)

# Cone: apex at origin, axis along Z, semi-angle arctan(0.5)
cone_axis_origin = f.cartesian_point((0.0, 0.0, 0.0))
cone_z_dir = f.direction((0.0, 0.0, 1.0))
cone_x_dir = f.direction((1.0, 0.0, 0.0))
cone_placement = f.axis2_placement_3d(cone_axis_origin, cone_z_dir, cone_x_dir)
semi_angle = math.atan(0.5)  # radians
cone = f.conical_surface(cone_placement, 0.0, semi_angle)  # base radius 0, semi-angle

# Edge from apex to a point on the cone
# Use raw line from apex to edge_pt
line_dir = f.direction((0.5, 0.0, 1.0))
line_mag = math.sqrt(0.5**2 + 1.0**2)  # ~1.118
line_vec = f.vector(line_dir, line_mag)
line = f.line(apex, line_vec)

edge = f.edge_curve(v_apex, v_edge, line)
oe = f.oriented_edge(edge, True)
loop = f.edge_loop([oe])

# Face on the cone
face = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
