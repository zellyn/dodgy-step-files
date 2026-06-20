"""Gn092 — ShapeAnalysis_Curve.GetSamplePoints offset-curve sample-density.

Catalog claim: OFFSET_CURVE wrapping a B-spline; sample density inherited
from base curve doesn't account for offset's local curvature change.
Degree-3 B-spline with 8 control points wrapped by OFFSET_CURVE with 1.5mm
offset in Z direction.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 8 control points (base).
    n=8, p=3 → n+p+1=12. Knots (0.0,0.25,0.5,0.75,1.0) mults (4,1,2,1,4)
    sum=12 ✓.
  - OFFSET_CURVE_3D wrapping the B-spline with offset_distance=1.5,
    ref_direction=(0,0,1).
    Sample density from the base curve is used for the offset curve;
    curvature concentration in the offset is missed.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the offset curve with insufficient sampling causes OCC
    shape analysis to produce null/empty result.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_CURVE_3D wrapping B_SPLINE_CURVE_WITH_KNOTS
    degree=3 8-pole; offset 1.5 in Z; IS defect edge SURFACE_CURVE.curve_3d;
    GetSamplePoints uses base-curve density → misses offset curvature extrema.
  - C-1 DRIVER: offset curve with bad sampling → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn092",
    defect=(
        "OFFSET_CURVE_3D wrapping B_SPLINE_CURVE_WITH_KNOTS degree=3 8-pole; "
        "offset_distance=1.5 ref_direction=(0,0,1); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints inherits base-curve sample density → misses offset curvature → shape_null=True"
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

# ── Base B-spline curve: degree 3, 8 CPs ─────────────────────────────────────
# n=8, p=3 → n+p+1=12. mults (4,1,2,1,4) sum=12 ✓; 5 distinct knots.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.5, 0.0))
cp2 = f.cartesian_point((2.0, 1.0, 0.0))
cp3 = f.cartesian_point((3.0, 0.5, 0.0))
cp4 = f.cartesian_point((4.0, 0.0, 0.0))   # high-curvature zone
cp5 = f.cartesian_point((5.0, 0.5, 0.0))
cp6 = f.cartesian_point((6.0, 0.5, 0.0))
cp7 = f.cartesian_point((7.0, 0.0, 0.0))

base_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn092_base',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},"
    f"#{cp4.eid},#{cp5.eid},#{cp6.eid},#{cp7.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,2,1,4),(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
)

# ── CATALOG MECHANISM: OFFSET_CURVE_3D wrapping the base B-spline ────────────
# offset_distance=1.5, self_intersect=.F., ref_direction=(0,0,1)
ref_dir = f.direction((0.0, 0.0, 1.0))
mech_3d = f._emit_raw(
    f"OFFSET_CURVE_3D('gn092_offset',#{base_bspline.eid},1.5,.F.,#{ref_dir.eid})"
)

# pcurve: simple line in 2D (healthy companion)
pp_s = f.cartesian_point((0.0, 0.0))
pp_e = f.cartesian_point((7.0, 0.0))
d2   = f.direction((1.0, 0.0))
v2   = f.vector(d2, 7.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn092_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn092_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn092_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p3_s = f.cartesian_point((0.0, 0.0, 0.0))
p3_e = f.cartesian_point((7.0, 0.0, 0.0))
vs = f.vertex_point(p3_s)
ve = f.vertex_point(p3_e)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn092_defect_edge',#{vs.eid},#{ve.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 7.5, -0.5, 0.0))
p_c = f.cartesian_point(( 7.5,  1.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 8.0)
e_right = mk_line_edge(v_b, v_c, ( 7.5,-0.5,0.0), (0.,1.,0.), ( 7.5,-0.5), (0.,1.), 2.0)
e_top   = mk_line_edge(v_c, v_d, ( 7.5, 1.5,0.0), (-1.,0.,0.),( 7.5, 1.5), (-1.,0.), 8.0)
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
