"""Tsh245 — Purpose-built candidate tie-break AND reciprocity-asymmetric
configuration (sew-candidate-tiebreak-reciprocity PARTIAL).

Catalog claim (occt-coverage PARTIAL `sew-candidate-tiebreak-reciprocity`):
per `occt-coverage/exchange/problems.json`, the sole existing fixture
(M045) hits the multi-candidate scenario only incidentally (its actual
purpose is an XCAF-attribute-loss demonstration) and neither engineers
genuinely equidistant candidates nor a reciprocity-asymmetric (A's best
match is B, but B's best match is C) configuration. This fixture
purpose-builds BOTH, in two spatially isolated (100mm apart in Y) groups
within one OPEN_SHELL:

  Group 1 — equidistant tie-break (`BRepBuilderAPI_Sewing::FindCandidates`,
  `BRepBuilderAPI_Sewing.cxx:1508-1519`): reference edge R at y=0 has TWO
  candidates equidistant at 0.6mm (B above at y=+0.6, C below at y=-0.6) —
  both within the 1.0mm sewing tolerance of R, but 1.2mm apart from EACH
  OTHER (beyond tolerance, so B and C are never candidates for each
  other), forcing the `arrMinDist` tie-break to pick between them for R.
  Live-verified (this worktree's OCP/OCCT 7.8.1): the tie-break resolves
  to a single definite winner — R merges with C (y~-0.3, nfaces=2) — while
  B (y=0.6, nfaces=1) is left free/unmerged; the point is that exactly
  ONE of the two equidistant candidates wins, not both and not neither
  (which candidate wins is an implementation detail of `arrMinDist`
  ordering, not asserted directionally).

  Group 2 — reciprocity-asymmetric chain (`BRepBuilderAPI_Sewing.cxx:1638
  -1653+`, the recursive `FindCandidates` reciprocal-match walk): D
  (reference), E (0.01mm from D), F (0.011mm from D, only 0.001mm from
  E). D's nearest candidate is E (0.01 < 0.011), but E's OWN nearest
  candidate is F (0.001 < 0.01), not D — a genuine reciprocity failure:
  D's pick doesn't pick D back. Live-verified: D remains a free/unmerged
  edge (y=100.0, nfaces=1) after Sewing, while E and F — whose distance
  IS each other's mutual minimum — merge into one shared edge (y~100.0105,
  nfaces=2), exactly the "walks to the next candidate / defers to the
  closer reciprocal pair" behavior this class targets.

Six triangular faces (2 groups of 3), each contributing exactly one
"test" edge along x:[0,10] at a distinct y-offset; Group 1's non-test
(apex) edges use deliberately very different depths (3 / 40 / -40mm) so
they diverge rapidly and are never themselves within sewing tolerance of
each other — confirmed live and fixed during authoring: near-equal apex
depths let R/B/C's near-parallel leg edges spuriously chain-merge with
each other, contaminating the tie-break test with an unrelated mechanism.

Mechanism IS the shell topology: all six test edges are real ADVANCED_FACE
boundary edges in one OPEN_SHELL, not orphaned scaffold entities.

Live verification: reader-default STEPControl_Reader does not itself
invoke BRepBuilderAPI_Sewing. The mechanism is demonstrated via a runtime
scaffold that explicitly constructs BRepBuilderAPI_Sewing(tolerance=1.0)
over the translated shape and calls Perform() — see catalog Notes field
for the live per-edge face-multiplicity results (R stays free; exactly
one of B/C merges with R per the tie-break; E and F merge with each
other, not with D).

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 6
  - count_entity_def(b'OPEN_SHELL') == 1
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh245",
    defect=(
        "OPEN_SHELL with SIX ADVANCED_FACEs in two spatially isolated "
        "groups: Group 1 (y~0) has reference edge R with TWO genuinely "
        "equidistant (0.6mm) candidates B/C on opposite sides, requiring "
        "BRepBuilderAPI_Sewing::FindCandidates' arrMinDist tie-break; "
        "Group 2 (y~100) has D/E/F at 0mm/0.01mm/0.011mm offsets forming "
        "a reciprocity-asymmetric chain (D's nearest is E, but E's own "
        "nearest is F, not D) exercising the recursive mutual-match walk"
    ),
)


def strip_face(y, apex_dy, apex_depth):
    """One triangular ADVANCED_FACE contributing exactly one 'test' edge
    along x:[0,10] at height y; apex at (5, y+apex_dy+apex_depth) — a
    unique depth per call keeps every triangle's non-test edges from ever
    being collinear with another triangle's. Returns (face, test_edge).
    """
    p0 = f.cartesian_point((0.0, y, 0.0))
    p1 = f.cartesian_point((10.0, y, 0.0))
    papex = f.cartesian_point((5.0, y + apex_dy + apex_depth, 0.0))
    v0 = f.vertex_point(p0)
    v1 = f.vertex_point(p1)
    vapex = f.vertex_point(papex)

    d_test = f.direction((1.0, 0.0, 0.0))
    vec_test = f.vector(d_test, 10.0)
    ln_test = f.line(p0, vec_test)
    e_test = f.edge_curve(v0, v1, ln_test)

    def mk_leg(pa, va, pb, vb):
        dx = pb.args[1][0] - pa.args[1][0]
        dy = pb.args[1][1] - pa.args[1][1]
        length = (dx * dx + dy * dy) ** 0.5
        d = f.direction((dx / length, dy / length, 0.0))
        vec = f.vector(d, length)
        ln = f.line(pa, vec)
        return f.edge_curve(va, vb, ln)

    e_leg1 = mk_leg(p1, v1, papex, vapex)
    e_leg2 = mk_leg(papex, vapex, p0, v0)

    loop = f.edge_loop([
        f.oriented_edge(e_test, True),
        f.oriented_edge(e_leg1, True),
        f.oriented_edge(e_leg2, True),
    ])
    orig = p0
    zdir = f.direction((0.0, 0.0, 1.0))
    xdir = f.direction((1.0, 0.0, 0.0))
    plc = f.axis2_placement_3d(orig, zdir, xdir)
    plane = f.plane(plc)
    fob = f.face_outer_bound(loop)
    face = f.advanced_face([fob], plane)
    return face, e_test


# ── Group 1: equidistant tie-break (R vs B/C, 0.6mm each side) ─────────────
# Apex depths deliberately very different (3 / 40 / -40) so R/B/C's own
# non-test leg edges diverge rapidly and are never themselves within
# sewing tolerance of each other (confirmed live and fixed during
# authoring: near-equal apex depths let the near-parallel leg edges
# spuriously chain-merge across R/B/C, contaminating the tie-break test).
face_R, edge_R = strip_face(0.0, 0.0, 3.0)
face_B, edge_B = strip_face(0.6, 0.0, 40.0)     # 0.6mm above R, apex far up
face_C, edge_C = strip_face(-0.6, 0.0, -40.0)   # 0.6mm below R, apex far down

# ── Group 2: reciprocity-asymmetric chain (D/E/F), isolated 100mm away ─────
face_D, edge_D = strip_face(100.0, 0.0, 3.0)
face_E, edge_E = strip_face(100.01, 0.0, 4.0)
face_F, edge_F = strip_face(100.011, 0.0, 5.0)

# ── All six faces in one OPEN_SHELL ─────────────────────────────────────────
shell = f.open_shell(
    [face_R, face_B, face_C, face_D, face_E, face_F],
    name="tsh245_tiebreak_reciprocity_shell",
)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
