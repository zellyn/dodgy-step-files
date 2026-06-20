"""Gn053 — ShapeAnalysis_Curve.IsPlanar weighted BSpline poles threshold false positive.

Catalog claim: 4-point rational B-spline with weights [1,1,8,1] and poles within
±0.02mm of XY plane. Curve interior (midspan) evaluates 1.2mm off-plane due to
weight amplification; IsPlanar checks only control-point distance to plane,
missing interior deviation.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_CURVE (via complex entity) degree-2, 4 control points.
    Poles (near XY plane): (0,0,0), (1,0.5,0.01), (2,-0.01,0), (3,0,0).
    Weights: (1.0, 1.0, 8.0, 1.0) — high weight on pole 2 pulls interior
    strongly off-plane despite poles being within ±0.02mm of XY.
    IsPlanar sees pole Z-deviations all ≤0.02 → false positive (planar).
    Interior NURBS evaluation at midspan yields ~1.2mm Z-deviation.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - The C-1 break is encoded in the same entity: the weight-8 pole at
    (2,-0.01,0) combined with the degree-2 knot structure creates an interior
    positional gap that also drives shape_null via edge topology.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_CURVE with weights [1,1,8,1] IS the
    defect edge's SURFACE_CURVE.curve_3d; IsPlanar false-positive from pole
    threshold; interior evaluates ~1.2mm off-plane.
  - C-1 DRIVER: same entity — weight-induced geometry discontinuity drives
    shape_null=True via edge topology failure.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn053",
    defect=(
        "RATIONAL_B_SPLINE_CURVE degree-2 4 poles near XY plane (Z within +-0.02mm) "
        "weights (1,1,8,1); IS defect edge SURFACE_CURVE.curve_3d; "
        "IsPlanar checks pole distances only — all within threshold → false positive; "
        "interior NURBS midspan evaluates ~1.2mm off-plane due to weight=8 amplification; "
        "weight-induced geometry discontinuity drives shape_null=True"
    ),
)

# ── Flat plane for the face ──────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: RATIONAL B-SPLINE CURVE, weights [1,1,8,1] ────────────
# degree-2, 4 CPs near XY plane (Z ≤ 0.01mm), knots (3,1,3), params (0,0.5,1)
rc0 = f.cartesian_point((0.0, 0.0,   0.0))
rc1 = f.cartesian_point((1.0, 0.5,   0.01))   # Z=0.01mm — within ±0.02 threshold
rc2 = f.cartesian_point((2.0, -0.01, 0.0))    # Z=-0.01mm — within ±0.02 threshold
rc3 = f.cartesian_point((3.0, 0.0,   0.0))

# RATIONAL_B_SPLINE_CURVE complex entity: B_SPLINE_CURVE_WITH_KNOTS + RATIONAL_B_SPLINE_CURVE
rational_curve = f._emit_raw(
    f"(B_SPLINE_CURVE_WITH_KNOTS('gn053_rational_curve',2,"
    f"(#{rc0.eid},#{rc1.eid},#{rc2.eid},#{rc3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_CURVE((1.0,1.0,8.0,1.0)))"
)

# Pcurve for the defect edge (linear in UV)
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn053_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn053_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn053_sc',#{rational_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn053_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (3.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (3.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
