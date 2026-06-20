"""Gn151 — B-spline C0 interior knot discontinuity.

Catalog claim: B_SPLINE_CURVE_WITH_KNOTS (degree 3, 5 poles). Interior knot at
parameter 0.5 with multiplicity 4 (=degree). Defect: C0 discontinuity (tangent
jump). Knot arithmetic: 4+4+1=9 ✓. Healing must detect via
Geom2dConvert::C0BSplineToC1 and upgrade continuity. No forward refs.
Invariants: DIRECTION unit.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree=3, 5 poles. Knots (0.0,0.5,1.0) mults
    (4,4,1) sum=9 → n_poles=5 ✓ (n+d+1=5+3+1=9). Interior knot mult=4=degree
    creates C0 discontinuity (tangent jump at t=0.5). IS the defect edge 3D
    curve; healer must run Geom2dConvert::C0BSplineToC1.
  - C-1 DRIVER: tangent jump at t=0.5 from interior knot mult=degree; wired
    into face topology via SURFACE_CURVE on a flat plane.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree=3; 5 poles;
    knots (0.0,0.5,1.0) mults (4,4,1) sum=9 → n=5 ✓;
    interior mult=4=degree → C0 discontinuity; IS defect edge 3D curve.
  - C-1 DRIVER: tangent jump at t=0.5 → C0BSplineToC1 continuity upgrade needed.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn151",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3; 5 poles; "
        "knots (0.0,0.5,1.0) mults (4,4,1) sum=9 → n=5 ✓; "
        "interior knot mult=4=degree → C0 discontinuity (tangent jump); "
        "IS defect edge 3D curve; "
        "Geom2dConvert::C0BSplineToC1 continuity-upgrade healing needed"
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

# ── CATALOG MECHANISM: degree-3 B-spline with C0 interior knot mult ────────────
# 5 poles: degree=3, n=5 → n+d+1=9. mults (4,4,1) → sum=9 ✓.
# Interior knot at t=0.5, mult=4=degree → C0 discontinuity (G0 only, tangent jump).
# Poles: start at (0,0,0), break at (2,0,0)→(2,1,0), end at (4,0,0).
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.5, 0.0))
cp2 = f.cartesian_point((2.0, 0.0, 0.0))   # left of C0 break
cp3 = f.cartesian_point((2.0, 1.0, 0.0))   # right of C0 break (tangent jump)
cp4 = f.cartesian_point((4.0, 0.0, 0.0))
cp_list = ",".join(f"#{p.eid}" for p in [cp0, cp1, cp2, cp3, cp4])

mech_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn151_c0_interior_mult',3,"
    f"({cp_list}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4,1),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# ── Wire mech_curve into face topology as the defect edge 3D curve ────────────
# Flat quad face; bottom edge uses mech_curve.
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
