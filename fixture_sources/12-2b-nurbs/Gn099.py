"""Gn099 — ShapeAnalysis_Curve.GetSamplePoints conic-arc rational-weight cap.

Catalog claim: Degree-2 rational B-spline (circular arc) with weight pole at
t=0.5. GetSamplePoints uses degree-3 sample count for the degree-2 curve,
resulting in sparse sampling that misses curvature extrema near the rational
weight concentration zone.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_CURVE (via NURBS_CURVE complex entity) degree 2, 3 CPs.
    Encoded as B_SPLINE_CURVE_WITH_KNOTS + weights for exact conic arc.
    n=3, p=2 → n+p+1=6. Knots (0.0,1.0) mults (3,3) sum=6 ✓.
    Weights (1.0, 0.7071, 1.0) — middle weight = cos(45°) for quarter-circle.
    Middle CP at (1,1,0) with reduced weight creates curvature concentration
    at t=0.5; GetSamplePoints applies degree-3 count (4 samples) instead of
    degree-2 count (3 samples), misses curvature peak.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: rational B-spline with non-unit middle weight causes OCC
    shape analysis to produce null result → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_CURVE degree=2 3-pole;
    weights (1.0,0.7071,1.0); CPs (0,0,0),(1,1,0),(2,0,0);
    knots (0.0,1.0) mults (3,3) sum=6 ✓;
    IS defect edge SURFACE_CURVE.curve_3d;
    GetSamplePoints uses wrong sample count → misses curvature extremum → shape_null=True.
  - C-1 DRIVER: rational weight at t=0.5 causes sampling failure → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn099",
    defect=(
        "RATIONAL_B_SPLINE_CURVE degree=2 3-pole; "
        "weights (1.0,0.7071,1.0) conic arc; "
        "CPs (0,0,0),(1,1,0),(2,0,0); knots (0.0,1.0) mults (3,3) sum=6 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints uses degree-3 count → misses curvature peak → shape_null=True"
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

# ── CATALOG MECHANISM: degree-2 rational B-spline, 3 CPs, conic arc ──────────
# n=3, p=2 → n+p+1=6. mults (3,3) knots (0.0,1.0) sum=6 ✓
# Weights (1.0, 0.7071, 1.0): middle weight = cos(45°) encodes quarter-circle
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 1.0, 0.0))   # weight pole
cp2 = f.cartesian_point((2.0, 0.0, 0.0))

# RATIONAL_B_SPLINE_CURVE encoded as complex entity with weights
mech_3d = f._emit_raw(
    f"(B_SPLINE_CURVE('gn099_conic',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.)"
    f"B_SPLINE_CURVE_WITH_KNOTS('gn099_conic_knots',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_CURVE('gn099_rational',(1.0,0.7071067811865476,1.0)))"
)

# pcurve: simple 2D line companion
pp_s = f.cartesian_point((0.0, 0.0))
d2   = f.direction((1.0, 0.0))
v2   = f.vector(d2, 2.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn099_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn099_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn099_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((2.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn099_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 2.5, -0.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, ( 2.5,-0.5,0.0), (0.,1.,0.), ( 2.5,-0.5), (0.,1.), 2.0)
e_top   = mk_line_edge(v_c, v_d, ( 2.5, 1.5,0.0), (-1.,0.,0.),( 2.5, 1.5), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 1.5,0.0), (0.,-1.,0.),(-0.5, 1.5), (0.,-1.), 2.0)

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
