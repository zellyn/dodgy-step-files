"""Gp103 — ShapeAnalysis_Edge.CheckPCurveRange CIRCLE-vs-trim-mismatch.

Catalog claim: Plane edge with 3D circle arc from parameter 0.5 to 6.0 rad
(outside [0, 2pi]). PCurve is untrimmed circle [0, 2pi]. CheckPCurveRange
fails to detect parameter range mismatch between pcurve domain and edge vertex
parameters.

STEP mechanism (literal):
  - PLANE Z=0 face, rectangular [0,4] x [0,2].
  - Bottom edge: EDGE_CURVE via SURFACE_CURVE.
    3D curve: CIRCLE radius=1, center=(2,0,0), wrapped in TRIMMED_CURVE with
    trim_1=PARAMETER_VALUE(0.5) and trim_2=PARAMETER_VALUE(6.0). The trim range
    [0.5, 6.0] exceeds the CIRCLE's natural period [0, 2*pi ~ 6.283].
    PCurve: bare CIRCLE in UV (radius=1, center=(2,0)) — no trim wrapper —
    so the pcurve domain is the full circle [0, 2*pi], NOT [0.5, 6.0].
  - THE CATALOG MECHANISM: CheckPCurveRange should detect that the TRIMMED_CURVE
    edge parameters [0.5, 6.0] exceed the underlying CIRCLE's period and that
    the pcurve domain [0, 2*pi] does not match the edge's parametric bounds —
    but it doesn't flag this mismatch. OCC heals silently.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp103",
    defect=(
        "PLANE Z=0 rectangle [0,4]x[0,2]; bottom edge: SURFACE_CURVE wrapping "
        "TRIMMED_CURVE(CIRCLE radius=1 center=(2,0,0), trim=[0.5,6.0] rad) — "
        "exceeds [0,2pi]; PCurve: bare CIRCLE radius=1 center=(2,0) in UV "
        "(no trim, domain [0,2pi]); CheckPCurveRange fails to flag mismatch "
        "between trim params [0.5,6.0] and pcurve domain [0,2pi]; "
        "OCC heals silently; shape(1)/shape(1)"
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

# Simple rectangle [0,4] x [0,2]. Bottom is the defect arc edge.
# Bottom edge goes v_a(0,0,0) -> v_b(4,0,0) — we use a LINE for this edge
# but the defect is a SURFACE_CURVE wrapping a TRIMMED_CURVE circle arc
# with the pcurve being a bare CIRCLE without matching trim.
# (We override the straight bottom with the arc in the SURFACE_CURVE wrapper.)
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) with pcurves
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
# THE CATALOG MECHANISM:
#
# 3D curve: CIRCLE radius=1, center=(2,0,0), wrapped in TRIMMED_CURVE.
# trim_1=0.5 rad, trim_2=6.0 rad. The trim [0.5, 6.0] exceeds [0, 2pi~6.283].
# This is the "over-period" trim that CheckPCurveRange should flag.
#
# PCurve: bare CIRCLE (no TRIMMED_CURVE wrapper) in UV at center=(2,0), radius=1.
# Its parameter domain is [0, 2*pi] — does NOT match [0.5, 6.0].
# CheckPCurveRange fails to detect this mismatch; OCC heals silently.

# 3D CIRCLE: center (2,0,0), normal Z, x-axis X
circ3d_ctr = f.cartesian_point((2.0, 0.0, 0.0))
circ3d_ax  = f.axis2_placement_3d(circ3d_ctr, zdir, xdir)
circ3d     = f._emit_raw(f"CIRCLE('trim_circ_3d',#{circ3d_ax.eid},1.0)")

# TRIMMED_CURVE: trim from 0.5 to 6.0 rad (PARAMETER_VALUE)
trim3d = f._emit_raw(
    f"TRIMMED_CURVE('trim_arc',#{circ3d.eid},"
    f"(PARAMETER_VALUE(0.5)),(PARAMETER_VALUE(6.0)),.T.,.PARAMETER.)"
)

# PCurve CIRCLE: center (2,0) in UV, radius=1.0 — bare, no trim wrapper.
# AXIS2_PLACEMENT_2D('name', location_2d, ref_direction_2d)
pc_ctr    = f.cartesian_point((2.0, 0.0))
pc_refdir = f.direction((1.0, 0.0))
pc_ax2    = f._emit_raw(f"AXIS2_PLACEMENT_2D('pc_ax2',#{pc_ctr.eid},#{pc_refdir.eid})")
pc_circ   = f._emit_raw(f"CIRCLE('trim_pc_circ',#{pc_ax2.eid},1.0)")

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('trim_pc_def',(#{pc_circ.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('trim_pcurve',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('trim_sc',#{trim3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('trim_mismatch_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
