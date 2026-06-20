"""Gn158 — B-spline curve with clustered interior knots, condition-number escalation.

Catalog claim: B_SPLINE_CURVE_WITH_KNOTS, degree 3, 7 poles. Interior knots
clustered: 0.5, 0.501, 0.502 (spacing ~0.001). Knot multiplicities (4,1,1,1,4),
sum=11=n+d+1=7+3+1=11. Healing challenge: tight knot spacing (ratio ~0.001:0.5)
creates ill-conditioned basis matrix; conditioning number grows exponentially
with clustering. Expected: detect knot clustering and apply knot removal or
uniform reparametrization.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree=3, 7 poles, clamped.
    Knots (0.0, 0.5, 0.501, 0.502, 1.0) mults (4,1,1,1,4) sum=11=7+3+1 ✓.
    Interior knot spacing 0.001 (ratio 0.001:0.5 = 1:500 → ill-conditioned).
    IS the face surface: wired directly as the B-spline curve body.

Mechanism vs driver:
  - CATALOG MECHANISM: clustered interior knots (0.5, 0.501, 0.502) in a
    degree-3 B_SPLINE_CURVE_WITH_KNOTS; IS the defect edge 3D curve.
  - No C-1 break; geometry is valid → shape(1)/shape(1).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn158",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree=3, 7 poles; "
        "interior knots (0.5,0.501,0.502) mults (4,1,1,1,4) sum=11=7+3+1 ✓; "
        "knot spacing ratio 1:500 → ill-conditioned basis matrix; "
        "IS defect edge 3D curve; geometry valid → shape(1)/shape(1)"
    ),
)

# ── Background flat plane ──────────────────────────────────────────────────────
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_axis = f.direction((0.0, 0.0, 1.0))
x_axis = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(origin, z_axis, x_axis)
plane = f.plane(placement)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: degree-3 B-spline, 7 poles, clustered interior knots ───
# 7 poles, degree=3, clamped.
# Knots: (0.0, 0.5, 0.501, 0.502, 1.0) mults (4,1,1,1,4) sum=11=7+3+1 ✓.
# Poles spread across [0,3] in X; slight Z variation for non-degenerate shape.
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((0.5, 0.0, 0.2))
cp2 = f.cartesian_point((1.0, 0.0, 0.1))
cp3 = f.cartesian_point((1.5, 0.0, 0.3))   # near clustered knot region
cp4 = f.cartesian_point((2.0, 0.0, 0.1))
cp5 = f.cartesian_point((2.5, 0.0, 0.2))
cp6 = f.cartesian_point((3.0, 0.0, 0.0))
cp_list = ",".join(f"#{p.eid}" for p in [cp0, cp1, cp2, cp3, cp4, cp5, cp6])

mech_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn158_clustered_knots',3,"
    f"({cp_list}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,1,4),(0.0,0.5,0.501,0.502,1.0),.UNSPECIFIED.)"
)

# ── Wire mech_curve into face topology as the defect edge 3D curve ────────────
p_a3 = f.cartesian_point((0.0, 0.0, 0.0))
p_b3 = f.cartesian_point((3.0, 0.0, 0.0))
p_c3 = f.cartesian_point((3.0, 2.0, 0.0))
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
d2_bot = f.direction((1.0, 0.0))
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

e_right = mk_line_edge(vt_b, vt_c, (3.0, 0.0, 0.0), (0., 1., 0.), (3.0, 0.0), (0., 1.), 2.0)
e_top   = mk_line_edge(vt_c, vt_d, (3.0, 2.0, 0.0), (-1., 0., 0.), (3.0, 2.0), (-1., 0.), 3.0)
e_left  = mk_line_edge(vt_d, vt_a, (0.0, 2.0, 0.0), (0., -1., 0.), (0.0, 2.0), (0., -1.), 2.0)

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
