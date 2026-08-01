"""Gp194 — CATIA-style like-seam edge on a host that is geometrically closed
in U yet reports NO period AND is not a B-spline: a
`SURFACE_OF_LINEAR_EXTRUSION` swept from a closed-but-non-periodic
`B_SPLINE_CURVE_WITH_KNOTS`.

Catalog claim (occt-coverage `tkshhealing/problems.json`
`tkshh-nonperiodic-bspline-seamlike-edge`, subvariant 3: "non-B-spline base
surface requiring approximation before periodicity can be set"):

  The repair arm this subvariant names -- `ShapeUpgrade_UnifySameDomain`'s
  approximate-then-periodize path, ShapeUpgrade_UnifySameDomain.cxx:3248-3271
  -- is guarded by TWO conditions on the host surface: the surface must report
  no period in the direction being closed (`Uperiod == 0.` at :3243, where
  Uperiod comes from `aBaseSurface->IsUPeriodic()` at :2946), AND it must NOT
  already be a `Geom_BSplineSurface` (`aBSplineSurface.IsNull()` at :3252),
  which is what makes `GeomConvert_ApproxSurface` (:3258) necessary before
  `SetUPeriodic` (:3264) can be called at all.

  The existing fixtures cannot satisfy both at once. Gp013 and Gp181 are
  B-spline hosts, so the approximation step is by definition not needed; and
  live-checking them in this worktree shows the reader has ALREADY periodized
  them by the time the shape exists (Gp013 reads back `IsUPeriodic == True`,
  Gp181 `IsVPeriodic == True`), so `Uperiod == 0` is false as well. Gp182 is a
  `CYLINDRICAL_SURFACE` -- genuinely not a B-spline, but inherently periodic
  (`IsUPeriodic == True`), so it can never require the approximation either.
  That is why the class notes record Gp182 as an honest non-firing sibling.

  This fixture supplies the host that does satisfy both. `Geom_SurfaceOf-
  LinearExtrusion::IsUPeriodic()` forwards to its basis curve's `IsPeriodic()`,
  so sweeping a CLOSED but NON-PERIODIC B-spline curve along +Z yields a
  surface that wraps around in U (`IsUClosed == True`) while reporting no
  period (`IsUPeriodic == False`) and is not a `Geom_BSplineSurface`.

Mechanism IS wired into the shape root: the like-seam `EDGE_CURVE` is used
twice (opposite orientations) inside the single `EDGE_LOOP` of the
`FACE_OUTER_BOUND` of the `ADVANCED_FACE`, exactly as in Gp013; its
`SURFACE_CURVE` carries TWO `PCURVE`s, both whose `basis_surface` is the
extrusion host -- one bank at u=0, one at u=1. Nothing is orphaned.

Live-verified (2026-07-31, this worktree, OCP/OCCT 7.8.1): the face reads back
on a `Geom_SurfaceOfLinearExtrusion` with `IsUPeriodic() == False`,
`IsUClosed() == True`, bounds U=[0,1], and the reader does NOT periodize it --
in contrast to Gp013/Gp181, whose B-spline hosts come back already periodic.
**Control**: the byte-identical construction with only the basis curve swapped
for a `CIRCLE` (a periodic curve) reads back on a
`Geom_SurfaceOfLinearExtrusion` with `IsUPeriodic() == True`, isolating the
closed-but-non-periodic basis curve as the sole cause.

HONEST LIMITATION (see the catalog Notes): this fixture supplies the input
precondition, and is the only fixture in the class that genuinely does. It
does NOT independently demonstrate the unify-level repair firing, because that
additionally requires two same-domain faces sharing an edge that carries two
pcurves on the reference face WITHOUT being really-closed there -- which the
STEP reader cannot produce (see the Notes for the file:line reasoning and the
live experiment).

Byte assertions:
  - count_entity_def(b'SURFACE_OF_LINEAR_EXTRUSION') == 1
  - count_entity_def(b'B_SPLINE_CURVE_WITH_KNOTS') == 1
  - contains(b'extrusion_like_seam')

Tier-3 assertions:
  - face[0].surface_type == "extrusion"
  - n_faces_total == 1
  - n_edges_total == 4

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1):
  occt=shape(1)/shape(1) gmsh=shape(6)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp194",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE hosted on a "
        "SURFACE_OF_LINEAR_EXTRUSION whose basis is a CLOSED but NON-PERIODIC "
        "B_SPLINE_CURVE_WITH_KNOTS (9 control points around a unit circle, "
        "first == last, degree 2, clamped knots) swept 1.0 along +Z: the "
        "surface wraps around in U yet reports no period, and is not a "
        "B-spline surface. A single like-seam EDGE_CURVE "
        "('extrusion_like_seam') whose SURFACE_CURVE carries TWO PCURVEs on "
        "that same host -- one bank at u=0, one at u=1 -- is used twice with "
        "opposite orientations in the face's only EDGE_LOOP, the CATIA idiom. "
        "Unlike Gp182's CYLINDRICAL_SURFACE (inherently periodic) and unlike "
        "Gp013/Gp181's B-spline hosts (which the reader periodizes on the way "
        "in), this host genuinely satisfies both preconditions of the "
        "approximate-before-periodize repair: no declared period, and not "
        "already a B-spline"
    ),
)


def circ_pt(a):
    return f.cartesian_point((math.cos(a), math.sin(a), 0.0))


# ── basis: closed but NON-periodic B-spline curve (first pole == last pole) ──
angles = [i * 2.0 * math.pi / 8.0 for i in range(9)]
basis = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[circ_pt(a) for a in angles],
    knot_multiplicities=[3, 1, 1, 1, 1, 1, 1, 3],
    knots=[0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 1.0],
)

extr_dir = f.direction((0.0, 0.0, 1.0))
extr_vec = f.vector(extr_dir, 1.0)
host = f._emit_raw(
    f"SURFACE_OF_LINEAR_EXTRUSION('extrusion_host',#{basis.eid},#{extr_vec.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)


def pcurve(u0, v0, du, dv, length, nm):
    p = f._emit_raw(f"CARTESIAN_POINT('',({u0:.12f},{v0:.12f}))")
    d = f._emit_raw(f"DIRECTION('',({du:.12f},{dv:.12f}))")
    v = f._emit_raw(f"VECTOR('',#{d.eid},{length:.12f})")
    ln = f._emit_raw(f"LINE('',#{p.eid},#{v.eid})")
    rep = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('{nm}',(#{ln.eid}),#{prc.eid})")
    return f._emit_raw(f"PCURVE('{nm}',#{host.eid},#{rep.eid})")


p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 1.0))
v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)

# ── THE LIKE-SEAM: one 3D LINE, two PCURVEs on the same non-periodic host ───
seam_3d = f.line(p_bot, f.vector(extr_dir, 1.0))
seam_sc = f._emit_raw(
    f"SURFACE_CURVE('extrusion_like_seam',#{seam_3d.eid},"
    f"(#{pcurve(0.0, 0.0, 0.0, 1.0, 1.0, 'seam_bank_u0').eid},"
    f"#{pcurve(1.0, 0.0, 0.0, 1.0, 1.0, 'seam_bank_u1').eid}),.PCURVE_S1.)"
)
e_seam = f._emit_raw(
    f"EDGE_CURVE('seam',#{v_bot.eid},#{v_top.eid},#{seam_sc.eid},.T.)")


def wrap_arc(z, vtx, nm):
    plc = f.axis2_placement_3d(
        f.cartesian_point((0.0, 0.0, z)), extr_dir, f.direction((1.0, 0.0, 0.0)))
    c3d = f._emit_raw(f"CIRCLE('',#{plc.eid},1.0)")
    p = pcurve(0.0, z, 1.0, 0.0, 1.0, nm + "_pc")
    sc = f._emit_raw(
        f"SURFACE_CURVE('{nm}',#{c3d.eid},(#{p.eid}),.PCURVE_S1.)")
    return f._emit_raw(
        f"EDGE_CURVE('{nm}',#{vtx.eid},#{vtx.eid},#{sc.eid},.T.)")


e_bot = wrap_arc(0.0, v_bot, "bot_arc")
e_top = wrap_arc(1.0, v_top, "top_arc")

# ── 4-edge loop: bot (v=0) -> seam (u=1) -> top (v=1, rev) -> seam (u=0, rev) ─
loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_seam, True),
    f.oriented_edge(e_top, False),
    f.oriented_edge(e_seam, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], host)
f.add_product_chain(f.shell_based_surface_model([f.open_shell([face])]))
