"""Gp145 — Zero Magnitude Tangent from Flat Section

Catalog claim: B-spline 2D pcurve with flat section at endpoint (control point
repeated). Finite difference produces zero-magnitude vector. Fallback dparam
becomes 0.0; D1 fallback escalates unnecessarily.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge having a PCurve with a flat (zero-length)
    section at the start endpoint.
  - THE CATALOG MECHANISM: B-spline 2D pcurve where the first three control
    points are all coincident (stacked at the same UV position). This creates a
    flat section of zero length at the start of the parameter domain: D1=0 at
    the endpoint. When GetEndTangent2d computes the finite difference, the
    numerator is a zero vector (because the curve doesn't move in the flat
    section). The computed dparam shrinks to 0.0, triggering the D1 derivative
    fallback path unnecessarily — even though the curve has genuine geometry
    beyond the flat section.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PCurve B-spline with 3 coincident CPs at start (flat
    section); finite difference zero-magnitude; dparam=0.0; D1 fallback
    triggered unnecessarily; finite_difference_degeneracy axis.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp145",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2: CP[0]=CP[1]=CP[2]=(0,0) "
        "(3 coincident control points — flat section at start); "
        "CP[3]=(1.0,0) CP[4]=(2.0,0): curve has genuine geometry only beyond t=0.5; "
        "GetEndTangent2d finite difference produces zero-magnitude vector at start; "
        "dparam shrinks to 0.0; D1 fallback escalated unnecessarily; "
        "finite_difference_degeneracy axis; shape_null=True"
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
    f"B_SPLINE_CURVE_WITH_KNOTS('zero_magnitude_tangent_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve B-spline degree-2 with 3 coincident CPs at start.
# CP[0] = CP[1] = CP[2] = (0,0): flat section of zero extent at parameter=0.
# Because the Bezier basis for degree-2 requires 3 CPs, all coincident here
# means the first Bezier segment is a point. D1 = 0 at parameter=0.
# Finite difference: curve(0+h) - curve(0) = 0 for small h → zero magnitude.
# dparam collapses to 0.0; the D1 escalation path is triggered unnecessarily
# even though the curve has valid geometry in the second Bezier segment.
pp0 = f.cartesian_point((0.0, 0.0))   # coincident
pp1 = f.cartesian_point((0.0, 0.0))   # coincident
pp2 = f.cartesian_point((0.0, 0.0))   # coincident — flat section at start
pp3 = f.cartesian_point((1.0, 0.0))
pp4 = f.cartesian_point((2.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('zero_magnitude_tangent_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('zero_magnitude_tangent_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('zero_magnitude_tangent_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('zero_magnitude_tangent_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('zero_magnitude_tangent_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
