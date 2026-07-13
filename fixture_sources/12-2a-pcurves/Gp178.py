"""Gp178 — Contour wrapping both a degenerated pole AND the periodic seam,
needing pcurve rebuild.

Work packet D1, item `tkshh-edge-crossing-surface-singularity` (PARTIAL,
missing 2 of 2), subvariant (b): "a contour wrapping both a degenerated
pole and the seam, needing pcurve rebuild with AdjustOverDegenMode=false."
Companion to Gp177 (subvariant a: interior-of-edge pole crossing on a
non-cap contour). This fixture is the classic "spherical cap" UV-rectangle
topology: u in [0, 2*pi] (full azimuth -- wraps the periodic seam), v in
[v0, pi/2] (up to the pole, which collapses to a single point -- the
degenerate top edge).

Geometry: SPHERICAL_SURFACE radius 1, standard placement. Four sides of
the UV rectangle:
  - bottom: latitude circle at v=v0 (healthy, self-loop, u: 0 -> 2*pi)
  - seam: meridian arc at u=0 from the equator-ish vertex up to the pole
    vertex -- used TWICE in the loop (once representing the u=0 bank, once
    the u=2*pi bank), same idiom as Gp013's CATIA-style seam
  - top: degenerate edge at the pole (v=pi/2, self-loop, zero-radius
    circle -- the whole row collapses to one point in 3D)

THE DEFECT: unlike Gp013 (which gives its shared seam edge BOTH pcurves,
one per bank), this SURFACE_CURVE carries only ONE pcurve (the u=0 bank)
even though the seam edge is referenced twice in the loop -- once for the
u=0 bank, once for the u=2*pi bank. The second (u=2*pi) occurrence has no
matching pcurve at all. A contour that wraps a degenerate pole (top) *and*
the periodic seam (left/right) but is missing half of its seam pcurve pair
needs the healer to rebuild the missing pcurve from the 3D curve/period,
not just reuse what's given.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp178",
    defect=(
        "Spherical-cap UV-rectangle contour (u:0->2pi wraps the periodic "
        "seam, v:v0->pi/2 reaches the degenerate pole row) whose shared "
        "seam EDGE_CURVE is used twice in the loop (u=0 bank and u=2pi "
        "bank, CATIA-seam idiom per Gp013) but its SURFACE_CURVE carries "
        "only ONE pcurve instead of two -- the u=2pi occurrence has no "
        "matching pcurve, forcing a rebuild rather than reuse."
    ),
)

v0 = 0.3  # latitude of the bottom rim, radians

# SPHERICAL_SURFACE, radius 1, standard placement (axis Z, ref X).
s_orig = f.cartesian_point((0.0, 0.0, 0.0))
s_axis = f.direction((0.0, 0.0, 1.0))
s_ref = f.direction((1.0, 0.0, 0.0))
s_plc = f.axis2_placement_3d(s_orig, s_axis, s_ref)
sphere = f.spherical_surface(s_plc, 1.0)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices: V_eq at (u=0,v=v0); V_pole at the north pole.
p_eq = f.cartesian_point((math.cos(v0), 0.0, math.sin(v0)))
p_pole = f.cartesian_point((0.0, 0.0, 1.0))
v_eq = f.vertex_point(p_eq)
v_pole = f.vertex_point(p_pole)

# ---- Bottom edge: latitude circle at v=v0, self-loop, healthy. ----
bot_loc = f.cartesian_point((0.0, 0.0, math.sin(v0)))
bot_axis = f.direction((0.0, 0.0, 1.0))
bot_ref = f.direction((1.0, 0.0, 0.0))
bot_plc = f.axis2_placement_3d(bot_loc, bot_axis, bot_ref)
bot_circle = f._emit_raw(f"CIRCLE('bottom_rim',#{bot_plc.eid},{math.cos(v0)!r})")

pc_bot_start = f.cartesian_point((0.0, v0))
pc_bot_dir = f.direction((1.0, 0.0))
pc_bot_vec = f.vector(pc_bot_dir, 2.0 * math.pi)
pc_bot_line = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot_def',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pcurve',#{sphere.eid},#{pc_bot_def.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bottom_rim_sc',#{bot_circle.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
edge_bot = f._emit_raw(
    f"EDGE_CURVE('bottom_edge',#{v_eq.eid},#{v_eq.eid},#{sc_bot.eid},.T.)"
)

# ---- Seam edge: meridian arc at u=0, from V_eq to V_pole. THE DEFECT:
# only ONE pcurve even though used twice in the loop below. ----
seam_loc = f.cartesian_point((0.0, 0.0, 0.0))
seam_axis = f.direction((0.0, -1.0, 0.0))
seam_ref = f.direction((1.0, 0.0, 0.0))
seam_plc = f.axis2_placement_3d(seam_loc, seam_axis, seam_ref)
seam_circle = f._emit_raw(f"CIRCLE('seam_meridian',#{seam_plc.eid},1.0)")
seam_trim = f._emit_raw(
    f"TRIMMED_CURVE('seam_trim',#{seam_circle.eid},"
    f"(PARAMETER_VALUE({v0!r})),(PARAMETER_VALUE({math.pi/2.0!r})),.T.,.PARAMETER.)"
)

# Only pcurve for the u=0 bank: UV line (0,v0) -> (0,pi/2).
pc_seam_start = f.cartesian_point((0.0, v0))
pc_seam_dir = f.direction((0.0, 1.0))
pc_seam_vec = f.vector(pc_seam_dir, math.pi / 2.0 - v0)
pc_seam_line = f.line(pc_seam_start, pc_seam_vec)
pc_seam_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_seam_u0_def',(#{pc_seam_line.eid}),#{prc.eid})"
)
pcurve_seam_u0 = f._emit_raw(f"PCURVE('seam_pcurve_u0_only',#{sphere.eid},#{pc_seam_def.eid})")
sc_seam = f._emit_raw(
    f"SURFACE_CURVE('seam_sc',#{seam_trim.eid},(#{pcurve_seam_u0.eid}),.PCURVE_S1.)"
)
edge_seam = f._emit_raw(
    f"EDGE_CURVE('seam_edge',#{v_eq.eid},#{v_pole.eid},#{sc_seam.eid},.T.)"
)

# ---- Top edge: degenerate at the pole, self-loop, zero-radius circle. ----
top_plc = f.axis2_placement_3d(p_pole, s_axis, s_ref)
top_circle = f._emit_raw(f"CIRCLE('pole_degenerate',#{top_plc.eid},0.0)")
pc_top_start = f.cartesian_point((2.0 * math.pi, math.pi / 2.0))
pc_top_dir = f.direction((-1.0, 0.0))
pc_top_vec = f.vector(pc_top_dir, 2.0 * math.pi)
pc_top_line = f.line(pc_top_start, pc_top_vec)
pc_top_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top_def',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_pcurve',#{sphere.eid},#{pc_top_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('pole_sc',#{top_circle.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
edge_top = f._emit_raw(
    f"EDGE_CURVE('pole_edge',#{v_pole.eid},#{v_pole.eid},#{sc_top.eid},.T.)"
)

# Loop, mirroring Gp013's seam idiom: bottom(fwd) -> seam(fwd, u=2pi bank,
# NO matching pcurve) -> top(rev) -> seam(rev, u=0 bank, uses the one
# pcurve we did provide).
loop = f.edge_loop([
    f.oriented_edge(edge_bot, True),
    f.oriented_edge(edge_seam, True),
    f.oriented_edge(edge_top, False),
    f.oriented_edge(edge_seam, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
