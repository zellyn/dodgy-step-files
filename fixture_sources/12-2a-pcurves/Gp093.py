"""Gp093 — ShapeFix_Edge.FixAddPCurve construct-on-conical-surface near-apex.

Catalog claim: Edge near cone apex where (u,v) projection is mathematically
unstable; FixAddPCurve constructs pcurve with NaN coordinates. Fixture has
LINE edge on CONICAL_SURFACE at apex singularity (parameter space [0.001,0.001]
→[0.002,0.002]).

STEP mechanism (literal):
  - CONICAL_SURFACE (semi-angle 45°, apex at origin, axis Z, base radius 0).
  - The defect edge: a bare EDGE_CURVE (no SURFACE_CURVE wrapper, no pcurve)
    whose 3D LINE lies at u=pi/6, v=0.001 to v=0.002 — within the apex
    singularity region where the metric degenerates.
  - FixAddPCurve must project this LINE onto the cone surface. Near v=0.001
    the cone metric v*sin(45°) ≈ 0.0007 — almost zero. The UV projection is
    numerically unstable; FixAddPCurve produces NaN in the pcurve coordinates.
  - OCC heals by clamping the UV endpoint (0, eps) to a valid position.
  - THE CATALOG MECHANISM: bare EDGE_CURVE at apex-singularity region on a
    CONICAL_SURFACE; pcurve endpoint sits at UV (0, epsilon) for small epsilon.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
import math
from step_corpus.step_builder import StepFile

EPS = 0.001   # v-coordinate of defect edge start — apex singularity zone

f = StepFile(
    catalog_id="Gp093",
    defect=(
        "CONICAL_SURFACE semi-angle=45deg apex at origin; defect edge: bare "
        "EDGE_CURVE (no SURFACE_CURVE, no pcurve) LINE from v=0.001 to v=0.002 "
        "at u=pi/6; apex metric v*sin(45deg)~7e-4 causes NaN UV projection in "
        "FixAddPCurve; OCC heals by clamping UV endpoint (0, eps); shape(1)/shape(1)"
    ),
)

# CONICAL_SURFACE: semi-angle 45° (pi/4), apex at origin, axis Z, base radius 0.
# Parametric map: P(u,v) = (v*cos(u), v*sin(u), v)  [tan(pi/4)=1, base_radius=0]
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cone = f.conical_surface(plc, 0.0, math.pi / 4)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Helper to build a SURFACE_CURVE edge on the cone with a proper pcurve
def mk_cone_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on the cone."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Patch corner points in 3D: a small quad patch near the apex.
# u ranges over [0, pi/2], v ranges over [EPS, 2*EPS].
# P(u,v) = (v*cos(u), v*sin(u), v)
u0 = 0.0
u1 = math.pi / 2
v0 = EPS
v1 = 2 * EPS

p00 = f.cartesian_point((v0 * math.cos(u0), v0 * math.sin(u0), v0))  # (0.001, 0, 0.001)
p10 = f.cartesian_point((v0 * math.cos(u1), v0 * math.sin(u1), v0))  # (0, 0.001, 0.001)
p01 = f.cartesian_point((v1 * math.cos(u0), v1 * math.sin(u0), v1))  # (0.002, 0, 0.002)
p11 = f.cartesian_point((v1 * math.cos(u1), v1 * math.sin(u1), v1))  # (0, 0.002, 0.002)

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v01 = f.vertex_point(p01)
v11 = f.vertex_point(p11)

# ── DEFECT EDGE — from p00 to p01 (spoke at u=0, v=EPS→2*EPS) ────────────────
# THE CATALOG MECHANISM: bare EDGE_CURVE — no SURFACE_CURVE, no pcurve.
# The pcurve endpoint sits at UV (u=0, v=EPS) = (0, 0.001) — the apex singularity.
# FixAddPCurve must project this LINE onto the cone; at v=EPS the metric
# degenerates and the UV reconstruction produces NaN coordinates.
defect_line_d = f.direction((math.cos(u0), math.sin(u0), 1.0) if False else
                             (v1*math.cos(u0) - v0*math.cos(u0),
                              v1*math.sin(u0) - v0*math.sin(u0),
                              v1 - v0))
# Normalize the direction
dx = (v1 - v0) * math.cos(u0)
dy = (v1 - v0) * math.sin(u0)
dz = v1 - v0
dl = math.sqrt(dx*dx + dy*dy + dz*dz)
defect_d  = f.direction((dx/dl, dy/dl, dz/dl))
defect_vv = f.vector(defect_d, dl)
defect_line_3d = f.line(p00, defect_vv)

# Bare EDGE_CURVE (no SURFACE_CURVE, no pcurve) — this is the defect
e_spoke_defect = f._emit_raw(
    f"EDGE_CURVE('apex_singular_bare',#{v00.eid},#{v01.eid},#{defect_line_3d.eid},.T.)"
)

# Context edges: the other three sides with proper pcurves
# Bottom arc: at v=EPS, u from 0 to pi/2 (quarter circle in near-apex plane)
# 3D: from p00 to p10, arc of radius v0 in plane z=v0
arc_ctr0 = f.cartesian_point((0.0, 0.0, v0))
arc_axis0 = f.axis2_placement_3d(arc_ctr0, zdir, xdir)
arc_circ0 = f._emit_raw(f"CIRCLE('bot_arc',#{arc_axis0.eid},{v0})")
bot_arc_pc_start = f.cartesian_point((u0, v0))
bot_arc_pc_dir   = f.direction((1.0, 0.0))
bot_arc_pc_vec   = f.vector(bot_arc_pc_dir, u1 - u0)
bot_arc_pc_line  = f.line(bot_arc_pc_start, bot_arc_pc_vec)
defrep_bot = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{bot_arc_pc_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_arc_pc',#{cone.eid},#{defrep_bot.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot_sc',#{arc_circ0.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc_edge',#{v00.eid},#{v10.eid},#{sc_bot.eid},.T.)"
)

# Right spoke: at u=pi/2, v from EPS to 2*EPS (clean, with pcurve)
e_right = mk_cone_edge_with_pc(
    v10, v11,
    (v0*math.cos(u1), v0*math.sin(u1), v0),
    (0.0, (v1-v0)/dl, (v1-v0)/dl),
    dl,
    (u1, v0),
    (0.0, 1.0),
)

# Top arc: at v=2*EPS, u from 0 to pi/2
arc_ctr1  = f.cartesian_point((0.0, 0.0, v1))
arc_axis1 = f.axis2_placement_3d(arc_ctr1, zdir, xdir)
arc_circ1 = f._emit_raw(f"CIRCLE('top_arc',#{arc_axis1.eid},{v1})")
top_arc_pc_start = f.cartesian_point((u0, v1))
top_arc_pc_vec   = f.vector(bot_arc_pc_dir, u1 - u0)
top_arc_pc_line  = f.line(top_arc_pc_start, top_arc_pc_vec)
defrep_top = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('top_pc_def',(#{top_arc_pc_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_arc_pc',#{cone.eid},#{defrep_top.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_sc',#{arc_circ1.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
e_top = f._emit_raw(
    f"EDGE_CURVE('top_arc_edge',#{v01.eid},#{v11.eid},#{sc_top.eid},.T.)"
)

# Loop: defect_spoke(fwd) + top_arc(fwd) + right_spoke(rev) + bot_arc(rev)
loop = f.edge_loop([
    f.oriented_edge(e_spoke_defect, True),
    f.oriented_edge(e_top,          True),
    f.oriented_edge(e_right,        False),
    f.oriented_edge(e_bot,          False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
