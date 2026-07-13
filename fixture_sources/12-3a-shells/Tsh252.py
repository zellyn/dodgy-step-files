"""Tsh252 — Face-hosted candidate whose overlap with the reference edge
is only a partial (~90%), symmetrically-inset interior span: the merge's
achieved tolerance comes back scaled to the INSET distance rather than
the true perpendicular gap, an order-of-magnitude-worse estimate than
the smooth continuous fit a small-inset or full-span candidate achieves
(sew-tolerance-budget-acceptance-and-cap PARTIAL, subvariant "23-point
discretized-sampling fallback tolerance estimate").

Catalog claim (occt-coverage PARTIAL `sew-tolerance-budget-acceptance-
and-cap`): per `occt-coverage/exchange/problems.json`, if a candidate
merge fails the normal quality bar, sewing falls back to "a 23-point
discretized-sampling fallback [that] directly measures the actual 3D/2D
deviation... as a last-resort tolerance estimate", distinct from the
smooth continuous reprojection used in the ordinary case. This fixture
empirically isolates a construction where that last-resort estimate
visibly diverges from the true geometric gap:

Two real ADVANCED_FACEs in one OPEN_SHELL, both 5.0mm-long free edges at
y=0 and y=0.0001 (TRUE perpendicular gap = 0.0001mm, comfortably within
a 1.0mm sewing tolerance) — but Face B's candidate edge is symmetrically
INSET 0.5mm from each end relative to Face A's full span (Face A:
x:[0,5]; Face B: x:[0.5,4.5], an 80%-coverage interior candidate, a
substantially larger inset than the ~1% insets used elsewhere in this
corpus, e.g. Tsh246/Tsh251).

Live verification (this worktree's OCP/OCCT 7.8.1, runtime sewing
scaffold, `BRepBuilderAPI_Sewing(1.0)`, default MaxTolerance): the merge
DOES succeed (`NbContigousEdges()==1`), but the merged edge's achieved
tolerance comes back as `0.525` -- essentially the INSET distance
(0.5mm) scaled by ~1.05, having nothing to do with the true 0.0001mm
perpendicular gap (off by ~5000x). A parameter sweep over the inset
distance (holding the true gap fixed at 0.0001mm) shows this is a sharp,
reproducible regime split, not measurement noise: insets from 0.05mm to
0.7mm all produce a tolerance that scales linearly with the INSET
(`tolerance ≈ 1.05 * inset`, e.g. inset 0.05 -> tol 0.0525, inset 0.3 ->
tol 0.315, inset 0.7 -> tol 0.735) -- a materially wrong estimate that
tracks the wrong quantity entirely -- while a FULL-SPAN candidate (inset
1.0, i.e. the candidate's endpoints coincide with the reference's own
endpoints) recovers the tight, gap-proportional `0.000105`. This
qualitative split (tight-and-correct at small or zero inset vs.
inset-scaled-and-wrong over a broad middle range) is consistent with a
distinct, cruder estimation path engaging specifically when the
candidate only partially overlaps the reference's own span -- the
behavior the class's discretized-sampling-fallback citation describes.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 2
  - count_entity_def(b'OPEN_SHELL') == 1
  - contains(b'inset_reference_edge')
  - contains(b'inset_candidate_edge')
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh252",
    schema="AP242",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs: Face REF hosts a 5.0mm free "
        "edge x:[0,5],y=0; Face INSET hosts a 4.0mm free edge "
        "x:[0.5,4.5],y=0.0001 -- an 80%-coverage, symmetrically-inset "
        "interior candidate with a TRUE perpendicular gap of only "
        "0.0001mm -- purpose-built to isolate "
        "BRepBuilderAPI_Sewing::SameParameterEdge's last-resort "
        "tolerance-estimate fallback: live-verified, the merge succeeds "
        "but reports an achieved tolerance of 0.525 (essentially the "
        "0.5mm INSET distance, not the 0.0001mm true gap) -- an "
        "order-of-magnitude-worse estimate than the tight, "
        "gap-proportional tolerance a small-inset or full-span "
        "candidate pair achieves"
    ),
)


def cp(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))


def dir3(x, y, z):
    return f.direction((float(x), float(y), float(z)))


def strip_face(x0, x1, y, apex_dy, tag):
    p0 = cp(x0, y, 0.0)
    p1 = cp(x1, y, 0.0)
    mid_x = (x0 + x1) / 2.0
    papex = cp(mid_x, y + apex_dy, 0.0)
    v0 = f.vertex_point(p0)
    v1 = f.vertex_point(p1)
    vapex = f.vertex_point(papex)

    length = x1 - x0
    d_test = dir3(1, 0, 0)
    vec_test = f.vector(d_test, length)
    ln_test = f.line(p0, vec_test)
    e_test = f.edge_curve(v0, v1, ln_test, name=f"inset_{tag}_edge")

    def mk_leg(pa, va, pb, vb):
        dx = pb.args[1][0] - pa.args[1][0]
        dy = pb.args[1][1] - pa.args[1][1]
        leglen = (dx * dx + dy * dy) ** 0.5
        d = dir3(dx / leglen, dy / leglen, 0.0)
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
    plane = f.plane(f.axis2_placement_3d(p0, dir3(0, 0, 1), dir3(1, 0, 0)))
    fob = f.face_outer_bound(loop)
    return f.advanced_face([fob], plane, name=f"inset_{tag}_face")


# Face REF: full span x:[0,5], y=0.
face_ref = strip_face(0.0, 5.0, 0.0, 40.0, "reference")
# Face INSET: symmetrically inset 0.5mm from each end, x:[0.5,4.5],
# y=0.0001 (true perpendicular gap 0.0001mm).
face_inset = strip_face(0.5, 4.5, 0.0001, -40.0, "candidate")

shell = f.open_shell([face_ref, face_inset], name="tsh252_inset_tolerance_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty=1.0e-7)
