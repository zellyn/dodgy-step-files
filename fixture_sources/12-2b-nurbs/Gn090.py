"""Gn090 — ShapeAnalysis_Curve.IsPlanar Z-NaN.

Catalog claim: B-spline with one control point having Z=1.0E+100 (simulating
NaN); IsPlanar's pole sampling produces a huge/NaN result, which IEEE
compare-with-zero returns false → "is planar" reported.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 6 control points.
    CP index 3 has Z=1.0E+100 (extreme/NaN-proxy).
    n=6, p=3 → n+p+1=10. Knots (0.0,0.25,0.5,1.0) mults (4,1,1,4) sum=10 ✓.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the huge Z coordinate on one pole causes OCC shape loading to
    produce null / empty result via topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3 6-pole; CP[3] Z=1E100;
    IS defect edge SURFACE_CURVE.curve_3d; IsPlanar pole-sampling hits 1E100 →
    false "planar" report (NaN-proxy behavior).
  - C-1 DRIVER: extreme Z pole causes degenerate shape → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn090",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3 6-pole; CP[3] Z=1.0E+100 (NaN-proxy); "
        "knots (0.0,0.25,0.5,1.0) mults (4,1,1,4) sum=10 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsPlanar pole-sampling hits 1E100 → false planar report → empty result"
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

# ── CATALOG MECHANISM: degree-3 B-spline, 6 CPs, CP[3] has Z=1E100 ───────────
# n=6, p=3 → n+p+1=10. knots (0.0,0.25,0.5,1.0) mults (4,1,1,4) sum=10 ✓
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.0, 0.0))
cp2 = f.cartesian_point((2.0, 0.0, 0.0))
cp3 = f.cartesian_point((3.0, 0.0, 1.0E+100))   # extreme Z — NaN-proxy
cp4 = f.cartesian_point((4.0, 0.0, 0.0))
cp5 = f.cartesian_point((5.0, 0.0, 0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn090_z_nan',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,0.25,0.5,1.0),.UNSPECIFIED.)"
)

# pcurve: corresponding 2D curve on the plane (healthy, no extreme coords)
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((1.0, 0.0))
pp2 = f.cartesian_point((2.0, 0.0))
pp3 = f.cartesian_point((3.0, 0.0))
pp4 = f.cartesian_point((4.0, 0.0))
pp5 = f.cartesian_point((5.0, 0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn090_pc',3,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,0.25,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn090_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn090_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn090_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Vertices at the two (degenerate) endpoints
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((5.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn090_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer square loop anchoring the face ─────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 5.5, -0.5, 0.0))
p_c = f.cartesian_point(( 5.5,  0.5, 0.0))
p_d = f.cartesian_point((-0.5,  0.5, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 6.0)
e_right = mk_line_edge(v_b, v_c, ( 5.5,-0.5,0.0), (0.,1.,0.), ( 5.5,-0.5), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, ( 5.5, 0.5,0.0), (-1.,0.,0.),( 5.5, 0.5), (-1.,0.), 6.0)
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
