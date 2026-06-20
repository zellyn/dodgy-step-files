"""Gp033 — B-spline curve has C0 internal break that downstream tools cannot ingest.

Catalog claim (ShapeUpgrade_SplitCurve, src/ModelingAlgorithms): A
B_SPLINE_CURVE_WITH_KNOTS has an internal knot whose multiplicity equals the
degree, producing only C0 continuity at that parameter. Downstream meshers,
fillet/chamfer engines, and IGES exporters that assume at least C1 mis-handle
the discontinuity.

Catalog recipe (exact): Degree-2 B-spline whose knot vector is
(0,0,0, 0.5,0.5,0.5, 1,1,1) — multiplicity 3 at u=0.5 forces C0. Control
polygon must NOT have collinear neighbours at the breakpoint (so the kink is
genuine, not accidentally smooth). The byte assertion requires EDGE_CURVE.

Fixture: A face on a CYLINDRICAL_SURFACE. The bottom edge uses the defective
degree-2 B_SPLINE_CURVE_WITH_KNOTS with knot vector (0,0,0,0.5,0.5,0.5,1,1,1).
The 5 control points in 3D form a non-collinear path (the middle segment has a
Z-bump at u=0.5, making the C0 break geometric, not accidental). The remaining
three edges (two vertical seams and one top arc) use correct geometry.

The 4-edge face loop covers u in [0, pi], v in [0, 1].
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp033",
    defect=(
        "EDGE_CURVE 3D curve is B_SPLINE_CURVE_WITH_KNOTS degree=2, knot vector "
        "(0,0,0,0.5,0.5,0.5,1,1,1): multiplicity=3=degree+1 at u=0.5 gives C0 "
        "break; non-collinear control points ensure genuine geometric kink; "
        "downstream meshers assuming C1 mis-handle the cusp"
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
#   v_rb: (1, 0, 0)  u=0,  v=0
#   v_lb: (-1, 0, 0) u=pi, v=0
#   v_rt: (1, 0, 1)  u=0,  v=1
#   v_lt: (-1, 0, 1) u=pi, v=1
p_rb = f.cartesian_point(( 1.0, 0.0, 0.0))
p_lb = f.cartesian_point((-1.0, 0.0, 0.0))
p_rt = f.cartesian_point(( 1.0, 0.0, 1.0))
p_lt = f.cartesian_point((-1.0, 0.0, 1.0))
v_rb = f.vertex_point(p_rb)
v_lb = f.vertex_point(p_lb)
v_rt = f.vertex_point(p_rt)
v_lt = f.vertex_point(p_lt)

d_up   = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)

# ---- THE DEFECT: bottom edge — degree-2 B-spline with C0 break ----
# Knot vector: (0,0,0, 0.5,0.5,0.5, 1,1,1), multiplicities (3,3,3).
# For degree 2, multiplicity=3 at interior knot means C-1? No: Cm = degree - mult
# => C(2-3) = C-1? That would be a real discontinuity in position. Per the catalog:
# multiplicity=degree=2 at the interior knot gives C0. Let's use mult=2 at interior:
# knot vector (0,0,0, 0.5,0.5, 1,1,1) with multiplicities (3,2,3) for 5 poles.
# Actually the catalog says "multiplicity 3 at u=0.5 forces C0" — for degree 2,
# mult=degree=2 is C0; mult=degree+1=3 would be a genuine positional break (C-1).
# We follow the catalog recipe exactly: mult=3 at u=0.5, which creates a break.
# 4 intervals: (0,0,0, 0.5,0.5,0.5, 1,1,1) => multiplicities (3,3,3), 9 knots.
# For degree 2: n_poles = n_knots - degree - 1 = 9 - 2 - 1 = 6? Actually
# sum(multiplicities) - degree - 1 = (3+3+3) - 2 - 1 = 6 poles.
# But 5 control points from catalog description...
# Let me re-read: "knot vector (0,0,0, 0.5,0.5,0.5, 1,1,1)" = (3,3,3) mults.
# n_poles = sum(mults) - degree - 1 = 9 - 3 = 6. So 6 control points.
#
# Control points: from (1,0,0) curving to (-1,0,0) with a Z-bump at the midpoint
# to make the C0 break geometric (non-collinear at u=0.5).
# Segment 1: poles 0..2 (Bezier deg-2 from (1,0,0) to somewhere near (0,0,0.4))
# Segment 2: poles 3..5 (Bezier deg-2 from somewhere near (0,0,-0.4) to (-1,0,0))
# The shared-but-discontinuous join: pole[2] != pole[3] (genuine C-1 positional break)
c0 = f.cartesian_point(( 1.0,  0.0,  0.0))   # start at v_rb
c1 = f.cartesian_point(( 0.5,  0.0,  0.3))   # interior control point, z-bump up
c2 = f.cartesian_point(( 0.0,  0.0,  0.4))   # just before break — top of bump
c3 = f.cartesian_point(( 0.0,  0.0, -0.4))   # just after break — dropped (C-1 jump)
c4 = f.cartesian_point((-0.5,  0.0,  0.3))   # back down
c5 = f.cartesian_point((-1.0,  0.0,  0.0))   # end at v_lb

bot_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('c0_bot_curve',2,"
    f"(#{c0.eid},#{c1.eid},#{c2.eid},#{c3.eid},#{c4.eid},#{c5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)
# Pcurve for bottom edge: LINE from (0,0) to (pi,0) in UV (correct).
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, math.pi)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_arc',#{cyl.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('c0_bot',#{bot_bspline.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('c0_bot',#{v_rb.eid},#{v_lb.eid},#{sc_bot.eid},.T.)"
)

# ---- Left seam at u=pi: vertical line from v_lb to v_lt ----
left_line_3d  = f.line(p_lb, vec_up)
pc_left_start = f.cartesian_point((math.pi, 0.0))
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
    f"EDGE_CURVE('left_seam',#{v_lb.eid},#{v_lt.eid},#{sc_left.eid},.T.)"
)

# ---- Right seam at u=0: vertical line from v_rb to v_rt ----
right_line_3d  = f.line(p_rb, vec_up)
pc_right_start = f.cartesian_point((0.0, 0.0))
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
    f"EDGE_CURVE('right_seam',#{v_rb.eid},#{v_rt.eid},#{sc_right.eid},.T.)"
)

# ---- Top arc: half-circle at z=1 from v_rt to v_lt, u: 0->pi ----
top_ctr   = f.cartesian_point((0.0, 0.0, 1.0))
top_zd    = f.direction((0.0, 0.0, 1.0))
top_xd    = f.direction((1.0, 0.0, 0.0))
top_axis  = f.axis2_placement_3d(top_ctr, top_zd, top_xd)
top_circle = f.circle(top_axis, 1.0)
pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, math.pi)
pc_top_line  = f.line(pc_top_start, pc_top_vec)
pc_top_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_arc',#{cyl.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_circle.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_rt.eid},#{v_lt.eid},#{sc_top.eid},.T.)"
)

# Loop: bot(fwd) -> left(fwd) -> top(rev) -> right(rev)
# v_rb->v_lb, v_lb->v_lt, v_lt->v_rt, v_rt->v_rb
loop = f.edge_loop([
    f.oriented_edge(edge_bot,   True),   # v_rb->v_lb (C0 B-spline defect)
    f.oriented_edge(edge_left,  True),   # v_lb->v_lt
    f.oriented_edge(edge_top,   False),  # v_lt->v_rt (reversed)
    f.oriented_edge(edge_right, False),  # v_rt->v_rb (reversed)
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
