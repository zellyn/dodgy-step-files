"""Gn102 — ShapeUpgrade_ConvertCurve2dToBezier degree-elevation-skip.

Catalog claim: Degree-0 B-spline (piecewise constant function). When
degree-elevation code computes target_degree - 0, it produces negative
values in certain code paths, causing integer underflow or division errors.
Special-case handling for low-degree curves is missing.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 0, 3 CPs (piecewise constant).
    n=3, p=0 → n+p+1=4. mults (1,1,1,1) knots (0.0,0.333,0.667,1.0) sum=4 ✓.
    Constant segments: (0,0,0) for t∈[0,0.333), (1,0,0) for t∈[0.333,0.667),
    (2,0,0) for t∈[0.667,1.0].
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: degree-0 B-spline triggers integer underflow in degree-elevation
    code → shape processing fails → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=0 3-pole piecewise-constant;
    mults (1,1,1,1) knots (0.0,0.333,0.667,1.0) sum=4 ✓;
    IS defect edge SURFACE_CURVE.curve_3d;
    ConvertCurve2dToBezier degree-elevation underflow → shape_null=True.
  - C-1 DRIVER: degree-0 B-spline elevation → integer underflow → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn102",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=0 3-pole piecewise-constant; "
        "mults (1,1,1,1) knots (0.0,0.333,0.667,1.0) sum=4 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "ConvertCurve2dToBezier degree-elevation underflow → shape_null=True"
    ),
)

# ── Flat plane for the face ───────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: degree-0 B-spline, 3 CPs, piecewise constant ──────────
# n=3, p=0 → n+p+1=4. mults (1,1,1,1) knots (0.0,0.333,0.667,1.0) sum=4 ✓
# Each CP is "active" for one segment interval — jump discontinuities at knots.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.0, 0.0))
cp2 = f.cartesian_point((2.0, 0.0, 0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn102_deg0',0,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(1,1,1,1),(0.0,0.3333333333333333,0.6666666666666666,1.0),.UNSPECIFIED.)"
)

# pcurve: simple 2D line companion
pp_s = f.cartesian_point((0.0, 0.0))
d2   = f.direction((1.0, 0.0))
v2   = f.vector(d2, 2.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn102_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn102_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn102_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((2.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn102_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 2.5, -0.5, 0.0))
p_c = f.cartesian_point(( 2.5,  0.5, 0.0))
p_d = f.cartesian_point((-0.5,  0.5, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_line_edge(vs_, ve_, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3_ = f.vector(d3e, length)
    l3  = f.line(p3e, v3_)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs_.eid},#{ve_.eid},#{sc_.eid},.T.)")

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, ( 2.5,-0.5,0.0), (0.,1.,0.), ( 2.5,-0.5), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, ( 2.5, 0.5,0.0), (-1.,0.,0.),( 2.5, 0.5), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 0.5,0.0), (0.,-1.,0.),(-0.5, 0.5), (0.,-1.), 1.0)

outer_loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
inner_loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
])

outer_bound = f.face_outer_bound(outer_loop)
inner_bound = f._emit_raw(f"FACE_BOUND('inner_bound',#{inner_loop.eid},.T.)")

face  = f.advanced_face([outer_bound, inner_bound], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
