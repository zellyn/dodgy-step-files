"""Gn021 — OFFSET_SURFACE of complex BSpline base fails parsing only when wrapped.

Catalog claim: A face referencing OFFSET_SURFACE wrapping a complex
B_SPLINE_SURFACE aggregate fails to render; replacing the OFFSET_SURFACE
directly with the B_SPLINE_SURFACE succeeds. Broken indirection through
OFFSET_SURFACE over a NURBS base.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE complex entity (degree 2,2; 3x3 net; flat patch [0,4]x[0,4])
    as the base of an OFFSET_SURFACE with distance 5.0.
  - ADVANCED_FACE references the OFFSET_SURFACE wrapper, NOT the raw B_SPLINE.
    This is the broken indirection: offset-of-spline wrapping fails on import.
  - C-1 DRIVER: bottom edge B_SPLINE_CURVE_WITH_KNOTS degree-2 positional break
    at t=0.5 (CP[2]=(2.0,0,0) vs CP[3]=(3.5,0,0), 1.5-unit gap) forces shape_null.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_SURFACE('',#base_bspline, 5.0, .F.) wrapping a
    complex B_SPLINE_SURFACE aggregate — broken indirection that fails parsing.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn021",
    defect=(
        "OFFSET_SURFACE wrapping complex B_SPLINE_SURFACE aggregate (degree 2,2 3x3 net); "
        "ADVANCED_FACE references OFFSET_SURFACE not raw B-spline — broken indirection; "
        "B_SPLINE_SURFACE base: U/V knots (0.0,1.0) mults (3,3) sum=6=2+3+1 ✓; "
        "offset distance 5.0; parsing fails only via OFFSET_SURFACE wrapper; "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(2.0,0,0) vs CP[3]=(3.5,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── BASE SURFACE: complex B_SPLINE_SURFACE aggregate, degree (2,2), 3x3 net ──
# Simple flat patch over [0,4]x[0,4] at Z=0.
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p01 = f.cartesian_point((2.0, 0.0, 0.0))
p02 = f.cartesian_point((4.0, 0.0, 0.0))
p10 = f.cartesian_point((0.0, 2.0, 0.0))
p11 = f.cartesian_point((2.0, 2.0, 0.0))
p12 = f.cartesian_point((4.0, 2.0, 0.0))
p20 = f.cartesian_point((0.0, 4.0, 0.0))
p21 = f.cartesian_point((2.0, 4.0, 0.0))
p22 = f.cartesian_point((4.0, 4.0, 0.0))

row0 = f"(#{p00.eid},#{p01.eid},#{p02.eid})"
row1 = f"(#{p10.eid},#{p11.eid},#{p12.eid})"
row2 = f"(#{p20.eid},#{p21.eid},#{p22.eid})"

# Complex entity: B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS
# Clamped degree-2 in both: U knots (0,1) mults (3,3), V knots (0,1) mults (3,3)
base_bspline = f._emit_raw(
    f"(B_SPLINE_SURFACE('offset_base_bspline',2,2,"
    f"({row0},{row1},{row2}),"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((3,3),(3,3),"
    f"(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
    f"REPRESENTATION_ITEM('offset_base_bspline')"
    f"SURFACE())"
)

# ── DEFECT SURFACE: OFFSET_SURFACE wrapping the complex B-spline ─────────────
# This is the broken indirection: ADVANCED_FACE will reference this, not base_bspline.
# Normal offset distance 5.0; .F. = no self-intersection avoidance.
surf = f._emit_raw(
    f"OFFSET_SURFACE('offset_of_nurbs',#{base_bspline.eid},5.0,.F.)"
)

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners in 3D (corners of the base patch; offset shifts Z by +5 but
# vertices are placed at base corner positions for structural completeness).
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 4.0, 0.0))
p_d = f.cartesian_point((0.0, 4.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


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


e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 4.0, (1.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 4.0, 0.0), (-1., 0., 0.), 4.0, (1.0, 1.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 4.0, 0.0), (0., -1., 0.), 4.0, (0.0, 1.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) — C-1 DRIVER ───────────────────────────
# degree-2 B-spline with 1.5-unit positional gap at t=0.5 forces shape_null.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.0, 0.0, 0.0))
dc2 = f.cartesian_point((2.0, 0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.5, 0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0, 0.0, 0.0))
dc5 = f.cartesian_point((4.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('offset_nurbs_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('offset_nurbs_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('offset_nurbs_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('offset_nurbs_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('offset_nurbs_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('offset_nurbs_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
