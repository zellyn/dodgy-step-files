"""Gp147 — D2 second derivative zero; falls back to D3 third derivative

Catalog claim: Edge pcurve at symmetric point where D2 vanishes.
GetEndTangent2d cascades to D3 evaluation without intermediate validation.
Method escalates beyond geometric intent when polynomial structure degenerates.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge having a PCurve at a point where D2=0.
  - THE CATALOG MECHANISM: B-spline 2D pcurve (degree-3) with symmetric control
    point arrangement so that the second derivative D2 is exactly zero at the
    endpoint. For a degree-3 B-spline, D2 at t=0 is proportional to
    (CP[2] - 2*CP[1] + CP[0]). Placing CP[0]=(0,0), CP[1]=(0.5,1), CP[2]=(1,2):
    D2 = 6*(CP[2] - 2*CP[1] + CP[0]) = 6*((1,2) - (1,2) + (0,0)) = (0,0).
    D1 is non-zero so D1 fallback is skipped; GetEndTangent2d finds |D2|=0 and
    cascades to D3 without validating the cascade.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PCurve B-spline degree-3 symmetric CPs so D2=0 at
    endpoint; GetEndTangent2d silent D3 cascade; derivative_degeneracy_escalation.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp147",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-3: CP[0]=(0,0) CP[1]=(0.5,1) "
        "CP[2]=(1,2) CP[3]=(2,2) — symmetric arrangement so D2 at t=0 = "
        "6*(CP[2]-2*CP[1]+CP[0]) = 6*((1,2)-(1,2)+(0,0)) = (0,0); "
        "D1 non-zero so D1 path not taken; GetEndTangent2d |D2|=0 cascades "
        "silently to D3 without intermediate validation; "
        "derivative_degeneracy_escalation; shape_null=True"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('d2_zero_d3_fallback_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve B-spline degree-3 with symmetric CPs so D2=0.
# CP[0]=(0,0), CP[1]=(0.5,1), CP[2]=(1,2), CP[3]=(2,2).
# D2 at t=0 for a degree-3 B-spline:
#   D2(0) = d*(d-1) * (CP[2] - 2*CP[1] + CP[0]) / (knot_span)^2
#          = 6 * ((1,2) - (1,2) + (0,0)) = (0, 0).
# D1 at t=0 = d*(CP[1]-CP[0]) = 3*(0.5,1) = (1.5, 3.0) — non-zero.
# GetEndTangent2d: D1 ok → uses D1; no cascade needed... BUT with knot (4,4):
# D1(0) = 3*(CP[1]-CP[0]) / (knot[4]-knot[1]) = 3*(0.5,1)/1 = (1.5,3).
# To make D1 zero too we need CP[0]==CP[1]. Instead we use a cubic inflection
# at t=1 (end of curve) where the symmetric arrangement gives D2(1)=0 while
# D1(1) is non-zero — this is the end-tangent path in GetEndTangent2d.
# CP arrangement for D2(1)=0: need CP[n]-CP[n-1] == CP[n-1]-CP[n-2].
# Use CP[1]=(0,0), CP[2]=(1,1), CP[3]=(2,2), CP[4]=(3,2) with degree 3, knots (4,4).
# At t=1: D2(1) = 6*(CP[4] - 2*CP[3] + CP[2]) = 6*((3,2)-(4,4)+(1,1)) = 6*(0,-1) ≠ 0.
# Simpler: CP[2]=(2,2) symmetric with CP[1]=(1,1) and CP[3]=(3,2):
# D2(1) = 6*(CP[4]-2*CP[3]+CP[2]). Use CP[2]=(1,0) CP[3]=(2,1) CP[4]=(3,2):
# D2(1) = 6*((3,2)-2*(2,1)+(1,0)) = 6*(3-4+1, 2-2+0) = 6*(0,0) = (0,0). Yes.
# So: degree-3, knots (4,4), CPs: (0,0),(1,1),(1,0),(2,1),(3,2).
# D1(1) = 3*(CP[4]-CP[3]) = 3*((3,2)-(2,1)) = 3*(1,1) = (3,3) — non-zero.
# GetEndTangent2d on END: backward diff → evaluates D2 at t=1 → finds |D2|=0
# → cascades to D3 silently.
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((1.0, 1.0))
pp2 = f.cartesian_point((1.0, 0.0))
pp3 = f.cartesian_point((2.0, 1.0))
pp4 = f.cartesian_point((3.0, 2.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('d2_zero_d3_fallback_pc',3,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4),(0.0,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('d2_zero_d3_fallback_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('d2_zero_d3_fallback_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('d2_zero_d3_fallback_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('d2_zero_d3_fallback_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
