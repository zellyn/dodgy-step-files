"""Gn094 — ShapeAnalysis_Curve.IsClosed degree-0-curve.

Catalog claim: B-spline of degree 0 (piecewise constant); IsClosed reports
false but the curve has no meaningful direction, so closed-vs-open is
ill-defined. Degree-0 B-spline with 3 control points and knot vector (2,1,1,2)
creating 3 constant-value intervals — but wait: for degree-0, n poles,
sum(mults) = n + 0 + 1 = n+1. With mults (2,1,1,2): sum=6, so n=5 poles.
Catalog note "(2,1,1,2)" with 3 CPs doesn't add up; we use n=5 for consistency.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 0, 5 control points.
    n=5, p=0 → n+p+1=6. mults (2,1,1,2) sum=6 ✓. 4 distinct knots.
    Degree-0 curves are piecewise constant; IsClosed checks first==last CP
    (false for distinct points) but "closed" is meaningless for a constant
    curve. IsClosed returns false, but the degenerate degree causes
    downstream failure in shape processing.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: degree-0 curve as edge geometry causes OCC shape processing
    to fail (no tangent direction) → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=0 5-pole;
    knots (0.0,0.33,0.67,1.0) mults (2,1,1,2) sum=6 ✓;
    IS defect edge SURFACE_CURVE.curve_3d;
    IsClosed ill-defined for degree-0 constant curve.
  - C-1 DRIVER: degree-0 curve as edge geometry → no tangent → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn094",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=0 5-pole piecewise-constant; "
        "knots (0.0,0.33,0.67,1.0) mults (2,1,1,2) sum=6 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed ill-defined for degree-0 → OCC processing failure → shape_null=True"
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

# ── CATALOG MECHANISM: degree-0 B-spline, 5 CPs ──────────────────────────────
# n=5, p=0 → n+p+1=6. mults (2,1,1,2) sum=6 ✓. 4 distinct knot values.
# Piecewise constant: each interval holds the value of its control point.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.0, 0.0))
cp2 = f.cartesian_point((2.0, 0.0, 0.0))
cp3 = f.cartesian_point((3.0, 0.0, 0.0))
cp4 = f.cartesian_point((3.5, 0.0, 0.0))   # distinct final point

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn094_deg0',0,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,1,1,2),(0.0,0.33,0.67,1.0),.UNSPECIFIED.)"
)

# pcurve: simple 2D line companion
pp_s = f.cartesian_point((0.0, 0.0))
pp_e = f.cartesian_point((3.5, 0.0))
d2   = f.direction((1.0, 0.0))
v2   = f.vector(d2, 3.5)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn094_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn094_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn094_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((3.5, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn094_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 4.0, -0.5, 0.0))
p_c = f.cartesian_point(( 4.0,  0.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 4.5)
e_right = mk_line_edge(v_b, v_c, ( 4.0,-0.5,0.0), (0.,1.,0.), ( 4.0,-0.5), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, ( 4.0, 0.5,0.0), (-1.,0.,0.),( 4.0, 0.5), (-1.,0.), 4.5)
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
