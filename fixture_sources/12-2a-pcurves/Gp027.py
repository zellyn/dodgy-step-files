"""Gp027 - Closed-face splitter leaves new pcurves out of sync with 3D curves
on CYLINDRICAL_SURFACE.

Catalog claim (13-quaoar.md B008): A pass that splits closed periodic faces
along their seams produces new edges whose pcurves do not satisfy the
same-parameter invariant. Typical pattern: an EDGE_CURVE traverses from
u=0 to u=pi in 3D (half-circle, parameter range [0,pi]), but the pcurve LINE
is parameterised over [0,1] instead of [0,pi] -- same UV path, wrong pace.
At t=0.5 the 3D curve evaluates to u=pi/2 (~1.57) but the pcurve yields u=0.5;
divergence ~1.07 >> tolerance. A topology checker reports invalid edges.

Fixture: A half-cylinder face (U in [0,pi], V in [0,1]) as produced by
splitting a full cylinder along u=pi. The bottom edge is a half-circle arc
(3D: a full CIRCLE, vertices define the trim from u=0 to u=pi). The pcurve
LINE for this edge -- the defect -- is parameterised over [0,1]: start at
(0,0) with magnitude 1.0, so it covers u in [0,1] in UV. The correct
pcurve should have magnitude pi covering u in [0,pi]. Same UV path, wrong
parameterisation pace: at any t, pcurve(t).u = t but 3Dcurve(t).u = t*pi.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp027",
    defect=(
        "Split-seam edge on cylinder: 3D half-circle arc parameterised over [0,pi] "
        "but pcurve LINE parameterised over [0,1]; at t=0.5, 3D gives u=pi/2~=1.57 "
        "but pcurve gives u=0.5; same-parameter invariant violated by factor pi"
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

# Vertices for the half-cylinder face:
#   A = (1, 0, 0)  at u=0,  v=0
#   B = (-1, 0, 0) at u=pi, v=0
#   A_top = (1, 0, 1)  at u=0,  v=1
#   B_top = (-1, 0, 1) at u=pi, v=1
p_a     = f.cartesian_point(( 1.0, 0.0, 0.0))
p_b     = f.cartesian_point((-1.0, 0.0, 0.0))
p_a_top = f.cartesian_point(( 1.0, 0.0, 1.0))
p_b_top = f.cartesian_point((-1.0, 0.0, 1.0))
v_a     = f.vertex_point(p_a)
v_b     = f.vertex_point(p_b)
v_a_top = f.vertex_point(p_a_top)
v_b_top = f.vertex_point(p_b_top)

# Up direction
d_up   = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)

# ---- THE DEFECT: bottom split edge -- half-circle arc, pcurve over [0,1]. ----
# 3D curve: a full circle in z=0 plane, radius 1. Vertices A and B define the
# half-arc trim (u from 0 to pi) implicitly.
arc_ctr   = f.cartesian_point((0.0, 0.0, 0.0))
arc_zaxis = f.direction((0.0, 0.0, 1.0))
arc_xaxis = f.direction((1.0, 0.0, 0.0))
arc_axis  = f.axis2_placement_3d(arc_ctr, arc_zaxis, arc_xaxis)
circle_bot_3d = f.circle(arc_axis, 1.0)
# Correct pcurve: LINE from (0,0) with direction (1,0), magnitude pi.
# THE DEFECT: magnitude is 1.0 instead of pi.
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, 1.0)   # DEFECT: should be math.pi
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_split_wrong_pace',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('split_wrong',#{cyl.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('split_edge',#{circle_bot_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('split_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# ---- Left seam at u=0: vertical line from A to A_top ----
left_line_3d  = f.line(p_a, vec_up)
pc_left_start = f.cartesian_point((0.0, 0.0))
pc_left_dir   = f.direction((0.0, 1.0))
pc_left_vec   = f.vector(pc_left_dir, 1.0)
pc_left_line  = f.line(pc_left_start, pc_left_vec)
pc_left_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_left',(#{pc_left_line.eid}),#{prc.eid})"
)
pcurve_left = f._emit_raw(f"PCURVE('left_seam',#{cyl.eid},#{pc_left_def.eid})")
sc_left = f._emit_raw(
    f"SURFACE_CURVE('left_seam',#{left_line_3d.eid},(#{pcurve_left.eid}),.PCURVE_S1.)"
)
edge_left = f._emit_raw(
    f"EDGE_CURVE('left_seam',#{v_a.eid},#{v_a_top.eid},#{sc_left.eid},.T.)"
)

# ---- Right seam at u=pi: vertical line from B to B_top ----
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

# ---- Top arc: half-circle from A_top to B_top at z=1, u: 0->pi. ----
top_ctr   = f.cartesian_point((0.0, 0.0, 1.0))
top_axis  = f.axis2_placement_3d(top_ctr, arc_zaxis, arc_xaxis)
circle_top_3d = f.circle(top_axis, 1.0)
pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, math.pi)  # correct here
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

# Loop: split_bot(fwd) -> right(fwd) -> top(rev) -> left(rev)
# v_a -> v_b -> v_b_top -> v_a_top -> v_a
loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),   # v_a->v_b (defective pcurve pace)
    f.oriented_edge(edge_right, True),   # v_b->v_b_top
    f.oriented_edge(edge_top,   False),  # v_b_top->v_a_top (reversed)
    f.oriented_edge(edge_left,  False),  # v_a_top->v_a (reversed)
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
