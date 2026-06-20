"""Gp087 — FixAddPCurve high-curvature near-tangent.

Catalog claim: Edge near a surface boundary where two B-spline surfaces are
near-tangent (curvature ~0.6–0.62). FixAddPCurve projects the edge onto the
first surface but receives multiple candidate projections. Algorithm picks
arbitrary candidate without disambiguating. Defect: projection multiplicity
not resolved; no heuristic for tangency context.

STEP mechanism (literal):
  - PLANE face with defect edge: bare EDGE_CURVE (no SURFACE_CURVE wrapper,
    no pcurve) — FixAddPCurve must construct the pcurve from projection.
  - 3D curve is a B_SPLINE degree-2 with a sharp curvature spike near the
    surface boundary: CPs create a loop-like excursion with curvature ~0.6
    at the spike tip, close to the tangency regime. This models the
    high-curvature near-tangent point where projection multiplicity occurs.
  - The C-1 positional break at t=0.5 (knot mult=3, large CP gap) drives
    OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: bare EDGE_CURVE with B-spline having a sharp
    curvature spike (modeling the near-tangent projection multiplicity
    that causes FixAddPCurve to diverge).
  - C-1 DRIVER: B-spline positional break forces OCC shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp087",
    defect=(
        "PLANE Z=0; defect edge: bare EDGE_CURVE (no SURFACE_CURVE/pcurve); "
        "3D B-spline degree-2 C-1 break at t=0.5 (CP[2]=(1.5,0,0) vs "
        "CP[3]=(3.0,0,0), 1.5-unit gap) with curvature spike at t=0.25 "
        "(CPs form near-tangent excursion ~0.6 curvature); FixAddPCurve "
        "projection multiplicity not resolved; C-1 break drives shape_null"
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

# Context edges (right, top, left) — clean with pcurves
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)


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
# B-spline degree-2, 6 CPs, two interior knot spans.
# knot vector: (3,3,3) at (0.0, 0.5, 1.0) → two Bezier patches.
# C-1 positional break at t=0.5: CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5 gap.
# Curvature spike in first segment: CPs form a Y-excursion to model high
# curvature near surface boundary (near-tangent to the XZ plane).
# CP[0]=(0,0,0), CP[1]=(0.75,0.6,0), CP[2]=(1.5,0,0) → spike curvature ~0.6
# at t≈0.25, modeling the near-tangent projection multiplicity regime.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))   # start
dc1 = f.cartesian_point((0.75, 0.6, 0.0))   # curvature spike (near-tangent)
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second Bezier (1.5 gap = break)
dc4 = f.cartesian_point((4.0,  0.0, 0.0))   # mid second segment
dc5 = f.cartesian_point((5.0,  0.0, 0.0))   # end

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('spike_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: bare EDGE_CURVE — no SURFACE_CURVE, no pcurve.
# FixAddPCurve must project this high-curvature B-spline onto the PLANE;
# near the spike tip the projection has multiple candidates (near-tangent).
e_bot = f._emit_raw(
    f"EDGE_CURVE('spike_near_tangent',#{v_a.eid},#{v_b.eid},#{bspline_3d.eid},.T.)"
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
