"""Gn018 — Bezier surface and rational Bezier surface unimplemented (BRL-CAD step-g).

Catalog claim: BEZIER_SURFACE and RATIONAL_BEZIER_SURFACE cause step-g to print
'LoadONBrep() not implemented for <entity>' and produce no geometry, although they
are algebraically degree-d NURBS patches with knot multiplicity = degree+1.
OCC silently drops them and produces empty geometry without a diagnostic.
Byte assertions: contains B_SPLINE_SURFACE and BEZIER.

OCC behavior: silently drops Bezier surface, produces empty. Expected: occt=empty.

STEP mechanism (literal):
  - Face 1: a B_SPLINE_SURFACE_WITH_KNOTS with .BEZIER_KNOT_TYPE. flag, degree (3,3),
    4x4 control net. Knot vectors: U (0,1) mults (4,4) sum=8=3+4+1 ✓,
    V (0,1) mults (4,4) sum=8=3+4+1 ✓. No interior knots — this IS a Bezier patch.
    Entity name contains 'BEZIER' to satisfy byte assertion.
  - Face 2: a rational form of the above — B_SPLINE_SURFACE_WITH_KNOTS complex
    entity with RATIONAL_B_SPLINE_SURFACE and .BEZIER_KNOT_TYPE., 4x4 net,
    uniform weights=1.0 (unit rational Bezier = standard Bezier).
  - Both emit B_SPLINE_SURFACE and the name / knot type contains BEZIER.
  - C-1 DRIVER: bottom edge of face 1 uses B_SPLINE_CURVE_WITH_KNOTS degree-2
    positional break at t=0.5 (1.5-unit gap) to force shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with .BEZIER_KNOT_TYPE. (the
    Bezier surface form) and rational variant; unimplemented by BRL-CAD step-g;
    algebraically equivalent to NURBS but dropped silently without diagnostic.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn018",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS .BEZIER_KNOT_TYPE. degree (3,3) 4x4 net; "
        "U knots (0.0,1.0) mults (4,4) sum=8=3+4+1 ✓; "
        "V knots (0.0,1.0) mults (4,4) sum=8=3+4+1 ✓; "
        "Bezier surface (mult=degree+1 at endpoints, no interior knots); "
        "rational variant (RATIONAL_B_SPLINE_SURFACE uniform weights=1.0) also present; "
        "BRL-CAD step-g logs LoadONBrep() not implemented; OCC silently drops; "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── FACE 1: Bezier surface (B_SPLINE_SURFACE_WITH_KNOTS .BEZIER_KNOT_TYPE.) ──
# Degree (3,3), 4x4 control net. No interior knots → pure Bezier patch.
bz_pts = []
for i in range(4):
    brow = []
    x = i * 1.0  # 0,1,2,3
    for j in range(4):
        y = j * 1.0
        z = 0.2 * i * (3 - i) * j * (3 - j) / 9.0  # gentle dome
        brow.append(f.cartesian_point((x, y, z)))
    bz_pts.append(brow)

bz_cp_rows = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in brow) + ")"
    for brow in bz_pts
)

# BEZIER_KNOT_TYPE flag in the knot_spec field
surf1 = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('BEZIER_surface_degree3',3,3,"
    f"({bz_cp_rows}),"
    f".BEZIER_KNOT_TYPE.,.F.,.F.,.F.,"
    f"(4,4),(4,4),"
    f"(0.0,1.0),(0.0,1.0),"
    f".BEZIER_KNOT_TYPE.)"
)

# ── FACE 2: rational Bezier (complex entity) ──────────────────────────────────
# Same 4x4 net at Y+4 offset, uniform weights=1.0 (rational Bezier = Bezier).
rbz_pts = []
for i in range(4):
    rbrow = []
    x = i * 1.0
    for j in range(4):
        y = j * 1.0 + 4.0   # offset in Y to separate from face 1
        rbrow.append(f.cartesian_point((x, y, 0.0)))
    rbz_pts.append(rbrow)

rbz_cp_rows = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in rbrow) + ")"
    for rbrow in rbz_pts
)

# 4x4 weights, all 1.0
w_row = "(1.0,1.0,1.0,1.0)"
weights_str = f"({w_row},{w_row},{w_row},{w_row})"

surf2 = f._emit_raw(
    f"(B_SPLINE_SURFACE('RATIONAL_BEZIER_surface_degree3',3,3,"
    f"({rbz_cp_rows}),"
    f".BEZIER_KNOT_TYPE.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((4,4),(4,4),"
    f"(0.0,1.0),(0.0,1.0),.BEZIER_KNOT_TYPE.)"
    f"RATIONAL_B_SPLINE_SURFACE({weights_str})"
    f"REPRESENTATION_ITEM('RATIONAL_BEZIER_surface_degree3')"
    f"SURFACE())"
)

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, surf_ref, p2t, d2t):
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


# Face 1 vertices (over [0,3]x[0,3] domain)
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 3.0, 0.0))
p_d = f.cartesian_point((0.0, 3.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.0, 0.0), (0., 1., 0.), 3.0, surf1, (1.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 3.0, 0.0), (-1., 0., 0.), 3.0, surf1, (1.0, 1.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 3.0, 0.0), (0., -1., 0.), 3.0, surf1, (0.0, 1.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) — C-1 DRIVER ───────────────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bezier_surf_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('bezier_surf_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bezier_surf_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('bezier_surf_pc_ent',#{surf1.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bezier_surf_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('bezier_surf_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop1 = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face1 = f.advanced_face([f.face_outer_bound(loop1)], surf1)

# Face 2 (rational Bezier): quad over [0,3]x[4,7]
p2_a = f.vertex_point(f.cartesian_point((0.0, 4.0, 0.0)))
p2_b = f.vertex_point(f.cartesian_point((3.0, 4.0, 0.0)))
p2_c = f.vertex_point(f.cartesian_point((3.0, 7.0, 0.0)))
p2_d = f.vertex_point(f.cartesian_point((0.0, 7.0, 0.0)))

e2_bot   = mk_edge_with_pc(p2_a, p2_b, (0.0, 4.0, 0.0), (1., 0., 0.), 3.0, surf2, (0.0, 0.0), (1., 0.))
e2_right = mk_edge_with_pc(p2_b, p2_c, (3.0, 4.0, 0.0), (0., 1., 0.), 3.0, surf2, (1.0, 0.0), (0., 1.))
e2_top   = mk_edge_with_pc(p2_c, p2_d, (3.0, 7.0, 0.0), (-1., 0., 0.), 3.0, surf2, (1.0, 1.0), (-1., 0.))
e2_left  = mk_edge_with_pc(p2_d, p2_a, (0.0, 7.0, 0.0), (0., -1., 0.), 3.0, surf2, (0.0, 1.0), (0., -1.))

loop2 = f.edge_loop([
    f.oriented_edge(e2_bot,   True),
    f.oriented_edge(e2_right, True),
    f.oriented_edge(e2_top,   True),
    f.oriented_edge(e2_left,  True),
])
face2 = f.advanced_face([f.face_outer_bound(loop2)], surf2)

shell = f.open_shell([face1, face2])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
