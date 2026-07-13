"""Tsh251 — Face-hosted gap candidate whose achieved merge tolerance
exceeds a caller-declared MaxTolerance cap: the merge is nullified
rather than returned with an out-of-spec tolerance
(sew-tolerance-budget-acceptance-and-cap PARTIAL, subvariant "hard
MaxTolerance cap with nullify-on-exceed").

Catalog claim (occt-coverage PARTIAL `sew-tolerance-budget-acceptance-
and-cap`): per `occt-coverage/exchange/problems.json`, the class's
base accept-and-tighten behavior is already genuinely exercised by the
existing gap fixtures, but none of its 3 named subvariants (swapped-
reference retry, discretized-sampling fallback, hard MaxTolerance cap)
had live confirmation — the N052/N145/N151/N153 wave was read and found
weak: a faceless GEOMETRIC_CURVE_SET whose decisive tolerance/cap values
exist only in comments, requiring a harness call a passive loader cannot
trigger. This fixture builds a genuine face-hosted candidate pair AND
demonstrates the cap subvariant via the corpus's established "runtime
sewing scaffold" convention (see Tsh243-247 precedent: `BRepBuilderAPI_
Sewing` is not automatically invoked by the default STEP read path; the
merge mechanism is exercised by explicitly running the sewing operator
against the loaded shape at verification time):

Two real ADVANCED_FACEs in one OPEN_SHELL: Face A hosts a 5.0mm free
edge x:[0,5], y=0; Face B hosts a 5.0mm free edge x:[0,5], y=0.05 (a
genuine 0.05mm gap on real face boundaries, mirroring N153's tolerance
pattern but rebuilt as its own independent fixture).

Live verification (this worktree's OCP/OCCT 7.8.1, runtime sewing
scaffold): with the operator's own tolerance/MaxTolerance left at their
shared default (both =1.0, the same value passed to the constructor),
the merge succeeds — `NbContigousEdges()==1`, the merged edge's achieved
tolerance is `0.0525` (gap-proportional, `BRep_Tool::SameParameter==
True`). With the SAME geometry but `SetMaxTolerance(0.01)` explicitly
declared BEFORE `Perform()` (0.01 < the 0.0525 tolerance the merge would
otherwise achieve) the merge is instead REJECTED entirely —
`NbContigousEdges()==0`, `NbFreeEdges()==6` (both original edges remain
unmerged, at their default 1e-7 tolerance) — a directly observable,
reproducible before/after contrast confirming the hard cap nullifies the
merge outright rather than returning an edge with an out-of-spec
tolerance.

Byte assertions:
  - count_entity_def(b'ADVANCED_FACE') == 2
  - count_entity_def(b'OPEN_SHELL') == 1
  - contains(b'cap_candidate_edge_a')
  - contains(b'cap_candidate_edge_b')
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh251",
    schema="AP242",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs: Face A hosts a 5.0mm free "
        "edge x:[0,5],y=0; Face B hosts a 5.0mm free edge x:[0,5],y=0.05 "
        "-- a genuine 0.05mm within-tolerance gap on real face "
        "boundaries -- purpose-built face-hosted candidate pair (N153's "
        "tolerance pattern rebuilt as an independent fixture) for "
        "exercising BRepBuilderAPI_Sewing::SameParameterEdge's hard "
        "MaxTolerance cap: with MaxTolerance left at the operator's own "
        "default the merge succeeds at tolerance 0.0525; with "
        "MaxTolerance explicitly set below 0.0525 the same candidate "
        "pair is instead nullified and left unmerged"
    ),
)


def cp(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))


def dir3(x, y, z):
    return f.direction((float(x), float(y), float(z)))


def strip_face(y, apex_dy, tag):
    p0 = cp(0.0, y, 0.0)
    p1 = cp(5.0, y, 0.0)
    papex = cp(2.5, y + apex_dy, 0.0)
    v0 = f.vertex_point(p0)
    v1 = f.vertex_point(p1)
    vapex = f.vertex_point(papex)

    d_test = dir3(1, 0, 0)
    vec_test = f.vector(d_test, 5.0)
    ln_test = f.line(p0, vec_test)
    e_test = f.edge_curve(v0, v1, ln_test, name=f"cap_candidate_edge_{tag}")

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
    return f.advanced_face([fob], plane, name=f"cap_face_{tag}")


# Apex offsets deliberately far apart (+40 / -40) so the non-test leg
# edges never themselves become spurious gap-merge candidates.
face_a = strip_face(0.0, 40.0, "a")
face_b = strip_face(0.05, -40.0, "b")

shell = f.open_shell([face_a, face_b], name="tsh251_tolerance_cap_shell")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty=1.0e-7)
