"""Gn013 — Convert elementary to BSpline (or back): producer/consumer mismatch.

Catalog claim: Some downstream tools require uniform NURBS for every face;
others require analytic primitives. A file with mixed PLANE, CYLINDRICAL_SURFACE,
and B_SPLINE_SURFACE_WITH_KNOTS faces where a consumer requires all NURBS (or
all analytic) triggers a conversion requirement. The healer must convert on demand.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - Face 1: PLANE surface (analytic primitive).
  - Face 2: B_SPLINE_SURFACE_WITH_KNOTS degree (1,1) 2x2 net — mathematically
    equivalent to a PLANE, but stored as NURBS. The mixed representation is the
    catalog defect: a consumer requiring uniform NURBS cannot use Face 1 without
    conversion, and a consumer requiring analytic primitives cannot use Face 2.
  - Both faces share a simple rectangular shell.
  - C-1 DRIVER: bottom edge of the B-spline face uses a degree-2 B-spline with
    a positional break at t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0),
    1.5-unit gap) to force shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: mixed PLANE + B_SPLINE_SURFACE_WITH_KNOTS faces in the
    same shell; producer/consumer form mismatch requires conversion healing.
  - C-1 DRIVER: B-spline positional break on the B-spline face bottom edge
    forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn013",
    defect=(
        "Mixed PLANE + B_SPLINE_SURFACE_WITH_KNOTS(1,1) 2x2 net in same shell; "
        "consumer requiring uniform NURBS cannot use PLANE face without conversion; "
        "consumer requiring analytic cannot use B-spline face without recognition; "
        "B-spline face bottom edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break "
        "at t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── FACE 1: PLANE surface (analytic) ──
orig1 = f.cartesian_point((0.0, 0.0, 0.0))
zdir1 = f.direction((0.0, 0.0, 1.0))
xdir1 = f.direction((1.0, 0.0, 0.0))
plc1  = f.axis2_placement_3d(orig1, zdir1, xdir1)
surf1 = f.plane(plc1)

# ── FACE 2: B_SPLINE_SURFACE_WITH_KNOTS degree (1,1) — a flat NURBS quad ──
# This is mathematically a PLANE but stored as NURBS: the form-mismatch defect.
# 2x2 control net, degree (1,1), clamped: U mults (2,2) sum=4=1+2+1 ✓,
#                                          V mults (2,2) sum=4=1+2+1 ✓.
# Place it at Z=0, Y in [3,6] to be adjacent to the plane face.
sq00 = f.cartesian_point((0.0, 3.0, 0.0))
sq01 = f.cartesian_point((0.0, 6.0, 0.0))
sq10 = f.cartesian_point((3.0, 3.0, 0.0))
sq11 = f.cartesian_point((3.0, 6.0, 0.0))

surf2 = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('nurbs_plane',1,1,"
    f"((#{sq00.eid},#{sq01.eid}),"
    f"(#{sq10.eid},#{sq11.eid})),"
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


def mk_edge_line(vs, ve, p3, d3t, len3, surf_ref, p2t, d2t):
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
    pc  = f._emit_raw(f"PCURVE('pc',#{surf_ref.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# ── FACE 1 (PLANE): simple rectangle [0,3] x [0,3] ──
pa_a = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
pa_b = f.vertex_point(f.cartesian_point((3.0, 0.0, 0.0)))
pa_c = f.vertex_point(f.cartesian_point((3.0, 3.0, 0.0)))
pa_d = f.vertex_point(f.cartesian_point((0.0, 3.0, 0.0)))

ea_bot   = mk_edge_line(pa_a, pa_b, (0.0, 0.0, 0.0), (1., 0., 0.), 3.0, surf1, (0.0, 0.0), (1., 0.))
ea_right = mk_edge_line(pa_b, pa_c, (3.0, 0.0, 0.0), (0., 1., 0.), 3.0, surf1, (3.0, 0.0), (0., 1.))
ea_top   = mk_edge_line(pa_c, pa_d, (3.0, 3.0, 0.0), (-1., 0., 0.), 3.0, surf1, (3.0, 3.0), (-1., 0.))
ea_left  = mk_edge_line(pa_d, pa_a, (0.0, 3.0, 0.0), (0., -1., 0.), 3.0, surf1, (0.0, 3.0), (0., -1.))

loop1 = f.edge_loop([
    f.oriented_edge(ea_bot,   True),
    f.oriented_edge(ea_right, True),
    f.oriented_edge(ea_top,   True),
    f.oriented_edge(ea_left,  True),
])
face1 = f.advanced_face([f.face_outer_bound(loop1)], surf1)

# ── FACE 2 (NURBS PLANE): rectangle [0,3] x [3,6] ──
pb_a = f.vertex_point(f.cartesian_point((0.0, 3.0, 0.0)))
pb_b = f.vertex_point(f.cartesian_point((3.0, 3.0, 0.0)))
pb_c = f.vertex_point(f.cartesian_point((3.0, 6.0, 0.0)))
pb_d = f.vertex_point(f.cartesian_point((0.0, 6.0, 0.0)))

# Context edges (right, top, left) with linear pcurves
eb_right = mk_edge_line(pb_b, pb_c, (3.0, 3.0, 0.0), (0., 1., 0.), 3.0, surf2, (1.0, 0.0), (0., 1.))
eb_top   = mk_edge_line(pb_c, pb_d, (3.0, 6.0, 0.0), (-1., 0., 0.), 3.0, surf2, (1.0, 1.0), (-1., 0.))
eb_left  = mk_edge_line(pb_d, pb_a, (0.0, 6.0, 0.0), (0., -1., 0.), 3.0, surf2, (0.0, 1.0), (0., -1.))

# ── DEFECT EDGE — bottom of NURBS face (pb_a -> pb_b) — C-1 DRIVER ───────────
dc0 = f.cartesian_point((0.0,  3.0, 0.0))
dc1 = f.cartesian_point((0.75, 3.0, 0.0))
dc2 = f.cartesian_point((1.5,  3.0, 0.0))
dc3 = f.cartesian_point((3.0,  3.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  3.0, 0.0))
dc5 = f.cartesian_point((3.0,  3.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('mixed_form_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('mixed_form_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('mixed_form_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('mixed_form_pc_ent',#{surf2.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('mixed_form_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
eb_bot = f._emit_raw(
    f"EDGE_CURVE('mixed_form_edge',#{pb_a.eid},#{pb_b.eid},#{sc_bot.eid},.T.)"
)

loop2 = f.edge_loop([
    f.oriented_edge(eb_bot,   True),
    f.oriented_edge(eb_right, True),
    f.oriented_edge(eb_top,   True),
    f.oriented_edge(eb_left,  True),
])
face2 = f.advanced_face([f.face_outer_bound(loop2)], surf2)

shell = f.open_shell([face1, face2])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
