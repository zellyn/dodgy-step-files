"""Gn009 — High-degree NURBS surface bloat (degree >5, redundant knots).

Catalog claim: A B_SPLINE_SURFACE_WITH_KNOTS of degree >5 with hundreds of
control points where degree-3 would suffice. Often produced by aggressive
degree-elevation in source kernels. Causes meshing slowdowns; main impact on
FEA prep. Expected kernel behavior: accept on import; offer heal-and-accept
(re-fit / degree-reduction) via ShapeCustom_BSplineRestriction.

OCC behavior: silently accepts but loads empty result. Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS of degree (9,9), 10x10 control net
    (minimum for clamped degree-9: 10 = 9+1). Knot vectors are clamped:
    U = (0.0, 1.0) with mults (10,10) = sum 20 = 9+10+1 = 20 ✓.
    V = (0.0, 1.0) with mults (10,10) = sum 20 = 9+10+1 = 20 ✓.
    A flat-ish patch that could have been expressed as a degree-3 bilinear.
    This is the "degree bloat" defect: degree 9 is overkill for a flat quad.
  - C-1 DRIVER: degree-2 B-spline positional break on the bottom edge at t=0.5
    (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree (9,9) on a 10x10
    net; all redundant degrees that a degree-restriction healer should reduce.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn009",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (9,9) 10x10 net; "
        "U knots (0.0,1.0) mults (10,10) sum=20=9+10+1 ✓; "
        "V knots (0.0,1.0) mults (10,10) sum=20=9+10+1 ✓; "
        "degree-9 overkill for a flat quad (degree-3 suffices); "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True"
    ),
)

# ── DEFECT SURFACE: B_SPLINE_SURFACE_WITH_KNOTS degree (9,9), 10x10 net ──
# Clamped knot vectors: U and V each (0.0, 1.0) with mults (10,10).
# 10x10 control net: simple grid over [0,3]x[0,3] in XY, Z varies slightly.
# Build the 10x10 grid of control points.
pts = []
for i in range(10):
    row = []
    x = i * (3.0 / 9.0)
    for j in range(10):
        y = j * (3.0 / 9.0)
        z = 0.1 * (i / 9.0) * (j / 9.0)  # slight bow
        row.append(f.cartesian_point((x, y, z)))
    pts.append(row)

# Emit the B_SPLINE_SURFACE_WITH_KNOTS entity directly
cp_rows = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in row) + ")"
    for row in pts
)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('degree9_bloat',9,9,"
    f"({cp_rows}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(10,10),(10,10),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Parametric context for pcurves ──
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners at parameter-space extremes (surface goes [0,3]x[0,3] in 3D)
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
# degree-2 B-spline with 1.5-unit positional gap at t=0.5 forces shape_null.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((3.5,  0.0, 0.0))
dc5 = f.cartesian_point((3.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degree9_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve for the defect edge (bottom: U from 0→1, V=0)
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degree9_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('degree9_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('degree9_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('degree9_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('degree9_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
