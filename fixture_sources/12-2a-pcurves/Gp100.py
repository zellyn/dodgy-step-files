"""Gp100 — ShapeAnalysis_Edge.GetEndTangent2d POLYLINE first-point.

Catalog claim: PCURVE as POLYLINE. GetEndTangent2d uses last two points for
last endpoint but forgets to use first two points for first endpoint, yielding
asymmetric tangent extraction.

STEP mechanism (literal):
  - PLANE face with a defect edge whose pcurve is a degree-1
    B_SPLINE_CURVE_WITH_KNOTS in .POLYLINE_FORM. with 4 control points.
  - THE CATALOG MECHANISM: the POLYLINE has a degenerate first segment:
    CP[0] == CP[1] (both at the same UV position). This means GetEndTangent2d,
    when computing the tangent at the first point by looking at CP[0]→CP[1],
    gets a zero-length direction vector and divides by zero.
  - C-1 DRIVER: the 3D curve is a degree-2 B_SPLINE_CURVE_WITH_KNOTS with a
    positional break (knot multiplicity 3 at interior knot, large CP gap)
    between segments, forcing OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: POLYLINE pcurve with CP[0]==CP[1] (degenerate first
    segment); GetEndTangent2d divides by zero on the leading direction.
  - C-1 DRIVER: degree-2 B-spline 3D curve with C-1 positional break at t=0.5
    forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp100",
    defect=(
        "PLANE Z=0; defect edge: 3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break "
        "at t=0.5 (CP[2]=(2.0,0,0) vs CP[3]=(3.5,0,0), 1.5-unit gap) drives "
        "shape_null; PCurve is B_SPLINE_CURVE_WITH_KNOTS .POLYLINE_FORM. degree-1 "
        "4-point with CP[0]==CP[1]=(0.0,0.0) (degenerate first segment); "
        "GetEndTangent2d divides by zero on CP[0]→CP[1] zero-length direction; "
        "shape_null=True"
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

# Context edges (right, top, left) — clean
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5.
# CP[2]=(2.0,0,0) vs CP[3]=(3.5,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((1.0, 0.0, 0.0))
dc2 = f.cartesian_point((2.0, 0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.5, 0.0, 0.0))   # start of second — 1.5 gap = C-1 break
dc4 = f.cartesian_point((4.2, 0.0, 0.0))
dc5 = f.cartesian_point((5.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('polyline_3d',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: POLYLINE pcurve.
# B_SPLINE_CURVE_WITH_KNOTS degree-1 .POLYLINE_FORM. with 4 CPs.
# CP[0] == CP[1] = (0.0, 0.0) — the DEGENERATE FIRST SEGMENT.
# GetEndTangent2d computes first-point tangent from CP[0]→CP[1] = zero vector
# → division by zero in the tangent normalization.
# CP[2] and CP[3] are normal UV progression points.
pp0 = f.cartesian_point((0.0, 0.0))   # degenerate: same as pp1
pp1 = f.cartesian_point((0.0, 0.0))   # degenerate: same as pp0 — zero first segment
pp2 = f.cartesian_point((2.5, 0.0))   # normal middle point
pp3 = f.cartesian_point((5.0, 0.0))   # end point

polyline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('degen_polyline_pc',1,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid}),"
    f".POLYLINE_FORM.,.F.,.F.,"
    f"(2,1,1,2),(0.0,0.333,0.667,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('polyline_pc_def',(#{polyline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('polyline_pcurve',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('polyline_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('polyline_degen_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
