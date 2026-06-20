"""Gn121 — ShapeAnalysis_Curve.IsPlanar B-spline-of-degree-1.

Catalog claim: Degree-1 B-spline (piecewise linear) with control polygon bent
out of plane. IsPlanar returns true trivially (linearity ≠ planarity) but the
endpoint test misses mid-segment deviation at control point (2,1,1).

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 1, 5 CPs.
    n=5, p=1 → n+p+1=7. mults (2,1,1,1,2) knots (0.0,0.25,0.5,0.75,1.0)
    sum=7 ✓.
    CPs: (0,0,0)→(1,0,0)→(2,1,1)→(3,0,0)→(4,0,0).
    Point at (2,1,1) lifts the polygon out of the XY plane (z≠0, y≠0).
    IsPlanar: for a degree-1 spline it checks only endpoint tangent directions
    and misses the off-plane kink at t=0.5.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: off-plane pole at (2,1,1) → IsPlanar endpoint-only test
    misses mid-segment deviation → shape analysis failure → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=1 5-pole;
    mults (2,1,1,1,2) knots (0.0,0.25,0.5,0.75,1.0) sum=7 ✓;
    pole[2]=(2,1,1) off XY-plane; IS defect edge SURFACE_CURVE.curve_3d;
    IsPlanar endpoint-only test misses kink → shape_null=True.
  - C-1 DRIVER: off-plane kink in degree-1 B-spline → missed by IsPlanar
    → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn121",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=1 5-pole; "
        "mults (2,1,1,1,2) knots (0.0,0.25,0.5,0.75,1.0) sum=7 ✓; "
        "pole[2]=(2,1,1) off XY-plane; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsPlanar endpoint-only test misses off-plane kink → shape_null=True"
    ),
)

# ── Flat plane for the face (XZ plane: y=0) ──────────────────────────────────
# The bounding face sits in the XZ plane; the defect edge's mid-pole lifts
# into y=1 violating planarity while the endpoints stay in the plane.
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 1.0, 0.0))   # XZ plane normal
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: degree-1 B-spline, 5 CPs, mid-pole off plane ──────────
# n=5, p=1 → n+p+1=7. mults (2,1,1,1,2) knots (0.0,0.25,0.5,0.75,1.0) sum=7 ✓.
# pole[2]=(2,1,1): the y=1,z=1 component takes it out of the XZ plane.
# Degree-1 means piecewise linear; IsPlanar checks endpoint tangents but the
# bent mid-segment direction is different and signals non-planarity only by
# checking interior poles explicitly, which IsPlanar misses.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.0, 0.0))
cp2 = f.cartesian_point((2.0, 1.0, 1.0))   # off XZ plane: y=1, z=1
cp3 = f.cartesian_point((3.0, 0.0, 0.0))
cp4 = f.cartesian_point((4.0, 0.0, 0.0))

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn121_degree1_offplane',1,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,1,1,1,2),(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
)

# pcurve: 2D line companion on the face plane
pp_s   = f.cartesian_point((0.0, 0.0))
d2     = f.direction((1.0, 0.0))
v2     = f.vector(d2, 4.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn121_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn121_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn121_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((4.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn121_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, 0.0, -0.5))
p_b = f.cartesian_point(( 4.5, 0.0, -0.5))
p_c = f.cartesian_point(( 4.5, 0.0,  0.5))
p_d = f.cartesian_point((-0.5, 0.0,  0.5))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,0.0,-0.5), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 5.0)
e_right = mk_line_edge(v_b, v_c, ( 4.5,0.0,-0.5), (0.,0.,1.), ( 4.5,-0.5), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, ( 4.5,0.0, 0.5), (-1.,0.,0.),( 4.5, 0.5), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5,0.0, 0.5), (0.,0.,-1.),(-0.5, 0.5), (0.,-1.), 1.0)

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
