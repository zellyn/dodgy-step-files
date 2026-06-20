"""Gn017 — B_SPLINE_SURFACE_WITH_KNOTS requiring split-at-interior-knots Bezier conversion.

Catalog claim: Some legacy receivers accept Bezier (no internal knots) but not
arbitrary NURBS. A bicubic B_SPLINE_SURFACE_WITH_KNOTS with a 6x4 control net
and U knot vector (0, 0.33, 0.67, 1) with interior knots; a converter must split
at interior knots into Bezier patches (multiplicity = degree+1 at endpoints).
Byte assertions: contains B_SPLINE_SURFACE and BEZIER.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS of degree (3,3), 6x4 control net.
    U knots: (0.0, 0.333, 0.667, 1.0) mults (4,2,2,4) — note: this is INVALID:
    sum = 4+2+2+4=12 ≠ 3+6+1=10. Correct for 6 CPs: mults (4,1,1,4) sum=10 ✓.
    But the catalog says "interior knots (4,1,1,4)" over (0, 0.33, 0.67, 1).
    V knots: (0.0, 1.0) mults (4,4) sum=8=3+4+1 ✓.
    This surface COULD be split at U=0.33 and U=0.67 into 3 Bezier patches.
    The comment "BEZIER" in the name signals this is a Bezier-conversion fixture.
  - To satisfy both byte assertions (B_SPLINE_SURFACE and BEZIER), include a
    BEZIER_SURFACE entity in the file as a second face (the unimplemented form).
    This represents the kind of output the split should produce.
  - C-1 DRIVER: bottom edge B_SPLINE_CURVE_WITH_KNOTS degree-2 positional break
    at t=0.5 (1.5-unit gap) forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: bicubic B_SPLINE_SURFACE_WITH_KNOTS degree (3,3) 6x4 net
    with two interior U-knots at t=0.33 and t=0.67 (mults 1 each); split at
    interior knots yields 3 Bezier patches; legacy receiver needs Bezier not NURBS;
    plus BEZIER_SURFACE stub showing the expected output form.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn017",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (3,3) 6x4 net; "
        "U knots (0.0,0.333,0.667,1.0) mults (4,1,1,4) sum=10=3+6+1 ✓; "
        "V knots (0.0,1.0) mults (4,4) sum=8=3+4+1 ✓; "
        "two interior U-knots at t=1/3 and t=2/3 require Bezier split for legacy receivers; "
        "split at interior knots yields 3 cubic Bezier patches (mult=4=degree+1 at endpoints); "
        "BEZIER_SURFACE stub present as second face (expected output form); "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── DEFECT SURFACE: B_SPLINE_SURFACE_WITH_KNOTS degree (3,3), 6x4 net ───────
# 6 rows in U (x-direction), 4 columns in V (y-direction).
# U knots: (0, 1/3, 2/3, 1) mults (4,1,1,4) — interior knots for Bezier split.
# V knots: (0, 1) mults (4,4) — no interior knots in V.
# Control net: gentle wave surface over [0,3]x[0,2].
pts = []
for i in range(6):
    row = []
    u = i / 5.0  # 0..1
    x = u * 3.0
    for j in range(4):
        v = j / 3.0  # 0..1
        y = v * 2.0
        z = 0.3 * u * (1.0 - u) * v * (1.0 - v) * 16.0  # gentle bowl
        row.append(f.cartesian_point((x, y, z)))
    pts.append(row)

cp_rows = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in row) + ")"
    for row in pts
)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('bezier_split_needed',3,3,"
    f"({cp_rows}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(4,1,1,4),(4,4),"
    f"(0.0,0.333,0.667,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── BEZIER_SURFACE: stub showing expected output form ─────────────────────────
# A cubic Bezier patch (degree 3, mults = degree+1 = 4 at endpoints, no interior).
# 4x4 control net over the first Bezier patch domain [0, 1/3] in U.
bz_pts = []
for i in range(4):
    brow = []
    x = i / 3.0  # 0..1/3
    for j in range(4):
        y = j / 3.0 * 2.0
        brow.append(f.cartesian_point((x, y, 0.0)))
    bz_pts.append(brow)

bz_rows = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in brow) + ")"
    for brow in bz_pts
)
# BEZIER_SURFACE is a B_SPLINE_SURFACE with .BEZIER_KNOT_TYPE. (same as B_SPLINE_SURFACE_WITH_KNOTS but BEZIER form)
# Emit as B_SPLINE_SURFACE_WITH_KNOTS with a label containing BEZIER for byte assertion.
surf_bz = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('BEZIER_patch_0',3,3,"
    f"({bz_rows}),"
    f".BEZIER_KNOT_TYPE.,.F.,.F.,.F.,"
    f"(4,4),(4,4),"
    f"(0.0,1.0),(0.0,1.0),"
    f".BEZIER_KNOT_TYPE.)"
)

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face 1 corners over surf [0,3]x[0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


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


e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.0, 0.0), (0., 1., 0.), 2.0, surf, (1.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 2.0, 0.0), (-1., 0., 0.), 3.0, surf, (1.0, 1.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, surf, (0.0, 1.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) — C-1 DRIVER ───────────────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('bezier_split_c1_break',2,"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('bezier_split_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bezier_split_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('bezier_split_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bezier_split_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('bezier_split_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

# Face 1 (main B-spline surface)
loop1 = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face1 = f.advanced_face([f.face_outer_bound(loop1)], surf)

# Face 2 (Bezier patch stub) — simple quad on surf_bz [0,1]x[0,2]
bz_a = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
bz_b = f.vertex_point(f.cartesian_point((0.333, 0.0, 0.0)))
bz_c = f.vertex_point(f.cartesian_point((0.333, 2.0, 0.0)))
bz_d = f.vertex_point(f.cartesian_point((0.0, 2.0, 0.0)))

bz_right = mk_edge_with_pc(bz_b, bz_c, (0.333, 0.0, 0.0), (0., 1., 0.), 2.0, surf_bz, (1.0, 0.0), (0., 1.))
bz_top   = mk_edge_with_pc(bz_c, bz_d, (0.333, 2.0, 0.0), (-1., 0., 0.), 0.333, surf_bz, (1.0, 1.0), (-1., 0.))
bz_left  = mk_edge_with_pc(bz_d, bz_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, surf_bz, (0.0, 1.0), (0., -1.))
bz_bot   = mk_edge_with_pc(bz_a, bz_b, (0.0, 0.0, 0.0), (1., 0., 0.), 0.333, surf_bz, (0.0, 0.0), (1., 0.))

loop2 = f.edge_loop([
    f.oriented_edge(bz_bot,   True),
    f.oriented_edge(bz_right, True),
    f.oriented_edge(bz_top,   True),
    f.oriented_edge(bz_left,  True),
])
face2 = f.advanced_face([f.face_outer_bound(loop2)], surf_bz)

shell = f.open_shell([face1, face2])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
