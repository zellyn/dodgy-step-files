"""Gn016 — SURFACE_OF_REVOLUTION on ELLIPSE: basis becomes TRIMMED_CURVE over
rational B-spline plus non-unit axis DIRECTION after round-trip.

Catalog claim: Writing a SURFACE_OF_REVOLUTION built on an ELLIPSE to STEP and
reading back yields a TRIMMED_CURVE wrapping a degree-2 rational B_SPLINE_CURVE_WITH_KNOTS
ellipse-equivalent instead of the original analytic ELLIPSE, plus drift in the
revolved-axis DIRECTION away from unit norm (e.g. (0.99999999875, 0.00005, 0.0)).
Analytic identity lost.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION whose basis curve is a TRIMMED_CURVE wrapping a
    RATIONAL_B_SPLINE_CURVE_WITH_KNOTS approximation of an ellipse (semi-axes
    a=2, b=1), rather than an analytic ELLIPSE entity.
  - Axis: AXIS1_PLACEMENT at origin, direction slightly off-unit:
    (0.99999999875, 0.00005, 0.0) — the round-trip drift.
  - Ellipse NURBS: degree 2, 5 CPs for a half-ellipse (0 to PI), with
    rational weights encoding the conic section.
    V knots (0.0, 0.5, 1.0) mults (3, 2, 3) sum=8=2+5+1 ✓.
    Weights: (1.0, w_mid, 1.0, w_mid, 1.0) where w_mid=sqrt(2)/2 for 90°-arc arcs.
  - TRIMMED_CURVE wraps the B-spline with sense agreement .T., producing the
    "TRIMMED_CURVE over rational B-spline" form from the round-trip.
  - C-1 DRIVER: bottom edge B_SPLINE_CURVE_WITH_KNOTS degree-2 positional break
    at t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) forces shape_null.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION with TRIMMED_CURVE(rational BSpline)
    basis instead of analytic ELLIPSE; axis DIRECTION non-unit (0.99999999875,...).
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn016",
    defect=(
        "SURFACE_OF_REVOLUTION with TRIMMED_CURVE over degree-2 rational "
        "B_SPLINE_CURVE_WITH_KNOTS (5 CPs, knots (0,0.5,1) mults (3,2,3) sum=8=2+5+1 ✓) "
        "encoding half-ellipse (a=2,b=1); weights (1,sqrt(2)/2,1,sqrt(2)/2,1); "
        "axis DIRECTION non-unit (0.99999999875,0.00005,0.0) — round-trip drift; "
        "analytic ELLIPSE identity lost; healer must recover analytic form + normalize axis; "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

w_mid = math.sqrt(2.0) / 2.0  # ~0.7071

# ── DEFECT SURFACE: SURFACE_OF_REVOLUTION ────────────────────────────────────
# Axis: slightly non-unit direction (round-trip drift)
axis_origin = f.cartesian_point((0.0, 0.0, 0.0))
axis_dir = f._emit_raw(
    "DIRECTION('non_unit_axis_dir',(0.99999999875,0.00005,0.0))"
)
axis1 = f._emit_raw(
    f"AXIS1_PLACEMENT('rev_axis',#{axis_origin.eid},#{axis_dir.eid})"
)

# Ellipse approximation as degree-2 rational B-spline (half ellipse, 0..PI)
# Semi-major=2 (X), semi-minor=1 (Z). 5 CPs: 2 arcs of 90° each.
# CPs: (2,0,0), (2,0,1), (0,0,1), (-2,0,1), (-2,0,0)
ep0 = f.cartesian_point((2.0, 0.0, 0.0))
ep1 = f.cartesian_point((2.0, 0.0, 1.0))
ep2 = f.cartesian_point((0.0, 0.0, 1.0))
ep3 = f.cartesian_point((-2.0, 0.0, 1.0))
ep4 = f.cartesian_point((-2.0, 0.0, 0.0))

# Rational B-spline curve: degree 2, 5 CPs, knots (0,0.5,1) mults (3,2,3)
bsp_ell = f._emit_raw(
    f"(B_SPLINE_CURVE('ellipse_bspline_approx',2,"
    f"(#{ep0.eid},#{ep1.eid},#{ep2.eid},#{ep3.eid},#{ep4.eid}),"
    f".UNSPECIFIED.,.F.,.F.)"
    f"B_SPLINE_CURVE_WITH_KNOTS((3,2,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
    f"BOUNDED_CURVE()"
    f"CURVE()"
    f"GEOMETRIC_REPRESENTATION_ITEM()"
    f"RATIONAL_B_SPLINE_CURVE((1.0,{w_mid},1.0,{w_mid},1.0))"
    f"REPRESENTATION_ITEM('ellipse_bspline_approx'))"
)

# Trim parameters: t1=0.0, t2=1.0
t1 = f._emit_raw("PARAMETER_VALUE(0.0)")
t2 = f._emit_raw("PARAMETER_VALUE(1.0)")

trimmed = f._emit_raw(
    f"TRIMMED_CURVE('ellipse_trimmed',#{bsp_ell.eid},"
    f"(#{t1.eid}),(#{t2.eid}),.T.,.PARAMETER.)"
)

surf = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('ellipse_revolution',#{trimmed.eid},#{axis1.eid})"
)

# ── Parametric context for pcurves ──
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Simple rectangular face over this surface
p_a = f.cartesian_point((2.0, 0.0, 0.0))
p_b = f.cartesian_point((-2.0, 0.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, len3)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Edges along the revolution surface seam (U=profile, V=revolution angle)
e_top   = mk_edge_with_pc(v_a, v_b, (2.0,  0.0, 0.0), (-1., 0., 0.), 4.0, (0.0, 0.0), (0., 1.))
e_left  = mk_edge_with_pc(v_b, v_a, (-2.0, 0.0, 0.0), (1., 0., 0.),  4.0, (0.0, 1.0), (0., -1.))

# ── DEFECT EDGE — C-1 DRIVER ─────────────────────────────────────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('ellipse_rev_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('ellipse_rev_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('ellipse_rev_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('ellipse_rev_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('ellipse_rev_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('ellipse_rev_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# Close the loop: e_bot goes v_a→v_b, e_top reversed goes v_a→v_b so reversed is v_b→v_a? No.
# e_top: v_a→v_b; e_left: v_b→v_a. e_bot: v_a→v_b.
# Loop: e_bot (v_a→v_b) + e_left reversed (v_b→v_a... wait e_left is v_b→v_a)
# Use: e_bot fwd, e_left fwd (v_b→v_a), e_top reversed (v_b→v_a... e_top is v_a→v_b so rev=v_b→v_a)
# Wait: loop must be closed.
# e_bot: v_a→v_b
# e_left: v_b→v_a (fwd)
# So loop: [e_bot fwd, e_left fwd] — closed 2-edge loop.
loop = f.edge_loop([
    f.oriented_edge(e_bot,  True),
    f.oriented_edge(e_left, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty_literal="LENGTH_MEASURE(1.0E-7)")  # bare typed real, not enum-wrapped (scaffolding-artifact fix)
