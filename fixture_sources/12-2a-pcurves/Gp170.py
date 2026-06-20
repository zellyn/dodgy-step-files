"""Gp170 — ProjectDegenerated.iso-flag-unvalidated

Catalog claim: Planar surface with U-iso degenerate edge. U-constant pcurve lacks
coordinate-axis consistency check; flag used without validation.
OCC cannot heal; produces empty/empty.

STEP mechanism (literal):
  - PLANE (Z=0) face with a defect edge whose pcurve is a U-constant (iso-u) LINE
    encoded in the wrong direction, making it appear to be a U-iso but failing
    the coordinate-axis consistency check.
  - THE CATALOG MECHANISM (iso-flag-unvalidated): ProjectDegenerated sets an
    iso-degenerate flag when it detects that a pcurve is constant in one
    coordinate (U or V). The flag is then consumed by downstream healing without
    validating whether the pcurve actually is consistent with a coordinate-axis
    iso line. For a pcurve that is nearly-U-constant but has a small V drift,
    the flag fires but the consistency check is absent; the flag is consumed
    incorrectly by the healing path. Combined with a C-1 break in the 3D B-spline,
    OCC cannot recover; shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5 (knot
    mult=3, 1.5-unit CP gap) forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE Z=0; defect pcurve LINE is nearly-U-constant but has
    a small V drift (0.005 per unit u): iso-flag fires on near-U-constant
    detection; coordinate-axis consistency check absent; flag consumed incorrectly;
    iso-flag-unvalidated axis; combined with C-1 break, OCC cannot heal;
    shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D positional break forces shape_null=True.

Distinction from Gp157-160 (various shape(1) ProjectDegenerated variants): those
are all OCC-healable. Gp170 adds the C-1 break that prevents healing, plus the
iso-flag-unvalidated trigger which is specific to coordinate-axis consistency.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp170",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2] vs CP[3] 1.5-unit gap) drives shape_null; "
        "PCurve LINE from (0.0,0.0) to (5.0,0.025) — nearly-U-constant "
        "(V drift=0.005/unit): iso-flag fires on near-U-constant detection; "
        "coordinate-axis consistency check absent; flag used without validation; "
        "iso-flag-unvalidated axis; shape_null=True"
    ),
)

# PLANE Z=0.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,5] x [0,2] in 3D (on the Z=0 plane).
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on plane."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.), 2.0)
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.), 5.0)
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.), 2.0)

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(2.5,0,0) vs CP[3]=(4.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.5,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('iso_flag_unvalidated_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve is nearly-U-constant (iso-u direction) with a
# small V drift of 0.005 per unit u (total V drift = 0.025 over u=0..5).
# ProjectDegenerated fires the iso-degenerate flag because the pcurve appears
# to be a U-iso line (V nearly constant). But it does NOT validate that the
# pcurve is exactly coordinate-axis-aligned; the small V drift means the
# consistency check would fail if it ran. The flag is used without this check;
# iso-flag-unvalidated axis. Combined with the C-1 break, OCC cannot heal.
V_DRIFT_TOTAL = 0.025   # small V drift: 0.005/unit over 5 units
pc_start = f.cartesian_point((0.0, 0.0))
# Direction includes the V drift: nearly (1,0) but with slight V tilt.
# Normalize the direction over length 5.
raw_d = (5.0, V_DRIFT_TOTAL)
raw_len = math.sqrt(raw_d[0]**2 + raw_d[1]**2)
pc_dir   = f.direction((raw_d[0] / raw_len, raw_d[1] / raw_len))
pc_vec   = f.vector(pc_dir, raw_len)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('iso_flag_unval_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('iso_flag_unval_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('iso_flag_unval_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('iso_flag_unval_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
