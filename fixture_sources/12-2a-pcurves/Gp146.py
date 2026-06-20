"""Gp146 — D1 derivative zero; falls back to D2 second derivative

Catalog claim: Edge pcurve at inflection point where D1 evaluation yields zero
magnitude. GetEndTangent2d silently escalates to D2 without reporting
degeneracy. Analyzer omits reporting inflection point condition before secondary
derivative fallback.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge having a PCurve at an inflection point
    at the endpoint where D1 = 0.
  - THE CATALOG MECHANISM: B-spline 2D pcurve where the endpoint is an
    inflection point: the curve's first derivative D1 at the endpoint parameter
    is zero (the curve momentarily has zero velocity — a cusp or stationary
    point). This occurs when the first two control points of the B-spline are
    coincident (so the degree-2 Bezier segment starts with zero D1).
    GetEndTangent2d detects |D1| = 0 and silently escalates to D2 (the second
    derivative) to determine the tangent direction, without logging the
    inflection point condition. The analyzer accepts D2 as a tangent proxy
    without flagging the derivative_degeneracy_escalation condition.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PCurve B-spline endpoint at D1=0 inflection point
    (first two CPs coincident); GetEndTangent2d escalates to D2 without
    reporting degeneracy; derivative_degeneracy_escalation axis.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp146",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2: CP[0]=(0,0) CP[1]=(0,0) "
        "CP[2]=(1.0,0) CP[3]=(2.0,0) — first two CPs coincident; "
        "D1 at parameter=0 evaluates to zero (inflection point / stationary point); "
        "GetEndTangent2d |D1|=0 triggers silent D2 escalation without reporting "
        "inflection point condition; analyzer omits derivative_degeneracy_escalation "
        "diagnostic; shape_null=True"
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

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('d1_zero_d2_fallback_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve B-spline degree-2 with first two CPs coincident.
# For a degree-2 B-spline with knots (3,2,3):
#   At t=0: B'(0) = degree * (CP[1] - CP[0]) / (knot[degree+1] - knot[1])
#   CP[0] = CP[1] = (0,0): B'(0) = 2*(0,0 - 0,0)/... = (0,0) — D1 is zero.
# GetEndTangent2d: |D1(t=0)| = 0 → escalates silently to D2 (curvature-based
# tangent) without flagging the inflection point / stationary point condition.
# D2 = 2*(CP[2] - 2*CP[1] + CP[0]) = 2*((1,0) - (0,0) - (0,0)) = (2,0).
# So D2 gives the tangent direction (1,0) silently, bypassing the D1=0 report.
pp0 = f.cartesian_point((0.0, 0.0))   # coincident with pp1 → D1=0 at t=0
pp1 = f.cartesian_point((0.0, 0.0))   # coincident
pp2 = f.cartesian_point((1.0, 0.0))
pp3 = f.cartesian_point((2.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('d1_zero_d2_fallback_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('d1_zero_d2_fallback_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('d1_zero_d2_fallback_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('d1_zero_d2_fallback_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('d1_zero_d2_fallback_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
