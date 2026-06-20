"""Gn114 — ShapeAnalysis_Curve.IsClosed knot-vector-not-symmetric.

Catalog claim: Closed B-spline curve (degree 3, 7 control points) with
asymmetric knot multiplicities at endpoints (multiplicity 2 at start, 2 at
end). Poles form a closed loop but knot vector lacks symmetry. IsClosed
incorrectly reports closed based on pole coincidence while downstream code
assumes symmetric knot structure.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 7 CPs.
    n=7, p=3 → n+p+1=11. mults (2,1,1,1,1,2) knots (0.0,0.2,0.4,0.6,0.8,1.0)
    sum=8 — only 8, not 11. Wait: 2+1+1+1+1+2=8. Need sum=11.
    Corrected: mults (2,1,1,1,1,2) sum=8; add more knots.
    Use n=7, p=3 → n+p+1=11. mults (3,1,1,1,1,3) knots (0.0,0.2,0.4,0.6,0.8,1.0)
    sum=3+1+1+1+1+3=10 — still not 11.
    Use mults (3,1,1,1,1,1,3) knots (0.0,0.167,0.333,0.5,0.667,0.833,1.0) sum=11 ✓.
    First pole == last pole (closed loop), mult 3 at start, mult 3 at end:
    this is symmetric. For asymmetric: mults (2,1,1,1,1,1,4) — but that
    changes the start side. Use (4,1,1,1,4) with 5 knots, n=8, p=3:
    n=8, p=3 → n+p+1=12. mults (4,1,1,1,1,4)=12 ✓ with 6 distinct knots.
    But catalog says 7 CPs, degree 3: n=7, p=3 → need sum=11.
    Use mults (3,1,1,1,1,1,3) knots (0.0,0.167,0.333,0.5,0.667,0.833,1.0)
    sum=11 ✓ — this is actually symmetric (3 at both ends).
    Asymmetric: change start mult to 2, end mult to 4:
    mults (2,1,1,1,1,1,4) sum=11 ✓.
    First and last poles coincident → closed loop, but knot mults differ
    (2 at start, 4 at end) causing asymmetric blending. IsClosed detects
    pole coincidence and reports closed; downstream assumes equal endpoint
    multiplicities and fails.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: pole-coincidence closed check ignores mult asymmetry (2 vs 4)
    → IsClosed reports closed while downstream logic fails → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3 7-pole;
    mults (2,1,1,1,1,1,4) knots (0.0,0.167,0.333,0.5,0.667,0.833,1.0) sum=11 ✓;
    first pole == last pole (closed loop); mult asymmetric (2 start, 4 end);
    IS defect edge SURFACE_CURVE.curve_3d;
    IsClosed reports closed from pole coincidence; downstream assumes symmetric
    mults → shape_null=True.
  - C-1 DRIVER: mult asymmetry at endpoints → downstream knot structure
    assumption violated → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn114",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3 7-pole; "
        "mults (2,1,1,1,1,1,4) knots (0.0,0.167,0.333,0.5,0.667,0.833,1.0) sum=11 ✓; "
        "first pole == last pole (closed loop); mult asymmetric (2 start, 4 end); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed reports closed via pole coincidence; downstream assumes symmetric "
        "mults → shape_null=True"
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

# ── CATALOG MECHANISM: degree-3 B-spline, 7 CPs, closed loop, asymmetric mults ──
# n=7, p=3 → n+p+1=11.
# mults (2,1,1,1,1,1,4) knots (0.0,0.167,0.333,0.5,0.667,0.833,1.0) sum=11 ✓.
# cp0 == cp6: first and last poles coincident → poles form a closed loop.
# Mult 2 at start, mult 4 at end: endpoint multiplicities differ (asymmetric).
# IsClosed sees cp0 ≈ cp6 and reports closed; downstream code that calls
# IsClosed then assumes symmetric endpoint mults for knot manipulation.
cp0 = f.cartesian_point((1.0,  0.5, 0.0))   # == cp6 (closed loop)
cp1 = f.cartesian_point((1.5,  1.0, 0.0))
cp2 = f.cartesian_point((2.0,  1.0, 0.0))
cp3 = f.cartesian_point((2.0,  0.0, 0.0))
cp4 = f.cartesian_point((1.5, -0.5, 0.0))
cp5 = f.cartesian_point((0.5,  0.0, 0.0))
cp6 = f.cartesian_point((1.0,  0.5, 0.0))   # == cp0

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn114_asym_mults',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid},#{cp6.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,1,1,1,1,1,4),(0.0,0.167,0.333,0.5,0.667,0.833,1.0),.UNSPECIFIED.)"
)

# pcurve: 2D line companion
pp_s   = f.cartesian_point((0.0, 0.0))
d2     = f.direction((1.0, 0.0))
v2     = f.vector(d2, 2.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn114_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn114_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn114_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((1.0, 0.5, 0.0))
p_end   = f.cartesian_point((1.0, 0.5, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn114_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -1.0, 0.0))
p_b = f.cartesian_point(( 2.5, -1.0, 0.0))
p_c = f.cartesian_point(( 2.5,  1.5, 0.0))
p_d = f.cartesian_point((-0.5,  1.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-1.0,0.0), (1.,0.,0.), (-0.5,-1.0), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, ( 2.5,-1.0,0.0), (0.,1.,0.), ( 2.5,-1.0), (0.,1.), 2.5)
e_top   = mk_line_edge(v_c, v_d, ( 2.5, 1.5,0.0), (-1.,0.,0.),( 2.5, 1.5), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 1.5,0.0), (0.,-1.,0.),(-0.5, 1.5), (0.,-1.), 2.5)

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
