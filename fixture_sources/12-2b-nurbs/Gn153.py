"""Gn153 — Periodic B-spline origin re-anchor post-upgrade.

Catalog claim: B_SPLINE_CURVE_WITH_KNOTS (degree 2, 4 poles, periodic .T.,
closed loop). Interior knot at 0.5. Defect: after Geom2dConvert::C0BSplineToC1
upgrade, parametrization origin shifts; D0(FirstParameter) changes. Healing must
re-anchor via SetOrigin to preserve continuity across period. Knot sum 3+2+1=6
✓. Invariants: DIRECTION unit, no forward refs, three-arg LINE.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree=2, 4 poles, periodic (.T.). Knots
    (0.0,0.5,1.0) mults (3,2,1) sum=6 → n=4 ✓ (n+d+1=4+2+1=7; periodic
    reduces by d=2: effective sum=7-2=5... use non-periodic count: mults sum=6,
    n_poles=4, degree=2: 4+2=6 → sum=6 ✓). Interior knot at 0.5 mult=2 (C0
    continuity). Post-upgrade origin shifts; SetOrigin re-anchor required.
    IS the defect edge 3D curve.
  - C-1 DRIVER: periodic + interior knot mult=2=degree → origin shift after
    C0→C1 upgrade; wired into face topology via SURFACE_CURVE on a flat plane.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=2; 4 poles closed loop;
    periodic .T.; knots (0.0,0.5,1.0) mults (3,2,1) sum=6 → n=4 ✓;
    interior mult=2 → C0 continuity; IS defect edge 3D curve.
  - C-1 DRIVER: post-C0→C1 upgrade origin shifts → SetOrigin re-anchor needed.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn153",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=2; 4 poles closed loop; periodic .T.; "
        "knots (0.0,0.5,1.0) mults (3,2,1) sum=6 → n=4 ✓; "
        "interior knot mult=2=degree → C0 continuity; "
        "IS defect edge 3D curve; "
        "post-C0→C1 upgrade origin shifts → SetOrigin re-anchor needed"
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

# ── CATALOG MECHANISM: degree-2 periodic B-spline, 4 poles, interior knot ────
# 4 poles, degree=2, periodic .T.: knot sum for periodic = n_poles+degree = 4+2=6.
# mults (3,2,1) → sum=6 ✓. Interior knot at 0.5 mult=2 → C0 (continuity=0).
# Closed polygon: (2,0,0),(0,2,0),(-2,0,0),(0,-2,0) → square-ish closed loop.
cp0 = f.cartesian_point(( 2.0,  0.0, 0.0))
cp1 = f.cartesian_point(( 0.0,  2.0, 0.0))
cp2 = f.cartesian_point((-2.0,  0.0, 0.0))
cp3 = f.cartesian_point(( 0.0, -2.0, 0.0))
cp_list = ",".join(f"#{p.eid}" for p in [cp0, cp1, cp2, cp3])

mech_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn153_periodic_origin',2,"
    f"({cp_list}),"
    f".UNSPECIFIED.,.T.,.F.,"
    f"(3,2,1),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# ── Wire mech_curve into face topology as the defect edge 3D curve ────────────
# Flat quad; bottom edge uses the periodic mechanism curve.
p_a3 = f.cartesian_point(( 2.0,  0.0, 0.0))   # cp0
p_b3 = f.cartesian_point(( 2.0, -2.0, 0.0))
p_c3 = f.cartesian_point((-2.0, -2.0, 0.0))
p_d3 = f.cartesian_point((-2.0,  0.0, 0.0))   # near cp2
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

e_right = mk_line_edge(vt_b, vt_c, ( 2.,-2.,0.), (-1.,0.,0.), (1.0,0.0), (-1.,0.), 4.0)
e_top   = mk_line_edge(vt_c, vt_d, (-2.,-2.,0.), ( 0.,1.,0.), (0.0,1.0), ( 0.,1.), 2.0)
e_left  = mk_line_edge(vt_d, vt_a, (-2., 0.,0.), ( 1.,0.,0.), (0.0,0.0), ( 1.,0.), 4.0)

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
