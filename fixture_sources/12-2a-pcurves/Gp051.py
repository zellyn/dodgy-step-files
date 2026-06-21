"""Gp051 — ShapeAnalysis_Edge.GetEndTangent2d B-spline endpoint tangent divergence.

Catalog claim: B-spline pcurve with degree=1 on non-uniform knot vector
[0, 0.5, 1.5, 2.5, 5]. Endpoint tangent computation uses control polygon
direction instead of analytic 2D tangent, causing divergence on non-uniform
knots.

Mechanism: The defect IS in the pcurve — a degree-1 B-spline with 4 CPs on
non-uniform knot vector [0, 0.5, 1.5, 2.5, 5]. The analytic tangent at the
endpoint is (CP3-CP2)/||(CP3-CP2)|| in the non-uniform knot parameterization;
GetEndTangent2d instead uses (CP3-CP2)/(last_knot-second_to_last_knot) which
diverges from the true tangent at the endpoint because the knot span is
non-uniform. The face loads cleanly (shape(1)) — the bug surfaces during
post-load healing analysis.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp051",
    defect=(
        "PLANE Z=0; degree-1 B-spline pcurve with 4 CPs on non-uniform knot "
        "vector [0, 0.5, 1.5, 2.5, 5]; GetEndTangent2d uses control-polygon "
        "slope instead of analytic 2D derivative at endpoint; non-uniform knot "
        "spans magnify divergence — last span is [2.5,5] (width 2.5) vs first "
        "span [0,0.5] (width 0.5); endpoint tangent computation is incorrect"
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

# Face corners: rectangle [0,5] x [0,3]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build a normal EDGE_CURVE with SURFACE_CURVE + linear PCURVE."""
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


e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 3.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 3.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 3.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 3.0, 0.0), (0., -1., 0.), 3.0, (0.0, 3.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ──────────────────────────────────────
# CATALOG MECHANISM: degree-1 B-spline pcurve on NON-UNIFORM knots.
# Knot vector: [0, 0.5, 1.5, 2.5, 5] with multiplicities [2, 1, 1, 1, 2]
# 4 CPs: (0,0), (1,0), (3,0), (5,0) — evenly spaced in X but knot spans
# are 0.5, 1.0, 1.0, 2.5 — highly non-uniform.
# GetEndTangent2d uses (CP3-CP2) / last_knot_span = (5-3)/2.5 = 0.8 (wrong)
# vs analytic tangent in the uniform direction = (1,0) (correct).

line_3d_p = f.cartesian_point((0.0, 0.0, 0.0))
line_3d_d = f.direction((1.0, 0.0, 0.0))
line_3d_v = f.vector(line_3d_d, 5.0)
line_3d   = f.line(line_3d_p, line_3d_v)

# Degree-1 B-spline pcurve with 4 CPs on non-uniform knots
cp0 = f.cartesian_point((0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.0))
cp2 = f.cartesian_point((3.0, 0.0))
cp3 = f.cartesian_point((5.0, 0.0))
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp051_tangent_pcurve',1,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,1,1,1,2),(0.0,0.5,1.5,2.5,5.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp051_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp051_uv',#{surf.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp051_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('gp051_bot_edge',#{v_a.eid},#{v_b.eid},#{surface_curve.eid},.T.)"
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
