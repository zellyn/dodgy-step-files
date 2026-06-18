"""N113 — UpdateEdgeTol with-coincident-vertices.

Catalog claim: "BRepLib.UpdateEdgeTol on edge with start and end vertices
coincident (degenerate); divides by edge length producing inf tolerance."

Demonstration: Degenerate edge where both vertices reference the same point
(#1); edge length is zero. UpdateEdgeTol attempts to compute tolerance by
dividing by edge length, yielding infinity.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N113",
             defect="UpdateEdgeTol on degenerate edge (zero length) produces inf tolerance")

# Single point for both start and end vertices
degenerate_pt = f.cartesian_point((0.5, 0.5, 0.0))
v_degenerate = f.vertex_point(degenerate_pt)

# Line curve with zero magnitude (degenerate curve)
line_dir = f.direction((0.0, 0.0, 1.0))
line_vec = f.vector(line_dir, 0.0)  # zero-magnitude vector
line = f.line(degenerate_pt, line_vec)

# Edge from the point to itself
edge = f.edge_curve(v_degenerate, v_degenerate, line)

# Wrap in a minimal loop
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
