"""Tsh246 — Two face-hosted candidate edges of unequal length within merge
tolerance: the LONGER edge must become the parametrization reference
(sew-longest-edge-reference-selection PARTIAL).

Catalog claim (occt-coverage PARTIAL `sew-longest-edge-reference-selection`):
per `occt-coverage/exchange/problems.json`, the sole existing fixture
(N148) presents a genuinely unequal-length near-coincident edge pair
(5.0 vs 4.9mm, 0.1mm apart) but is a faceless GEOMETRIC_CURVE_SET
(floating-mode-only structure, authored for a different mechanism,
EvaluateDistances projection) — every FACE-based merge fixture in the
corpus (Twi037, Tfa019, Tfa020, Tsh203, M045) pairs EQUAL-length edges,
leaving `BRepBuilderAPI_Sewing::SameParameterEdge`'s length-based
reference choice (`BRepBuilderAPI_Sewing.cxx:573-591`: on the first
top-level call, computes both candidate edges' 3D curve length via
`GCPnts_AbscissaPoint` and assigns the LONGER one to `edge1`, the
retained parametrization reference) unobservable. This fixture rebuilds
N148's length pattern face-hosted:

  - Face LONG hosts a 5.0mm edge, x:[0,5], y=0.
  - Face SHORT hosts a 4.9mm edge, x:[0.05,4.95], y=1e-4 (well within a
    1.0mm sewing tolerance; SHORT's endpoints are both interior to LONG's
    parametric span, distinct from Tsh243's rejected-as-sliver pattern
    since 4.9mm comfortably exceeds the myMinTolerance floor).

Live verification (this worktree's OCP/OCCT 7.8.1, runtime sewing
scaffold, tolerance=1.0): after sewing, the resulting shared edge's
BRep_Tool::Range is exactly (0.0, 5.0) — LONG's own original parameter
range — not SHORT's (0.0, 4.9), confirming LONG's parametrization
survived as the merge reference. (The two candidate edges' VERTEX
endpoints do get tolerance-averaged to (0.025, 4.975), a distinct,
separately-cataloged mechanism — sew-edge-endpoint-tolerance-
reconciliation — not this class; the load-bearing assertion here is the
retained parameter RANGE/curve identity, which the vertex averaging does
not disturb.)

Mechanism IS the shell topology: both edges are real ADVANCED_FACE
boundary edges in one OPEN_SHELL, not a faceless GEOMETRIC_CURVE_SET.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 2
  - count_entity_def(b'OPEN_SHELL') == 1
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh246",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs: Face LONG hosts a 5.0mm free "
        "edge x:[0,5],y=0; Face SHORT hosts a 4.9mm free edge "
        "x:[0.05,4.95],y=1e-4 (within-tolerance gap, endpoints strictly "
        "interior to LONG's span) — purpose-built unequal-length "
        "face-hosted merge candidate pair (N148's length pattern rebuilt "
        "on real faces, not a GEOMETRIC_CURVE_SET) exercising "
        "BRepBuilderAPI_Sewing::SameParameterEdge's longer-edge-becomes-"
        "reference selection"
    ),
)


def strip_face(x0, x1, y, apex_dx, apex_dy):
    p0 = f.cartesian_point((x0, y, 0.0))
    p1 = f.cartesian_point((x1, y, 0.0))
    papex = f.cartesian_point(((x0 + x1) / 2.0 + apex_dx, y + apex_dy, 0.0))
    v0 = f.vertex_point(p0)
    v1 = f.vertex_point(p1)
    vapex = f.vertex_point(papex)

    length = x1 - x0
    d_test = f.direction((1.0, 0.0, 0.0))
    vec_test = f.vector(d_test, length)
    ln_test = f.line(p0, vec_test)
    e_test = f.edge_curve(v0, v1, ln_test)

    def mk_leg(pa, va, pb, vb):
        dx = pb.args[1][0] - pa.args[1][0]
        dy = pb.args[1][1] - pa.args[1][1]
        leglen = (dx * dx + dy * dy) ** 0.5
        d = f.direction((dx / leglen, dy / leglen, 0.0))
        vec = f.vector(d, leglen)
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


# Apex offsets deliberately very different between the two faces (LONG's
# apex far in +Y, SHORT's apex far in -Y) so the non-test leg edges never
# themselves become spurious gap-merge candidates for each other.
face_long, edge_long = strip_face(0.0, 5.0, 0.0, 0.0, 40.0)
face_short, edge_short = strip_face(0.05, 4.95, 1.0e-4, 0.0, -40.0)

shell = f.open_shell([face_long, face_short], name="tsh246_longest_edge_ref_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
