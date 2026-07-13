"""Tsh243 — Within-tolerance gap but candidate edge shorter than the
min-length floor: rejected as a spurious sliver, not merged
(sew-free-edge-gap-merge PARTIAL, missing subvariant (a) of 2).

Catalog claim (occt-coverage PARTIAL `sew-free-edge-gap-merge`): per
`occt-coverage/exchange/problems.json`, the six existing fixtures (Tfa020,
Tsh203, Tsh187, Twi037, Tfa019, Tsh181) all present ordinary-length
within-tolerance gap-merge candidates; neither of the class's two named
subvariants is covered. This fixture builds subvariant (a):
`BRepBuilderAPI_Sewing::FindCandidates` (`BRepBuilderAPI_Sewing.cxx:1502`):
`if (aMaxDist >= 0.0 && aMaxDist <= myTolerance && arrLen(i) > myMinTolerance)`
— a candidate is accepted only if BOTH the sampled max distance is within
tolerance AND the matching span exceeds `myMinTolerance` (internally
`myTolerance * 1e-4`). This fixture presents a candidate edge whose gap
IS within tolerance but whose own LENGTH is far below that floor — a
spurious sliver that must be rejected, not merged.

Two faces, one OPEN_SHELL:
  - Face A: a 10mm-long reference free edge E = (0,0,0)-(10,0,0), hosted
    by a rectangle (y:[0,3]).
  - Face B: a genuinely tiny (5e-5mm-long) candidate edge sitting at
    x:[4.0, 4.00005], y=1e-4 (perpendicular gap 1e-4mm — comfortably
    within a 1.0mm sewing tolerance, so the gap check alone would pass),
    hosted by its own small triangular face. At operating tolerance 1.0,
    `myMinTolerance = myTolerance*1e-4 = 1e-4` — Face B's candidate span
    (5e-5) is HALF the floor, so `arrLen(i) > myMinTolerance` fails and
    the merge must be rejected (E remains free/unmatched at that
    location), unlike an ordinary-length candidate (verified separately,
    e.g. Tsh242's Face A/B pair, which DOES merge under the same harness).

Mechanism IS the shell topology: both edges are real ADVANCED_FACE
boundary edges in one OPEN_SHELL, not orphaned scaffold entities.

Live verification: reader-default STEPControl_Reader does not itself
invoke BRepBuilderAPI_Sewing. The mechanism is demonstrated via a runtime
scaffold that explicitly constructs BRepBuilderAPI_Sewing(tolerance=1.0)
over the translated shape and calls Perform() — see catalog Notes field
for the live free-edge counts (confirms no contiguous pairing forms for
the sliver candidate).

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 2
  - count_entity_def(b'OPEN_SHELL') == 1
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh243",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs: Face A hosts a 10mm reference "
        "free edge E=(0,0,0)-(10,0,0); Face B hosts a genuinely tiny "
        "(5e-5mm-long) candidate edge at x:[4.0,4.00005], y=1e-4 (gap "
        "well within a 1.0mm sewing tolerance) — purpose-built to fail "
        "BRepBuilderAPI_Sewing::FindCandidates' myMinTolerance span floor "
        "(arrLen(i) > myMinTolerance) despite passing the distance-gate, "
        "demonstrating the spurious-sliver rejection path"
    ),
)

# ── Face A: rectangle hosting reference free edge E = (0,0,0)-(10,0,0) ──────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((10.0, 0.0, 0.0))
p13 = f.cartesian_point((10.0, 3.0, 0.0))
p03 = f.cartesian_point((0.0, 3.0, 0.0))
v0 = f.vertex_point(p0)
v10 = f.vertex_point(p10)
v13 = f.vertex_point(p13)
v03 = f.vertex_point(p03)

d_px = f.direction((1.0, 0.0, 0.0))
d_py = f.direction((0.0, 1.0, 0.0))
d_mx = f.direction((-1.0, 0.0, 0.0))
d_my = f.direction((0.0, -1.0, 0.0))

vecE = f.vector(d_px, 10.0)
lnE = f.line(p0, vecE)
edgeE = f.edge_curve(v0, v10, lnE)

vec1 = f.vector(d_py, 3.0)
ln1 = f.line(p10, vec1)
e_right = f.edge_curve(v10, v13, ln1)

vec2 = f.vector(d_mx, 10.0)
ln2 = f.line(p13, vec2)
e_top = f.edge_curve(v13, v03, ln2)

vec3 = f.vector(d_my, 3.0)
ln3 = f.line(p03, vec3)
e_left = f.edge_curve(v03, v0, ln3)

loopA = f.edge_loop([
    f.oriented_edge(edgeE, True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_left, True),
])
orig = p0
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plcA = f.axis2_placement_3d(orig, zdir, xdir)
planeA = f.plane(plcA)
fobA = f.face_outer_bound(loopA)
faceA = f.advanced_face([fobA], planeA)

# ── Face B: tiny (5e-5mm) sliver candidate edge, within-tolerance gap ───────
# Face B's OTHER two edges (apex 2mm away) are ordinary-sized, so the whole
# face's free-boundary wire is NOT itself negligible-extent (avoiding the
# unrelated sew-degenerate-free-wire-collapse mechanism firing on the whole
# face — confirmed live and fixed during authoring: an all-tiny triangle
# got entirely flagged degenerate instead of exercising the length-floor
# rejection on just the candidate edge).
SLIVER_LEN = 5.0e-5
GAP = 1.0e-4
qs0 = f.cartesian_point((4.0, GAP, 0.0))
qs1 = f.cartesian_point((4.0 + SLIVER_LEN, GAP, 0.0))
qs2 = f.cartesian_point((4.0 + SLIVER_LEN / 2.0, GAP + 2.0, 0.0))
vqs0 = f.vertex_point(qs0)
vqs1 = f.vertex_point(qs1)
vqs2 = f.vertex_point(qs2)

# Sliver candidate edge (parallel to E, near-coincident).
vecS0 = f.vector(d_px, SLIVER_LEN)
lnS0 = f.line(qs0, vecS0)
edgeSliver = f.edge_curve(vqs0, vqs1, lnS0)

# Two more small edges to close a real triangular face (irrelevant to the
# mechanism, just legal topology).
import math
_len1 = math.hypot(SLIVER_LEN / 2.0, 0.002)
d_s1 = f.direction((-(SLIVER_LEN / 2.0) / _len1, 0.002 / _len1, 0.0))
vecS1 = f.vector(d_s1, _len1)
lnS1 = f.line(qs1, vecS1)
edgeS1 = f.edge_curve(vqs1, vqs2, lnS1)

d_s2 = f.direction(((SLIVER_LEN / 2.0) / _len1, -0.002 / _len1, 0.0))
vecS2 = f.vector(d_s2, _len1)
lnS2 = f.line(qs2, vecS2)
edgeS2 = f.edge_curve(vqs2, vqs0, lnS2)

loopB = f.edge_loop([
    f.oriented_edge(edgeSliver, True),
    f.oriented_edge(edgeS1, True),
    f.oriented_edge(edgeS2, True),
])
plcB = f.axis2_placement_3d(qs0, zdir, xdir)
planeB = f.plane(plcB)
fobB = f.face_outer_bound(loopB)
faceB = f.advanced_face([fobB], planeB)

# ── Both faces in one OPEN_SHELL ────────────────────────────────────────────
shell = f.open_shell([faceA, faceB], name="tsh243_sliver_reject_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
