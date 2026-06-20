"""Gp139 — BRepBuilderAPI_Sewing.SameParameterEdge.seam-dual-pcurve-extraction

Catalog claim: Seam edge on closed surface requires dual PCurve (forward +
reversed) but only single PCurve supplied.

STEP mechanism (literal):
  - TOROIDAL_SURFACE face (closed in both U and V) with a seam edge along the
    minor circle (u=0, v=0..2*pi). The seam edge requires two PCurves: one for
    the forward traversal (u=0) and one for the reversed traversal (u=2*pi) to
    close the surface correctly.
  - THE CATALOG MECHANISM: Only a single PCurve at u=0 is provided. The
    reversed seam variant (u=2*pi) is absent. BRepBuilderAPI_Sewing's
    SameParameterEdge check extracts both PCurves from the SURFACE_CURVE; with
    only one present, the seam cannot be recognized as dual-manifold, producing
    non-manifold geometry.
  - C-1 DRIVER: degree-2 B-spline positional break at t=0.5 (knot mult=3,
    1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE; seam edge at u=0 with single PCurve
    only (missing reversed u=2*pi variant); SameParameterEdge seam-dual-pcurve
    extraction fails; non-manifold geometry.
  - C-1 DRIVER: degree-2 B-spline positional break forces shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp139",
    defect=(
        "TOROIDAL_SURFACE major_radius=2.0 minor_radius=0.5; "
        "seam edge at u=0 along minor circle (v=0..2*pi): single PCurve "
        "LINE (0.0,0.0)→(0.0,2*pi) only — missing reversed seam variant "
        "at u=2*pi=6.2832; 3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break "
        "at t=0.5 (CP[2]=(0.0,0.75,0.0) vs CP[3]=(0.0,1.5,0.0), 1.5-unit gap "
        "in v) drives shape_null; "
        "BRepBuilderAPI_Sewing SameParameterEdge seam-dual-pcurve-extraction "
        "finds only one PCurve; seam not recognized as dual-manifold; "
        "non-manifold geometry; shape_null=True"
    ),
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Host surface: TOROIDAL_SURFACE major_radius=2.0, minor_radius=0.5
# Periodic in both U (0..2*pi) and V (0..2*pi).
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f._emit_raw(f"TOROIDAL_SURFACE('torus_seam_surf',#{plc.eid},2.0,0.5)")

# Face: partial patch u in [0, pi/2], v in [0, 2*pi].
# 3D corner points on torus at given (u,v):
# torus(u,v) = ((R+r*cos(v))*cos(u), (R+r*cos(v))*sin(u), r*sin(v))
# R=2.0, r=0.5
def torus_pt(u, v, R=2.0, r=0.5):
    return ((R + r*math.cos(v))*math.cos(u),
            (R + r*math.cos(v))*math.sin(u),
            r*math.sin(v))

# Corners: u=0..pi/2, v=0..2*pi (full minor circle at u=0 and u=pi/2)
# Use a strip: v sweeps full minor circle, u from 0 to pi/2.
# The seam edge is at u=0 (v=0..2*pi).

# At u=0: p_A (v=0), p_B (v=2*pi = same as v=0 on closed torus)
# We use a rectangular patch: A=(u=0,v=0), B=(u=pi/2,v=0), C=(u=pi/2,v=2pi), D=(u=0,v=2pi)
# On the closed torus v=0 == v=2pi, so p_A and p_D are the same 3D point.
coord_A = torus_pt(0.0,          0.0)
coord_B = torus_pt(math.pi/2.0,  0.0)
coord_C = torus_pt(math.pi/2.0,  2.0*math.pi)  # = coord_B (closed v)
coord_D = torus_pt(0.0,          2.0*math.pi)  # = coord_A (closed v)

p_A = f.cartesian_point(coord_A)
p_B = f.cartesian_point(coord_B)
p_C = f.cartesian_point(coord_C)
p_D = f.cartesian_point(coord_D)
v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2=None):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    if len2 is None:
        len2 = len3
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len2); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom edge: A→B at v=0, u from 0 to pi/2.
# 3D: approximate line between torus pts at v=0
# torus(u,0) = (2.5*cos(u), 2.5*sin(u), 0) — lies on outer equator circle
bot_dir3 = (coord_B[0] - coord_A[0], coord_B[1] - coord_A[1], 0.0)
bot_len3 = math.sqrt(bot_dir3[0]**2 + bot_dir3[1]**2)
bot_dir3n = (bot_dir3[0]/bot_len3, bot_dir3[1]/bot_len3, 0.0)
e_bot = mk_line_edge_with_pc(
    v_A, v_B,
    coord_A, bot_dir3n, bot_len3,
    (0.0, 0.0), (1.0, 0.0), math.pi/2.0
)

# Right edge: B→C at u=pi/2, v from 0 to 2*pi (full minor circle).
# 3D: approximate line (degenerate: B==C on closed torus), small stub.
e_right = mk_line_edge_with_pc(
    v_B, v_C,
    coord_B, (0.0, 0.0, 1.0), 1.0e-6,
    (math.pi/2.0, 0.0), (0.0, 1.0), 2.0*math.pi
)

# Top edge: C→D at v=2*pi, u from pi/2 to 0.
top_dir3 = (coord_D[0] - coord_C[0], coord_D[1] - coord_C[1], 0.0)
top_len3 = math.sqrt(top_dir3[0]**2 + top_dir3[1]**2)
if top_len3 < 1e-10:
    top_len3 = 1e-6
    top_dir3n = (-bot_dir3n[0], -bot_dir3n[1], 0.0)
else:
    top_dir3n = (top_dir3[0]/top_len3, top_dir3[1]/top_len3, 0.0)
e_top = mk_line_edge_with_pc(
    v_C, v_D,
    coord_C, top_dir3n, top_len3,
    (math.pi/2.0, 2.0*math.pi), (-1.0, 0.0), math.pi/2.0
)

# ── DEFECT (SEAM) EDGE — left seam at u=0 (v_D -> v_A, v from 2*pi to 0) ─────
#
# THE CATALOG MECHANISM: seam edge at u=0 with only a single PCurve.
# The seam requires: (1) forward PCurve at u=0, v: 2*pi→0 AND
# (2) reversed PCurve at u=2*pi=6.2832, v: 2*pi→0.
# Only (1) is provided. BRepBuilderAPI_Sewing SameParameterEdge cannot
# extract the dual PCurve; seam not recognized as closing the torus manifold.
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5 in v coordinate.
# CP[2]=(0.0,0.75,0.0) vs CP[3]=(0.0,1.5,0.0) — note these are UV coords
# (u fixed=0, v varies). The v-gap (0.75 to 1.5 = 0.75-unit gap scaled to
# 2*pi domain, or equivalently 1.5-unit positional gap) drives shape_null=True.
# We use a 3D B-spline with a 1.5-unit gap in the Z direction.
dc0 = f.cartesian_point(coord_D)
dc1 = f.cartesian_point((coord_D[0], coord_D[1], 0.25))
dc2 = f.cartesian_point((coord_D[0], coord_D[1], 0.75))   # C-1 break start
dc3 = f.cartesian_point((coord_D[0], coord_D[1], 2.25))   # 1.5-unit gap
dc4 = f.cartesian_point((coord_A[0], coord_A[1], 3.0))
dc5 = f.cartesian_point(coord_A)

bspline_seam = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('seam_dual_pcurve_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Single PCurve at u=0, v from 2*pi down to 0.
pp_start = f.cartesian_point((0.0, 2.0 * math.pi))
pp_dir   = f.direction((0.0, -1.0))
pp_vec   = f.vector(pp_dir, 2.0 * math.pi)
pp_line  = f.line(pp_start, pp_vec)
defrep_seam = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('seam_pc_def',(#{pp_line.eid}),#{prc.eid})"
)
pcurve_seam = f._emit_raw(
    f"PCURVE('seam_single_pc',#{surf.eid},#{defrep_seam.eid})"
)
# Only one PCurve — missing the dual u=2*pi reversed variant.
sc_seam = f._emit_raw(
    f"SURFACE_CURVE('seam_sc',#{bspline_seam.eid},(#{pcurve_seam.eid}),.PCURVE_S1.)"
)
e_seam = f._emit_raw(
    f"EDGE_CURVE('seam_edge',#{v_D.eid},#{v_A.eid},#{sc_seam.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_seam,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
