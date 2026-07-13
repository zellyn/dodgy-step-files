"""Gp182 — CATIA-style seam-like edge (two pcurves on one surface, same-
sense duplicate) on a non-B-spline base surface, forcing approximation
before periodicity handling.

Work packet D1, item `tkshh-nonperiodic-bspline-seamlike-edge` (PARTIAL,
missing 2 of 3), subvariant (b): "same defect on a non-B-spline base
surface, forcing GeomConvert_ApproxSurface before periodicity can be set."
problem_id `tkshh-nonperiodic-bspline-seamlike-edge`
(ShapeUpgrade_UnifySameDomain::IntUnifyFaces, ShapeUpgrade_UnifySameDomain.
cxx:3221 EdgeWith2pcurves&&!SeamFound detection, :3258 GeomConvert_
ApproxSurface for non-B-spline base, :3264/:3269 SetUPeriodic/
SetVPeriodic). Gp013 and Gp181 both use a B_SPLINE_SURFACE_WITH_KNOTS host
(where SetUPeriodic/SetVPeriodic apply directly, no conversion needed).
This fixture puts the identical seam-like-edge idiom on a CYLINDRICAL_
SURFACE host instead -- an elementary/analytic surface type that Geom's
API cannot mark periodic in place -- so a correct healer must approximate
it to a B-spline (GeomConvert_ApproxSurface) before it can invoke
SetUPeriodic on the result.

Geometry: a genuine unit cylinder (radius 1, height 1), but represented
directly as a CYLINDRICAL_SURFACE (not a near-closed B-spline approximation
of one). The shared seam EDGE_CURVE runs the height direction at u=0/u=2*pi
(both physically angle=0) and carries two pcurves on the same surface --
the identical "two pcurves on one surface acting like a seam" idiom Gp013
uses, just on an elementary surface class instead of a B-spline.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp182",
    defect=(
        "Unit cylinder (radius 1, height 1) represented directly as a "
        "CYLINDRICAL_SURFACE (elementary, non-B-spline). The shared seam "
        "EDGE_CURVE runs the height direction at u=0/u=2*pi (both "
        "physically angle=0) and carries two pcurves on the SAME surface "
        "-- Gp013's CATIA seam idiom, but on a surface class whose Geom "
        "API cannot be marked periodic in place, forcing GeomConvert_"
        "ApproxSurface before SetUPeriodic can apply."
    ),
)

# CYLINDRICAL_SURFACE, radius 1, standard placement (axis Z, ref X).
c_orig = f.cartesian_point((0.0, 0.0, 0.0))
c_axis = f.direction((0.0, 0.0, 1.0))
c_ref = f.direction((1.0, 0.0, 0.0))
c_plc = f.axis2_placement_3d(c_orig, c_axis, c_ref)
cyl = f.cylindrical_surface(c_plc, 1.0)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Seam vertices: physical points (1,0,0) and (1,0,1).
p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 1.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

# Seam edge — 3D line from (1,0,0) to (1,0,1), carries TWO pcurves at
# u=0 and u=2*pi (the cylinder's natural angular period).
d_up = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)
seam_line_3d = f.line(p_bot, vec_up)

pc_u0_start = f.cartesian_point((0.0, 0.0))
pc_u0_dir = f.direction((0.0, 1.0))
pc_u0_vec = f.vector(pc_u0_dir, 1.0)
pc_u0_line = f.line(pc_u0_start, pc_u0_vec)
pc_u0_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_u0_def',(#{pc_u0_line.eid}),#{prc.eid})"
)
pcurve_u0 = f._emit_raw(f"PCURVE('pc_u0_bank',#{cyl.eid},#{pc_u0_def.eid})")

pc_u2pi_start = f.cartesian_point((2.0 * math.pi, 0.0))
pc_u2pi_dir = f.direction((0.0, 1.0))
pc_u2pi_vec = f.vector(pc_u2pi_dir, 1.0)
pc_u2pi_line = f.line(pc_u2pi_start, pc_u2pi_vec)
pc_u2pi_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_u2pi_def',(#{pc_u2pi_line.eid}),#{prc.eid})"
)
pcurve_u2pi = f._emit_raw(f"PCURVE('pc_u2pi_bank',#{cyl.eid},#{pc_u2pi_def.eid})")

# THE DEFECT: single SURFACE_CURVE carries BOTH pcurves on the same
# elementary (non-B-spline) surface.
seam_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('catia_like_seam_cyl',#{seam_line_3d.eid},"
    f"(#{pcurve_u0.eid},#{pcurve_u2pi.eid}),.PCURVE_S1.)"
)
seam_edge = f._emit_raw(
    f"EDGE_CURVE('seam',#{v_bot.eid},#{v_top.eid},#{seam_surface_curve.eid},.T.)"
)

# Bottom rim: full circle at z=0, self-loop, healthy single pcurve.
bot_center = f.cartesian_point((0.0, 0.0, 0.0))
bot_placement = f.axis2_placement_3d(bot_center, c_axis, c_ref)
bot_circle = f._emit_raw(f"CIRCLE('bot_full',#{bot_placement.eid},1.0)")
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir = f.direction((1.0, 0.0))
pc_bot_vec = f.vector(pc_bot_dir, 2.0 * math.pi)
pc_bot_line = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot_def',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pcurve',#{cyl.eid},#{pc_bot_def.eid})")
bot_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bot_circle.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
bot_edge = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_bot.eid},#{v_bot.eid},#{bot_surface_curve.eid},.T.)"
)

# Top rim: full circle at z=1, self-loop, healthy single pcurve.
top_center = f.cartesian_point((0.0, 0.0, 1.0))
top_placement = f.axis2_placement_3d(top_center, c_axis, c_ref)
top_circle = f._emit_raw(f"CIRCLE('top_full',#{top_placement.eid},1.0)")
pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir = f.direction((1.0, 0.0))
pc_top_vec = f.vector(pc_top_dir, 2.0 * math.pi)
pc_top_line = f.line(pc_top_start, pc_top_vec)
pc_top_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top_def',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_pcurve',#{cyl.eid},#{pc_top_def.eid})")
top_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_circle.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
top_edge = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_top.eid},#{v_top.eid},#{top_surface_curve.eid},.T.)"
)

# 4-edge face loop, same idiom as Gp013: bot(fwd) -> seam(fwd, u=2pi bank)
# -> top(rev) -> seam(rev, u=0 bank).
loop = f.edge_loop([
    f.oriented_edge(bot_edge, True),
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge, False),
    f.oriented_edge(seam_edge, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
