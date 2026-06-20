"""Gn156 — Periodic B-spline with non-closing control polygon, origin-shift risk.

Catalog claim: Minimal reproducer: B_SPLINE_CURVE_WITH_KNOTS, degree 2, 5 poles
marked periodic (.T.), but P[0]=(1,0,0)≠P[4]=(0.9,−0.1,0). Knot structure:
multiplicities (2,2,2,1), sum=7=n+d for periodic. Closed-curve claim violated;
polygon open. Healing challenge: post-upgrade (Geom2dConvert C0→C1), periodic
origin may shift without SetOrigin re-anchor. Expected: enforce closure or strip
periodicity; re-anchor origin after continuity upgrade.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree=2, 5 poles, periodic (.T.).
    P[0]=(1,0,0) ≠ P[4]=(0.9,-0.1,0): non-closing polygon violates periodic
    closed-curve claim. Knots (0.0,0.25,0.5,0.75) mults (2,2,2,1) sum=7.
    Post C0→C1 upgrade origin may shift; SetOrigin re-anchor or periodicity
    strip required. IS the defect edge 3D curve.
  - C-1 DRIVER: periodic flag with non-closing polygon → origin shift after
    upgrade; wired into face topology via SURFACE_CURVE on a flat plane.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=2; 5 poles periodic .T.;
    P[0]≠P[4] (open polygon violates periodicity); knots (0.0,0.25,0.5,0.75)
    mults (2,2,2,1) sum=7; IS defect edge 3D curve.
  - C-1 DRIVER: non-closing polygon + periodic flag → post-upgrade origin shift;
    enforce closure or strip periodicity + SetOrigin re-anchor.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn156",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=2; 5 poles periodic .T.; "
        "P[0]=(1,0,0) ≠ P[4]=(0.9,-0.1,0) → non-closing polygon, periodicity violated; "
        "knots (0.0,0.25,0.5,0.75) mults (2,2,2,1) sum=7; "
        "IS defect edge 3D curve; "
        "post-upgrade origin-shift risk → SetOrigin re-anchor or periodicity strip"
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

# ── CATALOG MECHANISM: degree-2 periodic B-spline, 5 poles, non-closing ───────
# 5 poles, degree=2, periodic .T.
# For periodic: n_poles + degree = 5+2=7; mults (2,2,2,1) sum=7 ✓.
# Knots (0.0,0.25,0.5,0.75): 4 distinct knot values.
# P[0]=(1,0,0) ≠ P[4]=(0.9,-0.1,0) → open control polygon, violates closed claim.
cp0 = f.cartesian_point(( 1.0,  0.0, 0.0))   # start
cp1 = f.cartesian_point(( 0.0,  1.0, 0.0))   # quarter
cp2 = f.cartesian_point((-1.0,  0.0, 0.0))   # half
cp3 = f.cartesian_point(( 0.0, -1.0, 0.0))   # three-quarter
cp4 = f.cartesian_point(( 0.9, -0.1, 0.0))   # ≠ cp0: non-closing polygon
cp_list = ",".join(f"#{p.eid}" for p in [cp0, cp1, cp2, cp3, cp4])

mech_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn156_nonclosing_periodic',2,"
    f"({cp_list}),"
    f".UNSPECIFIED.,.T.,.F.,"
    f"(2,2,2,1),(0.0,0.25,0.5,0.75),.UNSPECIFIED.)"
)

# ── Wire mech_curve into face topology as the defect edge 3D curve ────────────
# Flat quad with the mechanism as the bottom edge.
p_a3 = f.cartesian_point(( 1.0,  0.0, 0.0))   # matches cp0
p_b3 = f.cartesian_point(( 1.0, -1.5, 0.0))
p_c3 = f.cartesian_point((-1.5, -1.5, 0.0))
p_d3 = f.cartesian_point((-1.5,  0.0, 0.0))
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

e_right = mk_line_edge(vt_b, vt_c, ( 1.,-1.5,0.), (-1.,0.,0.), (1.0,0.0), (-1.,0.), 2.5)
e_top   = mk_line_edge(vt_c, vt_d, (-1.5,-1.5,0.), (0.,1.,0.), (0.0,1.0), ( 0.,1.), 1.5)
e_left  = mk_line_edge(vt_d, vt_a, (-1.5, 0.,0.), ( 1.,0.,0.), (0.0,0.0), ( 1.,0.), 2.5)

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
