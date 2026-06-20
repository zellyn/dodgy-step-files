"""Gp144 — Asymmetric Start Tangent Forward Difference

Catalog claim: Composite 2D pcurve with tangent discontinuity at start. Method
uses forward finite difference (cf+delta) instead of derivative. Misses
asymmetry between start and end regularity.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge having a PCurve with a tangent
    discontinuity at the start endpoint.
  - THE CATALOG MECHANISM: B-spline 2D pcurve (degree-2, C-1 at t=0.5 in UV
    space) that has a tangent direction discontinuity at its start.
    The curve makes a sharp turn at the very beginning (parameter=0):
    control points arranged so the initial tangent direction (from CP[0] to
    CP[1]) is nearly perpendicular to the main curve direction.
    GetEndTangent2d uses forward finite difference (par + cf*delta) for the
    start endpoint but backward difference for the end endpoint, creating an
    asymmetric evaluation. This asymmetry misses the sharp start tangent
    discontinuity while correctly detecting the smooth end.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 in 3D (knot
    mult=3, 1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PCurve B-spline with tangent discontinuity at start
    (nearly-perpendicular initial control segment); forward-difference start
    vs backward-difference end asymmetry in GetEndTangent2d; asymmetric
    tangent computation misses start kink; tangent_computation_method_boundary.
  - C-1 DRIVER: degree-2 B-spline positional break in 3D forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp144",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2: CP[0]=(0,0) CP[1]=(0,0.8) "
        "CP[2]=(0.5,0.8) CP[3]=(1.5,0.8) CP[4]=(2.0,0.0) — initial control "
        "segment (0,0)→(0,0.8) perpendicular to main direction (horizontal); "
        "tangent discontinuity at start; GetEndTangent2d forward-difference "
        "(par+cf*delta) for start vs backward-difference for end creates "
        "asymmetric evaluation; start kink missed; "
        "tangent_computation_method_boundary axis; shape_null=True"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('asym_start_tangent_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve B-spline degree-2 with perpendicular initial
# control segment creating tangent discontinuity at start.
# CP[0]=(0,0) → CP[1]=(0,0.8): initial segment points straight up (y-direction).
# CP[2]=(0.5,0.8) → CP[3]=(1.5,0.8) → CP[4]=(2.0,0.0): curve turns and flows
# in the x-direction.
# At parameter=0: D1 = 2*(CP[1]-CP[0]) = (0, 1.6) — pointing up.
# Forward finite difference par+delta: curve already curving into x-direction.
# The asymmetric forward/backward diff in GetEndTangent2d means the start
# tangent (forward diff from interior) diverges from the true endpoint D1.
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((0.0, 0.8))
pp2 = f.cartesian_point((0.5, 0.8))
pp3 = f.cartesian_point((1.5, 0.8))
pp4 = f.cartesian_point((2.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('asym_start_tangent_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('asym_start_tangent_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('asym_start_tangent_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('asym_start_tangent_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('asym_start_tangent_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
