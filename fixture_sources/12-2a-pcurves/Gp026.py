"""Gp026 - EDGE_LOOP contour not closed in UV (Jordan-curve violation across
periodic-surface seam).

Catalog claim: A face on a CYLINDRICAL_SURFACE has an outer EDGE_LOOP whose
pcurve images do not form a closed contour in UV. The wire is closed in 3D
but open in UV because the seam edge is omitted - the wire jumps from u~=2pi
on one side to u~=0 on the other with no edge to bridge the gap.

Fixture: A full-cylinder face (U 0->2pi, V 0->1) with three edges: a bottom
full circle arc (u: 0->2pi at v=0), a left seam (v: 0->1 at u=0), and a top
full circle reversed (u: 2pi->0 at v=1). The right seam edge at u=2pi is
OMITTED. In 3D the loop is closed (all vertices are the same 3D point (1,0,*)).
In UV the contour is open: bot_arc ends at (2pi,0), but seam starts at (0,0)
- a gap of 2pi at the bottom; similarly top_arc reversed ends at (0,1) and
seam ends at (0,1) so those coincide but bot_arc->seam is an open jump.
The Jordan-curve condition fails.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp026",
    defect=(
        "Full-cylinder face outer loop missing right seam edge at u=2pi: "
        "UV contour open with gap 2pi at bottom-right, Jordan-curve violated; "
        "loop closed in 3D only"
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

# Seam vertex: on a full periodic cylinder u=0 and u=2pi coincide in 3D.
p_seam_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_seam_top = f.cartesian_point((1.0, 0.0, 1.0))
v_bot = f.vertex_point(p_seam_bot)
v_top = f.vertex_point(p_seam_top)

# ---- Bottom arc: full circle at v=0, u: 0->2pi ----
bot_ctr   = f.cartesian_point((0.0, 0.0, 0.0))
bot_zaxis = f.direction((0.0, 0.0, 1.0))
bot_xaxis = f.direction((1.0, 0.0, 0.0))
bot_axis  = f.axis2_placement_3d(bot_ctr, bot_zaxis, bot_xaxis)
bot_circle_3d = f.circle(bot_axis, 1.0)
# Pcurve: from (0,0) to (2pi,0) in UV.
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, 2.0 * math.pi)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_arc',#{cyl.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bot_circle_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
# Full-circle edge: start==end vertex (the seam vertex at (1,0,0))
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_bot.eid},#{v_bot.eid},#{sc_bot.eid},.T.)"
)

# ---- Left seam edge: vertical line at u=0 from (1,0,0) to (1,0,1) ----
d_up     = f.direction((0.0, 0.0, 1.0))
vec_up   = f.vector(d_up, 1.0)
seam_line_3d  = f.line(p_seam_bot, vec_up)
pc_seam_start = f.cartesian_point((0.0, 0.0))
pc_seam_dir   = f.direction((0.0, 1.0))
pc_seam_vec   = f.vector(pc_seam_dir, 1.0)
pc_seam_line  = f.line(pc_seam_start, pc_seam_vec)
pc_seam_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_seam',(#{pc_seam_line.eid}),#{prc.eid})"
)
pcurve_seam = f._emit_raw(f"PCURVE('seam',#{cyl.eid},#{pc_seam_def.eid})")
sc_seam = f._emit_raw(
    f"SURFACE_CURVE('seam',#{seam_line_3d.eid},(#{pcurve_seam.eid}),.PCURVE_S1.)"
)
edge_seam = f._emit_raw(
    f"EDGE_CURVE('seam',#{v_bot.eid},#{v_top.eid},#{sc_seam.eid},.T.)"
)

# ---- Top arc: full circle at v=1, used reversed in loop (2pi->0) ----
top_ctr   = f.cartesian_point((0.0, 0.0, 1.0))
top_axis  = f.axis2_placement_3d(top_ctr, bot_zaxis, bot_xaxis)
top_circle_3d = f.circle(top_axis, 1.0)
# Pcurve forward direction: (0,1) to (2pi,1).
pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, 2.0 * math.pi)
pc_top_line  = f.line(pc_top_start, pc_top_vec)
pc_top_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_arc',#{cyl.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_circle_3d.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_top.eid},#{v_top.eid},#{sc_top.eid},.T.)"
)

# THE DEFECT: outer loop has only THREE edges (missing right seam at u=2pi).
# In 3D: bot_arc starts/ends at v_bot; seam goes v_bot->v_top; top_arc
# starts/ends at v_top. The loop IS closed in 3D (all full circles return to
# start, seam connects bot to top).
# In UV:
#   bot_arc (fwd): (0,0) -> (2pi,0)
#   seam (fwd):    (0,0) -> (0,1)    [jumps back from 2pi,0 to 0,0 -- OPEN GAP]
#   top_arc (rev): (2pi,1) -> (0,1)  [connects to seam end at (0,1) -- ok]
# Missing: right seam edge (2pi,0)->(2pi,1) to close the UV contour.
loop = f.edge_loop([
    f.oriented_edge(edge_bot,  True),   # (0,0)->(2pi,0) in UV
    f.oriented_edge(edge_seam, True),   # (0,0)->(0,1) in UV [UV gap before this]
    f.oriented_edge(edge_top,  False),  # (2pi,1)->(0,1) in UV reversed
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
