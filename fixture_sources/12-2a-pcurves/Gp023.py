"""Gp023 - Point-projection onto trimmed periodic CYLINDRICAL_SURFACE returns
UV outside trimmed band (pcurve start parameter shifted by period).

Catalog claim: A face on a CYLINDRICAL_SURFACE is trimmed to U in [pi,2pi].
The pcurve LINE for an edge traversing that band starts at u=0 in UV (shifted
back by one period of pi) instead of the correct u=pi. When a kernel projects
a 3D point above the trimmed face band [pi,2pi] using ValueOfUV, it returns
U~=0 (wrong period) instead of U~=pi (inside the face band), because the
pcurve anchors at u=0.

Fixture: A half-cylinder face covering U in [pi,2pi], V in [0,1]. The outer
loop has four edges: two vertical seam lines at u=pi and u=2pi, and two
horizontal full-circles at v=0 and v=1 (vertices define the trim). The defect
is on the left vertical seam edge at u=pi: its pcurve LINE starts at (0, 0) in
UV - shifted by one period (minus pi) from the correct (pi, 0).
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp023",
    defect=(
        "Trimmed cylinder face U in [pi,2pi]: left seam edge pcurve LINE starts "
        "at u=0 (shifted by -pi from correct u=pi); point-projection returns UV "
        "outside the [pi,2pi] trimmed band"
    ),
)

# Cylindrical surface: radius 1, axis Z.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cyl  = f.cylindrical_surface(plc, 1.0)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices at the two seam edges:
#   left  seam: u=pi   -> 3D = (-1, 0, *)
#   right seam: u=2pi  -> 3D = ( 1, 0, *)
p_left_bot  = f.cartesian_point((-1.0, 0.0, 0.0))
p_right_bot = f.cartesian_point(( 1.0, 0.0, 0.0))
p_left_top  = f.cartesian_point((-1.0, 0.0, 1.0))
p_right_top = f.cartesian_point(( 1.0, 0.0, 1.0))
v_lb = f.vertex_point(p_left_bot)
v_rb = f.vertex_point(p_right_bot)
v_lt = f.vertex_point(p_left_top)
v_rt = f.vertex_point(p_right_top)

# Up direction
d_up   = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)

# ---- Left seam edge: 3D line from (-1,0,0) to (-1,0,1) at u=pi. ----
# THE DEFECT: pcurve LINE starts at (0, 0) instead of (pi, 0).
left_line_3d  = f.line(p_left_bot, vec_up)
pc_left_start = f.cartesian_point((0.0, 0.0))    # DEFECT: should be (math.pi, 0.0)
pc_left_dir   = f.direction((0.0, 1.0))
pc_left_vec   = f.vector(pc_left_dir, 1.0)
pc_left_line  = f.line(pc_left_start, pc_left_vec)
pc_left_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left_shifted',(#{pc_left_line.eid}),#{prc.eid})"
)
pcurve_left = f._emit_raw(
    f"PCURVE('left_period_shifted',#{cyl.eid},#{pc_left_def.eid})"
)
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_seam',#{left_line_3d.eid},(#{pcurve_left.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_seam',#{v_lb.eid},#{v_lt.eid},#{sc_left.eid},.T.)"
)

# ---- Right seam edge: 3D line from (1,0,0) to (1,0,1) at u=2pi. ----
# Pcurve is correct here (defect is only on left).
right_line_3d  = f.line(p_right_bot, vec_up)
pc_right_start = f.cartesian_point((2.0 * math.pi, 0.0))
pc_right_dir   = f.direction((0.0, 1.0))
pc_right_vec   = f.vector(pc_right_dir, 1.0)
pc_right_line  = f.line(pc_right_start, pc_right_vec)
pc_right_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(
    f"PCURVE('right_seam',#{cyl.eid},#{pc_right_def.eid})"
)
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_seam',#{right_line_3d.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_seam',#{v_rb.eid},#{v_rt.eid},#{sc_right.eid},.T.)"
)

# ---- Bottom arc: half-circle from (-1,0,0) to (1,0,0) at z=0, u: pi->2pi. ----
# Use a full CIRCLE; the EDGE_CURVE start/end vertices define the trim implicitly.
bot_ctr   = f.cartesian_point((0.0, 0.0, 0.0))
bot_zaxis = f.direction((0.0, 0.0, 1.0))
bot_xaxis = f.direction((1.0, 0.0, 0.0))
bot_axis  = f.axis2_placement_3d(bot_ctr, bot_zaxis, bot_xaxis)
bot_circle_3d = f.circle(bot_axis, 1.0)
# Pcurve: in UV from (pi,0) going right to (2pi,0).
pc_bot_start = f.cartesian_point((math.pi, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, math.pi)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_arc',#{cyl.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bot_circle_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_lb.eid},#{v_rb.eid},#{sc_bot.eid},.T.)"
)

# ---- Top arc: half-circle from (-1,0,1) to (1,0,1) at z=1. ----
top_ctr   = f.cartesian_point((0.0, 0.0, 1.0))
top_axis  = f.axis2_placement_3d(top_ctr, bot_zaxis, bot_xaxis)
top_circle_3d = f.circle(top_axis, 1.0)
pc_top_start = f.cartesian_point((math.pi, 1.0))
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, math.pi)
pc_top_line  = f.line(pc_top_start, pc_top_vec)
pc_top_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_arc',#{cyl.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_circle_3d.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_lt.eid},#{v_rt.eid},#{sc_top.eid},.T.)"
)

# Loop: bot(fwd) -> right(fwd) -> top(rev) -> left(rev)
# Traversal: v_lb->v_rb, v_rb->v_rt, v_rt->v_lt (top rev), v_lt->v_lb (left rev)
loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),
    f.oriented_edge(edge_right, True),
    f.oriented_edge(edge_top,   False),
    f.oriented_edge(edge_left,  False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
