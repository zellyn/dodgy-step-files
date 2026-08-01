"""Bo031 — BREP_WITH_VOIDS whose second void shell translates to nothing at
all: the solid is still built from the outer shell and the surviving void
(stp-partial-assembly-continuation, PARTIAL, missing variant: "BREP_WITH_VOIDS
with a FAILING void shell (existing void fixtures Tsh015/Tsh067/Bo003 all
have translatable voids)").

Catalog claim: StepToTopoDS_Builder::Init(BrepWithVoids)
(StepToTopoDS_Builder.cxx:226-246) iterates the solid's voids and adds each
one that translated, warning about (rather than aborting on) any that did
not -- in deliberate contrast with the OUTER shell at :210-216, whose
failure is fatal to the whole solid. Bo001/Bo002 already demonstrate the
fatal-outer-shell half of that contrast; every existing void fixture
(Tsh015, Tsh067, Bo003) has voids that translate cleanly.

Mechanism: a 10x10x10 outer CLOSED_SHELL, a good 2x2x2 void, and a second
void, 'failing_void_shell', which is a CLOSED_SHELL holding exactly one
ADVANCED_FACE, 'failing_void_face', whose `face_geometry` is unset (`$`).
That face cannot be translated (no surface), so the second void's shell
comes back carrying zero faces while the solid is still assembled from the
outer shell and the good void. `$`-as-face_geometry is the same
null-surface pattern Xp008 uses for its already-covered
container-drops-a-failed-face subvariant, here applied one container level
up, inside a void of a BREP_WITH_VOIDS.

HONEST SCOPE NOTE -- what this fixture does NOT show. The literal
" A Void from BrepWithVoids not mapped to TopoDS" warning at :244 is
structurally UNREACHABLE from a Part-21 file in OCCT 7.8.1, for two
independent reasons read from the source
(bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
  1. `StepToTopoDS_TranslateShell::Init(ConnectedFaceSet)` sets
     `done = Standard_True` unconditionally for ANY non-null
     ConnectedFaceSet (StepToTopoDS_TranslateShell.cxx:104-107). Faces that
     fail are individually skipped with their own warning at :95-97, and a
     shell that ends up with zero faces is still reported as done. So
     `aTranShell.IsDone()` at :231 cannot be false for a void whose
     reference resolves -- which is exactly what this fixture confirms
     live.
  2. The only path that leaves `done` false is the `CFS.IsNull()` early
     return at :61-62 -- and that return does NOT reset `done`, so after
     the outer shell's successful Init at :209 the flag is stale-true
     anyway. Reaching it at all requires an unresolvable void reference,
     and that construction is process-fatal: a variant of this fixture
     whose second ORIENTED_CLOSED_SHELL points at a non-existent entity
     was built and run, and OCCT 7.8.1 exits with signal 11 (exit 139)
     during the read. It was discarded as CI-unsafe and is not shipped.
What IS demonstrated, live, is the class's actual claim for this container:
a void member that contributes no geometry does not abort the parent solid.

Byte assertions:
  - contains(b'failing_void_shell')
  - contains(b'failing_void_face')
  - contains(b'good_void_bot')
  - count_entity_def(b'ORIENTED_CLOSED_SHELL') == 2
  - contains(b'BREP_WITH_VOIDS')

Tier-3 assertions:
  - shape_null == False
  - n_faces_total == 12

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1): see the catalog
entry's Expected-validation line. Live-verified: the transfer check list
carries the FAIL " Surface has not been created" (the `$` face_geometry)
and the WARNING " a Face from Shell not mapped to TopoDS"
(StepToTopoDS_TranslateShell.cxx:96) -- and NOT " A Void from BrepWithVoids
not mapped to TopoDS", exactly as the unreachability analysis above
predicts. (A third, incidental warning, "Shell has incorrect flag
isClosed", is present in the control too and is not part of the claim.)
The transferred shape is still 1 SOLID carrying 3 shells (outer, good void,
and the now-empty failing void) with 12 faces -- the outer shell's 6 plus
the good void's 6, the failing void contributing none.

Perturbation control (byte-level A/B): giving 'failing_void_face' a real
PLANE instead of `$` -- one reference changed, nothing else -- makes both
" Surface has not been created" and " a Face from Shell not mapped to
TopoDS" disappear and raises the face count 12 -> 13. The solid count
stays 1 either way, which is the point: unlike a failed OUTER shell, a
void that contributes nothing does not sink the solid.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo031",
    defect=(
        "BREP_WITH_VOIDS with a valid 10x10x10 outer CLOSED_SHELL, a valid "
        "2x2x2 void, and a SECOND void 'failing_void_shell' -- a "
        "CLOSED_SHELL holding exactly one ADVANCED_FACE "
        "'failing_void_face' whose face_geometry is unset ($), so that face "
        "cannot be translated and the void contributes no geometry at all. "
        "The per-void continuation of the BREP_WITH_VOIDS loop IS the "
        "mechanism under test: the solid must still be assembled from the "
        "outer shell and the surviving void, in contrast with a failed "
        "OUTER shell which is fatal (Bo001/Bo002). Both voids ARE listed in "
        "the BREP_WITH_VOIDS voids attribute; never orphaned"
    ),
)


def box_shell(ox, oy, oz, s, tag):
    """Watertight CLOSED_SHELL box, consistently outward-oriented."""
    P = [(ox, oy, oz), (ox + s, oy, oz), (ox + s, oy + s, oz), (ox, oy + s, oz),
         (ox, oy, oz + s), (ox + s, oy, oz + s), (ox + s, oy + s, oz + s),
         (ox, oy + s, oz + s)]
    pts = [f.cartesian_point(p) for p in P]
    vts = [f.vertex_point(p) for p in pts]

    def ed(a, b, d):
        return f.edge_curve(vts[a], vts[b],
                            f.line(pts[a], f.vector(f.direction(d), s)))

    b1 = ed(0, 1, (1., 0., 0.)); b2 = ed(1, 2, (0., 1., 0.))
    b3 = ed(2, 3, (-1., 0., 0.)); b4 = ed(3, 0, (0., -1., 0.))
    v1 = ed(0, 4, (0., 0., 1.)); v2 = ed(1, 5, (0., 0., 1.))
    v3 = ed(2, 6, (0., 0., 1.)); v4 = ed(3, 7, (0., 0., 1.))
    t1 = ed(4, 5, (1., 0., 0.)); t2 = ed(5, 6, (0., 1., 0.))
    t3 = ed(6, 7, (-1., 0., 0.)); t4 = ed(7, 4, (0., -1., 0.))

    def pl(i, ax, ref):
        return f.plane(f.axis2_placement_3d(
            pts[i], f.direction(ax), f.direction(ref)))

    def fc(name, surf, oes):
        loop = f.edge_loop([f.oriented_edge(e, o) for e, o in oes])
        return f.advanced_face([f.face_outer_bound(loop)], surf, name=name)

    faces = [
        fc(tag + "_bot", pl(0, (0., 0., -1.), (1., 0., 0.)),
           [(b4, False), (b3, False), (b2, False), (b1, False)]),
        fc(tag + "_frt", pl(0, (0., -1., 0.), (1., 0., 0.)),
           [(b1, True), (v2, True), (t1, False), (v1, False)]),
        fc(tag + "_rgt", pl(1, (1., 0., 0.), (0., 1., 0.)),
           [(b2, True), (v3, True), (t2, False), (v2, False)]),
        fc(tag + "_bck", pl(2, (0., 1., 0.), (-1., 0., 0.)),
           [(b3, True), (v4, True), (t3, False), (v3, False)]),
        fc(tag + "_lft", pl(0, (-1., 0., 0.), (0., -1., 0.)),
           [(b4, True), (v1, True), (t4, False), (v4, False)]),
        fc(tag + "_top", pl(4, (0., 0., 1.), (1., 0., 0.)),
           [(t1, True), (t2, True), (t3, True), (t4, True)]),
    ]
    return f.closed_shell(faces, name=tag)


outer_shell = box_shell(-5., -5., -5., 10., "outer")
good_void = box_shell(-2., -2., -2., 2., "good_void")

# ── THE DEFECT: a void CLOSED_SHELL whose only face has NO surface ────────
fp = f.cartesian_point((1.0, 1.0, 1.0))
fv = f.vertex_point(fp)
fln = f.line(fp, f.vector(f.direction((1., 0., 0.)), 1.0))
fe = f.edge_curve(fv, fv, fln, name="failing_void_edge")
floop = f.edge_loop([f.oriented_edge(fe, True)])
ffb = f.face_outer_bound(floop)
failing_face = f._emit_raw(
    f"ADVANCED_FACE('failing_void_face',(#{ffb.eid}),$,.T.)"
)
failing_void = f._emit_raw(
    f"CLOSED_SHELL('failing_void_shell',(#{failing_face.eid}))"
)

# cfs_faces is DERIVE'd in ORIENTED_CLOSED_SHELL (redeclared from
# connected_face_set), so the Part-21 attribute list carries a `*`
# placeholder for it: (name, *, closed_shell_element, orientation).
ocs_good = f._emit_raw(f"ORIENTED_CLOSED_SHELL('',*,#{good_void.eid},.F.)")
ocs_bad = f._emit_raw(f"ORIENTED_CLOSED_SHELL('',*,#{failing_void.eid},.F.)")
bwv = f._emit_raw(
    f"BREP_WITH_VOIDS('bo031_body',#{outer_shell.eid},"
    f"(#{ocs_good.eid},#{ocs_bad.eid}))"
)
f.add_product_chain(bwv, mode="brep_shape")
