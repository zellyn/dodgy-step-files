"""Gn084 — ShapeAnalysis_Curve.IsPlanar tolerance-zero.

Catalog claim: IsPlanar called with tolerance=0 (strict); implementation uses
tolerance > 0 comparison and returns false for any non-trivial floating-point
deviation.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 2, 5 control points.
    n=5, p=2 → n+p+1=8. Knots (0.0,0.5,1.0) mults (3,2,3) sum=8 ✓.
    Control points near XY plane: z-values alternately +1e-12 and -1e-12,
    so the curve is nearly but not exactly planar.
    IsPlanar(tol=0) fails because the implementation uses (deviation > tol)
    which is (1e-12 > 0) = true → reports not planar.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the near-planar B-spline with z-jitter ±1e-12 on a flat plane
    creates a 3D/2D geometry mismatch that drives shape_null=True via edge
    topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=2 5-pole z≈±1e-12;
    IS defect edge SURFACE_CURVE.curve_3d; IsPlanar(tol=0) → (1e-12 > 0) true
    → reports non-planar; strict tolerance-zero logic fails near-planar curve.
  - C-1 DRIVER: z-jitter on flat plane causes 3D/pcurve mismatch → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn084",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=2 5-pole near-XY-plane z=±1e-12; "
        "knots (0.0,0.5,1.0) mults (3,2,3) sum=8 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsPlanar(tol=0) uses (deviation > tol) → 1e-12 > 0 = true → reports not planar; "
        "strict tolerance-zero logic fails for floating-point near-planar curve; "
        "z-jitter on flat plane causes 3D/pcurve mismatch → shape_null=True"
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

# ── CATALOG MECHANISM: B-spline degree 2, z-values ±1e-12 ────────────────────
# n=5, p=2 → n+p+1=8. knots (0.0,0.5,1.0) mults (3,2,3) sum=8 ✓
# x: 0.0, 0.25, 0.5, 0.75, 1.0 (along edge of unit square)
# z: alternating ±1e-12 — triggers IsPlanar(tol=0) failure
cp0 = f.cartesian_point((0.0,  0.0,  1e-12))
cp1 = f.cartesian_point((0.25, 0.0, -1e-12))
cp2 = f.cartesian_point((0.5,  0.0,  1e-12))
cp3 = f.cartesian_point((0.75, 0.0, -1e-12))
cp4 = f.cartesian_point((1.0,  0.0,  1e-12))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn084_near_planar',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# pcurve: corresponding parameter-space line at v=0 (y=0 on plane)
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.75, 0.0))
pp4 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn084_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn084_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn084_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn084_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
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
    f"EDGE_CURVE('gn084_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_defect.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
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
