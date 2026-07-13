"""Tsh250 — Two stacked full-period cylindrical shells whose facing seam
edges are within sewing tolerance: the lower shell's seam candidate
carries only ONE explicit PCURVE (missing the dual forward+reversed
pair), reachable through an actual, live sewing merge
(sew-seam-dual-pcurve-preservation PARTIAL).

Catalog claim (occt-coverage PARTIAL `sew-seam-dual-pcurve-
preservation`): per `occt-coverage/exchange/problems.json`, the class was
DOWNGRADED COVERED->PARTIAL because Gp139 (the prior single-pcurve
mirror) is a dead scaffold — its accompanying degree-2 B-spline C-1
positional break forces `shape_null==True` before any merged edge can
ever exist, so no merge is ever reachable. Tsh209's cylinder seam is
live but self-contained inside ONE face (no sewing merge is needed or
attempted at all — the seam edge is simply part of that face's own
closed boundary). This fixture purpose-builds BOTH a live, reachable
shape AND a genuine sewing-merge opportunity:

Two independent OPEN_SHELLs, each ONE ADVANCED_FACE on a
CYLINDRICAL_SURFACE (radius 5, axis +Z), each built exactly like
Tsh209's full-period wraparound face (bottom full CIRCLE, right vertical
line, top full CIRCLE reversed, left vertical line reversed) — i.e. each
face's own top/bottom boundary is a genuine closed (start==end) seam
edge, not an open arc:
  - shell_lower: z:[0, 4]. Its TOP boundary (z=4 full circle) is the
    seam-merge candidate. Built explicitly via a SURFACE_CURVE binding
    the 3D CIRCLE to a SINGLE PCURVE (u:[0,2*pi] forward direction only)
    — missing the dual reversed-direction pcurve representation a
    genuine seam participant needs once merged.
  - shell_upper: z:[4.0005, 8.0005] (a 0.0005 gap from shell_lower's top,
    comfortably within a 1.0 sewing tolerance). Its BOTTOM boundary
    (z=4.0005 full circle) is the other seam-merge candidate, built the
    ordinary way (an EDGE_CURVE referencing the 3D CIRCLE directly, no
    explicit PCURVE entity — the reader derives the pcurve on demand).

Both shells load as live, independent shapes (neither carries a C-1
break or any other translation-defeating defect); the near-gap top/
bottom seam pair is a real, reachable candidate for
BRepBuilderAPI_Sewing to merge, at which point the lower shell's
single-pcurve seam edge is the one under test.

Byte assertions:
  - count_entity_def(b'CYLINDRICAL_SURFACE') == 2
  - count_entity_def(b'PCURVE') == 1
  - contains(b'lower_seam_single_pc')
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh250",
    schema="AP242",
    defect=(
        "TWO independent OPEN_SHELLs, each ONE ADVANCED_FACE on a "
        "CYLINDRICAL_SURFACE (radius 5, axis +Z), each structured like "
        "Tsh209's full-period wraparound face (bottom/top full CIRCLEs, "
        "two vertical seam-line edges): shell_lower z:[0,4] with its TOP "
        "seam candidate built via SURFACE_CURVE + a SINGLE explicit "
        "PCURVE (missing the dual reversed pair); shell_upper "
        "z:[4.0005,8.0005] (0.0005 gap, within a 1.0 sewing tolerance) "
        "with its BOTTOM seam candidate built the ordinary way — a "
        "genuine, live, reachable near-gap seam-merge pair, distinct "
        "from Gp139's dead C-1-broken scaffold and Tsh209's "
        "self-contained single-face seam (no merge opportunity at all)"
    ),
)


def cp(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))


def dir3(x, y, z):
    return f.direction((float(x), float(y), float(z)))


R = 5.0

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)


def cyl_wraparound_shell(z0, z1, tag, explicit_single_pcurve_on_top):
    """One full-period cylindrical face (Tsh209 pattern): bottom full
    circle (z0), right vertical seam line, top full circle reversed
    (z1), left vertical seam line reversed. If
    ``explicit_single_pcurve_on_top`` is True, the TOP circle edge is
    built via an explicit SURFACE_CURVE + single forward-only PCURVE
    instead of a plain EDGE_CURVE referencing the CIRCLE directly."""
    p_bot = cp(R, 0, z0)
    v_bot = f.vertex_point(p_bot)
    p_top = cp(R, 0, z1)
    v_top = f.vertex_point(p_top)

    cyl_ax = f.axis2_placement_3d(cp(0, 0, 0), dir3(0, 0, 1), dir3(1, 0, 0))
    cyl = f.cylindrical_surface(cyl_ax, R)

    bot_ax = f.axis2_placement_3d(cp(0, 0, z0), dir3(0, 0, 1), dir3(1, 0, 0))
    bot_circle = f.circle(bot_ax, R)
    e_bot_seam = f.edge_curve(v_bot, v_bot, bot_circle, same_sense=True)

    if explicit_single_pcurve_on_top:
        top_ax = f.axis2_placement_3d(cp(0, 0, z1), dir3(0, 0, 1), dir3(1, 0, 0))
        top_circle_3d = f.circle(top_ax, R)
        # 2D pcurve: u:[0,2*pi] forward direction only (u increasing).
        uv_start = f.cartesian_point((0.0, float(z1)))
        d2 = f.direction((1.0, 0.0))
        vec2 = f.vector(d2, 2.0 * math.pi)
        pc_line = f.line(uv_start, vec2)
        defrep = f._emit_raw(
            f"DEFINITIONAL_REPRESENTATION('{tag}_top_pc_def',(#{pc_line.eid}),#{prc.eid})"
        )
        pcurve = f._emit_raw(
            f"PCURVE('lower_seam_single_pc',#{cyl.eid},#{defrep.eid})"
        )
        surf_curve = f._emit_raw(
            f"SURFACE_CURVE('{tag}_top_seam_sc',#{top_circle_3d.eid},"
            f"(#{pcurve.eid}),.PCURVE_S1.)"
        )
        e_top_seam = f._emit_raw(
            f"EDGE_CURVE('{tag}_top_seam_edge',#{v_top.eid},#{v_top.eid},"
            f"#{surf_curve.eid},.T.)"
        )
    else:
        top_ax = f.axis2_placement_3d(cp(0, 0, z1), dir3(0, 0, 1), dir3(1, 0, 0))
        top_circle = f.circle(top_ax, R)
        e_top_seam = f.edge_curve(v_top, v_top, top_circle, same_sense=True)

    d_up = dir3(0, 0, 1)
    h = z1 - z0
    vec_up = f.vector(d_up, h)
    ln_right = f.line(p_bot, vec_up)
    e_right = f.edge_curve(v_bot, v_top, ln_right, same_sense=True)

    d_down = dir3(0, 0, -1)
    vec_down = f.vector(d_down, h)
    ln_left = f.line(p_top, vec_down)
    e_left = f.edge_curve(v_top, v_bot, ln_left, same_sense=True)

    loop = f.edge_loop([
        f.oriented_edge(e_bot_seam, True),
        f.oriented_edge(e_right, True),
        f.oriented_edge(e_top_seam, False),
        f.oriented_edge(e_left, False),
    ])
    face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], cyl, same_sense=True, name=f"{tag}_face")
    return f.open_shell([face], name=f"{tag}_shell")


shell_lower = cyl_wraparound_shell(0.0, 4.0, "lower", explicit_single_pcurve_on_top=True)
shell_upper = cyl_wraparound_shell(4.0005, 8.0005, "upper", explicit_single_pcurve_on_top=False)

sbsm = f.shell_based_surface_model([shell_lower, shell_upper])
f.add_product_chain(sbsm)
