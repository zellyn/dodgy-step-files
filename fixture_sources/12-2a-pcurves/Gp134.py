"""Gp134 — BoundedCurve endpoint distance early return bias.

Catalog claim: For bounded curves, endpoint distances are checked first. If
endpoint distance satisfies tolerance threshold, projection returns immediately
without checking if an interior point is actually closer. This bias favors
endpoint selection even when interior minima exist.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - 3D curve: B_SPLINE_CURVE_WITH_KNOTS degree-2 that forms a parabolic arc —
    interior point at t=0.5 is geometrically closer to a query point than
    either endpoint, but the endpoint check returns early.
  - PCurve: LINE in UV tracking the nominal path.
  - THE CATALOG MECHANISM: ShapeAnalysis_Curve::Project checks endpoint distances
    before exhaustive search. The B-spline is bounded; endpoint distance to the
    query point falls within tolerance. Project returns the endpoint parameter
    even though the interior minimum at t≈0.3 is significantly closer.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: bounded B-spline with interior minimum closer than
    endpoints; Project endpoint-distance early return bias selects wrong parameter.
    Arc shape: CP[1]=(2.5,1.5,0) creates an interior bulge above the chord,
    so the arc interior is farther from the X-axis than endpoints — the inverse
    case where a query on-chord triggers early endpoint return.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp134",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 parabolic arc: "
        "CP[0]=(0,0,0), CP[1]=(2.5,1.5,0) (interior bulge), "
        "CP[2]=(1.5,0,0) (end of first Bezier), "
        "CP[3]=(3.0,0,0) (1.5-unit C-1 gap drives shape_null), "
        "CP[4]=(4.0,0,0), CP[5]=(5,0,0); knots (3,3,3) at (0.0,0.5,1.0); "
        "ShapeAnalysis_Curve::Project endpoint-distance check returns early "
        "for bounded curve — interior minimum not searched; "
        "PCurve LINE (0,0)→(5,0); shape_null=True"
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

# Context edges (right, top, left) with proper pcurves
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
# THE CATALOG MECHANISM: Parabolic arc shape with interior bulge.
# CP[1]=(2.5,1.5,0) creates a bulge above the chord. For a query point on
# the chord, the endpoint distance check fires first and returns early,
# even though the interior of the arc is farther (or closer for different queries).
# The bounded-curve early-return bias prevents exhaustive interior search.
#
# C-1 DRIVER: CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit positional gap
# at knot t=0.5. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((2.5,  1.5, 0.0))   # interior bulge — parabolic arc shape
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('endpoint_bias_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve: LINE (0,0)→(5,0) — nominal path.
# Project on the parabolic 3D arc triggers endpoint early-return bias.
pp_start = f.cartesian_point((0.0, 0.0))
pp_dir   = f.direction((1.0, 0.0))
pp_vec   = f.vector(pp_dir, 5.0)
pp_line  = f.line(pp_start, pp_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('endpoint_bias_pc_def',(#{pp_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('endpoint_bias_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('endpoint_bias_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('endpoint_bias_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
