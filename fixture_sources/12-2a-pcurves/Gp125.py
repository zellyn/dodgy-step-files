"""Gp125 — ShapeAnalysis_Edge.GetEndTangent2d at-trim-boundary.

Catalog claim: Pcurve is TRIMMED_CURVE. GetEndTangent2d uses
untrimmed-curve tangent at trim boundary, producing wrong direction.

STEP mechanism (literal):
  - PLANE Z=0 face, rectangle [0,4] x [0,2].
  - Defect edge: SURFACE_CURVE; 3D LINE from (0,0,0) to (4,0,0).
  - THE CATALOG MECHANISM: The pcurve is a TRIMMED_CURVE wrapping a
    B-spline. The trim_1 boundary sits exactly at an interior knot of
    the B-spline. GetEndTangent2d evaluates the tangent of the underlying
    (untrimmed) B-spline at the trim boundary; at an interior knot the
    tangent has a potential one-sided discontinuity. GetEndTangent2d
    picks a side (the untrimmed-curve side), which may be inconsistent
    with the direction in which the trim approaches the boundary.
    OCC heals silently; shape(1)/shape(1).
  - 3D curve: a clean LINE from (0,0,0) to (4,0,0). Geometry is valid.
  - NO C-1 break (Archetype B: OCC silently heals; shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve TRIMMED_CURVE wrapping B-spline with
    trim_1 at interior knot; GetEndTangent2d untrimmed tangent direction;
    OCC heals silently.
"""
from step_corpus.step_builder import StepFile

# B-spline pcurve design:
# Degree-2, 5 control points, knots at 0.0, 0.5, 1.0.
# CPs produce a shape that runs (0,0)→(4,0) in UV, with an interior
# knot at t=0.5 (mid-parameter).
# TRIMMED_CURVE trim_1=0.5 (interior knot), trim_2=1.0 (end).
# This means GetEndTangent2d at the START of the trimmed curve uses
# the untrimmed B-spline tangent at t=0.5 (interior knot), which is
# the right-side tangent — not the trimmed-curve start tangent.
#
# B_SPLINE_CURVE_WITH_KNOTS degree=2, 5 CPs:
# knot multiplicities: [3, 2, 3] at knots [0.0, 0.5, 1.0]
# sum=8 = n_poles(5) + degree(2) + 1 = 8 ✓
# CPs: (0,0), (2,0), (2,0), (4,0), (4,0) — the middle segment has CPs near (2,0).
# At t=0: (0,0); at t=0.5: near (2,0); at t=1: (4,0). (Approx flat along v=0.)

f = StepFile(
    catalog_id="Gp125",
    defect=(
        "PLANE Z=0 rectangle [0,4]x[0,2]; defect edge: SURFACE_CURVE; "
        "3D LINE (0,0,0)→(4,0,0); PCurve: TRIMMED_CURVE wrapping "
        "B_SPLINE_CURVE_WITH_KNOTS degree=2 5CPs knots=[0,0.5,1] mult=[3,2,3]; "
        "trim_1=PARAMETER_VALUE(0.5) (interior knot), trim_2=PARAMETER_VALUE(1.0); "
        "GetEndTangent2d at trim_1=0.5 evaluates untrimmed B-spline tangent "
        "at interior knot, picking one-sided direction inconsistent with "
        "trimmed-curve traversal; OCC heals silently; shape(1)/shape(1)"
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

# Face corners
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 2.0, 0.0), (-1., 0., 0.), 4.0, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
# 3D curve: clean LINE
line_p  = f.cartesian_point((0.0, 0.0, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 4.0)
line_3d = f.line(line_p, line_v)

# THE CATALOG MECHANISM: B-spline pcurve with interior knot at t=0.5.
# CPs all along v=0 in UV: (0,0), (1,0), (2,0), (3,0), (4,0)
# Degree=2, knots [0, 0.5, 1], multiplicities [3, 2, 3] → sum=8 = 5+2+1 ✓
cp0 = f.cartesian_point((0.0, 0.0))
cp1 = f.cartesian_point((1.0, 0.0))
cp2 = f.cartesian_point((2.0, 0.0))
cp3 = f.cartesian_point((3.0, 0.0))
cp4 = f.cartesian_point((4.0, 0.0))

bspline_pc = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[cp0, cp1, cp2, cp3, cp4],
    knot_multiplicities=[3, 2, 3],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)

# TRIMMED_CURVE: trim_1=0.5 (interior knot boundary), trim_2=1.0 (end)
# This places the START of the trimmed curve exactly at the interior knot t=0.5.
# GetEndTangent2d at trim_1=0.5 will query the untrimmed B-spline tangent at t=0.5,
# which picks the right-side (t>0.5) derivative, potentially inconsistent with
# how the trimmed curve enters from that boundary.
pc_trim = f._emit_raw(
    f"TRIMMED_CURVE('knot_boundary_trim',#{bspline_pc.eid},"
    f"(PARAMETER_VALUE(0.5)),(PARAMETER_VALUE(1.0)),.T.,.PARAMETER.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('knot_trim_pc_def',(#{pc_trim.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('knot_trim_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('knot_trim_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('knot_trim_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
