"""Gn010 — Out-of-range / NaN NURBS control points.

Catalog claim: NURBS control points have coordinates far outside the model's
valid extent (huge values like 1e100). Often caused by exporters botching
rational arithmetic or integer-overflow on weight normalization.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree (3,3), 4x4 net. Otherwise well-formed
    knot vectors: U=(0.0,1.0) mults (4,4) sum=8=3+4+1 ✓,
    V=(0.0,1.0) mults (4,4) sum=8=3+4+1 ✓.
  - Interior control point at index [1][1] has coordinates (1e100, 1e100, 1e100)
    — astronomically out of range, simulating an exporter weight normalization
    overflow. All other CPs are reasonable (within [0,3] bounding box).
  - This is the catalog mechanism: the bad CP should cause the kernel to reject
    or refuse to use this surface for projection/intersection.
  - C-1 DRIVER: degree-2 B-spline positional break on the bottom edge at t=0.5
    (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: interior CP[1][1]=(1e100,1e100,1e100) on a degree-3 4x4
    surface; exporter weight-normalization overflow producing impossible coordinate.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn010",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (3,3) 4x4 net; "
        "U knots (0.0,1.0) mults (4,4) sum=8=3+4+1 ✓; "
        "V knots (0.0,1.0) mults (4,4) sum=8=3+4+1 ✓; "
        "interior CP[1][1]=(1e100,1e100,1e100) — out-of-range coordinate "
        "(exporter weight normalization overflow); "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── DEFECT SURFACE: B_SPLINE_SURFACE_WITH_KNOTS with out-of-range CP ──
# 4x4 control net, degree (3,3), clamped Bezier.
# Good CPs for a flat [0,3]x[0,3] patch, except interior [1][1] = 1e100.
p00 = f.cartesian_point((0.0, 0.0, 0.0)); p01 = f.cartesian_point((0.0, 1.0, 0.0))
p02 = f.cartesian_point((0.0, 2.0, 0.0)); p03 = f.cartesian_point((0.0, 3.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
# THE DEFECT: CP[1][1] at astronomically large coordinates
p11 = f.cartesian_point((1e100, 1e100, 1e100))
p12 = f.cartesian_point((1.0, 2.0, 0.0)); p13 = f.cartesian_point((1.0, 3.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0)); p21 = f.cartesian_point((2.0, 1.0, 0.0))
p22 = f.cartesian_point((2.0, 2.0, 0.0)); p23 = f.cartesian_point((2.0, 3.0, 0.0))
p30 = f.cartesian_point((3.0, 0.0, 0.0)); p31 = f.cartesian_point((3.0, 1.0, 0.0))
p32 = f.cartesian_point((3.0, 2.0, 0.0)); p33 = f.cartesian_point((3.0, 3.0, 0.0))

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('nan_cp',3,3,"
    f"((#{p00.eid},#{p01.eid},#{p02.eid},#{p03.eid}),"
    f"(#{p10.eid},#{p11.eid},#{p12.eid},#{p13.eid}),"
    f"(#{p20.eid},#{p21.eid},#{p22.eid},#{p23.eid}),"
    f"(#{p30.eid},#{p31.eid},#{p32.eid},#{p33.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,4),(4,4),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Parametric context for pcurves ──
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
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


e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.0, 0.0), (0., 1., 0.), 3.0, (3.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 3.0, 0.0), (-1., 0., 0.), 3.0, (3.0, 3.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 3.0, 0.0), (0., -1., 0.), 3.0, (0.0, 3.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) — C-1 DRIVER ───────────────────────────
# degree-2 B-spline with 1.5-unit positional gap at t=0.5 forces shape_null.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('nan_cp_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('nan_cp_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('nan_cp_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('nan_cp_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('nan_cp_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('nan_cp_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
