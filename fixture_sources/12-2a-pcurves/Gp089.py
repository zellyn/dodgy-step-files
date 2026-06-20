"""Gp089 — FixReversed2d trimmed-circle.

Catalog claim: Pcurve TRIMMED_CURVE wrapping CIRCLE; 3D edge is TRIMMED_CURVE
wrapping CIRCLE with different trim parameters. FixReversed2d reverses the
circle geometry but ignores trim bounds, causing parameter reversal to
overshoot. Defect: circle-reversal logic does not propagate trim-parameter
semantics.

STEP mechanism (literal):
  - PLANE face with defect edge.
  - PCurve: TRIMMED_CURVE wrapping a CIRCLE in UV space. Circle radius pi/4,
    arc trimmed [0, pi/2]. The trim encodes a quarter-arc in parameter space.
  - 3D curve: TRIMMED_CURVE wrapping CIRCLE (radius 1.0) trimmed [0, pi/2].
    EDGE_CURVE has same_sense=.F. (reversed).
  - THE DEFECT: FixReversed2d reverses the UV CIRCLE geometry but does not
    adjust trim bounds [0, pi/2]. A naive reversal leaves [pi/2, 0] which
    overshoots the intended angular range. The broken geometry + reversed
    EDGE_CURVE causes OCC shape_null=True.
  - C-1 DRIVER: also add a degree-2 B-spline 3D curve with positional break
    at t=0.5 to ensure shape_null.

Mechanism vs driver:
  - CATALOG MECHANISM: TRIMMED_CURVE wrapping CIRCLE as pcurve + reversed
    EDGE_CURVE (same_sense=.F.) — FixReversed2d trim-bounds overshoot.
  - C-1 DRIVER: B-spline positional break in 3D curve forces shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp089",
    defect=(
        "PLANE Z=0; defect edge: 3D B-spline C-1 break at t=0.5 (CP[2]=(1.5,0,0) "
        "vs CP[3]=(3.0,0,0), 1.5-unit gap); PCurve TRIMMED_CURVE(CIRCLE radius=pi/4, "
        "trim=[0,pi/2]); EDGE_CURVE same_sense=.F.; FixReversed2d reverses CIRCLE "
        "but ignores trim bounds [0,pi/2] → overshoot; C-1 break drives shape_null"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) — clean
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# 3D curve: degree-2 B-spline with C-1 positional break at t=0.5.
# This drives shape_null=True.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.8, 0.0, 0.0))
dc2 = f.cartesian_point((1.5, 0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0, 0.0, 0.0))   # start of second (1.5-unit gap = break)
dc4 = f.cartesian_point((4.0, 0.0, 0.0))
dc5 = f.cartesian_point((5.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('tc_circle_3d',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve is TRIMMED_CURVE wrapping a CIRCLE in UV space.
# Circle center at (2.5, 0) in UV, radius=pi/4.
# At angle=0: UV=(2.5+pi/4, 0); at angle=pi/2: UV=(2.5, pi/4).
# Trim [0, pi/2] selects the quarter arc.
# EDGE_CURVE same_sense=.F. triggers FixReversed2d.
# FixReversed2d reverses the CIRCLE (negating its X-axis) but leaves
# trim bounds [0, pi/2] unchanged → the reversed circle with same trim
# traverses from a different start angle, overshooting the intended arc.
pc_ctr = f.cartesian_point((2.5, 0.0))
pc_x_dir = f.direction((1.0, 0.0))
pc_axis = f._emit_raw(
    f"AXIS2_PLACEMENT_2D('pc_ctr',#{pc_ctr.eid},#{pc_x_dir.eid})"
)
pc_circle = f._emit_raw(
    f"CIRCLE('pc_circle',#{pc_axis.eid},{math.pi / 4})"
)
pc_tc = f._emit_raw(
    f"TRIMMED_CURVE('pc_tc',#{pc_circle.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi / 2})),.T.,.PARAMETER.)"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{pc_tc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('bot_circle_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# THE DEFECT: same_sense=.F. → FixReversed2d ignores trim bounds on the CIRCLE pcurve.
e_bot = f._emit_raw(
    f"EDGE_CURVE('tc_circle_reversed',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.F.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
