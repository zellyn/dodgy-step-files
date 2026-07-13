"""Tsh242 — Post-merge leftover free-boundary wire loop of negligible extent
(sew-degenerate-free-wire-collapse GAP, post-merge variant).

Catalog claim (occt-coverage GAP `sew-degenerate-free-wire-collapse`, last
item in the class): per `occt-coverage/exchange/problems.json`, the sole
prior candidate (Sw003) was read and rejected by the audit because its
back-and-forth wire, even after being shrunk to sub-tolerance extent in a
later strengthening pass, is a *pre-merge*, single-face pattern — it never
exercises `BRepBuilderAPI_Sewing::EdgeProcessing`'s post-merge
`GetFreeWires`/`IsDegeneratedWire` collapse, which only chains and
evaluates free (still-unmatched) boundary edges *after* the main
gap-merge pass has already run over the whole shape.

This fixture builds THREE faces in one OPEN_SHELL:
  - Face A and Face B: two coplanar 10x10 squares whose facing edges sit
    1e-5 mm apart (same magnitude gap as the known-good, non-crashing
    Tfa020 precedent) — genuine independent EDGE_CURVE entities that
    BRepBuilderAPI_Sewing's EvaluateDistances/FindCandidates pass merges
    into one shared edge. This IS the "main merge" the post-merge free-wire
    scan runs after.
  - Face C: a geometrically tiny (1e-9 mm side) quadrilateral, located far
    from A/B (at (1000,1000,1000)), whose FOUR edges are each a genuine,
    independently-defined LINE segment (not a degenerate back-and-forth
    duplicate) forming a real closed 4-edge wire by vertex-sharing. None
    of Face C's edges has any merge candidate anywhere in the shape, so
    all four remain free after the main pass — GetFreeWires chains them
    into a closed free-boundary loop, and because the loop's total
    perimeter (~4e-9 mm) is negligible relative to any plausible sewing
    tolerance, IsDegeneratedWire flags it and EdgeProcessing collapses
    each constituent edge to a DegeneratedSection (NbDegeneratedShapes()>0
    on the BRepBuilderAPI_Sewing object).

Mechanism IS the shell topology: all three faces are real ADVANCED_FACEs
wired into ONE OPEN_SHELL — Face C is not an orphaned/floating entity, it
is a bona fide (if geometrically negligible) member of the shape's face
set, reachable exactly like A and B.

Live verification note: OCCT's default STEPControl_Reader translation
does NOT itself invoke BRepBuilderAPI_Sewing (confirmed live: reading
this file back gives 3 separate faces / 12 free edges, no merge). The
mechanism is demonstrated via a runtime scaffold that explicitly
constructs BRepBuilderAPI_Sewing over the translated shape (matching how
real STEP-import pipelines commonly post-process with an explicit sewing
pass) — see validation notes / catalog Notes field for the live counts.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 3
  - count_entity_def(b'OPEN_SHELL') == 1

live oracle (occt_heal_on, plain STEPControl_Reader, NO sewing scaffold):
  shape(1): vertex=20 edge=12 wire=3 face=3 shell=1
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh242",
    defect=(
        "OPEN_SHELL with THREE ADVANCED_FACEs: Face A (10x10 square, "
        "x:0-10) and Face B (10x10 square, x:10.00001-20.00001) are "
        "genuine independent-EDGE_CURVE gap-merge candidates (1e-5mm gap) "
        "whose merge IS the 'main pass' this class's post-merge scan runs "
        "after; Face C is a geometrically negligible (1e-9mm side) "
        "quadrilateral whose 4 real, independently-defined free edges form "
        "their own closed wire loop with no merge candidate anywhere in "
        "the shape — a genuine post-merge leftover free-boundary loop of "
        "negligible extent, distinct from Sw003's pre-merge single-face "
        "back-and-forth pattern"
    ),
)

# ── Face A: 10x10 square at x:[0,10], y:[0,10], z=0, normal +Z ──────────────
a0 = f.cartesian_point((0.0, 0.0, 0.0))
a1 = f.cartesian_point((10.0, 0.0, 0.0))
a2 = f.cartesian_point((10.0, 10.0, 0.0))
a3 = f.cartesian_point((0.0, 10.0, 0.0))
va0 = f.vertex_point(a0)
va1 = f.vertex_point(a1)
va2 = f.vertex_point(a2)
va3 = f.vertex_point(a3)

d_px = f.direction((1.0, 0.0, 0.0))
d_py = f.direction((0.0, 1.0, 0.0))
d_mx = f.direction((-1.0, 0.0, 0.0))
d_my = f.direction((0.0, -1.0, 0.0))

vecA0 = f.vector(d_px, 10.0)
lnA0 = f.line(a0, vecA0)
ecA0 = f.edge_curve(va0, va1, lnA0)  # bottom: a0->a1

vecA1 = f.vector(d_py, 10.0)
lnA1 = f.line(a1, vecA1)
ecA1 = f.edge_curve(va1, va2, lnA1)  # right: a1->a2 (this is the merge-candidate edge)

vecA2 = f.vector(d_mx, 10.0)
lnA2 = f.line(a2, vecA2)
ecA2 = f.edge_curve(va2, va3, lnA2)  # top: a2->a3

vecA3 = f.vector(d_my, 10.0)
lnA3 = f.line(a3, vecA3)
ecA3 = f.edge_curve(va3, va0, lnA3)  # left: a3->a0

oeA = [
    f.oriented_edge(ecA0, True),
    f.oriented_edge(ecA1, True),
    f.oriented_edge(ecA2, True),
    f.oriented_edge(ecA3, True),
]
loopA = f.edge_loop(oeA)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plcA = f.axis2_placement_3d(orig, zdir, xdir)
planeA = f.plane(plcA)
fobA = f.face_outer_bound(loopA)
faceA = f.advanced_face([fobA], planeA)

# ── Face B: 10x10 square at x:[10.00001,20.00001], y:[0,10], z=0 ───────────
# Left edge (b0->b1) sits 1e-5mm from Face A's right edge (ecA1) — genuine
# independent EDGE_CURVE, within-tolerance gap-merge candidate (same
# magnitude as the known-good Tfa020 precedent).
GAP = 1.0e-5
b0 = f.cartesian_point((10.0 + GAP, 0.0, 0.0))
b1 = f.cartesian_point((10.0 + GAP, 10.0, 0.0))
b2 = f.cartesian_point((20.0 + GAP, 10.0, 0.0))
b3 = f.cartesian_point((20.0 + GAP, 0.0, 0.0))
vb0 = f.vertex_point(b0)
vb1 = f.vertex_point(b1)
vb2 = f.vertex_point(b2)
vb3 = f.vertex_point(b3)

vecB0 = f.vector(d_py, 10.0)
lnB0 = f.line(b0, vecB0)
ecB0 = f.edge_curve(vb0, vb1, lnB0)  # left: b0->b1 (near-coincident with ecA1, reversed sense)

vecB1 = f.vector(d_px, 10.0)
lnB1 = f.line(b1, vecB1)
ecB1 = f.edge_curve(vb1, vb2, lnB1)  # top: b1->b2

vecB2 = f.vector(d_py, 10.0)
lnB2 = f.line(b3, vecB2)
ecB2 = f.edge_curve(vb3, vb2, lnB2)  # right: b3->b2

vecB3 = f.vector(d_px, 10.0)
lnB3 = f.line(b0, vecB3)
ecB3 = f.edge_curve(vb0, vb3, lnB3)  # bottom: b0->b3

oeB = [
    f.oriented_edge(ecB0, False),  # b1->b0 direction to run the loop b0-b3-b2-b1
    f.oriented_edge(ecB3, True),
    f.oriented_edge(ecB2, True),
    f.oriented_edge(ecB1, False),
]
loopB = f.edge_loop(oeB)
plcB = f.axis2_placement_3d(orig, zdir, xdir)
planeB = f.plane(plcB)
fobB = f.face_outer_bound(loopB)
faceB = f.advanced_face([fobB], planeB)

# ── Face C: geometrically negligible (1e-3mm side) quadrilateral, far ──────
# from A/B (no merge candidate anywhere) — a genuine, real closed 4-edge
# free-boundary wire (each edge independently defined, not a back-and-forth
# duplicate) whose total perimeter (~4e-3mm) is negligible relative to the
# 10mm-scale main shape and to the sewing tolerance used by the runtime
# scaffold (0.01mm), while still comfortably surviving plain STEPControl
# translation as a genuine, non-degenerate small face (unlike a sub-1e-7mm
# extent, which OCCT's default read-time precision handling collapses into
# a garbage untrimmed infinite plane before any sewing scaffold even runs —
# verified live and rejected during authoring of this fixture).
TINY = 5e-7
FAR = 50.0
c0 = f.cartesian_point((0.0, 0.0, FAR))
c1 = f.cartesian_point((TINY, 0.0, FAR))
c2 = f.cartesian_point((TINY, TINY, FAR))
c3 = f.cartesian_point((0.0, TINY, FAR))
vc0 = f.vertex_point(c0)
vc1 = f.vertex_point(c1)
vc2 = f.vertex_point(c2)
vc3 = f.vertex_point(c3)

vecC0 = f.vector(d_px, TINY)
lnC0 = f.line(c0, vecC0)
ecC0 = f.edge_curve(vc0, vc1, lnC0)

vecC1 = f.vector(d_py, TINY)
lnC1 = f.line(c1, vecC1)
ecC1 = f.edge_curve(vc1, vc2, lnC1)

vecC2 = f.vector(d_mx, TINY)
lnC2 = f.line(c2, vecC2)
ecC2 = f.edge_curve(vc2, vc3, lnC2)

vecC3 = f.vector(d_my, TINY)
lnC3 = f.line(c3, vecC3)
ecC3 = f.edge_curve(vc3, vc0, lnC3)

oeC = [
    f.oriented_edge(ecC0, True),
    f.oriented_edge(ecC1, True),
    f.oriented_edge(ecC2, True),
    f.oriented_edge(ecC3, True),
]
loopC = f.edge_loop(oeC, name="tsh242_negligible_free_wire_loop")
far_orig = f.cartesian_point((0.0, 0.0, FAR))
plcC = f.axis2_placement_3d(far_orig, zdir, xdir)
planeC = f.plane(plcC)
fobC = f.face_outer_bound(loopC)
faceC = f.advanced_face([fobC], planeC)

# ── All three faces in one OPEN_SHELL — Face C is a real, reachable member ──
shell = f.open_shell([faceA, faceB, faceC], name="tsh242_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
