"""Gp029 — Period-shift fix on revolved face leaves wire in inconsistent UV band.

Catalog claim (03-occt-tests.md R082, bug26716): After a period-shift pass on a
revolved face's wire, the wire endpoints land in an inconsistent parameter band —
some pcurve endpoints in [0,2π], others in [2π,4π] — even though all should sit
in a single period band. The inconsistency blocks subsequent triangulation, which
expects a single coherent parameter window.

Fixture: A face on a SURFACE_OF_REVOLUTION (full torus-like surface of revolution,
radius 1, revolved line at distance 2 from axis). The outer loop has 4 edges: two
"parallel" arcs at the top and bottom of the revolution profile, and two "meridian"
seam edges at u=0 and u=2pi. The defect: the top arc's pcurve is placed in the
[2π, 4π] band (start at (2π, 1)) while the bottom arc and both seam edges are in
[0, 2π]. This mixed-band state is exactly what a misfiring period-shift pass
produces: one edge landed in the next period band while the rest were left in [0,2π].

The receiver must detect the inconsistent UV band and either refuse the shape or
correct all pcurves to a single period window.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp029",
    defect=(
        "SURFACE_OF_REVOLUTION face: period-shift pass left top-arc pcurve in "
        "[2pi,4pi] band (start u=2pi) while bottom-arc and seam pcurves stay in "
        "[0,2pi] band; inconsistent UV bands block triangulation"
    ),
)

# Surface of revolution: revolve a vertical line segment (at x=2 from axis)
# around the Z axis. The profile goes from (2, 0, 0) to (2, 0, 1) in XZ plane.
# SURFACE_OF_REVOLUTION = swept profile around axis.
# We build it using a LINE as the swept curve.
#
# The surface parametrisation: u = revolution angle [0, 2pi], v = profile param.
# At u=0: point = (2*cos(0), 2*sin(0), v) = (2, 0, v).
# At u=2pi: same physical point (2, 0, v) — one full revolution.

orig_axis = f.cartesian_point((0.0, 0.0, 0.0))
z_axis_dir = f.direction((0.0, 0.0, 1.0))
x_ref_dir  = f.direction((1.0, 0.0, 0.0))
axis_place = f.axis2_placement_3d(orig_axis, z_axis_dir, x_ref_dir)

# Axis of revolution: Z-axis through origin.
axis_line_pt = f.cartesian_point((0.0, 0.0, 0.0))
axis_line_dir = f.direction((0.0, 0.0, 1.0))
axis_line_vec = f.vector(axis_line_dir, 1.0)
revolution_axis_line = f.line(axis_line_pt, axis_line_vec)
revolution_axis = f._emit_raw(
    f"AXIS1_PLACEMENT('rev_axis',#{axis_line_pt.eid},#{axis_line_dir.eid})"
)

# Profile curve: a vertical line at x=2 from z=0 to z=1.
profile_start = f.cartesian_point((2.0, 0.0, 0.0))
profile_dir   = f.direction((0.0, 0.0, 1.0))
profile_vec   = f.vector(profile_dir, 1.0)
profile_line  = f.line(profile_start, profile_vec)

# SURFACE_OF_REVOLUTION
sor = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('sor',#{profile_line.eid},#{revolution_axis.eid})"
)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# 3D vertices at u=0/2pi seam, v=0 and v=1:
#   bot_seam: (2, 0, 0) at u=0 (or 2pi), v=0
#   top_seam: (2, 0, 1) at u=0 (or 2pi), v=1
p_bot = f.cartesian_point((2.0, 0.0, 0.0))
p_top = f.cartesian_point((2.0, 0.0, 1.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

d_up   = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)

# ---- Left seam edge: u=0, from v_bot to v_top ----
# Correct band [0, 2pi]: pcurve LINE at u=0 going upward (v: 0->1)
left_line_3d  = f.line(p_bot, vec_up)
pc_left_start = f.cartesian_point((0.0, 0.0))
pc_left_dir   = f.direction((0.0, 1.0))
pc_left_vec   = f.vector(pc_left_dir, 1.0)
pc_left_line  = f.line(pc_left_start, pc_left_vec)
pc_left_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_seam_u0',(#{pc_left_line.eid}),#{prc.eid})"
)
pcurve_left = f._emit_raw(f"PCURVE('seam_u0',#{sor.eid},#{pc_left_def.eid})")
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_seam',#{left_line_3d.eid},(#{pcurve_left.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_seam',#{v_bot.eid},#{v_top.eid},#{sc_left.eid},.T.)"
)

# ---- Right seam edge: u=2pi, from v_bot to v_top ----
# Correct band [0, 2pi]: pcurve LINE at u=2pi going upward
right_line_3d  = f.line(p_bot, vec_up)  # same 3D line (seam)
pc_right_start = f.cartesian_point((2.0 * math.pi, 0.0))
pc_right_dir   = f.direction((0.0, 1.0))
pc_right_vec   = f.vector(pc_right_dir, 1.0)
pc_right_line  = f.line(pc_right_start, pc_right_vec)
pc_right_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_seam_u2pi',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('seam_u2pi',#{sor.eid},#{pc_right_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_seam',#{right_line_3d.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_seam',#{v_bot.eid},#{v_top.eid},#{sc_right.eid},.T.)"
)

# ---- Bottom arc: full circle at v=0 (z=0), u: 0->2pi ----
# 3D: full circle of radius 2 in z=0 plane.
bot_ctr   = f.cartesian_point((0.0, 0.0, 0.0))
bot_zd    = f.direction((0.0, 0.0, 1.0))
bot_xd    = f.direction((1.0, 0.0, 0.0))
bot_axis  = f.axis2_placement_3d(bot_ctr, bot_zd, bot_xd)
bot_circle = f.circle(bot_axis, 2.0)
# Pcurve: in [0, 2pi] band — correct, start (0, 0), magnitude 2pi in u direction.
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, 2.0 * math.pi)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_arc',#{sor.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bot_circle.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_bot.eid},#{v_bot.eid},#{sc_bot.eid},.T.)"
)

# ---- Top arc: full circle at v=1 (z=1), u: 0->2pi ----
# THE DEFECT: pcurve starts at u=2pi (next period band) instead of u=0.
# A misfiring period-shift pass produced this: start is (2pi, 1) going right
# by 2pi more, so the top arc pcurve covers [2pi, 4pi] in u.
# All other pcurves are in [0, 2pi]. Mixed bands block triangulation.
top_ctr   = f.cartesian_point((0.0, 0.0, 1.0))
top_axis  = f.axis2_placement_3d(top_ctr, bot_zd, bot_xd)
top_circle = f.circle(top_axis, 2.0)
# DEFECT: start at (2pi, 1) — shifted into [2pi, 4pi] band by a misfired period-shift.
pc_top_start = f.cartesian_point((2.0 * math.pi, 1.0))   # DEFECT: should be (0.0, 1.0)
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, 2.0 * math.pi)        # covers [2pi, 4pi] — wrong band
pc_top_line  = f.line(pc_top_start, pc_top_vec)
pc_top_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top_shifted',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_arc_shifted',#{sor.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_circle.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_top.eid},#{v_top.eid},#{sc_top.eid},.T.)"
)

# Loop: bot(fwd) -> right(fwd) -> top(rev) -> left(rev)
# v_bot->v_bot (full circle), v_bot->v_top, v_top->v_top (full circle, rev), v_top->v_bot
loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),   # bot arc: v_bot->v_bot, pcurve [0,2pi]
    f.oriented_edge(edge_right, True),   # right seam: v_bot->v_top, pcurve at u=2pi
    f.oriented_edge(edge_top,   False),  # top arc reversed: v_top->v_top, DEFECT pcurve [2pi,4pi]
    f.oriented_edge(edge_left,  False),  # left seam reversed: v_top->v_bot, pcurve at u=0
])
face = f.advanced_face([f.face_outer_bound(loop)], sor)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
