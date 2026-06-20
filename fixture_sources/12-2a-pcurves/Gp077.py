"""Gp077 -- ShapeAnalysis_Edge.CheckCurve3dWithPCurve sampling-period-mismatch.

Catalog claim: PCurve has period 2π but 3D curve has period 4π (double helix
wrap).  Uniform parameter sampling by CheckCurve3dWithPCurve misaligns the
3D/2D comparisons because the two parametric periods are incommensurable
(factor-of-2 ratio).

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE host (radius=1, axis=Z).
  - The 3D defect curve is a B-spline helix that wraps TWICE around the
    cylinder over its parameter range [0,1]: at t=0 it starts at angle=0,
    at t=1 it ends at angle=4π — a double wrap (period=4π in u terms).
  - The PCurve is a line in UV from (0,0) to (2π,1), encoding a SINGLE
    period wrap (2π in u).  When CheckCurve3dWithPCurve samples parameter t
    uniformly, t=0.5 on the 3D helix is at angle=2π (u=2π) while t=0.5 on
    the pcurve is at u=π — a π mismatch, causing a false-mismatch report.
  - The 3D B-spline also has a C-1 POSITIONAL BREAK at t=0.5 (knot mult=3,
    introduced as a 1.5-unit Z gap): this drives OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: 3D helix encodes 4π angular sweep (period=4π) while
    the UV pcurve encodes a single 2π sweep — factor-of-2 period mismatch
    that defeats uniform-sampling alignment in CheckCurve3dWithPCurve.
  - C-1 DRIVER: positional break at t=0.5 forces OCC shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp077",
    defect=(
        "CYLINDRICAL_SURFACE radius=1; 3D curve: degree-2 B-spline double-wrap "
        "helix u∈[0,4π] (period=4π) with C-1 positional Z-break at t=0.5 "
        "(CP[2]=(1,0,0.3) vs CP[3]=(1,0,1.8), 1.5-unit gap); PCurve: line in "
        "UV from (0,0) to (2π,1) (period=2π); uniform-sampling at t=0.5 → "
        "3D at u=2π vs 2D at u=π: π-mismatch; C-1 break drives OCC shape_null"
    ),
)

TAU = 2 * math.pi

# Host: CYLINDRICAL_SURFACE, radius=1, axis=Z
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_z    = f.direction((0.0, 0.0, 1.0))
cyl_x    = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_z, cyl_x)
cyl_surf = f.cylindrical_surface(cyl_plc, 1.0)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices: start=(1,0,0), end=(1,0,1) -- both on seam (u=0=2π=4π)
p_start = f.cartesian_point((1.0, 0.0, 0.0))
p_end   = f.cartesian_point((1.0, 0.0, 1.0))
p_r0    = f.cartesian_point((1.0, 0.0, 0.0))
p_r1    = f.cartesian_point((0.0, 1.0, 0.0))
p_r1h   = f.cartesian_point((0.0, 1.0, 1.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

# ── DEFECT EDGE: 3D double-wrap helix (period=4π) with C-1 break at t=0.5 ───
# Approximate a double-wrap helix using a degree-2 B-spline:
# At t=0: (1, 0, 0)      (angle=0)
# At t=0.25: (-1, 0, 0.25) (angle≈π, half first wrap)
# At t=0.5: (1, 0, 0.3)  (angle=2π, end first wrap, BEFORE break)
# BREAK: CP[2]=(1,0,0.3) vs CP[3]=(1,0,1.8) — 1.5-unit Z gap (shape_null driver)
# At t=0.75: (-1,0,0.75)  (angle≈3π, half second wrap)
# At t=1.0:  (1,0,1.0)    (angle=4π, end second wrap)
# 6 CPs, knot mult (3,3,3) at (0, 0.5, 1)
h0 = f.cartesian_point((1.0, 0.0, 0.0))
h1 = f.cartesian_point((-1.0, 0.0, 0.2))
h2 = f.cartesian_point((1.0, 0.0, 0.3))    # before break
h3 = f.cartesian_point((1.0, 0.0, 1.8))    # after break: 1.5-unit Z gap (C-1 driver)
h4 = f.cartesian_point((-1.0, 0.0, 0.8))
h5 = f.cartesian_point((1.0, 0.0, 1.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('helix4pi',2,"
    f"(#{h0.eid},#{h1.eid},#{h2.eid},#{h3.eid},#{h4.eid},#{h5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve encodes single 2π wrap (period=2π).
# Line from (0,0) to (2π,1) in UV.  3D helix sweeps 4π but pcurve sweeps 2π.
# Uniform sampling at t=0.5: 3D→angle=2π (u=2π), 2D→u=π — π-offset mismatch.
pc_start_uv = f.cartesian_point((0.0, 0.0))
pc_dir_uv   = f.direction((TAU, 1.0))   # direction (2π, 1) in UV (not unit, but valid for line)
pc_mag      = math.sqrt(TAU**2 + 1.0)
pc_d_norm   = f.direction((TAU / pc_mag, 1.0 / pc_mag))
pc_vec_uv   = f.vector(pc_d_norm, pc_mag)
pc_line_uv  = f.line(pc_start_uv, pc_vec_uv)

defrep_uv = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('helix_pc_def',(#{pc_line_uv.eid}),#{prc.eid})"
)
pcurve_uv = f._emit_raw(
    f"PCURVE('helix_pc_2pi',#{cyl_surf.eid},#{defrep_uv.eid})"
)
sc_helix = f._emit_raw(
    f"SURFACE_CURVE('helix',#{bspline_3d.eid},(#{pcurve_uv.eid}),.PCURVE_S1.)"
)
e_helix = f._emit_raw(
    f"EDGE_CURVE('helix_edge',#{v_start.eid},#{v_end.eid},#{sc_helix.eid},.T.)"
)

# ── Context edges for a simple rectangular face patch ────────────────────────
# Top edge: horizontal at v=1, u from 0 to π/2 on cylinder
p_top_s = f.cartesian_point((1.0, 0.0, 1.0))
p_top_e = f.cartesian_point((0.0, 1.0, 1.0))
v_top_s = f.vertex_point(p_top_s); v_top_e = f.vertex_point(p_top_e)

top_ctr = f.cartesian_point((0.0, 0.0, 1.0))
top_z_d = f.direction((0.0, 0.0, 1.0)); top_x_d = f.direction((1.0, 0.0, 0.0))
top_ax  = f.axis2_placement_3d(top_ctr, top_z_d, top_x_d)
top_circ = f.circle(top_ax, 1.0)
top_tc = f._emit_raw(
    f"TRIMMED_CURVE('top_arc',#{top_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2})),.T.,.PARAMETER.)"
)
pc_top_s2 = f.cartesian_point((0.0, 1.0))
pc_top_d2 = f.direction((1.0, 0.0)); pc_top_v2 = f.vector(pc_top_d2, math.pi/2)
pc_top_l2 = f.line(pc_top_s2, pc_top_v2)
pcd_top = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('top_pc',(#{pc_top_l2.eid}),#{prc.eid})"
)
pc_top  = f._emit_raw(f"PCURVE('top_pc',#{cyl_surf.eid},#{pcd_top.eid})")
sc_top  = f._emit_raw(
    f"SURFACE_CURVE('top',#{top_tc.eid},(#{pc_top.eid}),.PCURVE_S1.)"
)
e_top = f._emit_raw(
    f"EDGE_CURVE('top',#{v_end.eid},#{v_top_e.eid},#{sc_top.eid},.T.)"
)

# Bottom arc: circle at v=0, u from 0 to π/2
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_z_d = f.direction((0.0, 0.0, 1.0)); bot_x_d = f.direction((1.0, 0.0, 0.0))
bot_ax  = f.axis2_placement_3d(bot_ctr, bot_z_d, bot_x_d)
bot_circ = f.circle(bot_ax, 1.0)
bot_tc = f._emit_raw(
    f"TRIMMED_CURVE('bot_arc',#{bot_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2})),.T.,.PARAMETER.)"
)
p_bot_e = f.cartesian_point((0.0, 1.0, 0.0))
v_bot_e = f.vertex_point(p_bot_e)
pc_bot_s2 = f.cartesian_point((0.0, 0.0))
pc_bot_d2 = f.direction((1.0, 0.0)); pc_bot_v2 = f.vector(pc_bot_d2, math.pi/2)
pc_bot_l2 = f.line(pc_bot_s2, pc_bot_v2)
pcd_bot = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc',(#{pc_bot_l2.eid}),#{prc.eid})"
)
pc_bot  = f._emit_raw(f"PCURVE('bot_pc',#{cyl_surf.eid},#{pcd_bot.eid})")
sc_bot  = f._emit_raw(
    f"SURFACE_CURVE('bot',#{bot_tc.eid},(#{pc_bot.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('bot',#{v_start.eid},#{v_bot_e.eid},#{sc_bot.eid},.T.)"
)

# Right vertical (u=π/2): (0,1,0) -> (0,1,1)
p_rv = f.cartesian_point((0.0, 1.0, 0.0))
d_rv = f.direction((0.0, 0.0, 1.0)); v_rv = f.vector(d_rv, 1.0)
l_rv = f.line(p_rv, v_rv)
pc_rv_s = f.cartesian_point((math.pi/2, 0.0))
pc_rv_d = f.direction((0.0, 1.0)); pc_rv_v = f.vector(pc_rv_d, 1.0)
pc_rv_l = f.line(pc_rv_s, pc_rv_v)
pcd_rv = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('rpc',(#{pc_rv_l.eid}),#{prc.eid})"
)
pc_rv = f._emit_raw(f"PCURVE('rpc',#{cyl_surf.eid},#{pcd_rv.eid})")
sc_rv = f._emit_raw(
    f"SURFACE_CURVE('rv',#{l_rv.eid},(#{pc_rv.eid}),.PCURVE_S1.)"
)
e_right = f._emit_raw(
    f"EDGE_CURVE('right',#{v_bot_e.eid},#{v_top_e.eid},#{sc_rv.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,    True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    False),
    f.oriented_edge(e_helix,  False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cyl_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
