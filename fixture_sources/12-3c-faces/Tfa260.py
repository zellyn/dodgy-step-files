"""Tfa260 — Conical face bounded ONLY by a single full-revolution belt circle,
with the apex ABOVE the belt in the surface's own V parameter (belt on the
mirrored nappe).

Catalog claim (occt-coverage `tkshhealing/problems.json`
`tkshh-wire-missing-or-bad-degenerated-edge`, subvariant 7: "cone with single
closed belt wire: degenerated apex edge synthesized, apex below vs above the
wire V-range" — `ShapeFix_Face::FixPeriodicDegenerated`,
`ShapeFix_Face.cxx:2647-2788`; apex-ABOVE arm at `:2746-2751`):

  The mirror of Tfa259. The apex-position test at ShapeFix_Face.cxx:2733-2751
  has three outcomes: bail out if the apex falls inside (or within Precision()
  of) the loop's V range (`:2733-2735`); build the apex 2D line at
  (minLoopU, apexV) running in +U and reverse the wire unless U already
  decreases, when the apex is BELOW (`:2739-2744`); build it at
  (maxLoopU, apexV) running in -U and reverse the wire when U DOES decrease,
  when the apex is ABOVE (`:2746-2751`). The apex-above arm had never had a
  fixture at all: Tfa071/Tfa103/Tfa150 were all apex-below cases and were in
  any event found in the 2026-07-17 re-audit never to invoke this repair.

  Reaching "apex above" from a conforming STEP file constrains the geometry.
  `CONICAL_SURFACE` requires radius >= 0 and 0 < semi_angle < pi/2, so the apex
  V coordinate -radius/sin(semi_angle) is always <= 0; a belt on the ordinary
  nappe (V > 0) therefore always puts the apex BELOW. The only conforming way
  to put it ABOVE is to place the belt at a V below the apex, i.e. on the
  mirrored nappe of the double cone, where the parametric radius
  radius + V*sin(semi_angle) is negative and the U direction is consequently
  mirrored. This fixture does exactly that, and its 3D `CIRCLE` placement uses
  ref_direction (-1,0,0) so that the belt's 3D parametrization agrees with the
  surface's own U at every point rather than only at the seam.

Geometry: `CONICAL_SURFACE` with radius 3 at V=0 and semi-angle 30 degrees, so
the apex sits at V = -6. The belt is at V = -10, on the mirrored nappe:
parametric radius 3 + (-10)*sin(30) = -2, i.e. a 3D circle of radius 2 at
z = -10*cos(30) = -8.6602540, starting at (-2, 0, -8.6602540) for U = 0.
apexV = -6 > maxLoopV = -10, so the apex is ABOVE the belt.

Mechanism IS the shape root: the `EDGE_LOOP` is referenced by a
`FACE_OUTER_BOUND` inside the `ADVANCED_FACE` of an `OPEN_SHELL` reached from
the shape representation; nothing is orphaned.

Live-verified (2026-07-31, this worktree, OCP/OCCT 7.8.1): ONE declared
`EDGE_CURVE` reads back as a face with THREE edges (four oriented edges), one
seam used twice and one `BRep_Tool::Degenerated == True` whose pcurve is a
`Geom2d_Line` at loc=(6.283185, -6.0), dir=(-1, 0), range [0, 2*pi] — the
maxLoopU / decreasing-U construction, the exact mirror of Tfa259's
loc=(0.0, -6.0), dir=(+1, 0). The belt edge's orientation in the healed wire
also flips between the two fixtures, reflecting the different `Reverse()`
guard in each arm.

Byte assertions:
  - count_entity_def(b'CONICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_CURVE') == 1
  - contains(b'belt_above_apex')

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
V_BELT = -10.0                    # belt on the mirrored nappe, below the apex

R_SIGNED = RADIUS + V_BELT * math.sin(SEMI_ANGLE)   # -2.0
R_BELT = abs(R_SIGNED)                              # 2.0
Z_BELT = V_BELT * math.cos(SEMI_ANGLE)              # -8.6602540

f = StepFile(
    catalog_id="Tfa260",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CONICAL_SURFACE (radius 3 at "
        "V=0, semi-angle 30 deg, axis +Z, so the apex sits at V = -6 = "
        "-radius/sin(semi_angle)); FACE_OUTER_BOUND references a SINGLE-edge "
        "EDGE_LOOP whose only member is the full-revolution belt CIRCLE at "
        "V=-10 ('belt_above_apex', on the MIRRORED nappe: parametric radius "
        "3 + (-10)*sin(30) = -2, emitted as a 3D CIRCLE of radius 2 at "
        "z=-8.6602540 whose ref_direction is (-1,0,0) so its parametrization "
        "matches the surface's own mirrored U). The apex row is left "
        "unbounded: no apex-bridging degenerate edge and no seam are present "
        "in the file, and the apex lies ABOVE the belt in V (-6 > -10) -- the "
        "branch that must build the apex 2D line at the loop's maximum U "
        "running in -U, the mirror of Tfa259. The EDGE_LOOP IS wired into "
        "FACE_OUTER_BOUND, ADVANCED_FACE and OPEN_SHELL; never orphaned"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
cone = f._emit_raw(
    f"CONICAL_SURFACE('',#{f.axis2_placement_3d(orig, zdir, xdir).eid},"
    f"{RADIUS:.10f},{SEMI_ANGLE:.10f})"
)

p_belt = f.cartesian_point((R_SIGNED, 0.0, Z_BELT))
v_belt = f.vertex_point(p_belt)
belt_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, Z_BELT)), zdir, f.direction((-1.0, 0.0, 0.0)))
belt_circle = f._emit_raw(f"CIRCLE('',#{belt_plc.eid},{R_BELT:.10f})")
e_belt = f._emit_raw(
    f"EDGE_CURVE('belt_above_apex',#{v_belt.eid},#{v_belt.eid},"
    f"#{belt_circle.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(e_belt, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
f.add_product_chain(f.shell_based_surface_model([shell]))
