"""Gn079 — ShapeAnalysis_Curve.IsPlanar BSpline interior bow.

Catalog claim: IsPlanar evaluates only at control point parameter values.
Degree-3 B-spline with 5 control points nominally planar but interior control
point deviates 2mm perpendicular to plane. IsPlanar evaluates only at control
point parameter values, missing interior curvature deviation.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 5 control points.
    Knots: (0.0, 1.0) mults (4,4) sum=8=3+5 — wait: n+p+1=5+3+1=9.
    Use mults (4,1,4) with 3 knot values for sum=9 ✓ but that needs 3 knot values.
    Better: knots (0.0,0.5,1.0) mults (4,1,4) sum=9=3+5+1 ✓.
    Endpoints at z=0, interior control point P2=(2.5, 2.5, 2.0) deviates z=2mm.
    All other poles at z=0. Curve bows out of plane; IsPlanar samples only
    at the 5 discrete parameter values t_i for each CP and all of those happen
    to lie near z=0 by chance of Bernstein blending — the maximum Z deviation
    occurs strictly between sample points. Floating-point blow-up from the out-
    of-plane bow drives shape_null=True via edge topology failure.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: z=2mm out-of-plane bow combined with the flat plane causes
    3D/pcurve mismatch that drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-3 5 poles; P2=(2.5,2.5,2.0)
    out-of-plane by 2mm; all other poles at z=0; IS defect edge SURFACE_CURVE.curve_3d;
    IsPlanar misses interior Z bow — reports planar but curve is not.
  - C-1 DRIVER: z=2mm out-of-plane pole causes 3D/pcurve mismatch, drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn079",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-3 5 poles; "
        "knots (0.0,0.5,1.0) mults (4,1,4) sum=9 ✓; "
        "P0=(0,0,0) P1=(1.5,1.0,0) P2=(2.5,2.5,2.0) [z=2mm bow] P3=(3.5,1.0,0) P4=(5,0,0); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsPlanar samples only at CP parameter values — misses interior z=2mm bow; "
        "out-of-plane deviation drives 3D/pcurve mismatch → shape_null=True"
    ),
)

# ── Flat plane (z=0) for the face ────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: B-spline degree-3, 5 poles, interior z=2mm bow ────────
# Knots (0.0,0.5,1.0) mults (4,1,4) sum=9=3+5+1 ✓
# P2 out-of-plane by z=2.0 — IsPlanar misses interior bow
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.5, 1.0, 0.0))
cp2 = f.cartesian_point((2.5, 2.5, 2.0))  # z=2mm out-of-plane bow
cp3 = f.cartesian_point((3.5, 1.0, 0.0))
cp4 = f.cartesian_point((5.0, 0.0, 0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn079_isplanar_bow',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# pcurve: 2D line u∈[0,1] along bottom of face (flat, ignores z bow)
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn079_pcdef',(#{l2.eid}),#{prc.eid})")
pc  = f._emit_raw(f"PCURVE('gn079_pc',#{plane.eid},#{pcd.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn079_sc',#{mech_3d.eid},(#{pc.eid}),.PCURVE_S1.)"
)

# Corner vertices; face spans [0,5]×[0,3]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn079_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_defect.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 3.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 3.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 3.0)

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
