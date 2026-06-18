"""Tsh036 — Revolved shape imported with complementary (reversed) angle.

Catalog claim: "A revolved shape comes out with the complementary (reversed)
angular sweep. Visible in standard XDE display. Axis orientation is misinterpreted."

Demonstration: Build a SURFACE_OF_REVOLUTION with a profile arc and axis
positioned such that the angular sweep direction is ambiguous or easily inverted.
The revolved face should display with the wrong sweep angle.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh036",
             defect="Revolved surface imported with complementary (reversed) angle")

# Build a simple revolved surface: revolve a line profile around an axis.
# The profile is a vertical line segment from (1,0,0) to (1,0,1).
# The axis is the Z-axis at origin.
# Revolution should sweep from 0 to 360 degrees, but may be read as 0 to -360.

# Profile points: vertical line segment
p_profile_base = f.cartesian_point((1.0, 0.0, 0.0))
p_profile_top = f.cartesian_point((1.0, 0.0, 1.0))

v_profile_base = f.vertex_point(p_profile_base)
v_profile_top = f.vertex_point(p_profile_top)

# Profile edge (straight vertical line)
d = f.direction((0.0, 0.0, 1.0)); vec = f.vector(d, 1.0); ln = f.line(p_profile_base, vec)
profile_edge = f.edge_curve(v_profile_base, v_profile_top, ln)

# Profile loop (single edge)
profile_loop = f.edge_loop([f.oriented_edge(profile_edge, True)])

# Axis of revolution: Z-axis at origin
axis_origin = f.cartesian_point((0.0, 0.0, 0.0))
axis_dir = f.direction((0.0, 0.0, 1.0))
axis_ref = f.direction((1.0, 0.0, 0.0))
axis_plc = f.axis2_placement_3d(axis_origin, axis_dir, axis_ref)

# SURFACE_OF_REVOLUTION with profile and axis
# The axis direction is Z+ but the profile is at radius 1 in the XY plane.
# Ambiguity: rotation could be read as +360 or -360 degrees.
# Use raw emit since SURFACE_OF_REVOLUTION is not in the basic builder
revolved_surface = f._emit("SURFACE_OF_REVOLUTION", profile_loop, axis_plc)

# Face on the revolved surface
face = f.advanced_face([f.face_outer_bound(profile_loop)], revolved_surface)

# Open shell containing the revolved face
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
