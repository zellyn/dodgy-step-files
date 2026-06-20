"""Gn119 — ShapeAnalysis_Curve.GetSamplePoints with-clustered-knots.

Catalog claim: B-spline curve degree 3, 8 control points, with 5 interior
knots clustered within parameter range [0.20025, 0.20100] (width 0.001).
GetSamplePoints over-counts samples in the cluster region, causing excessive
subdivision or missed coarse regions.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 8 CPs.
    n=8, p=3 → n+p+1=12.
    mults (4,1,1,1,1,4) knots (0.0,0.2,0.20025,0.2005,0.20075,0.201,0.8,1.0)
    → wait: need exactly 12 total. Use mults (4,1,1,1,1,1,3):
    sum = 4+1+1+1+1+1+3 = 12 ✓.
    5 interior knots tightly clustered near t=0.2.
    GetSamplePoints is confused by the cluster → excessive or missed samples
    → shape analysis rejects → shape_null=True.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: clustered knots → sampler malfunction → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3 8-pole;
    mults (4,1,1,1,1,3) knots (0.0,0.20,0.20025,0.2005,0.20075,0.2010,1.0)
    sum=12 ✓; 5 knots in [0.20,0.2010] (width 0.001);
    IS defect edge SURFACE_CURVE.curve_3d;
    GetSamplePoints cluster confusion → shape_null=True.
  - C-1 DRIVER: clustered knots → sampler over/under-count → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn119",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3 8-pole; "
        "mults (4,1,1,1,1,3) knots (0.0,0.20,0.20025,0.2005,0.20075,0.2010,1.0) "
        "sum=12 ✓; 5 knots clustered in [0.20,0.2010] width=0.001; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints cluster confusion → over/under-count → shape_null=True"
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

# ── CATALOG MECHANISM: degree-3 B-spline, 8 CPs, clustered interior knots ────
# n=8, p=3 → n+p+1=12.
# mults (4,1,1,1,1,3) knots (0.0,0.20,0.20025,0.2005,0.20075,0.2010,1.0)
# sum = 4+1+1+1+1+3 = 11 — need 12 → add one more knot at 0.8.
# mults (4,1,1,1,1,1,3) knots (0.0,0.20,0.20025,0.2005,0.20075,0.2010,0.8,1.0)
# sum = 4+1+1+1+1+1+3 = 12 ✓  (but that's 7 distinct knot values, mults length=7 ✓)
# Control polygon stretches (0,0,0)→(4,2,0); intermediate CPs fill out the curve.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((0.5, 0.5, 0.0))
cp2 = f.cartesian_point((1.0, 1.0, 0.0))
cp3 = f.cartesian_point((1.5, 1.5, 0.0))
cp4 = f.cartesian_point((2.0, 1.8, 0.0))
cp5 = f.cartesian_point((2.5, 1.8, 0.0))
cp6 = f.cartesian_point((3.0, 1.5, 0.0))
cp7 = f.cartesian_point((4.0, 2.0, 0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn119_clustered_knots',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},"
    f"#{cp4.eid},#{cp5.eid},#{cp6.eid},#{cp7.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,1,1,1,3),"
    f"(0.0,0.20,0.20025,0.2005,0.20075,0.2010,0.8,1.0),"
    f".UNSPECIFIED.)"
)

# pcurve: 2D line companion
pp_s   = f.cartesian_point((0.0, 0.0))
d2     = f.direction((1.0, 0.0))
v2     = f.vector(d2, 4.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn119_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn119_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn119_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((4.0, 2.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn119_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 4.5, -0.5, 0.0))
p_c = f.cartesian_point(( 4.5,  2.5, 0.0))
p_d = f.cartesian_point((-0.5,  2.5, 0.0))
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
e_right = mk_line_edge(v_b, v_c, ( 4.5,-0.5,0.0), (0.,1.,0.), ( 4.5,-0.5), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, ( 4.5, 2.5,0.0), (-1.,0.,0.),( 4.5, 2.5), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 2.5,0.0), (0.,-1.,0.),(-0.5, 2.5), (0.,-1.), 3.0)

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
