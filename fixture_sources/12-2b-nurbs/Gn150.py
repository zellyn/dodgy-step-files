"""Gn150 — Trimmed periodic basis unwrap.

Catalog claim: B_SPLINE_CURVE_WITH_KNOTS (degree 3, 5 poles, periodic closure
.T.). Full domain [0, 2π]. Wrapped in Geom_TrimmedCurve concept at [0.2, 2.8].
Defect: SameParameter healing without periodic-wrapping detection incorrectly
clamps parameters to trim bounds, losing closed semantics. Healing must detect
Geom_TrimmedCurve + periodic basis + skip clamping. Knot sum 4+2+2+2+4=14
(periodic accounting). Invariants: DIRECTION unit ratios.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree=3, 5 poles, periodic (.T.).
    Knots (0.0,1.0,2.0,3.0,4.0,6.283) mults (4,2,2,2,4) → sum=14.
    Control polygon forms a closed loop. IS the defect edge 3D curve;
    periodic flag + trim-range encoding triggers the healing path.
  - C-1 DRIVER: periodic B-spline edge curve with non-unit parameter range
    [0, 2π] triggers SameParameter healing clamping bug; wired into face
    topology via SURFACE_CURVE on a flat plane.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3; 5 poles closed loop;
    periodic .T.; knots (0.0,1.0,2.0,3.0,6.283) mults (4,2,2,2,4) sum=14;
    IS defect edge 3D curve; periodic basis unwrap defect.
  - C-1 DRIVER: periodic_flag .T. + parameter range [0,2π] → SameParameter
    healer clamps to [0.2,2.8] trim bounds, losing periodic closure.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gn150",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3; 5 poles closed loop; periodic .T.; "
        "knots (0.0,1.0,2.0,3.0,6.283) mults (4,2,2,2,4) sum=14; "
        "IS defect edge 3D curve; "
        "periodic basis unwrap → SameParameter healer clamps trim bounds, loses closure"
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

# ── CATALOG MECHANISM: periodic B-spline curve, degree 3, 5 poles ─────────────
# Closed control polygon: (3,0,0),(1,2,0),(-1,2,0),(-3,0,0),(1,-2,0).
# Poles form a near-closed loop; periodic .T. forces closure semantics.
# Knot arithmetic: periodic, degree=3, n_poles=5.
# Full-period knots: (0.0,1.0,2.0,3.0,6.283) mults (4,2,2,2,4) sum=14.
TWO_PI = round(2 * math.pi, 3)  # 6.283
cp0 = f.cartesian_point(( 3.0,  0.0, 0.0))
cp1 = f.cartesian_point(( 1.0,  2.0, 0.0))
cp2 = f.cartesian_point((-1.0,  2.0, 0.0))
cp3 = f.cartesian_point((-3.0,  0.0, 0.0))
cp4 = f.cartesian_point(( 1.0, -2.0, 0.0))
cp_list = ",".join(f"#{p.eid}" for p in [cp0, cp1, cp2, cp3, cp4])

mech_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn150_periodic_trim',3,"
    f"({cp_list}),"
    f".UNSPECIFIED.,.T.,.F.,"
    f"(4,2,2,2,4),(0.0,1.0,2.0,3.0,{TWO_PI}),.UNSPECIFIED.)"
)

# ── Wire mech_curve into face topology as the defect edge 3D curve ────────────
# Face is a flat quad with the mechanism as one edge 3D curve (bottom edge).
# Corners at x∈[0,4], y∈[0,3], z=0. Mechanism bottom edge runs x=0..4, y=0, z=0.
p_a3 = f.cartesian_point(( 3.0,  0.0, 0.0))   # reuse cp0 position
p_b3 = f.cartesian_point(( 3.0, -2.0, 0.0))   # at cp4 vicinity
p_c3 = f.cartesian_point((-3.0, -2.0, 0.0))
p_d3 = f.cartesian_point((-3.0,  0.0, 0.0))   # at cp3 position
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

# Defect bottom edge: mechanism IS the 3D curve, linear pcurve in UV
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

e_right = mk_line_edge(vt_b, vt_c, ( 3.,-2., 0.), (-1., 0., 0.), (1.0,0.0), (-1.,0.), 6.0)
e_top   = mk_line_edge(vt_c, vt_d, (-3.,-2., 0.), ( 0., 1., 0.), (0.0,1.0), ( 0.,1.), 2.0)
e_left  = mk_line_edge(vt_d, vt_a, (-3., 0., 0.), ( 1., 0., 0.), (0.0,0.0), ( 1.,0.), 6.0)

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
