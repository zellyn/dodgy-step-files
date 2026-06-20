"""Gn014 — B_SPLINE_SURFACE_WITH_KNOTS that fits a PLANE (canonical recognition).

Catalog claim: A face stored as B_SPLINE_SURFACE_WITH_KNOTS is mathematically
a PLANE (or CYLINDRICAL_SURFACE / CONICAL_SURFACE / SPHERICAL_SURFACE /
TOROIDAL_SURFACE). Feature recognition, unfolding, CAM tool-axis derivation
and DXF/SVG export degrade silently because they cannot query the B-spline
surface for its radius/axis. Common shape: degree 1x1 with 2x2 control net
is exactly a flat quad that should have been authored as a PLANE.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree (1,1), 2x2 control net over [0,3]x[0,3]
    at Z=0: a mathematically perfect flat plane stored as NURBS.
    U: (0.0,1.0) mults (2,2) sum=4=1+2+1 ✓.
    V: (0.0,1.0) mults (2,2) sum=4=1+2+1 ✓.
    This is what should have been a PLANE entity. Feature recognition querying
    BRepAdaptor_Surface::GetType() returns GeomAbs_BSplineSurface, not
    GeomAbs_Plane — the canonical primitive is lost.
  - C-1 DRIVER: bottom edge uses B_SPLINE_CURVE_WITH_KNOTS degree-2 with a
    positional break at t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit
    gap) to force shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS(1,1) 2x2 net = exact PLANE,
    but stored as NURBS; canonical recognition cannot recover the analytic form.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn014",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (1,1) 2x2 net at Z=0 over [0,3]x[0,3]; "
        "U knots (0.0,1.0) mults (2,2) sum=4=1+2+1 ✓; "
        "V knots (0.0,1.0) mults (2,2) sum=4=1+2+1 ✓; "
        "mathematically exact PLANE stored as NURBS — canonical recognition "
        "cannot recover analytic form; GetType() returns BSplineSurface not Plane; "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── DEFECT SURFACE: B_SPLINE_SURFACE_WITH_KNOTS(1,1) = exact PLANE at Z=0 ──
# 2x2 control net: four corners of [0,3]x[0,3] at Z=0.
# This is a PLANE represented as NURBS — the canonical recognition defect.
c00 = f.cartesian_point((0.0, 0.0, 0.0))
c01 = f.cartesian_point((0.0, 3.0, 0.0))
c10 = f.cartesian_point((3.0, 0.0, 0.0))
c11 = f.cartesian_point((3.0, 3.0, 0.0))

surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('plane_as_nurbs',1,1,"
    f"((#{c00.eid},#{c01.eid}),"
    f"(#{c10.eid},#{c11.eid})),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(2,2),(2,2),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Parametric context for pcurves ──
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, len3)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.0, 0.0), (0., 1., 0.), 3.0, (3.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 3.0, 0.0), (-1., 0., 0.), 3.0, (3.0, 3.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 3.0, 0.0), (0., -1., 0.), 3.0, (0.0, 3.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) — C-1 DRIVER ───────────────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('plane_as_nurbs_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('plane_as_nurbs_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('plane_as_nurbs_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('plane_as_nurbs_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('plane_as_nurbs_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('plane_as_nurbs_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
