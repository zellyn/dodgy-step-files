"""Gn152 — Knot ratio anomaly post-C0→C1 upgrade.

Catalog claim: B_SPLINE_CURVE_WITH_KNOTS (degree 2, 6 poles). Clustered
interior knots: [0.01, 0.02] vs [0.98, 1.0] ratio >100:1. Defect: after
C0->C1 upgrade, knot spacing becomes ill-conditioned (IsBad flag true). Healing
must detect via ratio criterion (>10) and apply arc-length reparametrization
(Approx_CurvilinearParameter). Knot sum 3+3+2+1=9 ✓. DIRECTION unit ratios.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree=2, 6 poles. Knots
    (0.0,0.01,0.02,0.98,1.0) mults (3,1,1,1,3) sum=9 → n=6 ✓ (n+d+1=6+2+1=9).
    Clustered interior knots at [0.01,0.02] vs sparse [0.98]. Post-C0→C1 upgrade
    the knot ratio exceeds 100:1 → IsBad flag → arc-length reparametrization
    required. IS the defect edge 3D curve.
  - C-1 DRIVER: ill-conditioned knot spacing after continuity upgrade; wired
    into face topology via SURFACE_CURVE on a flat plane.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=2; 6 poles;
    knots (0.0,0.01,0.02,0.98,1.0) mults (3,1,1,1,3) sum=9 → n=6 ✓;
    clustered interior knots ratio >100:1; IS defect edge 3D curve.
  - C-1 DRIVER: post-C0→C1 upgrade IsBad flag → Approx_CurvilinearParameter
    arc-length reparametrization needed.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn152",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=2; 6 poles; "
        "knots (0.0,0.01,0.02,0.98,1.0) mults (3,1,1,1,3) sum=9 → n=6 ✓; "
        "clustered interior knots [0.01,0.02] vs [0.98]: ratio >100:1; "
        "IS defect edge 3D curve; "
        "post-C0→C1 upgrade IsBad → Approx_CurvilinearParameter reparametrization"
    ),
)

# ── Background flat plane surface ──────────────────────────────────────────────
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_axis = f.direction((0.0, 0.0, 1.0))
x_axis = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(origin, z_axis, x_axis)
plane = f.plane(placement)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: degree-2 B-spline, 6 poles, clustered knots ────────────
# n=6, d=2 → n+d+1=9. knots (0.0,0.01,0.02,0.98,1.0) mults (3,1,1,1,3) sum=9 ✓.
# Clustered at 0.01,0.02 (spacing 0.01) vs 0.98 (spacing 0.96) → ratio ~96.
# Poles run from (0,0,0) to (4,0,0) with slight curvature.
cp0 = f.cartesian_point((0.00, 0.00, 0.0))
cp1 = f.cartesian_point((0.05, 0.20, 0.0))   # compressed near t=0 cluster
cp2 = f.cartesian_point((0.10, 0.00, 0.0))   # end of dense cluster region
cp3 = f.cartesian_point((2.00, 0.50, 0.0))   # sparse middle region
cp4 = f.cartesian_point((3.90, 0.20, 0.0))   # near t=0.98
cp5 = f.cartesian_point((4.00, 0.00, 0.0))
cp_list = ",".join(f"#{p.eid}" for p in [cp0, cp1, cp2, cp3, cp4, cp5])

mech_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn152_knot_ratio',2,"
    f"({cp_list}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,1,1,3),(0.0,0.01,0.02,0.98,1.0),.UNSPECIFIED.)"
)

# ── Wire mech_curve into face topology as the defect edge 3D curve ────────────
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((4.0, 0.0, 0.0))
p_c3 = f.cartesian_point((4.0, 2.0, 0.0))
p_d3 = f.cartesian_point((0.0, 2.0, 0.0))
vt_a = f.vertex_point(p_a3)
vt_b = f.vertex_point(p_b3)
vt_c = f.vertex_point(p_c3)
vt_d = f.vertex_point(p_d3)

def mk_line_edge(vs_, ve_, p3c, d3t, p2t, d2t, length):
    p3e  = f.cartesian_point(p3c)
    d3e  = f.direction(d3t)
    v3_  = f.vector(d3e, length)
    l3   = f.line(p3e, v3_)
    p2e  = f.cartesian_point(p2t)
    d2e  = f.direction(d2t)
    v2_  = f.vector(d2e, length)
    l2_  = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs_.eid},#{ve_.eid},#{sc_.eid},.T.)")

# Defect bottom edge: mech_curve IS the 3D curve
pp0 = f.cartesian_point((0.0, 0.0))
d2_bot = f.direction((1., 0.))
v2_bot = f.vector(d2_bot, 1.0)
l2_bot = f.line(pp0, v2_bot)
pcd_bot = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pcdef_bot',(#{l2_bot.eid}),#{prc.eid})"
)
pc_bot  = f._emit_raw(f"PCURVE('pc_bot',#{plane.eid},#{pcd_bot.eid})")
sc_bot  = f._emit_raw(
    f"SURFACE_CURVE('sc_bot',#{mech_curve.eid},(#{pc_bot.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('ec_bot',#{vt_a.eid},#{vt_b.eid},#{sc_bot.eid},.T.)"
)

e_right = mk_line_edge(vt_b, vt_c, (4.,0.,0.), (0.,1.,0.), (1.0,0.0), (0.,1.), 2.0)
e_top   = mk_line_edge(vt_c, vt_d, (4.,2.,0.), (-1.,0.,0.), (1.0,1.0), (-1.,0.), 4.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.,2.,0.), (0.,-1.,0.), (0.0,1.0), (0.,-1.), 2.0)

loop  = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
