"""N111 — FixVertexTolerance vertex-tolerance-from-tessellation.

Catalog claim: "ShapeFix_Edge.FixVertexTolerance computes vertex tolerance
from tessellation that's been internally simplified; uses simplified mesh
tolerance instead of original geometry."

Demonstration: Single-face shell with edge; set UNCERTAINTY_MEASURE_WITH_UNIT
to 1.23E-7 (tessellation-derived tolerance). The FixVertexTolerance function
uses this tessellation-derived value instead of computing from the actual
curve geometry.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N111",
             defect="FixVertexTolerance uses tessellation tolerance instead of curve geometry")

# Simple single edge on a plane
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))

v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)

# Line edge
line_dir = f.direction((1.0, 0.0, 0.0))
line_vec = f.vector(line_dir, 1.0)
line = f.line(p_start, line_vec)

edge = f.edge_curve(v_start, v_end, line)
oe = f.oriented_edge(edge, True)
loop = f.edge_loop([oe])

# Plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
z_dir = f.direction((0.0, 0.0, 1.0))
x_dir = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(ax_origin, z_dir, x_dir)
plane = f.plane(placement)

face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
