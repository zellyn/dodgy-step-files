"""Gn128 — ShapeAnalysis_Curve.IsClosed B-spline with-identical-knots-different-poles.

Catalog claim: Periodic B-spline with knot parameters identical at boundaries
but control poles differing by 1e-3. IsClosed checks knot equality only and
reports true, but geometry gap persists at closure point.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree=3, 5 poles, periodic knot vector
    where first pole = (0,0,0) and last pole = (0,0.001,0) — differ by 1e-3
    in Y. Knot range [0,1] is identical at both boundary parameter values.
    IsClosed tests only that first_knot_value == last_knot_value (true here),
    but never tests pole distance. Reports closed=True while a geometric gap
    of 1e-3 remains. The B_SPLINE_CURVE_WITH_KNOTS IS the
    SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: knot-equal but pole-different → IsClosed false positive
    → geometric gap 1e-3 → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3; poles
    [(0,0,0),(1,1,0),(2,1,0),(3,0,0),(4,0,0)]; first≠last by 1e-3 in Y
    (pole[0]=(0,0,0), pole[4]=(0,0.001,0)); mults (4,1,4) knots (0.0,0.5,1.0);
    IS defect edge SURFACE_CURVE.curve_3d;
    IsClosed knot-equality check passes → geometric gap persists → shape_null=True.
  - C-1 DRIVER: pole gap 1e-3 hidden by knot-only closure test → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn128",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3; poles (0,0,0)(1,1,0)(2,1,0)(3,0,0)(0,0.001,0); "
        "first≠last by 1e-3 in Y; mults (4,1,4) knots (0.0,0.5,1.0); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed knot-equality check passes → geometric gap 1e-3 persists → shape_null=True"
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

# ── CATALOG MECHANISM: B-spline curve, knot-equal but pole-different ends ────
# degree=3, 5 poles.  mults (4,1,4) → sum=9 → n+p+1=5+3+1=9 ✓.
# pole[0]=(0,0,0), pole[4]=(0,0.001,0) — gap of 1e-3 in Y at closure.
q0 = f.cartesian_point((0.0, 0.000, 0.0))  # first pole
q1 = f.cartesian_point((1.0, 1.000, 0.0))
q2 = f.cartesian_point((2.0, 1.000, 0.0))
q3 = f.cartesian_point((3.0, 0.000, 0.0))
q4 = f.cartesian_point((0.0, 0.001, 0.0))  # last pole — differs by 1e-3

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn128_pole_gap_closure',3,"
    f"(#{q0.eid},#{q1.eid},#{q2.eid},#{q3.eid},#{q4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# pcurve: 2D companion — straight line in UV from (0,0) to (1,0).
pp0 = f.cartesian_point((0.0, 0.0))
dp  = f.direction((1.0, 0.0))
vp  = f.vector(dp, 1.0)
lp  = f.line(pp0, vp)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn128_pcdef',(#{lp.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn128_pc',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn128_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

v_start = f.vertex_point(q0)
v_end   = f.vertex_point(q4)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn128_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 3.5, -0.5, 0.0))
p_c = f.cartesian_point(( 3.5,  1.5, 0.0))
p_d = f.cartesian_point((-0.5,  1.5, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_line_edge(vs_, ve_, p3c, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3c)
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 4.0)
e_right = mk_line_edge(v_b, v_c, ( 3.5,-0.5,0.), (0.,1.,0.), ( 3.5,-0.5), (0.,1.), 2.0)
e_top   = mk_line_edge(v_c, v_d, ( 3.5, 1.5,0.), (-1.,0.,0.),( 3.5, 1.5), (-1.,0.), 4.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 1.5,0.), (0.,-1.,0.),(-0.5, 1.5), (0.,-1.), 2.0)

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
