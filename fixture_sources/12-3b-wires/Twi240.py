"""Twi240 — FixShifted seam-vertex position mismatch.

Catalog claim: seam edge starts at a position not matching the nominal
wire start point on a periodic/wrapped surface. FixShifted must
reparametrize.

Previous fixture had a flat PLANE — seam semantics require a
periodic surface (cylinder/torus). Regen on a CYLINDRICAL_SURFACE
with an EDGE_LOOP that starts at a shifted position relative to the
canonical wire start.
"""
from math import pi
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Twi240",
             defect="seam edge on cylinder with shifted wire-start position")

# Cylindrical surface.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{plc.eid},1.0)")

# Seam edge along u=0 (the line x=1, y=0, z=0..2).
p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 2.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)
seam_dir = f.direction((0.0, 0.0, 1.0))
seam_vec = f.vector(seam_dir, 2.0)
seam_line = f.line(p_bot, seam_vec)
seam_edge = f.edge_curve(v_bot, v_top, seam_line)

# Top and bottom circles.
top_center = f.cartesian_point((0.0, 0.0, 2.0))
top_plc = f.axis2_placement_3d(top_center, zdir, xdir)
top_circle = f._emit_raw(f"CIRCLE('top',#{top_plc.eid},1.0)")
top_edge = f.edge_curve(v_top, v_top, top_circle)

bot_plc = f.axis2_placement_3d(orig, zdir, xdir)
bot_circle = f._emit_raw(f"CIRCLE('bot',#{bot_plc.eid},1.0)")
bot_edge = f.edge_curve(v_bot, v_bot, bot_circle)

# Shifted wire: start with top_edge instead of bot_edge. Nominal canonical
# ordering would be [bot, seam_up, top, seam_down]; this fixture starts
# the EDGE_LOOP at edge index 2 (top), forcing FixShifted to detect the
# shift and reparametrize the seam-vertex pairing.
loop = f.edge_loop([
    f.oriented_edge(top_edge, True),       # SHIFTED start
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(bot_edge, True),
    f.oriented_edge(seam_edge, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
