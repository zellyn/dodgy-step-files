"""Gp076 -- ShapeFix_Edge.FixAddPCurve periodic-surface-seam.

Catalog claim: Edge 3D curve lies on the cylindrical seam (u=0 ≡ u=2π).
FixAddPCurve constructs a pcurve at u=0 but should also accept u=2π as
equivalent on periodic surfaces.  The pcurve is placed at u=2π (the
period-shifted branch of the seam), which FixAddPCurve incorrectly rejects.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE host, axis = Z, radius 1.
  - 3D defect curve: vertical line at X=1, Y=0 (the seam in world coords).
  - PCurve placed at u=2π (the period-shifted seam branch): a vertical line in
    UV at u=2π, v in [0,1].  FixAddPCurve checks whether the pcurve is on the
    surface; a pcurve at u=2π is geometrically on the seam but the algorithm
    only recognises u=0 as valid, flagging u=2π as a missing-pcurve case.
  - The 3D defect curve is also a degree-2 B-spline with a C-1 POSITIONAL BREAK
    at t=0.5 (knot mult=3, 1.5-unit Z gap) as the shape_null vehicle.

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve placed at u=2π (period-shifted seam branch) on
    a periodic CYLINDRICAL_SURFACE — FixAddPCurve only recognises u=0.
  - C-1 DRIVER: positional break in the B-spline 3D curve forces OCC
    shape_null=True (expected outcome).
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp076",
    defect=(
        "CYLINDRICAL_SURFACE radius=1, axis=Z; defect edge 3D curve = seam "
        "line at (1,0,*) (u=0=2π branch); PCurve placed at u=2π (period-shifted "
        "seam): vertical line (2π,0)→(2π,1) in UV; FixAddPCurve constructs "
        "pcurve only at u=0 and rejects u=2π as missing; 3D B-spline has C-1 "
        "positional break at t=0.5 (Z gap 1.5 units) driving OCC shape_null=True"
    ),
)

TAU = 2 * math.pi

# Host: CYLINDRICAL_SURFACE, radius=1, axis=Z through origin
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_z    = f.direction((0.0, 0.0, 1.0))
cyl_x    = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_z, cyl_x)
cyl_surf = f.cylindrical_surface(cyl_plc, 1.0)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Corner 3D points (on the cylinder surface, face patch u∈[0,π/2], v∈[0,1])
# At u=0: (1,0,*); at u=π/2: (0,1,*)
p00 = f.cartesian_point((1.0, 0.0, 0.0))   # u=0,    v=0
p10 = f.cartesian_point((0.0, 1.0, 0.0))   # u=π/2,  v=0
p11 = f.cartesian_point((0.0, 1.0, 1.0))   # u=π/2,  v=1
p01 = f.cartesian_point((1.0, 0.0, 1.0))   # u=0,    v=1
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

# ── DEFECT EDGE — left seam (v_00 -> v_01) at u=0 ────────────────────────────
# 3D B-spline: degree 2, 6 CPs, knots (3,3,3) at (0, 0.5, 1).
# Nominal path: (1,0,0) -> (1,0,1) (seam line).
# C-1 positional break at t=0.5: CP[2]=(1,0,0.3) vs CP[3]=(1,0,1.8) — 1.5-unit Z gap.
s0 = f.cartesian_point((1.0, 0.0, 0.0))
s1 = f.cartesian_point((1.0, 0.0, 0.1))
s2 = f.cartesian_point((1.0, 0.0, 0.3))   # before break
s3 = f.cartesian_point((1.0, 0.0, 1.8))   # after break: 1.5-unit Z gap
s4 = f.cartesian_point((1.0, 0.0, 0.9))
s5 = f.cartesian_point((1.0, 0.0, 1.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('seam_break',2,"
    f"(#{s0.eid},#{s1.eid},#{s2.eid},#{s3.eid},#{s4.eid},#{s5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: pcurve at u=2π (period-shifted seam branch).
# FixAddPCurve checks u=0 seam; u=2π is geometrically identical but
# algorithm-side is treated as distinct and flagged as missing pcurve.
pc_start_seam = f.cartesian_point((TAU, 0.0))   # u=2π, v=0
pc_dir_seam   = f.direction((0.0, 1.0))          # along v (Z direction)
pc_vec_seam   = f.vector(pc_dir_seam, 1.0)
pc_line_seam  = f.line(pc_start_seam, pc_vec_seam)

defrep_seam = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('seam_pc_def',(#{pc_line_seam.eid}),#{prc.eid})"
)
pcurve_seam = f._emit_raw(
    f"PCURVE('seam_pc_2pi',#{cyl_surf.eid},#{defrep_seam.eid})"
)
sc_seam = f._emit_raw(
    f"SURFACE_CURVE('seam',#{bspline_3d.eid},(#{pcurve_seam.eid}),.PCURVE_S1.)"
)
e_seam = f._emit_raw(
    f"EDGE_CURVE('seam_edge',#{v00.eid},#{v01.eid},#{sc_seam.eid},.T.)"
)

# ── Context edges: top arc, right arc, left seam ─────────────────────────────
# Top arc (v=1): CIRCLE trimmed [0, π/2]
top_ctr = f.cartesian_point((0.0, 0.0, 1.0))
top_z   = f.direction((0.0, 0.0, 1.0))
top_x   = f.direction((1.0, 0.0, 0.0))
top_ax  = f.axis2_placement_3d(top_ctr, top_z, top_x)
top_circ = f.circle(top_ax, 1.0)
top_tc = f._emit_raw(
    f"TRIMMED_CURVE('top_arc',#{top_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2})),.T.,.PARAMETER.)"
)
pc_top_s = f.cartesian_point((0.0, 1.0))
pc_top_d = f.direction((1.0, 0.0)); pc_top_v = f.vector(pc_top_d, math.pi/2)
pc_top_l = f.line(pc_top_s, pc_top_v)
pcd_top = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('top_pc_def',(#{pc_top_l.eid}),#{prc.eid})"
)
pc_top  = f._emit_raw(f"PCURVE('top_pc',#{cyl_surf.eid},#{pcd_top.eid})")
sc_top  = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_tc.eid},(#{pc_top.eid}),.PCURVE_S1.)"
)
e_top = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v01.eid},#{v11.eid},#{sc_top.eid},.T.)"
)

# Bottom arc (v=0): CIRCLE trimmed [0, π/2]
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_z   = f.direction((0.0, 0.0, 1.0))
bot_x   = f.direction((1.0, 0.0, 0.0))
bot_ax  = f.axis2_placement_3d(bot_ctr, bot_z, bot_x)
bot_circ = f.circle(bot_ax, 1.0)
bot_tc = f._emit_raw(
    f"TRIMMED_CURVE('bot_arc',#{bot_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2})),.T.,.PARAMETER.)"
)
pc_bot_s = f.cartesian_point((0.0, 0.0))
pc_bot_d = f.direction((1.0, 0.0)); pc_bot_v = f.vector(pc_bot_d, math.pi/2)
pc_bot_l = f.line(pc_bot_s, pc_bot_v)
pcd_bot = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{pc_bot_l.eid}),#{prc.eid})"
)
pc_bot  = f._emit_raw(f"PCURVE('bot_pc',#{cyl_surf.eid},#{pcd_bot.eid})")
sc_bot  = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bot_tc.eid},(#{pc_bot.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v00.eid},#{v10.eid},#{sc_bot.eid},.T.)"
)

# Right vertical (u=π/2): line at (0,1,*), v from 0 to 1
p_rr = f.cartesian_point((0.0, 1.0, 0.0))
d_rr = f.direction((0.0, 0.0, 1.0)); v_rr = f.vector(d_rr, 1.0)
l_rr = f.line(p_rr, v_rr)
pc_r_s = f.cartesian_point((math.pi/2, 0.0))
pc_r_d = f.direction((0.0, 1.0)); pc_r_v = f.vector(pc_r_d, 1.0)
pc_r_l = f.line(pc_r_s, pc_r_v)
pcd_r = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('rpc_def',(#{pc_r_l.eid}),#{prc.eid})"
)
pc_r = f._emit_raw(f"PCURVE('rpc',#{cyl_surf.eid},#{pcd_r.eid})")
sc_r = f._emit_raw(
    f"SURFACE_CURVE('right_vert',#{l_rr.eid},(#{pc_r.eid}),.PCURVE_S1.)"
)
e_right = f._emit_raw(
    f"EDGE_CURVE('right_vert',#{v10.eid},#{v11.eid},#{sc_r.eid},.T.)"
)

# Face loop: bottom arc (v00->v10), right vert (v10->v11), top arc reversed (v11->v01), seam (v01->v00 reversed)
loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   False),
    f.oriented_edge(e_seam,  False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
