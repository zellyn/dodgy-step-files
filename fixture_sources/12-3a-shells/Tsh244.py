"""Tsh244 — Within-tolerance gap but sampled-point coverage below ~50%:
rejected as insufficient overlap evidence, not merged
(sew-free-edge-gap-merge PARTIAL, missing subvariant (b) of 2).

Catalog claim (occt-coverage PARTIAL `sew-free-edge-gap-merge`): the class's
second named subvariant, distinct from Tsh243's min-length-floor rejection.
`BRepBuilderAPI_Sewing::EvaluateDistances` (`BRepBuilderAPI_Sewing.cxx:1053
-1247`) discretizes both curves at 8 points each and first tries a cheap
"betweenness" test (how many of the candidate's 8 sampled points fall
between the reference curve's two endpoints along its direction); when
fewer than half (`nbFound < npt*0.5`) qualify, it falls back to projecting
all 8 candidate points onto the reference's BOUNDED parameter range
(`ProjectPointsOnCurve(..., isConsiderEnds=False)`). Points whose true
position lies far outside the reference's actual span get clamped to the
nearest segment endpoint for projection purposes, which inflates the
recorded distance for those points; the final `dist` fed back to
`FindCandidates` is the MAX over all sampled distances. When only a small
fraction of the candidate curve actually overlaps the reference's span,
most of the 8 sample points sit far past the reference's own endpoint,
driving that max distance well past `myTolerance` — `FindCandidates`
(`BRepBuilderAPI_Sewing.cxx:1502`, `aMaxDist <= myTolerance`) then
rejects the pairing outright, even though the CLOSEST points (in the
genuinely-overlapping 10% region) sit well within tolerance.

Two faces, one OPEN_SHELL:
  - Face A: 10mm-long reference free edge E = (0,0,0)-(10,0,0).
  - Face B: a 10mm-long candidate edge C = (9,1e-4,0)-(19,1e-4,0) — a
    genuine within-tolerance PERPENDICULAR gap (1e-4mm) along its full
    length, but only x:[9,10] (10% of C's own extent, well below the
    ~50% coverage threshold) actually falls within E's own parametric
    span [0,10]. The remaining 90% of C's sample points, when clamped to
    E's nearest endpoint (x=10) for projection, sit up to ~9mm away —
    driving the sampled max-distance metric far past tolerance and
    rejecting the pairing, unlike Tsh243's short-but-fully-contained
    sliver (which instead fails the myMinTolerance span floor with every
    sample point genuinely close).

Mechanism IS the shell topology: both edges are real ADVANCED_FACE
boundary edges in one OPEN_SHELL, not orphaned scaffold entities.

Live verification: reader-default STEPControl_Reader does not itself
invoke BRepBuilderAPI_Sewing. The mechanism is demonstrated via a runtime
scaffold that explicitly constructs BRepBuilderAPI_Sewing(tolerance) over
the translated shape and calls Perform() — see catalog Notes field for
the live free-edge counts (confirms no contiguous pairing forms despite
the genuine partial overlap being within-tolerance).

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 2
  - count_entity_def(b'OPEN_SHELL') == 1
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh244",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs: Face A hosts a 10mm reference "
        "free edge E=(0,0,0)-(10,0,0); Face B hosts a 10mm candidate edge "
        "C=(9,1e-4,0)-(19,1e-4,0) — genuine within-tolerance perpendicular "
        "gap along its whole length, but only 10% of C's own extent "
        "(x:9-10) actually overlaps E's parametric span, well below the "
        "~50% sampled-point coverage BRepBuilderAPI_Sewing::EvaluateDistances "
        "requires before accepting the cheap betweenness test, forcing the "
        "endpoint-clamped fallback whose inflated max-distance rejects the "
        "pairing in FindCandidates despite the genuinely-overlapping region "
        "being well within tolerance"
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

# ── Face B: candidate edge C, only 10% parametric overlap with E ───────────
GAP = 1.0e-4
qc0 = f.cartesian_point((9.5, GAP, 0.0))
qc1 = f.cartesian_point((19.5, GAP, 0.0))
qc2 = f.cartesian_point((14.5, GAP + 2.0, 0.0))
vqc0 = f.vertex_point(qc0)
vqc1 = f.vertex_point(qc1)
vqc2 = f.vertex_point(qc2)

vecC = f.vector(d_px, 10.0)
lnC = f.line(qc0, vecC)
edgeC = f.edge_curve(vqc0, vqc1, lnC)

import math
_len1 = math.hypot(5.0, 2.0)
d_c1 = f.direction((-5.0 / _len1, 2.0 / _len1, 0.0))
vecC1 = f.vector(d_c1, _len1)
lnC1 = f.line(qc1, vecC1)
edgeC1 = f.edge_curve(vqc1, vqc2, lnC1)

d_c2 = f.direction((-5.0 / _len1, -2.0 / _len1, 0.0))
vecC2 = f.vector(d_c2, _len1)
lnC2 = f.line(qc2, vecC2)
edgeC2 = f.edge_curve(vqc2, vqc0, lnC2)

loopB = f.edge_loop([
    f.oriented_edge(edgeC, True),
    f.oriented_edge(edgeC1, True),
    f.oriented_edge(edgeC2, True),
])
plcB = f.axis2_placement_3d(qc0, zdir, xdir)
planeB = f.plane(plcB)
fobB = f.face_outer_bound(loopB)
faceB = f.advanced_face([fobB], planeB)

# ── Both faces in one OPEN_SHELL ────────────────────────────────────────────
shell = f.open_shell([faceA, faceB], name="tsh244_low_coverage_reject_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
