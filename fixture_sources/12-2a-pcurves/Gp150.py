"""Gp150 — Edge orientation reversal negates computed tangent post-computation

Catalog claim: Edge with REVERSED orientation; tangent computed then negated
without validation of orientation consistency with curve parameterization.
Analyzer fails to detect when orientation reversal applied post-computation
masks tangent-reversal errors.

STEP mechanism (literal):
  - PLANE Z=0 face with a REVERSED edge having a PCurve with a specific
    tangent direction. The orientation flag is .F. (REVERSED) on the
    ORIENTED_EDGE.
  - THE CATALOG MECHANISM: An ORIENTED_EDGE with orientation=.F. causes
    GetEndTangent2d to negate the computed tangent after computation (the
    reversal is applied post-hoc). This means the final reported tangent
    direction is the negative of the curve's natural D1. The analyzer does
    not validate that the negated direction remains consistent with the
    actual curve parameterization. If the curve's parameterization and
    edge traversal direction diverge, the masked reversal leads to
    incorrect tangent-based downstream operations.
    The PCurve has a well-defined D1 at t=1 (end, since reversed edge
    evaluates at the opposite parameter). The B-spline pcurve has
    asymmetric tangent at t=0 vs t=1 to expose the reversal effect.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: ORIENTED_EDGE with orientation=.F. (REVERSED);
    GetEndTangent2d computes tangent then negates without consistency
    check; orientation_reversal_semantics GET_END_TANGENT_2D_B010;
    reversed tangent may diverge from parameterization intent.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp150",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2: CP[0]=(0,0) CP[1]=(1,1) "
        "CP[2]=(2,0) — asymmetric tangents at t=0 vs t=1; "
        "ORIENTED_EDGE orientation=.F. (REVERSED): GetEndTangent2d negates "
        "the computed tangent post-computation without validating that the "
        "negated direction is consistent with curve parameterization; "
        "reversed tangent may diverge from parameterization intent; "
        "orientation_reversal_semantics GET_END_TANGENT_2D_B010; shape_null=True"
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

def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_b -> v_a, REVERSED orientation) ───────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
# Note: EDGE_CURVE runs v_a→v_b (forward), but the ORIENTED_EDGE will be .F.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('orientation_reversal_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve B-spline degree-2 with asymmetric tangents.
# CP[0]=(0,0), CP[1]=(1,1), CP[2]=(2,0).
# D1(t=0) = 2*(CP[1]-CP[0]) = 2*(1,1) = (2,2) — direction (1,1).
# D1(t=1) = 2*(CP[2]-CP[1]) = 2*(1,-1) = (2,-2) — direction (1,-1).
# The ORIENTED_EDGE orientation is .F. (REVERSED): the edge is traversed
# from v_b to v_a, so GetEndTangent2d evaluates at t=1 of the PCurve
# (the start of the reversed traversal) and then negates the result.
# Computed: D1(t=1) = (2,-2). Negated: (-2,+2) — direction (-1,1).
# The negation post-computation is applied without checking if the reversed
# direction is consistent with the actual curve shape at the traversal start.
# orientation_reversal_semantics GET_END_TANGENT_2D_B010.
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((1.0, 1.0))
pp2 = f.cartesian_point((2.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('orientation_reversal_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('orientation_reversal_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('orientation_reversal_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('orientation_reversal_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# EDGE_CURVE: topological sense v_a -> v_b
e_bot = f._emit_raw(
    f"EDGE_CURVE('orientation_reversal_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# THE REVERSAL: oriented_edge with .F. — traversal is v_b→v_a (reversed).
# GetEndTangent2d computes tangent at the start of traversal (t=1 of pcurve)
# then negates it without orientation consistency check.
oe_bot_rev = f._emit_raw(
    f"ORIENTED_EDGE('',*,*,#{e_bot.eid},.F.)"
)
oe_right = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_right.eid},.T.)")
oe_top   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_top.eid},.T.)")
oe_left  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e_left.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_bot_rev.eid},#{oe_right.eid},#{oe_top.eid},#{oe_left.eid}))"
)
fb   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face = f._emit_raw(f"ADVANCED_FACE('',(#{fb.eid}),#{surf.eid},.T.)")
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
