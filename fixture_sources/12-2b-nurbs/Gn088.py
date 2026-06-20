"""Gn088 — ShapeAnalysis_Curve.IsClosed B-spline open-via-knots.

Catalog claim: B-spline whose control polygon closes but the knot vector is
clamped with multiplicity degree+1 at endpoints (intentionally open); IsClosed
reports closed based on polygon instead of knot structure.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 6 control points.
    n=6, p=3 → n+p+1=6+3+1=10. Knots (0.0,0.33,0.67,1.0) mults (4,1,1,4)
    sum=10 ✓. First and last control points coincident at (0,0,0);
    knot multiplicities (4,…,4) clamp endpoints — curve is open despite
    polygon forming a closed loop. IsClosed checks if first==last CP
    (polygon closure) rather than evaluating curve(t_start)==curve(t_end),
    falsely reporting closed → fails downstream processing → empty result.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: the open-but-polygon-closed B-spline on a plane creates
    a topology inconsistency (edge start != edge end in 3D) that drives
    shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3 6-pole closed-polygon;
    knots (0.0,0.33,0.67,1.0) mults (4,1,1,4) sum=10 ✓; first==last CP at origin;
    IS defect edge SURFACE_CURVE.curve_3d; IsClosed checks CP polygon not curve
    endpoints — false closed report for clamped-knot open curve.
  - C-1 DRIVER: open curve with closed polygon causes vertex mismatch → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn088",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3 6-pole closed-polygon open-via-knots; "
        "first==last CP at (0,0,0); "
        "knots (0.0,0.33,0.67,1.0) mults (4,1,1,4) sum=10 ✓; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed checks CP polygon not curve endpoints → false closed report; "
        "clamped-knot open curve reported as closed → empty result; "
        "open curve with closed polygon causes vertex mismatch → shape_null=True"
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

# ── CATALOG MECHANISM: degree-3 B-spline, 6 CPs, first==last at origin ───────
# n=6, p=3 → n+p+1=10. knots (0.0,0.33,0.67,1.0) mults (4,1,1,4) sum=10 ✓
# Control polygon forms a closed loop: CP0==CP5==(0,0,0)
# But clamped knots (mult=4 at ends) make it an OPEN curve:
#   curve(0) = CP0 = (0,0,0), curve(1) is blend of last 4 CPs ≠ (0,0,0) exactly
# IsClosed() sees CP0==CP5 → reports closed (false positive)
cp0 = f.cartesian_point((0.0,  0.0,  0.0))   # first CP (coincident with last)
cp1 = f.cartesian_point((1.0,  0.0,  0.0))
cp2 = f.cartesian_point((1.0,  1.0,  0.0))
cp3 = f.cartesian_point((0.0,  1.0,  0.0))
cp4 = f.cartesian_point((-0.3, 0.5,  0.0))
cp5 = f.cartesian_point((0.0,  0.0,  0.0))   # last CP == first CP (polygon closes)

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn088_open_polygon_closed',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,0.33,0.67,1.0),.UNSPECIFIED.)"
)

# pcurve: corresponding 2D curve on the plane
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((1.0,  0.0))
pp2 = f.cartesian_point((1.0,  1.0))
pp3 = f.cartesian_point((0.0,  1.0))
pp4 = f.cartesian_point((-0.3, 0.5))
pp5 = f.cartesian_point((0.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn088_pc',3,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,0.33,0.67,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn088_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn088_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn088_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Use same vertex for start and end (polygon says closed, but curve is open)
p_seam = f.cartesian_point((0.0, 0.0, 0.0))
v_seam = f.vertex_point(p_seam)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn088_defect_edge',#{v_seam.eid},#{v_seam.eid},#{sc_defect.eid},.T.)"
)

# Build a simple square outer loop on the plane to anchor the face
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 1.5, -0.5, 0.0))
p_c = f.cartesian_point(( 1.5,  1.5, 0.0))
p_d = f.cartesian_point((-0.5,  1.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (0.0, 0.0), (1.,0.), 2.0)
e_right = mk_line_edge(v_b, v_c, ( 1.5,-0.5,0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 2.0)
e_top   = mk_line_edge(v_c, v_d, ( 1.5, 1.5,0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 2.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 1.5,0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 2.0)

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
