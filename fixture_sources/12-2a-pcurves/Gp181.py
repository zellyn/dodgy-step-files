"""Gp181 — CATIA-style near-closed non-periodic B-spline seam-like edge,
mirrored onto the V direction (Gp013 is the U-direction original).

Work packet D1, item `tkshh-nonperiodic-bspline-seamlike-edge` (PARTIAL,
missing 2 of 3), subvariant (a): "Same CATIA-style near-closed non-periodic
B-spline seam-like-edge pattern as Gp013 but in the V direction instead of
U." problem_id `tkshh-nonperiodic-bspline-seamlike-edge`
(ShapeUpgrade_UnifySameDomain::IntUnifyFaces, ShapeUpgrade_UnifySameDomain.
cxx:3221/3242-3246/3264/3269 -- myConcatBSplines && EdgeWith2pcurves &&
!SeamFound detection, then SetUPeriodic/SetVPeriodic): a closed body encoded
on a B-spline surface that is geometrically closed but NOT declared
periodic; a shared edge carries two pcurves on the same surface, behaving
like a seam. Gp013 only exercises the U-direction branch (SetUPeriodic);
this fixture is the untested V-direction branch (SetVPeriodic).

Geometry: identical unit cylinder (radius 1, height 1) to Gp013, but with
the roles of U and V swapped end to end: the B_SPLINE_SURFACE_WITH_KNOTS
here has degree 1 in U (2 rows = height) and degree 2 in V (9 columns =
the near-closed angular sweep, same 9-point circle discretization as
Gp013's U direction). The seam-like edge now runs along U (height) at
v=0/v=1 (both physically angle=0); the two cap edges are full circles
varying along V at fixed U=0 (bottom rim) and U=1 (top rim). Structurally
this is Gp013 with U and V transposed throughout -- same defect, same
physical cylinder, orthogonal parametric direction.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp181",
    defect=(
        "Unit cylinder (radius 1, height 1) as a non-periodic "
        "B_SPLINE_SURFACE_WITH_KNOTS, U/V-transposed relative to Gp013: "
        "degree 1 in U (2 height rows), degree 2 in V (9-point near-closed "
        "angular sweep). The shared seam EDGE_CURVE runs along U at "
        "v=0/v=1 (both physically angle=0) and carries two pcurves on the "
        "same non-periodic surface -- like a seam, but the surface lacks "
        "declared periodicity in V. Exercises SetVPeriodic instead of "
        "Gp013's SetUPeriodic."
    ),
)


def xy(angle, z):
    return f.cartesian_point((math.cos(angle), math.sin(angle), z))


angles = [0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi,
          5 * math.pi / 4, 3 * math.pi / 2, 7 * math.pi / 4, 2 * math.pi]
# control_points_grid indexed [U][V]: U=height row (2), V=angle column (9).
row_bottom = [xy(a, 0.0) for a in angles]
row_top = [xy(a, 1.0) for a in angles]
net = [row_bottom, row_top]

host_surface = f.b_spline_surface_with_knots(
    u_degree=1, v_degree=2,
    control_points_grid=net,
    u_multiplicities=[2, 2],
    v_multiplicities=[3, 1, 1, 1, 1, 1, 1, 3],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
)

# 3D vertices at the seam location: physical points (1,0,0) and (1,0,1).
p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 1.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Seam edge — single 3D line from (1,0,0) to (1,0,1), running along U
# (height) at fixed angle. Carries TWO pcurves: v=0 bank and v=1 bank.
d_up = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)
seam_line_3d = f.line(p_bot, vec_up)

# Pcurve at v=0: 2D line (u=0,v=0) -> (u=1,v=0).
pc_v0_start = f.cartesian_point((0.0, 0.0))
pc_v0_dir = f.direction((1.0, 0.0))
pc_v0_vec = f.vector(pc_v0_dir, 1.0)
pc_v0_line = f.line(pc_v0_start, pc_v0_vec)
pc_v0_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_v0_def',(#{pc_v0_line.eid}),#{prc.eid})"
)
pcurve_v0 = f._emit_raw(f"PCURVE('pc_v0_bank',#{host_surface.eid},#{pc_v0_def.eid})")

# Pcurve at v=1: 2D line (u=0,v=1) -> (u=1,v=1).
pc_v1_start = f.cartesian_point((0.0, 1.0))
pc_v1_dir = f.direction((1.0, 0.0))
pc_v1_vec = f.vector(pc_v1_dir, 1.0)
pc_v1_line = f.line(pc_v1_start, pc_v1_vec)
pc_v1_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_v1_def',(#{pc_v1_line.eid}),#{prc.eid})"
)
pcurve_v1 = f._emit_raw(f"PCURVE('pc_v1_bank',#{host_surface.eid},#{pc_v1_def.eid})")

# THE DEFECT: single SURFACE_CURVE carries BOTH pcurves on the same
# non-periodic surface (V direction), mirroring Gp013's U-direction idiom.
seam_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('catia_like_seam_v',#{seam_line_3d.eid},"
    f"(#{pcurve_v0.eid},#{pcurve_v1.eid}),.PCURVE_S1.)"
)
seam_edge = f._emit_raw(
    f"EDGE_CURVE('seam',#{v_bot.eid},#{v_top.eid},#{seam_surface_curve.eid},.T.)"
)

# Bottom rim: full circle at U=0 (z=0), self-loop, healthy single pcurve.
bot_center = f.cartesian_point((0.0, 0.0, 0.0))
bot_z = f.direction((0.0, 0.0, 1.0))
bot_x = f.direction((1.0, 0.0, 0.0))
bot_axis = f.axis2_placement_3d(bot_center, bot_z, bot_x)
bot_circle = f._emit_raw(f"CIRCLE('bot_full',#{bot_axis.eid},1.0)")
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir = f.direction((0.0, 1.0))
pc_bot_vec = f.vector(pc_bot_dir, 1.0)
pc_bot_line = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot_def',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(f"PCURVE('bot_pcurve',#{host_surface.eid},#{pc_bot_def.eid})")
bot_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bot_circle.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
bot_edge = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_bot.eid},#{v_bot.eid},#{bot_surface_curve.eid},.T.)"
)

# Top rim: full circle at U=1 (z=1), self-loop, healthy single pcurve.
top_center = f.cartesian_point((0.0, 0.0, 1.0))
top_axis = f.axis2_placement_3d(top_center, bot_z, bot_x)
top_circle = f._emit_raw(f"CIRCLE('top_full',#{top_axis.eid},1.0)")
pc_top_start = f.cartesian_point((1.0, 0.0))
pc_top_dir = f.direction((0.0, 1.0))
pc_top_vec = f.vector(pc_top_dir, 1.0)
pc_top_line = f.line(pc_top_start, pc_top_vec)
pc_top_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top_def',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_pcurve',#{host_surface.eid},#{pc_top_def.eid})")
top_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_circle.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
top_edge = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_top.eid},#{v_top.eid},#{top_surface_curve.eid},.T.)"
)

# 4-edge face loop: bot_rim (U=0, forward) -> seam (v=1 bank, forward) ->
# top_rim (U=1, reversed) -> seam (v=0 bank, reversed).
loop = f.edge_loop([
    f.oriented_edge(bot_edge, True),
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge, False),
    f.oriented_edge(seam_edge, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], host_surface)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
