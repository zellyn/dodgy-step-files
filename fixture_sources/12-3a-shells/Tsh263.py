"""Tsh263 — Sliver body sharing a LITERAL wall face with its neighbour: the
input that makes the fold-into-the-neighbour repair disposition reachable
(as opposed to the delete disposition Tsh234/Tsh235 exercise).

Catalog claim (occt-coverage `tkshhealing/problems.json`
`tkshh-sliver-solid`, subvariant 3: "repair mode: delete vs fold into
neighboring solid, selectable via SetFixMode(0/1/2)"):

  The fold-into-the-neighbour disposition (`ShapeFix_FixSmallSolid::Merge`,
  ShapeFix_FixSmallSolid.cxx:401) only has anything to do once the small body
  and a non-small body share a boundary face *by identity*: its helper
  `FindMostSharedShell` (ShapeFix_FixSmallSolid.cxx:219) looks each of the
  small body's faces up in a map keyed by the non-small bodies' faces
  (`theMapFacesToOuterShells.Seek(aFace)`, :247) and bails out returning
  nothing when no lookup succeeds (:270-272). Merely *touching* geometry
  is not enough — Tsh234/Tsh235/Tsh238/Tsh239 all place their sliver flush
  against the normal body but with its own independent boundary entities, and
  all four were live-confirmed to leave the fold disposition inert (solid and
  face counts unchanged in every threshold/mode combination) while the delete
  disposition fires on each of them.

  This fixture supplies the missing precondition: ONE `ADVANCED_FACE` entity
  is listed by BOTH `CLOSED_SHELL`s, and the four `EDGE_CURVE`s and four
  `VERTEX_POINT`s of that wall are likewise listed by the adjoining faces of
  both bodies — a genuinely shared boundary, not a coincident duplicate.
  The two shells are carried by ONE `SHELL_BASED_SURFACE_MODEL`, which is
  what preserves the sharing through translation: the receiver's
  shell-based-surface-model branch allocates a single translation cache for
  every shell in the model (StepToTopoDS_Builder.cxx:390-393, used by the
  shell loop at :413-443), whereas its manifold-solid-brep branch allocates a
  fresh cache per solid (StepToTopoDS_Builder.cxx:119, :128-129) so two
  top-level solids can never come back sharing a face however many entity IDs
  they have in common. That asymmetry was live-verified both ways in this
  worktree (see Notes) and is why this fixture is authored as a shared-face
  shell pair rather than as two `MANIFOLD_SOLID_BREP`s.

Geometry: body A is a 12 x 9 x 6 block (volume 648) at x in [0,12]; body B is
a 0.04 x 9 x 6 flake (volume 2.16 = 0.333% of A; width factor
vol/(area/2) = 2.16/54.6 = 0.0396 mm) at x in [12, 12.04]. The wall at
x = 12 -- `shared_sliver_wall` -- is the single shared `ADVANCED_FACE`.

Mechanism IS wired into the shape root: `shared_sliver_wall` is a member of
both `CLOSED_SHELL`s, both of which are `SHELL_BASED_SURFACE_MODEL` boundary
items reached from the shape representation; nothing here is an orphan.

Byte assertions:
  - count_entity_def(b'CLOSED_SHELL') == 2
  - count_entity_def(b'ADVANCED_FACE') == 11
  - contains(b'shared_sliver_wall')

Tier-3 assertions:
  - n_faces_total == 11
  - face[0].surface_type == "plane"

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1):
  occt=shape(1)/shape(1) gmsh=shape(52)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh263",
    defect=(
        "SHELL_BASED_SURFACE_MODEL carrying two watertight CLOSED_SHELLs that "
        "share ONE ADVANCED_FACE entity ('shared_sliver_wall', the x=12 wall) "
        "plus its four EDGE_CURVEs and four VERTEX_POINTs: body A is a "
        "12x9x6 block (volume 648), body B a 0.04x9x6 flake (volume 2.16, "
        "0.333% of A, width factor 0.0396mm). The shared boundary face is "
        "the precondition a fold-into-the-neighbour sliver repair needs and "
        "that Tsh234/Tsh235's merely-touching slivers lack"
    ),
)

AX = 12.0     # block thickness in x
BX = 0.04     # flake thickness in x
SY = 9.0      # common y extent
SZ = 6.0      # common z extent

x0, x1, x2 = 0.0, AX, AX + BX


def P(x, y, z):
    return f.cartesian_point((x, y, z))


pts = {
    'a00': P(x0, 0.0, 0.0), 'a10': P(x0, SY, 0.0),
    'a01': P(x0, 0.0, SZ),  'a11': P(x0, SY, SZ),
    'm00': P(x1, 0.0, 0.0), 'm10': P(x1, SY, 0.0),
    'm01': P(x1, 0.0, SZ),  'm11': P(x1, SY, SZ),
    'b00': P(x2, 0.0, 0.0), 'b10': P(x2, SY, 0.0),
    'b01': P(x2, 0.0, SZ),  'b11': P(x2, SY, SZ),
}
vts = {k: f.vertex_point(p) for k, p in pts.items()}


def E(k1, k2, d, mag):
    return f.edge_curve(vts[k1], vts[k2],
                        f.line(pts[k1], f.vector(f.direction(d), mag)))


def PL(o, zd, xd):
    return f.plane(f.axis2_placement_3d(P(*o), f.direction(zd), f.direction(xd)))


def FACE(ews, plane, nm=""):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in ews])
    return f.advanced_face([f.face_outer_bound(loop)], plane, name=nm)


# ── the four EDGE_CURVEs of the shared wall at x = AX ───────────────────────
#    each of these is referenced by faces of BOTH bodies.
e_m_bot = E('m00', 'm10', (0, 1, 0), SY)   # z = 0
e_m_top = E('m01', 'm11', (0, 1, 0), SY)   # z = SZ
e_m_y0 = E('m00', 'm01', (0, 0, 1), SZ)    # y = 0
e_m_y1 = E('m10', 'm11', (0, 0, 1), SZ)    # y = SY

# ── body A's own far wall (x = 0) and its four x-direction connectors ───────
e_a_bot = E('a00', 'a10', (0, 1, 0), SY)
e_a_top = E('a01', 'a11', (0, 1, 0), SY)
e_a_y0 = E('a00', 'a01', (0, 0, 1), SZ)
e_a_y1 = E('a10', 'a11', (0, 0, 1), SZ)
ca00 = E('a00', 'm00', (1, 0, 0), AX)
ca10 = E('a10', 'm10', (1, 0, 0), AX)
ca01 = E('a01', 'm01', (1, 0, 0), AX)
ca11 = E('a11', 'm11', (1, 0, 0), AX)

# ── body B's own far wall (x = AX+BX) and its four connectors ──────────────
e_b_bot = E('b00', 'b10', (0, 1, 0), SY)
e_b_top = E('b01', 'b11', (0, 1, 0), SY)
e_b_y0 = E('b00', 'b01', (0, 0, 1), SZ)
e_b_y1 = E('b10', 'b11', (0, 0, 1), SZ)
cb00 = E('m00', 'b00', (1, 0, 0), BX)
cb10 = E('m10', 'b10', (1, 0, 0), BX)
cb01 = E('m01', 'b01', (1, 0, 0), BX)
cb11 = E('m11', 'b11', (1, 0, 0), BX)

# ── THE SHARED FACE: the wall at x = AX, listed by both CLOSED_SHELLs ──────
shared_wall = FACE(
    [(e_m_bot, True), (e_m_y1, True), (e_m_top, False), (e_m_y0, False)],
    PL((x1, 0.0, 0.0), (1, 0, 0), (0, 1, 0)), nm="shared_sliver_wall")

# ── body A: the 12 x 9 x 6 block ───────────────────────────────────────────
fa_far = FACE([(e_a_bot, True), (e_a_y1, True), (e_a_top, False), (e_a_y0, False)],
              PL((x0, 0.0, 0.0), (-1, 0, 0), (0, 1, 0)))
fa_bot = FACE([(e_a_bot, True), (ca10, True), (e_m_bot, False), (ca00, False)],
              PL((x0, 0.0, 0.0), (0, 0, -1), (1, 0, 0)))
fa_top = FACE([(e_a_top, True), (ca11, True), (e_m_top, False), (ca01, False)],
              PL((x0, 0.0, SZ), (0, 0, 1), (1, 0, 0)))
fa_y0 = FACE([(e_a_y0, True), (ca01, True), (e_m_y0, False), (ca00, False)],
             PL((x0, 0.0, 0.0), (0, -1, 0), (1, 0, 0)))
fa_y1 = FACE([(e_a_y1, True), (ca11, True), (e_m_y1, False), (ca10, False)],
             PL((x0, SY, 0.0), (0, 1, 0), (1, 0, 0)))

# ── body B: the 0.04 x 9 x 6 flake ─────────────────────────────────────────
fb_far = FACE([(e_b_bot, True), (e_b_y1, True), (e_b_top, False), (e_b_y0, False)],
              PL((x2, 0.0, 0.0), (1, 0, 0), (0, 1, 0)))
fb_bot = FACE([(e_m_bot, True), (cb10, True), (e_b_bot, False), (cb00, False)],
              PL((x1, 0.0, 0.0), (0, 0, -1), (1, 0, 0)))
fb_top = FACE([(e_m_top, True), (cb11, True), (e_b_top, False), (cb01, False)],
              PL((x1, 0.0, SZ), (0, 0, 1), (1, 0, 0)))
fb_y0 = FACE([(e_m_y0, True), (cb01, True), (e_b_y0, False), (cb00, False)],
             PL((x1, 0.0, 0.0), (0, -1, 0), (1, 0, 0)))
fb_y1 = FACE([(e_m_y1, True), (cb11, True), (e_b_y1, False), (cb10, False)],
             PL((x1, SY, 0.0), (0, 1, 0), (1, 0, 0)))

shell_a = f.closed_shell([fa_far, fa_bot, fa_top, fa_y0, fa_y1, shared_wall],
                         name="tsh261_block")
shell_b = f.closed_shell([shared_wall, fb_bot, fb_top, fb_y0, fb_y1, fb_far],
                         name="tsh261_flake")

sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm)
