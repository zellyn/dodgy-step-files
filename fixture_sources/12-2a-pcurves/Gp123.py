"""Gp123 — ShapeAnalysis_Edge.CheckPCurveRange CIRCLE with-large-radius.

Catalog claim: Pcurve CIRCLE with radius 1e6 on a small face.
CheckPCurveRange's range check uses absolute parameter not arc-length,
so the tolerance check overflows for the extremely large-radius circle;
OCC heals.

STEP mechanism (literal):
  - PLANE Z=0 face, rectangle [0,4] x [0,2].
  - Defect edge: SURFACE_CURVE; 3D LINE from (0,0,0) to (4,0,0).
  - THE CATALOG MECHANISM: PCurve is a CIRCLE with radius 1e6 in UV
    (center far away), parameters [0, 4e-6 rad] — the tiny arc at huge
    radius subtends exactly 4 UV units (arc-length = radius * angle =
    1e6 * 4e-6 = 4). CheckPCurveRange's range check computes parameter
    tolerance in absolute units (not arc-length units), so the 4e-6 rad
    range looks vanishingly small and "overflows" the tolerance threshold.
    OCC heals silently; shape(1)/shape(1).
  - NO C-1 break (Archetype B: OCC silently heals; shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve CIRCLE radius=1e6; parameter range ~4e-6 rad;
    CheckPCurveRange absolute-param tolerance overflow; OCC heals silently.
"""
import math
from step_corpus.step_builder import StepFile

# Large-radius circle: center at (0, -1e6) in UV, radius=1e6.
# At parameter t=0: point = center + radius*(cos(0), sin(0)) = (1e6, -1e6) + ...
# Use AXIS2_PLACEMENT_2D with center at (0, -1e6).
# At t=0: (0 + 1e6*1, -1e6 + 1e6*0) = (1e6, -1e6)... that's not (0,0).
# Better: center at (0, -1e6, 0) UV, with x-ref axis pointing (0,1) so
# t=0 puts us at (0, 0) in UV (due to AXIS2_PLACEMENT_2D convention).
# STEP CIRCLE(placement, radius): P(t) = loc + r*(cos(t)*refdir + sin(t)*normal_x_refdir)
# With loc=(0,-1e6), refdir=(0,1): P(0) = (0,-1e6) + 1e6*(0,1) = (0,0). ✓
# P(4e-6) ≈ (0,-1e6) + 1e6*(sin(4e-6), cos(4e-6))
#           ≈ (0,-1e6) + 1e6*(4e-6, 1) = (4, 0) in UV. ✓

RADIUS = 1e6
ANGLE  = 4.0 / RADIUS   # ≈ 4e-6 rad; arc-length = RADIUS * ANGLE = 4.0
# Format ANGLE without scientific notation for STEP part21 compliance
ANGLE_STR = f"{ANGLE:.10f}"  # e.g. "0.0000040000" — no scientific notation

f = StepFile(
    catalog_id="Gp123",
    defect=(
        "PLANE Z=0 rectangle [0,4]x[0,2]; defect edge: SURFACE_CURVE; "
        "3D LINE (0,0,0)→(4,0,0); PCurve CIRCLE radius=1e6 center=(0,-1e6) "
        "ref_dir=(0,1) in UV — so P(0)=(0,0), P(4e-6)≈(4,0); "
        "parameter range [0, 4e-6 rad] spans arc-length=4 but absolute "
        "param is 4e-6; CheckPCurveRange absolute-param tolerance check "
        "overflows for large-radius circle; OCC heals silently; shape(1)/shape(1)"
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
# THE CATALOG MECHANISM: PCurve is CIRCLE with radius=1e6.
# AXIS2_PLACEMENT_2D: center=(0,-1e6) in UV, ref_dir=(0,1).
# This places P(0)=(0,0) and P(ANGLE)≈(4,0) in UV.
# The parameter range [0, ANGLE] where ANGLE≈4e-6 is tiny in absolute terms.
# CheckPCurveRange uses absolute parameter tolerance — 4e-6 rad overflows threshold.
# The 3D curve is a clean LINE from (0,0,0)→(4,0,0).

# 3D LINE
line_p  = f.cartesian_point((0.0, 0.0, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 4.0)
line_3d = f.line(line_p, line_v)

# PCurve CIRCLE: AXIS2_PLACEMENT_2D at (0, -1e6), ref_dir=(0,1)
# CIRCLE wraps a 2D placement. In STEP, CIRCLE uses the placement's location
# and ref_direction to define the circle parametrization.
pc_ctr    = f.cartesian_point((0.0, -1000000.0))
pc_refdir = f.direction((0.0, 1.0))
pc_ax2    = f._emit_raw(f"AXIS2_PLACEMENT_2D('large_r_ax2',#{pc_ctr.eid},#{pc_refdir.eid})")
pc_circ   = f._emit_raw(f"CIRCLE('large_r_circ',#{pc_ax2.eid},{RADIUS:.1f})")

# Wrap in TRIMMED_CURVE to set the parameter range [0, ANGLE]
pc_trim = f._emit_raw(
    f"TRIMMED_CURVE('large_r_trim',#{pc_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({ANGLE_STR})),.T.,.PARAMETER.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('large_r_pc_def',(#{pc_trim.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('large_r_pcurve',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('large_r_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('large_r_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
