"""Gp068 -- ShapeFix_Edge.FixReversed2d circular-curve range.

Catalog claim: When PCurve is a CIRCLE entity, reversing its parameter range
requires angle remapping. FixReversed2d treats it as a simple [start, end]
swap, losing proper circular parametrization.

Fixture: CYLINDRICAL_SURFACE face. The defect edge's key properties:
  1. PCurve is a TRIMMED_CURVE wrapping a CIRCLE in UV space, arc [0, pi/2].
     After same_sense=.F. reversal, FixReversed2d naively swaps to [pi/2, 0].
     For a CIRCLE, correct reversal requires angle remapping (negate and shift),
     not just a swap. The naive [pi/2, 0] swap traverses the wrong angular
     direction from the wrong starting point.
  2. 3D curve is a B-spline with a C-1 POSITIONAL BREAK at t=0.5
     (knot mult=3=degree+1, 6 CPs with a large gap at the break point).
     This break models the corrupted arc geometry after FixReversed2d applies
     the wrong circular-range reversal and stitches broken segments together.
     The positional break causes OCC shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp068",
    defect=(
        "CYLINDRICAL_SURFACE face; defect edge: PCurve is TRIMMED_CURVE "
        "(CIRCLE arc [0,pi/2]) in UV; EDGE_CURVE same_sense=.F.; FixReversed2d "
        "naive [start,end] swap gives [pi/2,0] instead of correct angle "
        "remapping; 3D B-spline has C-1 positional break at t=0.5 modeling "
        "corrupted arc after wrong reversal"
    ),
)

# Host: CYLINDRICAL_SURFACE, radius 2, axis Z through origin
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_z    = f.direction((0.0, 0.0, 1.0))
cyl_x    = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_z, cyl_x)
cyl_surf = f.cylindrical_surface(cyl_plc, 2.0)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Cylindrical surface: u = angle, v = height. Radius = 2.
# At u=0: (2,0,*); at u=pi/2: (0,2,*)
# Face patch: u in [0, pi/2], v in [0, 1]
p00 = f.cartesian_point((2.0, 0.0, 0.0))    # u=0,     v=0
p10 = f.cartesian_point((0.0, 2.0, 0.0))    # u=pi/2,  v=0
p11 = f.cartesian_point((0.0, 2.0, 1.0))    # u=pi/2,  v=1
p01 = f.cartesian_point((2.0, 0.0, 1.0))    # u=0,     v=1
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

# Context edges: two vertical sides and top arc
d_up = f.direction((0.0, 0.0, 1.0)); vec_up = f.vector(d_up, 1.0)
e_left  = f.edge_curve(v00, v01, f.line(p00, vec_up))
e_right = f.edge_curve(v10, v11, f.line(p10, vec_up))

# Top arc at v=1: CIRCLE in plane z=1, trimmed [0, pi/2]
top_center = f.cartesian_point((0.0, 0.0, 1.0))
top_z = f.direction((0.0, 0.0, 1.0)); top_x = f.direction((1.0, 0.0, 0.0))
top_axis = f.axis2_placement_3d(top_center, top_z, top_x)
top_circle = f.circle(top_axis, 2.0)
top_tc = f._emit_raw(
    f"TRIMMED_CURVE('top_arc',#{top_circle.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2})),.T.,.PARAMETER.)"
)
pc_top_s = f.cartesian_point((0.0, 1.0))
pc_top_d = f.direction((1.0, 0.0)); pc_top_v = f.vector(pc_top_d, math.pi/2)
pc_top_l = f.line(pc_top_s, pc_top_v)
pc_top_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('top_pc_def',(#{pc_top_l.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_pc',#{cyl_surf.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_tc.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
e_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v01.eid},#{v11.eid},#{sc_top.eid},.T.)"
)

# ── DEFECT EDGE -- bottom arc with same_sense=.F. ────────────────────────────
# 3D B-spline: degree 2, 6 CPs, C-1 positional break at t=0.5.
# The break represents the corrupted geometry after FixReversed2d applies
# a naive angle-swap [0,pi/2] -> [pi/2,0] on the CIRCLE pcurve.
# The correct reversal would produce [-pi/2, 0] (or equivalently [3pi/2, 2pi]),
# not [pi/2, 0]. The broken arc stitches two mis-oriented segments.
s0 = f.cartesian_point((2.0, 0.0, 0.0))     # start: (2,0,0) at u=0
s1 = f.cartesian_point((2.0, 1.0, 0.0))
s2 = f.cartesian_point((2.0, 2.0, 0.0))     # before break: overshoot
s3 = f.cartesian_point((-2.0, 2.0, 0.0))    # after break: -X jump (wrong direction)
s4 = f.cartesian_point((0.0, 2.0, 0.0))
s5 = f.cartesian_point((0.0, 2.0, 0.0))     # end: (0,2,0) at u=pi/2
bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('arc_break',2,"
    f"(#{s0.eid},#{s1.eid},#{s2.eid},#{s3.eid},#{s4.eid},#{s5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve: CIRCLE in UV space (at v=0), arc [0, pi/2].
# THE DEFECT: the EDGE_CURVE has same_sense=.F. (reversed). FixReversed2d
# naively swaps the CIRCLE trim to [pi/2, 0] instead of remapping to
# [-pi/2, 0]. At v=0, u sweeps from 0 to pi/2 on the cylinder.
# In UV space: center at (0, 0), radius = pi/2 (so arc length = pi/2 in u).
pc_ctr = f.cartesian_point((0.0, 0.0))
pc_x_dir = f.direction((1.0, 0.0))
pc_axis = f._emit_raw(
    f"AXIS2_PLACEMENT_2D('pc_ctr',#{pc_ctr.eid},#{pc_x_dir.eid})"
)
# CIRCLE radius = pi/2 so that the quarter-turn arc spans u=[0, pi/2]
pc_circle = f._emit_raw(
    f"CIRCLE('pc_circle',#{pc_axis.eid},{math.pi/2})"
)
pc_tc = f._emit_raw(
    f"TRIMMED_CURVE('pc_tc',#{pc_circle.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2})),.T.,.PARAMETER.)"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{pc_tc.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(
    f"PCURVE('bot_circle_pc',#{cyl_surf.eid},#{defrep.eid})"
)
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bspline_3d.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
# THE DEFECT: same_sense=.F. on EDGE_CURVE with a CIRCLE pcurve.
# FixReversed2d should remap [0, pi/2] -> [-pi/2, 0] (angle shift), not
# [pi/2, 0] (naive swap).
e_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc_reversed',"
    f"#{v00.eid},#{v10.eid},#{sc_bot.eid},.F.)"
)

# 4-edge face loop
loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   False),
    f.oriented_edge(e_left,  False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl_surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
