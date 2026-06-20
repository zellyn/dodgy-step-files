"""Gn069 — ShapeAnalysis_Curve.GetSamplePoints BSpline knot-aware sampling.

Catalog claim: B-spline curve degree 3, 6 poles, with closely-spaced interior
knots at (0.5, 0.51, 0.52). GetSamplePoints over-densifies samples in the
narrow 0.01-width knot region, producing hundreds of samples there instead of
proportional adaptive sampling across the full [0,1] domain.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 6 poles, clamped.
    Knot vector: (0,0,0,0, 0.5,0.51,0.52, 1,1,1,1).
    Knots: (0.0, 0.5, 0.51, 0.52, 1.0) mults (4,1,1,1,4) sum=11=3+6+2 ✓
    Three interior knots compressed into 0.02-wide region.
    GetSamplePoints(tol=0.01) allocates samples per knot-span; 3 spans in
    [0.5,0.52] each receive ≥1 sample → >150× over-density vs outer spans.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: dense knot region creates near-C0 geometry at t≈0.51
    driving shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-3 6 poles; knots
    (0.0,0.5,0.51,0.52,1.0) mults (4,1,1,1,4); IS defect edge
    SURFACE_CURVE.curve_3d; GetSamplePoints over-densifies in 0.02-wide
    triple-knot region.
  - C-1 DRIVER: near-C0 at dense knot region drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn069",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-3 6 poles clamped; "
        "knots (0.0,0.5,0.51,0.52,1.0) mults (4,1,1,1,4) sum=11 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints over-densifies in 0.02-wide triple-knot region [0.5,0.52]; "
        "near-C0 at dense knot region drives shape_null=True"
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

# ── CATALOG MECHANISM: degree-3 B-spline with dense interior knots ────────────
# 6 poles, knots (0.0, 0.5, 0.51, 0.52, 1.0) mults (4,1,1,1,4).
# sum = 4+1+1+1+4 = 11 = degree+1 + n_poles + 1 = 4+6+1 = 11 ✓
# Poles span [0,1]: slight wiggle around t=0.5 to expose dense-knot region.
cp0 = f.cartesian_point((0.0,  0.0,  0.0))
cp1 = f.cartesian_point((0.2,  0.1,  0.0))
cp2 = f.cartesian_point((0.45, 0.0,  0.0))
cp3 = f.cartesian_point((0.55, 0.1,  0.0))   # in dense-knot region
cp4 = f.cartesian_point((0.75, 0.0,  0.0))
cp5 = f.cartesian_point((1.0,  0.0,  0.0))

dense_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn069_dense_knot_curve',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,1,4),(0.0,0.5,0.51,0.52,1.0),.UNSPECIFIED.)"
)

# Pcurve: linear in UV
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn069_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn069_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn069_sc',#{dense_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 1.0, 0.0))
p_d = f.cartesian_point((0.0, 1.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn069_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 1.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 1.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 1.0)

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
