"""Gp035 — Edge has 3D curve but no pcurve, requiring projection onto host surface.

Catalog defect: A vertical EDGE_CURVE on a CYLINDRICAL_SURFACE carries only
a 3D LINE representation — no SURFACE_CURVE / PCURVE. The kernel must project
the 3D curve into UV (synthesizing a 2D analytic line) or reject the shape.
OCC silently accepts without doing either, which is outside the allowed set.

Fixture: A half-cylinder face (u in [0,pi], v in [0,1]) whose left seam edge
is a bare EDGE_CURVE with a raw LINE3D as its curve attribute — no
SURFACE_CURVE wrapper, no PCURVE. The three other edges are correct
SURFACE_CURVEs so the face is well-formed except for that one missing pcurve.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp035",
    defect=(
        "Left seam EDGE_CURVE on CYLINDRICAL_SURFACE has only a bare 3D LINE as "
        "its curve attribute — no SURFACE_CURVE wrapper and no PCURVE; kernel must "
        "project to synthesize the missing 2D analytic line or reject the edge"
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

# 3D vertices:
#   A = (1, 0, 0)  at u=0,  v=0
#   B = (-1, 0, 0) at u=pi, v=0
#   A_top = (1, 0, 1)  at u=0,  v=1
#   B_top = (-1, 0, 1) at u=pi, v=1
p_a     = f.cartesian_point(( 1.0,  0.0, 0.0))
p_b     = f.cartesian_point((-1.0,  0.0, 0.0))
p_a_top = f.cartesian_point(( 1.0,  0.0, 1.0))
p_b_top = f.cartesian_point((-1.0,  0.0, 1.0))
v_a     = f.vertex_point(p_a)
v_b     = f.vertex_point(p_b)
v_a_top = f.vertex_point(p_a_top)
v_b_top = f.vertex_point(p_b_top)

d_up   = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)

# ---- THE DEFECT: left seam edge — bare 3D LINE, no SURFACE_CURVE/PCURVE ----
# Correct encoding would be SURFACE_CURVE with a PCURVE inside.
# Here the EDGE_CURVE references the raw LINE entity directly.
left_line_3d = f.line(p_a, vec_up)
# No SURFACE_CURVE wrapping — the LINE is used directly as the edge curve.
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_no_pcurve',#{v_a.eid},#{v_a_top.eid},#{left_line_3d.eid},.T.)"
)

# ---- Right seam at u=pi: correct SURFACE_CURVE with PCURVE ----
right_line_3d  = f.line(p_b, vec_up)
pc_right_start = f.cartesian_point((math.pi, 0.0))
pc_right_dir   = f.direction((0.0, 1.0))
pc_right_vec   = f.vector(pc_right_dir, 1.0)
pc_right_line  = f.line(pc_right_start, pc_right_vec)
pc_right_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_right',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('right_seam',#{cyl.eid},#{pc_right_def.eid})")
sc_right = f._emit_raw(
    f"SURFACE_CURVE('right_seam',#{right_line_3d.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
edge_right = f._emit_raw(
    f"EDGE_CURVE('right_seam',#{v_b.eid},#{v_b_top.eid},#{sc_right.eid},.T.)"
)

# ---- Bottom arc: half-circle from A to B at z=0, u: 0->pi ----
arc_ctr   = f.cartesian_point((0.0, 0.0, 0.0))
arc_zaxis = f.direction((0.0, 0.0, 1.0))
arc_xaxis = f.direction((1.0, 0.0, 0.0))
arc_axis  = f.axis2_placement_3d(arc_ctr, arc_zaxis, arc_xaxis)
circle_bot_3d = f.circle(arc_axis, 1.0)
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, math.pi)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_arc',#{cyl.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{circle_bot_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# ---- Top arc: half-circle from A_top to B_top at z=1 ----
top_ctr  = f.cartesian_point((0.0, 0.0, 1.0))
top_axis = f.axis2_placement_3d(top_ctr, arc_zaxis, arc_xaxis)
circle_top_3d = f.circle(top_axis, 1.0)
pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, math.pi)
pc_top_line  = f.line(pc_top_start, pc_top_vec)
pc_top_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_arc',#{cyl.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{circle_top_3d.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_a_top.eid},#{v_b_top.eid},#{sc_top.eid},.T.)"
)

# Loop: bot_arc(fwd) -> right(fwd) -> top(rev) -> left(rev)
# v_a -> v_b -> v_b_top -> v_a_top -> v_a
loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),   # v_a->v_b
    f.oriented_edge(edge_right, True),   # v_b->v_b_top
    f.oriented_edge(edge_top,   False),  # v_b_top->v_a_top (reversed)
    f.oriented_edge(edge_left,  False),  # v_a_top->v_a (reversed, bare-LINE defect)
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
