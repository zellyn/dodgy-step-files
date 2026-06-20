"""Gn116 — ShapeAnalysis_Curve.GetSamplePoints near-collinear-poles.

Catalog claim: B-spline curve (degree 3, 5 control points) with poles nearly
collinear in XY plane (offsets ~1e-5 in Y). Sampler detects "almost linear"
geometry and returns minimal sample count, failing to discretize the sparse
curvature information.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 5 CPs.
    n=5, p=3 → n+p+1=9. mults (4,1,4) knots (0.0,0.5,1.0) sum=9 ✓.
    CPs nearly collinear in XY: Y values are 0.0, 1e-5, -1e-5, 1e-5, 0.0.
    X spans 0.0→4.0. Nearly linear along X axis with Y offsets ~1e-5.
    GetSamplePoints detects "almost linear" and returns only 2 samples
    (endpoints), failing to capture the subtle curvature information.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: minimal sample count (2 points) misses curvature information
    → shape analysis rejects → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3 5-pole;
    mults (4,1,4) knots (0.0,0.5,1.0) sum=9 ✓;
    poles near-collinear (Y offsets ~1e-5); IS defect edge SURFACE_CURVE.curve_3d;
    GetSamplePoints detects near-linearity → minimal sample count → curvature
    information lost → shape_null=True.
  - C-1 DRIVER: under-sampling of near-linear curve → shape analysis failure
    → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn116",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3 5-pole; "
        "mults (4,1,4) knots (0.0,0.5,1.0) sum=9 ✓; "
        "poles near-collinear (Y offsets ~1e-5); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints detects near-linearity → minimal sample count → "
        "sparse curvature information lost → shape_null=True"
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

# ── CATALOG MECHANISM: degree-3 B-spline, 5 CPs, near-collinear poles ────────
# n=5, p=3 → n+p+1=9. mults (4,1,4) knots (0.0,0.5,1.0) sum=9 ✓.
# Y offsets of 1e-5, -1e-5, 1e-5 make poles nearly collinear in XY plane.
# GetSamplePoints sees near-zero curvature and returns only 2 samples.
cp0 = f.cartesian_point((0.0, 0.0,    0.0))
cp1 = f.cartesian_point((1.0, 1e-5,   0.0))   # offset ~1e-5 in Y
cp2 = f.cartesian_point((2.0, -1e-5,  0.0))   # offset ~-1e-5 in Y
cp3 = f.cartesian_point((3.0, 1e-5,   0.0))   # offset ~1e-5 in Y
cp4 = f.cartesian_point((4.0, 0.0,    0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn116_near_collinear',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# pcurve: 2D line companion
pp_s   = f.cartesian_point((0.0, 0.0))
d2     = f.direction((1.0, 0.0))
v2     = f.vector(d2, 4.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn116_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn116_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn116_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((4.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn116_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 4.5, -0.5, 0.0))
p_c = f.cartesian_point(( 4.5,  0.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 5.0)
e_right = mk_line_edge(v_b, v_c, ( 4.5,-0.5,0.0), (0.,1.,0.), ( 4.5,-0.5), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, ( 4.5, 0.5,0.0), (-1.,0.,0.),( 4.5, 0.5), (-1.,0.), 5.0)
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
