"""Gp013 — CATIA "like-seam": two pcurves on same near-closed B_SPLINE_SURFACE_WITH_KNOTS.

Catalog claim: CATIA encodes a cylinder as a FACE_SURFACE on a nearly-
closed (but non-periodic) B_SPLINE_SURFACE_WITH_KNOTS. The shared
EDGE_CURVE stores two pcurves on the same B-spline surface — one at
(u≈0) and one at (u≈1) — like a seam edge but the surface lacks declared
periodicity. Generic seam handling misfires; the translator must detect
the CATIA idiom.

Fixture (rebuilt 2026-06-19 after Sonnet flagged degenerate face loops):
A single ADVANCED_FACE on a non-periodic B-spline surface approximating a
cylinder. The face's outer loop is a proper 4-edge rectangle in
UV-parameter space:
  bot_arc (v=0)  →  seam_edge (u=1)  →  top_arc (v=1, reversed)  →
    seam_edge (u=0, reversed orientation)
Where bot_arc / top_arc traverse the full surface in u, and the
*single* seam EDGE_CURVE — whose SURFACE_CURVE stores two pcurves at
u=0 and u=1 on the same non-periodic surface — appears twice in the
loop with opposite orientations. That is the catalog's specific defect:
one 3D edge, two pcurves on the same non-periodic NURBS host.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp013",
             defect="CATIA like-seam: single EDGE_CURVE with two pcurves on non-periodic B-spline surface, used twice in a proper 4-edge face loop")

# Non-periodic B-spline surface approximating a unit cylinder (radius 1,
# height 1). 9 control points in u (degree 2, clamped), 2 in v (degree 1).
# u=0 row's first control point and u=1 row's last are both at angle 0 in
# 3D (i.e. (1,0,*)) but are DIFFERENT parameter positions on the surface.
def xy(angle, z):
    return f.cartesian_point((math.cos(angle), math.sin(angle), z))

angles = [0.0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi,
          5*math.pi/4, 3*math.pi/2, 7*math.pi/4, 2*math.pi]
net = [[xy(a, 0.0), xy(a, 1.0)] for a in angles]

host_surface = f.b_spline_surface_with_knots(
    u_degree=2, v_degree=1,
    control_points_grid=net,
    u_multiplicities=[3, 1, 1, 1, 1, 1, 1, 3],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 1.0],
    v_knots=[0.0, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
)

# 3D vertices at the seam location: same (1, 0, *) physical points.
p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 1.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

# Vertices on the bottom-arc and top-arc (we'll route bot_arc/top_arc as
# the v=0 and v=1 lines of the surface, parametrised in u).
# The arc endpoints in 3D are the same as the seam endpoints because the
# surface wraps around: arc starts at (1,0,0) (u=0) and ends at (1,0,0) (u=1).
# In topology terms we use the same vertices for bot_arc start/end.

# UV parametric context for pcurves
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Seam edge — single 3D line from (1,0,0) to (1,0,1).
d_up = f.direction((0.0, 0.0, 1.0))
vec_up = f.vector(d_up, 1.0)
seam_line_3d = f.line(p_bot, vec_up)

# Pcurve at u=0: a 2D line going (u=0, v=0) → (u=0, v=1).
pc_u0_start = f.cartesian_point((0.0, 0.0))
pc_u0_dir = f.direction((0.0, 1.0))
pc_u0_vec = f.vector(pc_u0_dir, 1.0)
pc_u0_line = f.line(pc_u0_start, pc_u0_vec)
pc_u0_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_u0_def',(#{pc_u0_line.eid}),#{prc.eid})"
)
pcurve_u0 = f._emit_raw(
    f"PCURVE('pc_u0_bank',#{host_surface.eid},#{pc_u0_def.eid})"
)

# Pcurve at u=1: a 2D line going (u=1, v=0) → (u=1, v=1).
pc_u1_start = f.cartesian_point((1.0, 0.0))
pc_u1_dir = f.direction((0.0, 1.0))
pc_u1_vec = f.vector(pc_u1_dir, 1.0)
pc_u1_line = f.line(pc_u1_start, pc_u1_vec)
pc_u1_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_u1_def',(#{pc_u1_line.eid}),#{prc.eid})"
)
pcurve_u1 = f._emit_raw(
    f"PCURVE('pc_u1_bank',#{host_surface.eid},#{pc_u1_def.eid})"
)

# THE DEFECT: single SURFACE_CURVE carries BOTH pcurves on the same
# non-periodic surface. A correctly-periodic surface would have one
# pcurve covering both seam banks via period-shift; CATIA emits both
# pcurves explicitly because the surface is declared non-periodic.
seam_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('catia_like_seam',#{seam_line_3d.eid},"
    f"(#{pcurve_u0.eid},#{pcurve_u1.eid}),.PCURVE_S1.)"
)
seam_edge = f._emit_raw(
    f"EDGE_CURVE('seam',#{v_bot.eid},#{v_top.eid},#{seam_surface_curve.eid},.T.)"
)

# Bottom arc: from (1,0,0) traversing v=0 around the full surface back to (1,0,0).
# 3D representation: full circle in z=0 plane, parametrised counterclockwise.
bot_center = f.cartesian_point((0.0, 0.0, 0.0))
bot_z = f.direction((0.0, 0.0, 1.0))
bot_x = f.direction((1.0, 0.0, 0.0))
bot_axis = f.axis2_placement_3d(bot_center, bot_z, bot_x)
bot_circle = f._emit_raw(f"CIRCLE('bot_full',#{bot_axis.eid},1.0)")

# Pcurve for bot_arc on the host surface: a 2D line in pcurve space from
# (u=0, v=0) → (u=1, v=0).
pc_bot_start = f.cartesian_point((0.0, 0.0))
pc_bot_dir = f.direction((1.0, 0.0))
pc_bot_vec = f.vector(pc_bot_dir, 1.0)
pc_bot_line = f.line(pc_bot_start, pc_bot_vec)
pc_bot_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_bot_def',(#{pc_bot_line.eid}),#{prc.eid})"
)
pcurve_bot = f._emit_raw(
    f"PCURVE('bot_pcurve',#{host_surface.eid},#{pc_bot_def.eid})"
)
bot_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('bot_arc',#{bot_circle.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
)
bot_edge = f._emit_raw(
    f"EDGE_CURVE('bot_arc',#{v_bot.eid},#{v_bot.eid},#{bot_surface_curve.eid},.T.)"
)

# Top arc: same construction at z=1.
top_center = f.cartesian_point((0.0, 0.0, 1.0))
top_axis = f.axis2_placement_3d(top_center, bot_z, bot_x)
top_circle = f._emit_raw(f"CIRCLE('top_full',#{top_axis.eid},1.0)")

pc_top_start = f.cartesian_point((0.0, 1.0))
pc_top_dir = f.direction((1.0, 0.0))
pc_top_vec = f.vector(pc_top_dir, 1.0)
pc_top_line = f.line(pc_top_start, pc_top_vec)
pc_top_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_top_def',(#{pc_top_line.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(
    f"PCURVE('top_pcurve',#{host_surface.eid},#{pc_top_def.eid})"
)
top_surface_curve = f._emit_raw(
    f"SURFACE_CURVE('top_arc',#{top_circle.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
top_edge = f._emit_raw(
    f"EDGE_CURVE('top_arc',#{v_top.eid},#{v_top.eid},#{top_surface_curve.eid},.T.)"
)

# 4-edge face loop: bot_arc (v=0, forward) → seam (u=1, forward) →
# top_arc (v=1, reversed) → seam (u=0, reversed orientation).
# The seam EDGE_CURVE is used twice — once for each side of the
# non-periodic mapping. That's the catalog defect.
loop = f.edge_loop([
    f.oriented_edge(bot_edge, True),
    f.oriented_edge(seam_edge, True),   # uses pcurve at u=1 (forward)
    f.oriented_edge(top_edge, False),
    f.oriented_edge(seam_edge, False),  # uses pcurve at u=0 (reversed)
])
face = f.advanced_face([f.face_outer_bound(loop)], host_surface)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
