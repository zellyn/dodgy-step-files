"""Tsh253 — Two coplanar, adjacent (not coincident) unit-square faces
whose shared boundary candidate is traversed in genuinely opposite
directions on each side (the ordinary CCW/outward-normal convention for
two faces meeting at a common edge): a clean second cross-pairing
demonstration, distinct from Tsh176's degenerate coincident-cancel-out
collapse (sew-vertex-endpoint-pairing-orientation PARTIAL).

Catalog claim (occt-coverage PARTIAL `sew-vertex-endpoint-pairing-
orientation`): per `occt-coverage/exchange/problems.json`, the class was
DOWNGRADED COVERED->PARTIAL because two of its three prior fixtures were
found off-target on re-audit: Tsh086 exercises a DIFFERENT shell-
orientation-normalization mechanism entirely, and M045's misaligned
endpoints are rejected earlier in `FindCandidates`, never reaching the
cross-pairing gate; only Tsh176 cleanly demonstrates cross-pairing, and
it does so via two fully COINCIDENT, opposite-facing faces whose merge
collapses to a geometrically degenerate (`shape_null==True`) result.
This fixture is a second, independent cross-pairing demonstration built
so the merge instead produces a genuinely VALID, non-degenerate result:

Two ADVANCED_FACEs in one OPEN_SHELL, each its own unit square,
ADJACENT (not coincident) and coplanar (z=0): Face A occupies
x:[0,1],y:[0,1]; Face B occupies x:[0,1],y:[-1,-0.0005] (a 0.0005mm gap
from Face A along y=0, within a 1.0mm sewing tolerance). Both faces use
the ordinary CCW-traversal/outward-+Z-normal convention — under that
convention, Face A's boundary edge along y=0 is traversed
(0,0,0)->(1,0,0), while Face B's corresponding boundary edge along
y=-0.0005 is traversed IN THE OPPOSITE DIRECTION, (1,-0.0005,0)->
(0,-0.0005,0) — the genuine "one is effectively reversed relative to
the other" pairing case the class describes, arising from ordinary,
correctly-oriented adjacent-face geometry (not a defect in the input,
but the standard case the cross-pairing logic must handle correctly
every time two faces are sewn together).

Live verification (this worktree's OCP/OCCT 7.8.1, runtime sewing
scaffold, `BRepBuilderAPI_Sewing(1.0)`): the pair merges cleanly --
`NbContigousEdges()==1`, `NbMultipleEdges()==0` -- into a genuinely
valid, non-degenerate 2-face shell (both faces retained,
`edge->face-count histogram: {1: 6 free edges, 2: 1 shared edge}`), the
shared edge's achieved tolerance `0.000525` (gap-proportional), sharply
distinct from Tsh176's outcome where the equivalent merge instead
collapses the whole shape to `shape_null==True`.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 2
  - count_entity_def(b'OPEN_SHELL') == 1
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh253",
    schema="AP242",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs, coplanar (z=0) and ADJACENT "
        "(not coincident): Face A unit square x:[0,1],y:[0,1] with "
        "boundary edge along y=0 traversed (0,0,0)->(1,0,0); Face B unit "
        "square x:[0,1],y:[-1,-0.0005] with its corresponding boundary "
        "edge along y=-0.0005 traversed in the OPPOSITE direction "
        "(1,-0.0005,0)->(0,-0.0005,0), under the ordinary CCW/outward-"
        "+Z-normal convention -- a clean, genuinely non-degenerate "
        "cross-pairing merge candidate, second independent demonstration "
        "distinct from Tsh176's coincident opposite-facing (degenerate, "
        "shape_null==True) collapse"
    ),
)


def cp(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))


def dir3(x, y, z):
    return f.direction((float(x), float(y), float(z)))


def led(va, vb, pt, dx, dy, length):
    d = dir3(dx, dy, 0.0)
    vec = f.vector(d, length)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)


GAP = 0.0005

# Face A: unit square x:[0,1], y:[0,1], z=0, normal +Z, CCW from +Z.
pa00 = cp(0, 0, 0); pa10 = cp(1, 0, 0); pa11 = cp(1, 1, 0); pa01 = cp(0, 1, 0)
va00 = f.vertex_point(pa00); va10 = f.vertex_point(pa10)
va11 = f.vertex_point(pa11); va01 = f.vertex_point(pa01)
ea_bot = led(va00, va10, pa00, 1, 0, 1.0, )  # (0,0)->(1,0), +X -- shared candidate
ea_rgt = led(va10, va11, pa10, 0, 1, 1.0)
ea_top = led(va01, va11, pa01, 1, 0, 1.0)
ea_lft = led(va00, va01, pa00, 0, 1, 1.0)
loop_a = f.edge_loop([
    f.oriented_edge(ea_bot, True),
    f.oriented_edge(ea_rgt, True),
    f.oriented_edge(ea_top, False),
    f.oriented_edge(ea_lft, False),
])
plane_a = f.plane(f.axis2_placement_3d(pa00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)

# Face B: unit square x:[0,1], y:[-1,-GAP], z=0, normal +Z. Its edge
# adjacent to face A (at y=-GAP) is naturally traversed in the REVERSED
# (-X) direction under the same CCW/+Z-normal convention: (1,-GAP)->
# (0,-GAP) -- the cross-pairing candidate.
pb00 = cp(0, -1, 0); pb10 = cp(1, -1, 0)
pb11 = cp(1, -GAP, 0); pb01 = cp(0, -GAP, 0)
vb00 = f.vertex_point(pb00); vb10 = f.vertex_point(pb10)
vb11 = f.vertex_point(pb11); vb01 = f.vertex_point(pb01)
eb_bot = led(vb00, vb10, pb00, 1, 0, 1.0)
eb_rgt = led(vb10, vb11, pb10, 0, 1, 1.0 - GAP)
eb_top = led(vb11, vb01, pb11, -1, 0, 1.0)  # (1,-GAP)->(0,-GAP), -X -- shared candidate
eb_lft = led(vb00, vb01, pb00, 0, 1, 1.0 - GAP)
loop_b = f.edge_loop([
    f.oriented_edge(eb_bot, True),
    f.oriented_edge(eb_rgt, True),
    f.oriented_edge(eb_top, True),
    f.oriented_edge(eb_lft, False),
])
plane_b = f.plane(f.axis2_placement_3d(pb00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane_b, same_sense=True)

shell = f.open_shell([face_a, face_b], name="tsh253_cross_pairing_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
