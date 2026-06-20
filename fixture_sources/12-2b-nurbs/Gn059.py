"""Gn059 — ShapeAnalysis_Curve.FillBndBox SearchForExtremum drift.

Catalog claim: Non-uniform B-spline with sharp peak at u=0.5. Fixed-step
extremum search overshoots peak; bbox too small at cusp. Captures defect in
FillBndBox where SearchForExtremum skips the actual extremum due to coarse
step size.

OCC behavior: loads and returns shape. Expected: occt=shape(1)/shape(1).

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree-2, 5 control points.
    Non-uniform knots: (0.0, 0.4, 0.6, 1.0) mults (3,1,1,3) sum=8=2+5+1 ✓
    Sharp peak at u=0.5: CP2=(0.5, 10.0, 0.0) — extreme Y excursion.
    Adjacent CPs at Y=0 create cusp that fixed-step SearchForExtremum
    overshoots, reporting bbox Y_max too small.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - LOAD DRIVER: shape_null=False (load==ok per catalog); valid knot structure
    allows OCC to read the shape; FillBndBox SearchForExtremum misses peak but
    does not prevent load.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS non-uniform knots, sharp peak
    at u=0.5 (Y=10.0); IS defect edge SURFACE_CURVE.curve_3d; FillBndBox
    SearchForExtremum coarse step drifts past extremum, underreporting bbox.
  - LOAD DRIVER: valid NURBS — shape loads successfully (shape_null=False).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn059",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-2 5 poles; "
        "non-uniform knots (0.0,0.4,0.6,1.0) mults (3,1,1,3) sum=8 ✓; "
        "sharp peak at u=0.5 CP2=(0.5,10.0,0.0); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "FillBndBox SearchForExtremum coarse step overshoots peak — "
        "bbox Y_max reported too small; shape loads ok (shape_null=False)"
    ),
)

# ── Flat plane for the face ──────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: non-uniform B-spline with sharp peak at u=0.5 ─────────
# degree-2, 5 CPs. Non-uniform knots cluster around u=0.5.
# CP2 at Y=10.0 creates extreme cusp; adjacent CPs at Y=0.
# Knots (0.0,0.4,0.6,1.0) mults (3,1,1,3): sum=8=2+5+1 ✓
bc0 = f.cartesian_point((0.0,  0.0,  0.0))
bc1 = f.cartesian_point((0.25, 0.0,  0.0))
bc2 = f.cartesian_point((0.5,  10.0, 0.0))   # extreme peak: SearchForExtremum drifts past
bc3 = f.cartesian_point((0.75, 0.0,  0.0))
bc4 = f.cartesian_point((1.0,  0.0,  0.0))

bspline_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn059_peak_curve',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,1,3),(0.0,0.4,0.6,1.0),.UNSPECIFIED.)"
)

# Pcurve for the defect edge (linear in UV, U from 0→1, V=0)
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn059_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn059_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn059_sc',#{bspline_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0,  0.0, 0.0))
p_b = f.cartesian_point((1.0,  0.0, 0.0))
p_c = f.cartesian_point((1.0, 10.0, 0.0))
p_d = f.cartesian_point((0.0, 10.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn059_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0,  0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 10.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 10.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 10.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 10.0)

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
