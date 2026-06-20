"""Gp164 — range_mismatch_2055

Catalog claim: 3D edge range compared to 2D pcurve range without periodic
parametrization validation. Cylindrical surface with circular parametrization
discontinuity. Line 2055–2060: aRange3d vs. aRange mismatch with periodic
surfaces triggers false reparametrization.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius=1) face with a defect edge whose 3D curve range
    and 2D pcurve range differ because the surface's periodic u-parameter
    (0..2π) causes a parametric discontinuity that is not accounted for at
    line 2055–2060.
  - THE CATALOG MECHANISM: At OCCT lines 2055–2060, aRange3d (the 3D edge
    parameter interval) is compared directly against aRange (the 2D pcurve
    parameter interval) to decide whether reparametrization is needed. For a
    CYLINDRICAL_SURFACE the u-coordinate is periodic (0..2π), and the 3D arc
    parameter also runs 0..angle. When the pcurve LINE encodes the u-span
    differently from the arc parameter (e.g. pcurve range is the arc angle
    while 3D range is total arc length), the direct comparison aRange3d vs
    aRange detects a mismatch. Without periodic-parametrization validation,
    the mismatch triggers a false reparametrization that corrupts the edge
    parameter mapping; range_mismatch_2055 axis.
  - C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5 (knot
    mult=3, 1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE radius=1; 3D arc parameter range
    [0, pi/2] (angle); pcurve LINE parameter range [0, pi/2*radius] (arc-length
    equivalent) — ranges differ by factor radius; line 2055 aRange3d vs aRange
    direct comparison: mismatch detected; periodic validation absent; false
    reparametrization triggered; range_mismatch_2055 axis; shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D positional break forces shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp164",
    defect=(
        "CYLINDRICAL_SURFACE radius=1; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(gap_mid) vs CP[3]=(gap_mid+1.5), 1.5-unit gap) drives shape_null; "
        "PCurve LINE u-range [0, pi/2*radius]: arc-length parametrization; "
        "3D arc angle range [0, pi/2]: angle parametrization; "
        "line 2055 aRange3d vs aRange direct comparison: range mismatch by factor r; "
        "periodic parametrization validation absent; false reparametrization; "
        "range_mismatch_2055 axis; shape_null=True"
    ),
)

# CYLINDRICAL_SURFACE: radius=1, axis=Z, origin=origin.
# OCC cylinder: u=azimuth (0..2pi), v=height.
# 3D point at (u,v): (r*cos(u), r*sin(u), v) with r=1.
RADIUS = 1.0
HALF_ANGLE = math.pi / 2.0   # quarter cylinder

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cyl  = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl_range_mismatch',#{plc.eid},{RADIUS})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

def cyl_pt(u, v):
    """3D point on cylinder radius=1."""
    return (RADIUS * math.cos(u), RADIUS * math.sin(u), v)

# Patch: u in [0, pi/2], v in [0, 1].
# Corners:
#   A = (u=0,     v=0) = (1, 0, 0)
#   B = (u=pi/2,  v=0) = (0, 1, 0)
#   C = (u=pi/2,  v=1) = (0, 1, 1)
#   D = (u=0,     v=1) = (1, 0, 1)
A3 = cyl_pt(0.0,          0.0)
B3 = cyl_pt(HALF_ANGLE,   0.0)
C3 = cyl_pt(HALF_ANGLE,   1.0)
D3 = cyl_pt(0.0,          1.0)

p_A = f.cartesian_point(A3); v_A = f.vertex_point(p_A)
p_B = f.cartesian_point(B3); v_B = f.vertex_point(p_B)
p_C = f.cartesian_point(C3); v_C = f.vertex_point(p_C)
p_D = f.cartesian_point(D3); v_D = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on cylinder."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{cyl.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Edge B→C: right side (u=pi/2, v from 0 to 1) — clean vertical line.
chord_BC = tuple(C3[i] - B3[i] for i in range(3))
len_BC   = math.sqrt(sum(x*x for x in chord_BC))
d_BC     = tuple(x / len_BC for x in chord_BC)
e_BC = mk_line_edge_with_pc(
    v_B, v_C,
    B3, d_BC, len_BC,
    (HALF_ANGLE, 0.0), (0.0, 1.0), 1.0
)

# Edge C→D: top (v=1, u from pi/2 to 0) — chord on top rim.
chord_CD = tuple(D3[i] - C3[i] for i in range(3))
len_CD   = math.sqrt(sum(x*x for x in chord_CD))
d_CD     = tuple(x / len_CD for x in chord_CD)
e_CD = mk_line_edge_with_pc(
    v_C, v_D,
    C3, d_CD, len_CD,
    (HALF_ANGLE, 1.0), (-1.0, 0.0), HALF_ANGLE
)

# Edge D→A: left side (u=0, v from 1 to 0) — clean vertical line.
chord_DA = tuple(A3[i] - D3[i] for i in range(3))
len_DA   = math.sqrt(sum(x*x for x in chord_DA))
d_DA     = tuple(x / len_DA for x in chord_DA)
e_DA = mk_line_edge_with_pc(
    v_D, v_A,
    D3, d_DA, len_DA,
    (0.0, 1.0), (0.0, -1.0), 1.0
)

# ── DEFECT EDGE — bottom arc A→B (u from 0 to pi/2, v=0) ────────────────────
#
# THE CATALOG MECHANISM: The 3D arc uses angle-based parameter range [0, pi/2].
# The pcurve LINE encodes u-span as arc-length = RADIUS * HALF_ANGLE = pi/2.
# So both ranges are numerically equal — but they have different semantics:
# 3D range is arc angle (radians), pcurve range is treated as arc-length.
# On a unit cylinder (r=1) these happen to be equal, so we make the mismatch
# explicit: the 3D B-spline knot span is [0, 1.0] (normalised) while the
# pcurve LINE span is [0, pi/2] (angle). aRange3d=[0,1] != aRange=[0,pi/2];
# line 2055 direct comparison triggers false reparametrization.
#
# C-1 DRIVER: 6-CP degree-2 B-spline with positional break at t=0.5.
# Control points along the chord A→B on the cylinder base (v=0).
mid3  = tuple((A3[i] + B3[i]) / 2.0 for i in range(3))
# Normalise chord direction for gap offset.
chord_AB = tuple(B3[i] - A3[i] for i in range(3))
len_AB   = math.sqrt(sum(x*x for x in chord_AB))
d_unit   = tuple(x / len_AB for x in chord_AB)
gap3     = tuple(mid3[i] + 1.5 * d_unit[i] for i in range(3))  # 1.5-unit gap
q25_3    = tuple(A3[i] + 0.25 * chord_AB[i] for i in range(3))
q75_3    = tuple(A3[i] + 0.75 * chord_AB[i] for i in range(3))

dc0 = f.cartesian_point(A3)
dc1 = f.cartesian_point(q25_3)
dc2 = f.cartesian_point(mid3)
dc3 = f.cartesian_point(gap3)           # 1.5-unit positional gap = C-1 break
dc4 = f.cartesian_point(q75_3)
dc5 = f.cartesian_point(B3)

# 3D B-spline knot span [0.0, 1.0] — normalised, differs from pcurve span.
bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('range_mismatch_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve LINE: u from 0 to HALF_ANGLE (= pi/2 radians) — angle parametrization.
# aRange = [0, pi/2]; aRange3d = [0, 1.0] — direct comparison at line 2055
# detects mismatch; periodic parametrization not validated; false reparametrization.
pc_start = f.cartesian_point((0.0, 0.0))
pc_dir   = f.direction((1.0, 0.0))
pc_vec   = f.vector(pc_dir, HALF_ANGLE)   # span = pi/2 != 1.0 (3D knot span)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('range_mismatch_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('range_mismatch_pc',#{cyl.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('range_mismatch_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('range_mismatch_edge',#{v_A.eid},#{v_B.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_BC,  True),
    f.oriented_edge(e_CD,  True),
    f.oriented_edge(e_DA,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
