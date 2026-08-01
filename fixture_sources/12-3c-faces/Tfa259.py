"""Tfa259 — Conical face bounded ONLY by a single full-revolution belt circle,
with the apex BELOW the belt in the surface's own V parameter.

Catalog claim (occt-coverage `tkshhealing/problems.json`
`tkshh-wire-missing-or-bad-degenerated-edge`, subvariant 7: "cone with single
closed belt wire: degenerated apex edge synthesized, apex below vs above the
wire V-range" — `ShapeFix_Face::FixPeriodicDegenerated`,
`ShapeFix_Face.cxx:2647-2788`; apex-BELOW arm at `:2739-2744`):

  A conical face whose only boundary is one closed loop belting the cone
  through a full 2*pi is parametrically incomplete: the apex row is unbounded.
  The repair is cone-specific (the surface-type gate at
  ShapeFix_Face.cxx:2681-2683 rejects everything that is not a
  `Geom_ConicalSurface`, and the loop gate `IsPeriodicConicalLoop` at
  `:2570-2639` requires the accumulated |dU| to be 2*pi), and it splits in two
  depending on where the apex falls in V relative to the belt: BELOW
  (`:2739-2744`, this fixture) builds the apex 2D line at (minLoopU, apexV)
  running in +U; ABOVE (`:2746-2751`, Tfa260) builds it at (maxLoopU, apexV)
  running in -U. Both arms lost their fixtures in the 2026-07-17 re-audit,
  which found Tfa071/Tfa103/Tfa150 never invoke this repair at all.

Geometry: `CONICAL_SURFACE` with radius 3 at V=0 and semi-angle 30 degrees, so
the apex sits at V = -radius/sin(semi_angle) = -6. The belt is the circle at
V = +2 (3D radius 3 + 2*sin(30) = 4, at z = 2*cos(30) = 1.7320508), authored
as one closed `EDGE_CURVE` with the same `VERTEX_POINT` at both ends.
apexV = -6 < minLoopV = +2, so the apex is BELOW the belt.

Mechanism IS the shape root: the `EDGE_LOOP` is referenced by a
`FACE_OUTER_BOUND` inside the `ADVANCED_FACE` of an `OPEN_SHELL` reached from
the shape representation; nothing is orphaned.

Live-verified (2026-07-31, this worktree, OCP/OCCT 7.8.1): ONE declared
`EDGE_CURVE` reads back as a face with THREE edges (four oriented edges), one
seam used twice and one `BRep_Tool::Degenerated == True` whose pcurve is a
`Geom2d_Line` at loc=(0.0, -6.0), dir=(+1, 0), range [0, 2*pi]. The V value
-6.0 is exactly -radius/sin(semi_angle), the quantity computed at
ShapeFix_Face.cxx:2716-2717 and nowhere else in the healing stack; a sweep over
four (radius, semi-angle) pairs confirmed the synthesized edge tracks it (see
catalog Notes).

Byte assertions:
  - count_entity_def(b'CONICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_CURVE') == 1
  - contains(b'belt_below_apex')

Tier-3 assertions:
  - face[0].surface_type == "cone"
  - n_edges_total == 4
  - brepcheck.valid == True

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1):
  occt=shape(1)/shape(1) gmsh=shape(6)
"""
import math
from step_corpus.step_builder import StepFile

RADIUS = 3.0                      # cone radius at V = 0
SEMI_ANGLE = math.radians(30.0)
V_BELT = 2.0                      # belt on the first nappe, above the apex

R_BELT = RADIUS + V_BELT * math.sin(SEMI_ANGLE)   # 4.0
Z_BELT = V_BELT * math.cos(SEMI_ANGLE)            # 1.7320508

f = StepFile(
    catalog_id="Tfa259",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CONICAL_SURFACE (radius 3 at "
        "V=0, semi-angle 30 deg, axis +Z, so the apex sits at V = -6 = "
        "-radius/sin(semi_angle)); FACE_OUTER_BOUND references a SINGLE-edge "
        "EDGE_LOOP whose only member is the full-revolution belt CIRCLE at "
        "V=+2 ('belt_below_apex', radius 4 at z=1.7320508, the same "
        "VERTEX_POINT at both ends). The apex row is left unbounded: no "
        "apex-bridging degenerate edge and no seam are present in the file, "
        "and the apex lies BELOW the belt in V (-6 < +2) -- the branch that "
        "must build the apex 2D line at the loop's minimum U running in +U. "
        "The EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE and "
        "OPEN_SHELL; never orphaned"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
cone = f._emit_raw(
    f"CONICAL_SURFACE('',#{f.axis2_placement_3d(orig, zdir, xdir).eid},"
    f"{RADIUS:.10f},{SEMI_ANGLE:.10f})"
)

p_belt = f.cartesian_point((R_BELT, 0.0, Z_BELT))
v_belt = f.vertex_point(p_belt)
belt_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, Z_BELT)), zdir, f.direction((1.0, 0.0, 0.0)))
belt_circle = f._emit_raw(f"CIRCLE('',#{belt_plc.eid},{R_BELT:.10f})")
e_belt = f._emit_raw(
    f"EDGE_CURVE('belt_below_apex',#{v_belt.eid},#{v_belt.eid},"
    f"#{belt_circle.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(e_belt, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
f.add_product_chain(f.shell_based_surface_model([shell]))
