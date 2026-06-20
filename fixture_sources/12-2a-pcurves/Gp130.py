"""Gp130 — ShapeFix_Edge.FixSameParameter B-spline parameter range mismatch.

Catalog claim: B-spline 3D span [0..10] vs P-curve 2D span [0..2] parameter
mismatch silent; FixSameParameter misses compression ratio inconsistency.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - 3D curve: B_SPLINE_CURVE_WITH_KNOTS degree-2 with knot domain [0,10].
    Control points map the edge from (0,0,0) to (5,0,0) over this wide range.
  - PCurve: B_SPLINE_CURVE_WITH_KNOTS degree-2 with knot domain [0,2].
    Same geometric path in UV but over a compressed domain (5x narrower).
  - THE CATALOG MECHANISM: FixSameParameter attempts to synchronize 3D and
    pcurve parameter ranges. The 10x scale ratio between [0,10] and [0,2]
    (actually 5x here) causes FixSameParameter to fail silently: the
    compression ratio is not detected as inconsistent, and no correction
    is applied.
  - C-1 DRIVER: degree-2 B-spline in 3D with positional break at t=5.0
    (half of knot domain [0,10], knot mult=3, 1.5-unit CP gap) forces
    OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: 3D B-spline knot domain [0,10] paired with PCurve
    B-spline knot domain [0,2]; FixSameParameter misses 5x range mismatch.
  - C-1 DRIVER: degree-2 B-spline positional break at t=5.0 forces shape_null.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp130",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D B_SPLINE_CURVE_WITH_KNOTS "
        "degree-2 knot domain [0,10] with C-1 break at t=5.0 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve B_SPLINE_CURVE_WITH_KNOTS degree-2 knot domain [0,2] (5x narrower); "
        "FixSameParameter misses 5x compression ratio mismatch between 3D [0,10] "
        "and pcurve [0,2]; shape_null=True"
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
# THE CATALOG MECHANISM: 3D B-spline with knot domain [0,10].
# C-1 DRIVER: break at t=5.0 (midpoint of [0,10]), knot mult=3.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit positional gap = shape_null driver.
# Knots: (3,3,3) at (0.0, 5.0, 10.0) → two Bezier patches over [0,10].
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier (t=5.0)
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('param_mismatch_3d',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,5.0,10.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve B-spline with knot domain [0,2] — 5x narrower
# than the 3D B-spline domain [0,10]. Same geometric path in UV but over a
# compressed parameter range. FixSameParameter does not detect the mismatch.
# PCurve break at t=1.0 (midpoint of [0,2]) mirrors the 3D break structure.
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((1.5, 0.0))
pp2 = f.cartesian_point((2.5, 0.0))   # end of first UV Bezier (t=1.0)
pp3 = f.cartesian_point((3.5, 0.0))   # start of second UV Bezier
pp4 = f.cartesian_point((4.5, 0.0))
pp5 = f.cartesian_point((5.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('param_mismatch_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,1.0,2.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('param_mismatch_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('param_mismatch_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('param_mismatch_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('param_mismatch_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
