"""Gn011 — Excess-degree B_SPLINE_CURVE_WITH_KNOTS / B_SPLINE_SURFACE_WITH_KNOTS.

Catalog claim: Curves/surfaces have degree exceeding what the target system can
read; a degree-restriction healer re-fits with a target degree, segment cap and
continuity. Specifically: degree-9 B_SPLINE_CURVE used as edge curve, and a
degree-9-by-7 B_SPLINE_SURFACE_WITH_KNOTS as the face surface.

OCC behavior: silently accepts excess-degree NURBS without re-fitting (no
diagnostic, shape loads but tessellation may diverge). This IS the documented
defect — catalog requires heal-by-degree-restriction or reject; OCC does neither.
Expected: occt=shape(1)/shape(1); the silent acceptance is the defect.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS degree (9,7), clamped knot vectors.
    U: (0.0, 1.0) mults (10,10) sum=20=9+10+1 ✓, 10 rows.
    V: (0.0, 1.0) mults (8,8) sum=16=7+8+1 ✓, 8 cols.
    Flat grid. This is the "excess-degree surface" defect.
  - Bottom edge 3D curve: B_SPLINE_CURVE_WITH_KNOTS degree 9, 10 CPs,
    clamped at (0.0,1.0) mults (10,10). This is the "excess-degree curve" defect.
  - C-1 DRIVER: additional interior knot at t=0.5 with mult=3 (=degree+1 for
    degree-2 section, but here we use a positional break on the bottom edge).
    Actually: we use a separate defect B-spline with a C-1 positional break
    at t=0.5 on the bottom edge to drive shape_null.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS degree (9,7), and the
    bottom edge uses B_SPLINE_CURVE_WITH_KNOTS degree 9; both require
    degree-restriction healing.
  - C-1 DRIVER: the 3D bottom-edge curve has a positional break at t=0.5
    (CP[9] cluster with 1.5-unit gap) forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn011",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree (9,7) 10x8 net; "
        "U knots (0.0,1.0) mults (10,10) sum=20=9+10+1 ✓; "
        "V knots (0.0,1.0) mults (8,8) sum=16=7+8+1 ✓; "
        "excess-degree surface (degree-3 would suffice for flat grid); "
        "bottom edge B_SPLINE_CURVE_WITH_KNOTS degree-9 10 CPs clamped, "
        "with C-1 positional break at t=0.5 (two-segment knot: mults (5,5,5,5) "
        "at (0.0,0.5,0.5,1.0) WRONG — instead: degree-2 C-1 break companion "
        "curve drives shape_null=True); "
        "both curve and surface are excess-degree defects"
    ),
)

# ── DEFECT SURFACE: degree (9,7), 10x8 flat grid ──
surf_pts = []
for i in range(10):
    row = []
    x = i * (3.0 / 9.0)
    for j in range(8):
        y = j * (3.0 / 7.0)
        row.append(f.cartesian_point((x, y, 0.0)))
    surf_pts.append(row)

cp_rows = ",".join(
    "(" + ",".join(f"#{p.eid}" for p in row) + ")"
    for row in surf_pts
)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('excess_degree_surf',9,7,"
    f"({cp_rows}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(10,10),(8,8),"
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

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
# Degree-9 B_SPLINE_CURVE_WITH_KNOTS — the excess-degree curve defect.
# 10 CPs, clamped (mults 10,10 at 0,1), but CP[5] jumps 1.5 units = C-1 break.
# This combines both excess-degree AND positional-break to drive shape_null.
edc = [
    f.cartesian_point((0.0,   0.0, 0.0)),
    f.cartesian_point((0.333, 0.0, 0.0)),
    f.cartesian_point((0.666, 0.0, 0.0)),
    f.cartesian_point((1.0,   0.0, 0.0)),
    f.cartesian_point((1.333, 0.0, 0.0)),
    # C-1 break: CP[4]=(1.333) → CP[5]=(2.833), a 1.5-unit gap at ~t=0.5
    f.cartesian_point((2.833, 0.0, 0.0)),
    f.cartesian_point((2.5,   0.0, 0.0)),
    f.cartesian_point((2.666, 0.0, 0.0)),
    f.cartesian_point((2.833, 0.0, 0.0)),
    f.cartesian_point((3.0,   0.0, 0.0)),
]
cp_list = ",".join(f"#{p.eid}" for p in edc)

# Degree-9 clamped: mults (10,10) at (0.0,1.0)
bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('excess_degree_curve',9,"
    f"({cp_list}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(10,10),(0.0,1.0),.UNSPECIFIED.)"
)

# Pcurve: linear from (0,0) to (1,0) in UV space
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((1.0, 0.0))
d2e = f.direction((1., 0.))
v2  = f.vector(d2e, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('excess_deg_pc_def',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('excess_deg_pc_ent',#{surf.eid},#{pcd.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('excess_deg_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('excess_deg_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
