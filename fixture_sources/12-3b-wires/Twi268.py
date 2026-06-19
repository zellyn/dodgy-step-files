"""Twi268 — ShapeAnalysis_Wire.CheckSeam seam-edge classification.

Catalog claim: Seam edge classification; seam flag not detected when edge
traverses a surface's parametric seam discontinuity.

Demonstration: cylindrical surface (periodic in U with period 2π). Build a
wire on the cylinder where one edge runs along the u=0 seam line. The seam
edge should be flagged when it lies on the parametric discontinuity.
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Twi268",
             defect="seam edge classification on periodic cylindrical surface")

# Cylindrical surface, radius 1, axis along Z.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cylinder',#{plc.eid},1.0)")

# Seam edge along u=0 (the line x=1, y=0, z=0..2).
p_seam_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_seam_top = f.cartesian_point((1.0, 0.0, 2.0))
v_bot = f.vertex_point(p_seam_bot)
v_top = f.vertex_point(p_seam_top)
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, 2.0)
seam_line = f.line(p_seam_bot, seam_vec)
seam_edge = f.edge_curve(v_bot, v_top, seam_line)

# Top circle at z=2 (full periodic loop around cylinder, u=0..2π).
p_top_center = f.cartesian_point((0.0, 0.0, 2.0))
plc_top = f.axis2_placement_3d(p_top_center, zdir, xdir)
circle_top = f._emit_raw(f"CIRCLE('top',#{plc_top.eid},1.0)")
top_edge = f.edge_curve(v_top, v_top, circle_top)

# Bottom circle at z=0.
p_bot_center = f.cartesian_point((0.0, 0.0, 0.0))
plc_bot = f.axis2_placement_3d(p_bot_center, zdir, xdir)
circle_bot = f._emit_raw(f"CIRCLE('bot',#{plc_bot.eid},1.0)")
bot_edge = f.edge_curve(v_bot, v_bot, circle_bot)

# Wire: bottom → up the seam → around top → down (seam again, oriented .F.).
loop = f.edge_loop([
    f.oriented_edge(bot_edge, True),
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge, True),
    f.oriented_edge(seam_edge, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
