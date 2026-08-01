"""Tfa258 — Spherical face bounded ONLY by the equator: the pole-bridging
degenerate edge and the seam are both absent from the file.

Catalog claim (occt-coverage `tkshhealing/problems.json`
`tkshh-wire-missing-or-bad-degenerated-edge`, subvariant 6: "sphere with
single wire open in U: degenerated pole edge synthesized (FixMissingSeam)"
— `ShapeFix_Face::FixMissingSeam`, `ShapeFix_Face.cxx:1631-1699`, sphere arm
at `:1651-1656`):

  When a face on a U-closed surface has exactly ONE wire and that wire is open
  in 2D by a full U period, the missing-seam repair first has to invent the
  degenerate edge that closes the parametric rectangle at the singular row,
  and only then can it lay in the seam. The surface-type branch chain at
  ShapeFix_Face.cxx:1638-1681 picks WHICH singular row: degenerate torus
  (:1639-1650, Twi296's subvariant), sphere (:1651-1656, THIS fixture),
  B-spline V-pinch (:1657-1665, Twi297's subvariant), B-spline U-pinch
  (:1666-1680); anything else falls through to `return Standard_False`
  (:1680). The sphere arm was left with no fixture after the 2026-07-17
  re-audit removed Tfa245 (which turned out to contain no sphere pole at all).

  This fixture is the minimal input for it: a `SPHERICAL_SURFACE` of radius 5
  and an `ADVANCED_FACE` whose `FACE_OUTER_BOUND` is a one-edge `EDGE_LOOP`
  holding the equator `CIRCLE` as a closed `EDGE_CURVE` (same `VERTEX_POINT`
  at both ends). One wire, open in U by exactly 2*pi in 2D. No seam edge and
  no pole edge anywhere in the bytes.

Mechanism IS the shape root: the `EDGE_LOOP` is referenced by a
`FACE_OUTER_BOUND` inside the `ADVANCED_FACE` of an `OPEN_SHELL` reached from
the shape representation; nothing is orphaned.

Live-verified (2026-07-31, this worktree, OCP/OCCT 7.8.1) — see the catalog
Notes for the full numbers: ONE declared `EDGE_CURVE` reads back as a face
with THREE edges (four oriented edges), of which one is a seam used twice and
one comes back `BRep_Tool::Degenerated == True` with a `Geom2d_Line` pcurve at
loc=(6.283185, 1.570796), dir=(-1, 0), range [0, 2*pi] — i.e. v = +pi/2, the
north pole, traversed in decreasing U. That is bit-for-bit the construction at
ShapeFix_Face.cxx:1652-1654 for ismodeu = +1.

Byte assertions:
  - count_entity_def(b'SPHERICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_CURVE') == 1
  - contains(b'equator_only_bound')

Tier-3 assertions:
  - face[0].surface_type == "sphere"
  - n_edges_total == 4
  - brepcheck.valid == True

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1):
  occt=shape(1)/shape(1) gmsh=shape(6)
"""
from step_corpus.step_builder import StepFile

RADIUS = 5.0

f = StepFile(
    catalog_id="Tfa258",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a SPHERICAL_SURFACE (radius 5, "
        "centre at the origin, axis +Z); FACE_OUTER_BOUND references a "
        "SINGLE-edge EDGE_LOOP whose only member is the equator CIRCLE as a "
        "closed EDGE_CURVE ('equator_only_bound', the same VERTEX_POINT at "
        "both ends) -- one wire, open in 2D by a full 2*pi U period. NEITHER "
        "the seam edge NOR the degenerate pole-bridging edge that a complete "
        "parametric boundary needs is present in the file; a receiver must "
        "invent the pole edge at v = +pi/2 before it can lay in the seam. "
        "The EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE and "
        "OPEN_SHELL; never orphaned"
    ),
)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
sphere = f.spherical_surface(f.axis2_placement_3d(orig, zdir, xdir), RADIUS)

# ── the single equator edge: closed CIRCLE, one VERTEX_POINT reused ─────────
p_eq = f.cartesian_point((RADIUS, 0.0, 0.0))
v_eq = f.vertex_point(p_eq)
eq_plc = f.axis2_placement_3d(f.cartesian_point((0.0, 0.0, 0.0)), zdir, xdir)
eq_circle = f.circle(eq_plc, RADIUS)
e_eq = f._emit_raw(
    f"EDGE_CURVE('equator_only_bound',#{v_eq.eid},#{v_eq.eid},"
    f"#{eq_circle.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(e_eq, True)])
face = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
f.add_product_chain(f.shell_based_surface_model([shell]))
