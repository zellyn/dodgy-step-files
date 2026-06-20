"""Gp119 — Cylinder seam-edge pcurve ambiguity.

Catalog claim: ShapeFix_Edge.FixSameParameter handles seam edge (u=0 vs u=2π)
ambiguously; pcurve parameter mismatch between 0 and 2π. OCC picks one
consistently.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE (radius=1, axis=Z) face with a seam edge at the
    cylinder seam. The seam corresponds to u=0 which is equivalent to u=2π
    by periodicity.
  - THE CATALOG MECHANISM: The defect edge sits on the cylinder seam. Its
    SURFACE_CURVE provides a pcurve that uses u=2π (≈6.2832) instead of u=0.
    Both u=0 and u=2π map to the same 3D line (at angle 0 on the cylinder),
    but FixSameParameter must determine which periodic branch to use. The
    pcurve parameter u=2π is valid but non-canonical; the parameter mismatch
    between the canonical u=0 and the encoded u=2π triggers the ambiguity.
    OCC picks one branch consistently and heals to shape(1)/shape(1).
  - 3D curve: clean LINE running along the cylinder seam at (1,0,z), z from 0
    to 1. Geometry is valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: CYLINDRICAL_SURFACE seam edge with pcurve at u=2π
    instead of canonical u=0; FixSameParameter seam ambiguity; OCC heals.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp119",
    defect=(
        "CYLINDRICAL_SURFACE radius=1 axis=Z; seam edge at u=0 (≡u=2π); "
        "defect edge: SURFACE_CURVE; 3D LINE on seam (1,0,0)→(1,0,1); "
        "PCurve LINE in UV from (2π, 0.0) direction (0.0,1.0) length 1 "
        "(non-canonical u=2π instead of u=0); FixSameParameter seam "
        "ambiguity: u=0 vs u=2π both valid; OCC picks canonical branch; "
        "shape(1)/shape(1)"
    ),
)

# CYLINDRICAL_SURFACE: radius=1, axis=Z, origin at (0,0,0)
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
cyl   = f._emit_raw(f"CYLINDRICAL_SURFACE('cylinder_r1',#{plc.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face: quarter-cylinder patch, u∈[0, π/2], v∈[0, 1].
# 3D corners:
#   A = (1, 0, 0)   u=0,    v=0
#   B = (0, 1, 0)   u=π/2,  v=0
#   C = (0, 1, 1)   u=π/2,  v=1
#   D = (1, 0, 1)   u=0,    v=1  (= u=2π, the seam)
p_A = f.cartesian_point((1.0, 0.0, 0.0))
p_B = f.cartesian_point((0.0, 1.0, 0.0))
p_C = f.cartesian_point((0.0, 1.0, 1.0))
p_D = f.cartesian_point((1.0, 0.0, 1.0))
v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# ── DEFECT EDGE A→D (seam at u=0≡u=2π, v from 0 to 1): pcurve uses u=2π ──────
# THE CATALOG MECHANISM: 3D LINE on seam, pcurve LINE at u=2π (non-canonical).
seam_dir  = f.direction((0.0, 0.0, 1.0))
seam_v    = f.vector(seam_dir, 1.0)
seam_3d   = f.line(p_A, seam_v)

# PCurve at u=2π (non-canonical seam branch)
pc_seam_start = f.cartesian_point((2.0 * math.pi, 0.0))
pc_seam_dir   = f.direction((0.0, 1.0))
pc_seam_vec   = f.vector(pc_seam_dir, 1.0)
pc_seam_line  = f.line(pc_seam_start, pc_seam_vec)
defrep_seam = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('seam_pc_def',(#{pc_seam_line.eid}),#{prc.eid})"
)
pcurve_seam = f._emit_raw(f"PCURVE('seam_2pi_pc',#{cyl.eid},#{defrep_seam.eid})")
sc_AD = f._emit_raw(
    f"SURFACE_CURVE('seam_sc',#{seam_3d.eid},(#{pcurve_seam.eid}),.PCURVE_S1.)"
)
e_AD = f._emit_raw(
    f"EDGE_CURVE('seam_edge',#{v_A.eid},#{v_D.eid},#{sc_AD.eid},.T.)"
)

# ── Clean bottom arc A→B (v=0, u from 0 to π/2) ──────────────────────────────
# CIRCLE at z=0, radius=1
bot_ctr  = f.cartesian_point((0.0, 0.0, 0.0))
bot_ax   = f.axis2_placement_3d(bot_ctr, zdir, xdir)
bot_circ = f._emit_raw(f"CIRCLE('bot_circ',#{bot_ax.eid},1.0)")
bot_trim = f._emit_raw(
    f"TRIMMED_CURVE('bot_arc',#{bot_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2.0})),.T.,.PARAMETER.)"
)
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir   = f.direction((1.0, 0.0))
pc_bot_vec   = f.vector(pc_bot_dir, math.pi / 2.0)
pc_bot_line  = f.line(pc_bot_start, pc_bot_vec)
defrep_bot = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pc',#{cyl.eid},#{defrep_bot.eid})")
sc_AB = f._emit_raw(
    f"SURFACE_CURVE('bot_sc',#{bot_trim.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
e_AB = f._emit_raw(
    f"EDGE_CURVE('bot_arc_edge',#{v_A.eid},#{v_B.eid},#{sc_AB.eid},.T.)"
)

# ── Clean right spoke B→C (u=π/2, v from 0 to 1) ─────────────────────────────
right_dir = f.direction((0.0, 0.0, 1.0))
right_v   = f.vector(right_dir, 1.0)
right_3d  = f.line(p_B, right_v)
pc_right_start = f.cartesian_point((math.pi / 2.0, 0.0))
pc_right_dir   = f.direction((0.0, 1.0))
pc_right_vec   = f.vector(pc_right_dir, 1.0)
pc_right_line  = f.line(pc_right_start, pc_right_vec)
defrep_right = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('right_pc_def',(#{pc_right_line.eid}),#{prc.eid})"
)
pcurve_right = f._emit_raw(f"PCURVE('right_pc',#{cyl.eid},#{defrep_right.eid})")
sc_BC = f._emit_raw(
    f"SURFACE_CURVE('right_sc',#{right_3d.eid},(#{pcurve_right.eid}),.PCURVE_S1.)"
)
e_BC = f._emit_raw(
    f"EDGE_CURVE('right_spoke',#{v_B.eid},#{v_C.eid},#{sc_BC.eid},.T.)"
)

# ── Clean top arc D→C (v=1, u from 0 to π/2) ─────────────────────────────────
top_ctr  = f.cartesian_point((0.0, 0.0, 1.0))
top_ax   = f.axis2_placement_3d(top_ctr, zdir, xdir)
top_circ = f._emit_raw(f"CIRCLE('top_circ',#{top_ax.eid},1.0)")
top_trim = f._emit_raw(
    f"TRIMMED_CURVE('top_arc',#{top_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2.0})),.T.,.PARAMETER.)"
)
pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir   = f.direction((1.0, 0.0))
pc_top_vec   = f.vector(pc_top_dir, math.pi / 2.0)
pc_top_line  = f.line(pc_top_start, pc_top_vec)
defrep_top = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('top_pc_def',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_pc',#{cyl.eid},#{defrep_top.eid})")
sc_DC = f._emit_raw(
    f"SURFACE_CURVE('top_sc',#{top_trim.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
e_DC = f._emit_raw(
    f"EDGE_CURVE('top_arc_edge',#{v_D.eid},#{v_C.eid},#{sc_DC.eid},.T.)"
)

# Loop: A→B (fwd), B→C (fwd), C→D (rev top), D→A (rev seam)
loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BC, True),
    f.oriented_edge(e_DC, False),
    f.oriented_edge(e_AD, False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
