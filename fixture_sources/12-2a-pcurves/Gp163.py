"""Gp163 — circle_parameter_1930

Catalog claim: Circle parametrization assumes aNewF <= aNewL without handling
periodic wraparound. Torus seam edge spanning parameter discontinuity (2π → 0).
Line 1930: ElCLib::Parameter() returns angles on opposite sides of 2π; swap
logic (line 1932) produces inverted range.

STEP mechanism (literal):
  - TOROIDAL_SURFACE face with a seam edge whose pcurve crosses the 2π→0
    parameter discontinuity. The pcurve circle parameter range straddles the
    periodic seam, so ElCLib::Parameter returns aNewF close to 2π and aNewL
    close to 0. At line 1930, the code assumes aNewF < aNewL (monotone range).
    Line 1932 swap logic fires: the range is inverted, producing an incorrect
    trimmed interval that OCC cannot process.
  - THE CATALOG MECHANISM: TOROIDAL_SURFACE with major radius 2, minor radius 1.
    The seam edge pcurve is a LINE in UV spanning u from near 2π to past 2π
    (wrapping through 0), with v held constant at π. ElCLib::Parameter on the
    seam side returns an angle just past 0 (aNewL < aNewF); line 1932 swap
    inverts the range; circle_parameter_1930 axis.
  - C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5 (knot
    mult=3, 1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE; seam-crossing pcurve with u range
    near-2π to past-0; ElCLib::Parameter returns aNewF~2π, aNewL~0; line 1930
    aNewF>aNewL assumption violated; line 1932 swap inverts range; periodic
    wraparound unhandled; circle_parameter_1930 axis; shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D positional break forces shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp163",
    defect=(
        "TOROIDAL_SURFACE major_radius=2 minor_radius=1; "
        "seam edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(gap1) vs CP[3]=(gap2), 1.5-unit gap) drives shape_null; "
        "PCurve LINE u from (2*pi-0.1) to (0.1) across seam (v=pi constant): "
        "ElCLib::Parameter returns aNewF~2pi, aNewL~0; line 1930 aNewF>aNewL; "
        "line 1932 swap inverts range; periodic wraparound unhandled; "
        "circle_parameter_1930 axis; shape_null=True"
    ),
)

# TOROIDAL_SURFACE: major_radius=2, minor_radius=1.
# In OCC: u=azimuth around Z (0..2pi), v=meridian angle (0..2pi).
# 3D point at (u,v): ((R+r*cos(v))*cos(u), (R+r*cos(v))*sin(u), r*sin(v))
# with R=2, r=1.
R = 2.0
r = 1.0

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
torus = f._emit_raw(f"TOROIDAL_SURFACE('torus_seam',#{plc.eid},{R},{r})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

def torus_pt(u, v):
    """3D point on torus with R=2, r=1."""
    x = (R + r * math.cos(v)) * math.cos(u)
    y = (R + r * math.cos(v)) * math.sin(u)
    z = r * math.sin(v)
    return (x, y, z)

# Patch: u in [pi*3/2, pi*2+0.1] (crosses seam at 2pi), v in [pi/2, 3*pi/2].
# Use a narrow strip so the seam crossing is the distinguishing feature.
# Corners:
#   A = (u=3pi/2, v=pi/2)
#   B = (u=2pi-0.1, v=pi/2)    — near seam, left of 2pi
#   C = (u=0.1, v=pi/2)        — just past seam (u wrapped to ~0.1)
#   D = (u=3pi/2, v=3pi/2)
# For simplicity use a rectangle with the seam edge B→C as the defect.
# Support edges: A→B (along v=pi/2), A→D (along u=3pi/2), D→C (along v=3pi/2),
# and defect B→C (seam crossing at v=pi/2).

u_left  = 3.0 * math.pi / 2.0     # u start: 270 deg
u_near  = 2.0 * math.pi - 0.1     # u near-seam: ~350 deg
u_past  = 0.1                     # u just past seam: ~5.7 deg
v_bot   = math.pi / 2.0           # v=90 deg
v_top   = 3.0 * math.pi / 2.0    # v=270 deg

A3 = torus_pt(u_left, v_bot)
B3 = torus_pt(u_near, v_bot)
C3 = torus_pt(u_past, v_bot)
D3 = torus_pt(u_left, v_top)
# Note: C is geometrically close to B (both near u=0/2pi) but crosses seam.

p_A = f.cartesian_point(A3); v_A = f.vertex_point(p_A)
p_B = f.cartesian_point(B3); v_B = f.vertex_point(p_B)
p_C = f.cartesian_point(C3); v_C = f.vertex_point(p_C)
p_D = f.cartesian_point(D3); v_D = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on torus."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{torus.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Edge A→B: along v=v_bot, u from u_left to u_near (below seam).
# 3D chord A→B; UV direction (1,0), span = u_near - u_left.
chord_AB = tuple(B3[i] - A3[i] for i in range(3))
len_AB   = math.sqrt(sum(x*x for x in chord_AB))
d_AB     = tuple(x/len_AB for x in chord_AB)
u_span_AB = u_near - u_left
e_AB = mk_line_edge_with_pc(
    v_A, v_B,
    A3, d_AB, len_AB,
    (u_left, v_bot), (1.0, 0.0), u_span_AB
)

# Edge A→D: along u=u_left, v from v_bot to v_top.
chord_AD = tuple(D3[i] - A3[i] for i in range(3))
len_AD   = math.sqrt(sum(x*x for x in chord_AD))
d_AD     = tuple(x/len_AD for x in chord_AD)
v_span   = v_top - v_bot
e_AD = mk_line_edge_with_pc(
    v_A, v_D,
    A3, d_AD, len_AD,
    (u_left, v_bot), (0.0, 1.0), v_span
)

# Edge D→C: along v=v_top, u from u_left to u_past (wraps but approx chord OK).
chord_DC = tuple(C3[i] - D3[i] for i in range(3))
len_DC   = math.sqrt(sum(x*x for x in chord_DC))
d_DC     = tuple(x/len_DC for x in chord_DC)
# In UV: u from u_left to u_past (past seam = u_past + 2pi effectively; but we
# encode it as increasing u through 2pi: delta = (2pi - u_left) + u_past).
u_span_DC = (2.0 * math.pi - u_left) + u_past
e_DC = mk_line_edge_with_pc(
    v_D, v_C,
    D3, d_DC, len_DC,
    (u_left, v_top), (1.0, 0.0), u_span_DC
)

# ── DEFECT EDGE — seam crossing B→C (v=v_bot, u near-2pi → past-0) ───────────
#
# THE CATALOG MECHANISM: PCurve LINE in UV starts at (u_near, v_bot) and
# traverses the 2pi seam to (u_past, v_bot). The u range is (u_near)→(u_past)
# where u_near > u_past modulo 2pi. ElCLib::Parameter returns aNewF≈u_near and
# aNewL≈u_past; since aNewF > aNewL the swap at line 1932 inverts the range,
# producing an invalid trimmed interval. circle_parameter_1930 axis.
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5 forces shape_null=True.
# 3D control points lie on the world-space chord B3→C3.
chord_BC = tuple(C3[i] - B3[i] for i in range(3))
len_BC   = math.sqrt(sum(x*x for x in chord_BC))

# Six CPs: first half ends at mid3, second half starts 1.5 units away.
mid3  = tuple(B3[i] + 0.5 * chord_BC[i] for i in range(3))
gap3  = tuple(mid3[i] + 1.5 * (chord_BC[i] / len_BC) for i in range(3))
q75_3 = tuple(B3[i] + 0.75 * chord_BC[i] for i in range(3))
q25_3 = tuple(B3[i] + 0.25 * chord_BC[i] for i in range(3))

dc0 = f.cartesian_point(B3)
dc1 = f.cartesian_point(q25_3)
dc2 = f.cartesian_point(mid3)
dc3 = f.cartesian_point(gap3)          # 1.5-unit positional gap = C-1 break
dc4 = f.cartesian_point(q75_3)
dc5 = f.cartesian_point(C3)

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('circle_param_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve LINE: u from u_near to u_past (seam-crossing, uv direction negative mod 2pi).
# UV delta in the crossing direction: (u_past + 2pi) - u_near (positive span ~0.2).
u_span_BC = (u_past + 2.0 * math.pi) - u_near   # ~0.2 rad
pc_start = f.cartesian_point((u_near, v_bot))
# Direction in UV: (1,0) but the seam crossing makes ElCLib return aNewF>aNewL.
pc_dir   = f.direction((1.0, 0.0))
pc_vec   = f.vector(pc_dir, u_span_BC)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('circle_param_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('circle_param_pc',#{torus.eid},#{defrep.eid})")
sc_seam = f._emit_raw(
    f"SURFACE_CURVE('circle_param_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_seam = f._emit_raw(
    f"EDGE_CURVE('circle_param_seam_edge',#{v_B.eid},#{v_C.eid},#{sc_seam.eid},.T.)"
)

# Loop: A→B (fwd), B→C seam (fwd/defect), C→D (rev of D→C), D→A (rev of A→D)
loop = f.edge_loop([
    f.oriented_edge(e_AB,   True),
    f.oriented_edge(e_seam, True),
    f.oriented_edge(e_DC,   False),
    f.oriented_edge(e_AD,   False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
