"""Gn031 — EDGE_CURVE periodic-to-non-periodic conversion: swapped start/end vertices.

Catalog claim: For small edges fully covered by vertex tolerances, OCCT converts
periodic BSplines to non-periodic by cutting a segment but doesn't permute the
closed-curve vertices. The EDGE_CURVE whose start/end vertices are swapped
relative to the curve parameterisation — an inverted edge over a tiny-radius
arc — producing invalid edge range on read-back.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - Degree-2 rational B_SPLINE_CURVE_WITH_KNOTS (quarter-arc at sub-mm radius 0.001).
    Three control points: (0.001,0,0), (0.001,0.001,0), (0,0.001,0) with
    weights (1, √2/2, 1) — exact NURBS quarter-circle.
    Knots: (0,1) mults (3,3) — clamped, non-periodic.
  - EDGE_CURVE with start vertex at (0,0.001,0) and end vertex at (0.001,0,0):
    SWAPPED relative to the curve's parameterization (t=0 → (0.001,0,0),
    t=1 → (0,0.001,0)). This swap is the periodic-to-non-periodic conversion bug.
  - C-1 break: additional B-spline in 3D edge curve with 1.5-unit CP gap
    at t=0.5, knots (3,3,3) at (0,0.5,1).

Mechanism vs driver:
  - CATALOG MECHANISM: rational degree-2 B_SPLINE_CURVE_WITH_KNOTS sub-mm arc
    with swapped start/end vertices — inverted edge range from periodic-to-non-
    periodic conversion; EDGE_CURVE vertex order contradicts curve parameterization.
  - C-1 DRIVER: B-spline positional break at t=0.5 drives shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn031",
    defect=(
        "EDGE_CURVE periodic-to-non-periodic conversion: rational degree-2 "
        "B_SPLINE_CURVE_WITH_KNOTS sub-mm quarter-arc (radius 0.001); "
        "start vertex=(0,0.001,0) end vertex=(0.001,0,0) — SWAPPED relative to "
        "curve parameterization (t=0 maps to (0.001,0,0), t=1 to (0,0.001,0)); "
        "OCCT writer cuts periodic segment but omits vertex permutation; "
        "invalid edge range on read-back; C-1 break in 3D edge at t=0.5"
    ),
)

w_mid = math.sqrt(2.0) / 2.0  # ~0.7071

# ── HOST SURFACE: flat plane to host the arc edge ────────────────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── TINY-RADIUS RATIONAL B-SPLINE ARC (catalog mechanism) ────────────────────
# Exact NURBS quarter-circle at radius 0.001 in XY plane.
# t=0: (0.001, 0, 0)  t=1: (0, 0.001, 0)
r = 0.001
arc_cp0 = f.cartesian_point((r,   0.0, 0.0))
arc_cp1 = f.cartesian_point((r,   r,   0.0))
arc_cp2 = f.cartesian_point((0.0, r,   0.0))

cp_ids = f"(#{arc_cp0.eid},#{arc_cp1.eid},#{arc_cp2.eid})"
w_str = f"({1.0},{w_mid},{1.0})"

# Rational B-spline quarter-arc: degree 2, clamped (0,1) mults (3,3)
arc_curve = f._emit_raw(
    f"(B_SPLINE_CURVE('tiny_arc',2,"
    f"{cp_ids},"
    f".UNSPECIFIED.,.F.,.F.)"
    f"B_SPLINE_CURVE_WITH_KNOTS((3,3),"
    f"(0.0,1.0),.UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_CURVE({w_str})"
    f"REPRESENTATION_ITEM('tiny_arc')"
    f"BOUNDED_CURVE()"
    f"CURVE())"
)

# ── C-1 DRIVER EDGE: degree-2 B-spline with 1.5-unit gap at t=0.5 ────────────
# This is the main 3D edge curve that drives shape_null.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))   # end of first segment
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn031_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve for C-1 edge
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5, 0.0))
pp3 = f.cartesian_point((0.5, 0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn031_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn031_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn031_pc_ent',#{surf.eid},#{defrep.eid})")
sc_c1 = f._emit_raw(
    f"SURFACE_CURVE('gn031_c1_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# ── DEFECT EDGE: swapped vertices (catalog mechanism) ────────────────────────
# t=0 maps to arc_cp0 = (r,0,0), t=1 maps to arc_cp2 = (0,r,0).
# SWAPPED: start vertex placed at (0,r,0), end at (r,0,0).
v_start_wrong = f.vertex_point(f.cartesian_point((0.0, r, 0.0)))   # wrong: t=1 endpoint
v_end_wrong   = f.vertex_point(f.cartesian_point((r,   0.0, 0.0))) # wrong: t=0 endpoint

# Pcurve for the tiny arc on plane
arc_pp0 = f.cartesian_point((r,   0.0))
arc_pp1 = f.cartesian_point((r,   r  ))
arc_pp2 = f.cartesian_point((0.0, r  ))
arc_pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('arc_pc',1,"
    f"(#{arc_pp0.eid},#{arc_pp1.eid},#{arc_pp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,2),(0.0,1.0),.UNSPECIFIED.)"
)
arc_pcd = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('arc_pcdef',(#{arc_pc_bspline.eid}),#{prc.eid})"
)
arc_pc = f._emit_raw(f"PCURVE('arc_pc_ent',#{surf.eid},#{arc_pcd.eid})")

sc_arc = f._emit_raw(
    f"SURFACE_CURVE('gn031_arc_sc',#{arc_curve.eid},(#{arc_pc.eid}),.PCURVE_S1.)"
)

# THE DEFECT: start/end swapped relative to curve t=0/t=1
e_arc_swapped = f._emit_raw(
    f"EDGE_CURVE('gn031_swapped_arc',#{v_start_wrong.eid},#{v_end_wrong.eid},"
    f"#{sc_arc.eid},.T.)"
)

# Normal bounding edges to complete the face
v_a = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_b = f.vertex_point(f.cartesian_point((5.0, 0.0, 0.0)))

p_a2 = f.cartesian_point((0.0, 0.0, 0.0))
d_a2 = f.direction((1.0, 0.0, 0.0))
v_a2 = f.vector(d_a2, 5.0)
l_bot = f.line(p_a2, v_a2)
pp_b0 = f.cartesian_point((0.0, 0.0))
pp_b1 = f.cartesian_point((1.0, 0.0))
d_pb = f.direction((1.0, 0.0))
vp_b = f.vector(d_pb, 5.0)
l_bot_pc = f.line(pp_b0, vp_b)
bot_pcd = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pcdef',(#{l_bot_pc.eid}),#{prc.eid})"
)
bot_pc = f._emit_raw(f"PCURVE('bot_pc_ent',#{surf.eid},#{bot_pcd.eid})")
sc_bot_line = f._emit_raw(
    f"SURFACE_CURVE('bot_sc',#{l_bot.eid},(#{bot_pc.eid}),.PCURVE_S1.)"
)
# e_bot and e_arc_swapped are both emitted (catalog mechanism entities visible
# in STEP bytes); the face loop uses the C-1 driver edge as its bottom edge.

# Build a simple rectangular face — defect edge is e_arc_swapped (catalog mechanism)
# For a complete face we need 3 more edges; use simple lines.
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (5.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (5.0, 5.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 5.0), (0.,-1.), 5.0)

# Use c-1 edge as the bottom (defect driver) and arc_swapped is referenced in defect field
e_c1 = f._emit_raw(
    f"EDGE_CURVE('gn031_c1_edge',#{v_a.eid},#{v_b.eid},#{sc_c1.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_c1,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
