"""Tsh264 — `DropSmallSolids` operator precondition with a LITERAL shared wall:
the input on which the operator's MergeSolids flag actually changes the outcome.

Catalog claim (occt-coverage `exchange/problems.json` `seq-drop-small-solids`,
subvariant 3: "remove vs merge disposition"; `ShapeProcess_OperLibrary.cxx`
:594-635, registered as `DropSmallSolids` at :908, backed by
`ShapeFix_FixSmallSolid`):

  The operator reads a `MergeSolids` boolean out of its resource scope and
  dispatches to either the delete path or the fold-into-the-neighbour path
  (ShapeProcess_OperLibrary.cxx:620-626). On Tsh238/Tsh239 -- the existing
  fixtures for this class -- the flag makes NO difference: both were
  live-confirmed in this worktree to give identical output for MergeSolids
  on and off, because the fold path's helper needs the small body and a
  non-small body to share a boundary face BY IDENTITY
  (`FindMostSharedShell`, ShapeFix_FixSmallSolid.cxx:219, face lookup at
  :247, bail-out at :270-272) and Tsh238/Tsh239's slivers merely TOUCH their
  neighbour with independent boundary entities.

  This fixture supplies that missing precondition, in the operator's own
  framing: ONE `ADVANCED_FACE` (`dss_shared_wall`) is listed by BOTH
  `CLOSED_SHELL`s, along with the four `EDGE_CURVE`s and four `VERTEX_POINT`s
  it is built from, so the flag genuinely selects between two different
  results (see Notes for the live operator run).

  The two shells are carried by ONE `SHELL_BASED_SURFACE_MODEL` because that
  is what preserves the sharing through translation: the receiver's
  shell-based-surface-model branch allocates ONE translation cache for every
  shell of the model (StepToTopoDS_Builder.cxx:390-393, shell loop
  :413-443), while its manifold-solid-brep branch allocates a fresh cache per
  solid (:119, :128-129) -- so two top-level solids can never come back
  sharing a face no matter how many entity IDs they have in common. Both
  halves of that asymmetry were live-verified in this worktree.

Geometry: body A is a 20 x 5 x 5 bar (volume 500) at x in [0,20]; body B is a
0.03 x 5 x 5 wafer (volume 0.75 = 0.15% of A; width factor
vol/(area/2) = 0.75/25.3 = 0.0296 mm) at x in [20, 20.03]. The wall at
x = 20 is the shared `ADVANCED_FACE`. Dimensions are deliberately distinct
from Tsh261's 12 x 9 x 6 / 0.04 pair (the same-family fixture framed against
`tkshh-sliver-solid` rather than against this operator).

Mechanism IS wired into the shape root: `dss_shared_wall` is a member of both
`CLOSED_SHELL`s, both of which are `SHELL_BASED_SURFACE_MODEL` boundary items
reached from the shape representation; nothing here is an orphan.

Byte assertions:
  - count_entity_def(b'CLOSED_SHELL') == 2
  - count_entity_def(b'ADVANCED_FACE') == 11
  - contains(b'dss_shared_wall')

Tier-3 assertions:
  - n_faces_total == 12
  - face[0].surface_type == "plane"
  - brepcheck.valid == True

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1):
  occt=shape(1)/shape(1) gmsh=shape(43)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh264",
    defect=(
        "SHELL_BASED_SURFACE_MODEL carrying two watertight CLOSED_SHELLs that "
        "share ONE ADVANCED_FACE entity ('dss_shared_wall', the x=20 wall) "
        "plus its four EDGE_CURVEs and four VERTEX_POINTs: body A is a "
        "20x5x5 bar (volume 500), body B a 0.03x5x5 wafer (volume 0.75, "
        "0.15% of A, width factor 0.0296mm). The shared boundary face is what "
        "makes the small-solid-dropping operator's MergeSolids flag select "
        "between two genuinely different outcomes, which Tsh238/Tsh239's "
        "merely-touching slivers cannot"
    ),
)

AX = 20.0     # bar length in x
BX = 0.03     # wafer thickness in x
SY = 5.0      # common y extent
SZ = 5.0      # common z extent

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


# ── the four EDGE_CURVEs of the shared wall at x = AX (used by both bodies) ─
e_m_bot = E('m00', 'm10', (0, 1, 0), SY)
e_m_top = E('m01', 'm11', (0, 1, 0), SY)
e_m_y0 = E('m00', 'm01', (0, 0, 1), SZ)
e_m_y1 = E('m10', 'm11', (0, 0, 1), SZ)

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
    PL((x1, 0.0, 0.0), (1, 0, 0), (0, 1, 0)), nm="dss_shared_wall")

# ── body A: the 20 x 5 x 5 bar ─────────────────────────────────────────────
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

# ── body B: the 0.03 x 5 x 5 wafer ─────────────────────────────────────────
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
                         name="tsh262_bar")
shell_b = f.closed_shell([shared_wall, fb_bot, fb_top, fb_y0, fb_y1, fb_far],
                         name="tsh262_wafer")

sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm)
