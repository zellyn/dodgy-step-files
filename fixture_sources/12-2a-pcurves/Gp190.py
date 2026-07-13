"""Gp190 — CATIA-style pseudo-seam split ACROSS TWO DIFFERENT FACES (not
one face, two wires): two independent ADVANCED_FACEs built on the SAME
near-closed, non-periodic B_SPLINE_SURFACE_WITH_KNOTS, each with its own
"seam-like" edge at the surface's u=0/u=1 near-closure locus
(stp-seam-pcurve-selection, PARTIAL, missing subvariant (a): "a CATIA-style
pseudo-seam where two DIFFERENT faces (not one face, two wires) are built
on the same not-formally-closed surface, sharing edge geometry across two
wires -- exercises IsLikeSeam").

Catalog claim: StepToTopoDS_GeometricTool::IsSeamCurve
(StepToTopoDS_GeometricTool.cxx:72-107) detects a formal SEAM_CURVE or an
EDGE_CURVE referenced twice within ONE wire (Gp013's pattern -- a single
face wraps fully around). StepToTopoDS_GeometricTool::IsLikeSeam
(:109-191) is the DIFFERENT, heuristic sibling: it compares two pcurves'
line origins/directions within tolerance ACROSS TWO DIFFERENT WIRES
(potentially of two different faces) to detect a pseudo-seam that isn't
formally declared and isn't a single-edge-twice-in-one-wire case either.
Gp013/Gp181/Gp182 are all single-face constructions (IsSeamCurve's
domain); this fixture is genuinely multi-face, putting IsLikeSeam's
cross-wire comparison to work.

Mechanism: the SAME B_SPLINE_SURFACE_WITH_KNOTS host as Gp013 (non-
periodic, 9x2 control net approximating a unit cylinder, u in [0,1] wraps
back to touching 3D geometry at u=0 vs u=1 despite the surface NOT being
declared periodic) is shared by TWO INDEPENDENT ADVANCED_FACEs, split
along v (height): face_lower spans v:[0, 0.5] (z:[0,0.5]) and face_upper
spans v:[0.5, 1] (z:[0.5,1]). EACH face independently reproduces Gp013's
own "one seam edge used twice in its own wire" pattern (bot_arc -> seam
fwd (u=1 bank) -> top_arc (reversed) -> seam rev (u=0 bank)) -- so BOTH
faces carry their own seam-like edge at the SAME u=0/u=1 locus of the
shared surface, in TWO SEPARATE wires belonging to TWO SEPARATE faces --
exactly the cross-face pseudo-seam pattern IsLikeSeam is meant to
disambiguate, as opposed to Gp013's single face using ONE edge twice.

Byte assertions:
  - count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 1
  - count_entity_def(b'ADVANCED_FACE') == 2
  - contains(b'face_lower_seam')
  - contains(b'face_upper_seam')

Tier-3 assertions:
  - n_faces_total == 2

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp190",
    defect=(
        "Two ADVANCED_FACEs (face_lower v:[0,0.5], face_upper v:[0.5,1]) "
        "built on the SAME B_SPLINE_SURFACE_WITH_KNOTS (Gp013's exact "
        "non-periodic near-closed-cylinder host); EACH face independently "
        "uses its own seam-like EDGE_CURVE (face_lower_seam, "
        "face_upper_seam) twice within its OWN wire (u=0/u=1 pcurve "
        "banks) at the surface's near-closure locus -- two DIFFERENT "
        "faces, two DIFFERENT wires, sharing the same conceptual seam "
        "geometry on the same underlying surface -- IsLikeSeam's "
        "cross-wire pseudo-seam domain, distinct from Gp013/Gp181/Gp182's "
        "single-face IsSeamCurve domain; EDGE_LOOPs IS wired into "
        "FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; never orphaned"
    ),
)


def xy(angle, z):
    return f.cartesian_point((math.cos(angle), math.sin(angle), z))


angles = [0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi,
          5 * math.pi / 4, 3 * math.pi / 2, 7 * math.pi / 4, 2 * math.pi]
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

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)


def build_seam_face(z0, z1, seam_name):
    """One Gp013-style face on host_surface spanning z:[z0,z1] (v:[z0,z1]
    since v_degree=1 over v_knots=[0,1] maps linearly to z), with its OWN
    seam edge (used twice, u=0/u=1 banks)."""
    p_bot = f.cartesian_point((1.0, 0.0, z0))
    p_top = f.cartesian_point((1.0, 0.0, z1))
    v_bot = f.vertex_point(p_bot)
    v_top = f.vertex_point(p_top)

    d_up = f.direction((0.0, 0.0, 1.0))
    vec_up = f.vector(d_up, z1 - z0)
    seam_line_3d = f.line(p_bot, vec_up)

    pc_u0_start = f.cartesian_point((0.0, z0))
    pc_u0_dir = f.direction((0.0, 1.0))
    pc_u0_vec = f.vector(pc_u0_dir, z1 - z0)
    pc_u0_line = f.line(pc_u0_start, pc_u0_vec)
    pc_u0_def = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_u0_line.eid}),#{prc.eid})"
    )
    pcurve_u0 = f._emit_raw(f"PCURVE('',#{host_surface.eid},#{pc_u0_def.eid})")

    pc_u1_start = f.cartesian_point((1.0, z0))
    pc_u1_dir = f.direction((0.0, 1.0))
    pc_u1_vec = f.vector(pc_u1_dir, z1 - z0)
    pc_u1_line = f.line(pc_u1_start, pc_u1_vec)
    pc_u1_def = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_u1_line.eid}),#{prc.eid})"
    )
    pcurve_u1 = f._emit_raw(f"PCURVE('',#{host_surface.eid},#{pc_u1_def.eid})")

    seam_surface_curve = f._emit_raw(
        f"SURFACE_CURVE('{seam_name}',#{seam_line_3d.eid},"
        f"(#{pcurve_u0.eid},#{pcurve_u1.eid}),.PCURVE_S1.)"
    )
    seam_edge = f._emit_raw(
        f"EDGE_CURVE('{seam_name}',#{v_bot.eid},#{v_top.eid},#{seam_surface_curve.eid},.T.)"
    )

    bot_center = f.cartesian_point((0.0, 0.0, z0))
    bot_z = f.direction((0.0, 0.0, 1.0))
    bot_x = f.direction((1.0, 0.0, 0.0))
    bot_axis = f.axis2_placement_3d(bot_center, bot_z, bot_x)
    bot_circle = f._emit_raw(f"CIRCLE('',#{bot_axis.eid},1.0)")
    pc_bot_start = f.cartesian_point((0.0, z0))
    pc_bot_dir = f.direction((1.0, 0.0))
    pc_bot_vec = f.vector(pc_bot_dir, 1.0)
    pc_bot_line = f.line(pc_bot_start, pc_bot_vec)
    pc_bot_def = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_bot_line.eid}),#{prc.eid})"
    )
    pcurve_bot = f._emit_raw(f"PCURVE('',#{host_surface.eid},#{pc_bot_def.eid})")
    bot_surface_curve = f._emit_raw(
        f"SURFACE_CURVE('',#{bot_circle.eid},(#{pcurve_bot.eid}),.PCURVE_S1.)"
    )
    bot_edge = f._emit_raw(
        f"EDGE_CURVE('',#{v_bot.eid},#{v_bot.eid},#{bot_surface_curve.eid},.T.)"
    )

    top_center = f.cartesian_point((0.0, 0.0, z1))
    top_axis = f.axis2_placement_3d(top_center, bot_z, bot_x)
    top_circle = f._emit_raw(f"CIRCLE('',#{top_axis.eid},1.0)")
    pc_top_start = f.cartesian_point((0.0, z1))
    pc_top_dir = f.direction((1.0, 0.0))
    pc_top_vec = f.vector(pc_top_dir, 1.0)
    pc_top_line = f.line(pc_top_start, pc_top_vec)
    pc_top_def = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_top_line.eid}),#{prc.eid})"
    )
    pcurve_top = f._emit_raw(f"PCURVE('',#{host_surface.eid},#{pc_top_def.eid})")
    top_surface_curve = f._emit_raw(
        f"SURFACE_CURVE('',#{top_circle.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
    )
    top_edge = f._emit_raw(
        f"EDGE_CURVE('',#{v_top.eid},#{v_top.eid},#{top_surface_curve.eid},.T.)"
    )

    loop = f.edge_loop([
        f.oriented_edge(bot_edge, True),
        f.oriented_edge(seam_edge, True),
        f.oriented_edge(top_edge, False),
        f.oriented_edge(seam_edge, False),
    ])
    return f.advanced_face([f.face_outer_bound(loop)], host_surface)


face_lower = build_seam_face(0.0, 0.5, "face_lower_seam")
face_upper = build_seam_face(0.5, 1.0, "face_upper_seam")

shell = f.open_shell([face_lower, face_upper])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
