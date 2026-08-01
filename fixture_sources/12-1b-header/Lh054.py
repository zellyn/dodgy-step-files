"""Lh054 — I-DEAS closing shell that OCCT actually merges: the closing shell's
edges are DISTINCT EDGE_CURVE entities carrying the SAME names as the open
shell's, which is the only encoding that registers them as non-manifold
(stp-ideas-shell-closing, PARTIAL: "an observable merge is required for
COVERED and none of the tested transfer configurations produce one").

Catalog claim: STEPControl_ActorRead recognizes the I-DEAS pattern -- one
"main" OPEN_SHELL plus extra shells made entirely of non-manifold (shared)
edges that exist only to close it -- finds those candidate closing shells
(`computeIDEASClosings`, STEPControl_ActorRead.cxx:2064-2086), merges their
faces in, verifies closure via BRepCheck_Shell and prunes back any closing
face not needed for closure (`closeIDEASShell`, :1997-2055).

Lh031 supplies only the header trigger (no shell topology at all). Lh053
supplies real open+closing shell topology but its closing shell reuses the
SAME `EDGE_CURVE` entities as the main shell -- and that, verified live
here, is exactly why no merge was ever observed for it.

Why entity sharing cannot work, read from the OCCT source
(bd2a789f15235755ce4d1a3b07379a2e062fdc2e):
`StepToTopoDS_NMTool::IsPureNMShell` (StepToTopoDS_NMTool.cxx:183-194)
requires EVERY edge of a candidate closing shell to have been passed to
`RegisterNMEdge`. `RegisterNMEdge` has exactly ONE call site:
StepToTopoDS_TranslateEdge.cxx:244, inside the I-DEAS branch at :237-249,
which is reached only when the EDGE_CURVE's own NAME is non-empty and a
DIFFERENT, already-translated EDGE_CURVE was bound under that same name
(:336-337). If the second shell reuses the same EDGE_CURVE *entity*, the
two earlier early-returns fire first -- `aTool.IsBound(EC)` at :208 and
`NMTool.IsBound(EC)` at :223 -- and `RegisterNMEdge` is never called at
all. Entity sharing therefore produces a closing shell that is adjacent
but not "pure non-manifold", so `IsSuspectedAsClosing` (:153-158) rejects
it and `computeIDEASClosings` returns an empty map.

Mechanism: a unit cube, consistently outward-oriented. Its bottom and four
sides form `main_open_shell` (5 faces, genuinely open -- no lid). The lid
is `closing_shell` (1 face). The lid's four boundary edges are four NEW
EDGE_CURVE entities whose names -- 'e_lid_1' .. 'e_lid_4' -- are byte-equal
to the four top edges already used by the side faces. That is the real
I-DEAS authoring shape: separate edge records per shell, matched by name.

A SECOND, unrelated representation item ('second_item_model', one open
square face off to the side) is required as well: when a shape
representation yields exactly one shape, the reader binds that per-item
shape directly (STEPControl_ActorRead.cxx:1015-1024) and silently
discards the compound that the I-DEAS closing and solid-reconstruction
passes actually wrote into. With one item the merge runs but is invisible.
(Same two-item requirement Tsh258 documents for shell-to-solid promotion.)

Byte assertions:
  - contains(b'I-DEAS')
  - contains(b'main_open_shell')
  - contains(b'closing_shell')
  - count_entity_def(b'OPEN_SHELL') == 3
  - count_entity_def(b'EDGE_CURVE') == 20

Tier-3 assertions:
  - shape_null == False
  - n_faces_total == 7

live oracle (2026-07-31, this worktree, OCP/OCCT 7.8.1): see the catalog
entry's Expected-validation line. Under this corpus's default oracle
settings the file reads verbatim -- 7 faces, 3 shells, 0 solids, 20 unique
edges, brepcheck valid -- because the whole I-DEAS pipeline is gated behind
two opt-in reader parameters.

Driving `read.step.nonmanifold=1` AND `read.step.ideas=1` (both required;
either alone leaves the result unchanged) via a StepData_ConfParameters
passed to ReadFile, the merge is DIRECTLY OBSERVED: 1 SOLID appears,
unique-edge count drops 20 -> 16 (the lid's four name-matched edges are
resolved to the main shell's own edges), and the shell count drops 3 -> 2
(the merged, now-closed cube shell inside the solid, plus the second item's
untouched open shell). brepcheck stays valid.

Perturbation control (byte-level A/B): repointing the lid face's four
ORIENTED_EDGEs at the main shell's own EDGE_CURVE entities -- four
reference numbers changed, Lh053's encoding, nothing else touched --
produces 0 solids and 3 shells under those same two enabled parameters
(vs. this fixture's 1 solid and 2 shells). The merge is caused
specifically by the distinct-entities-same-name encoding, which is what
the RegisterNMEdge call site requires.

NOTE on reader configuration: setting these parameters through
`Interface_Static` alone does NOT reach the transfer in this OCP build --
they must be carried in a `StepData_ConfParameters` handed to
`ReadFile(path, params)`. Prior investigations of this class that saw "no
merge even with the flags on" appear to have hit that plumbing gap.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh054",
    defect=(
        "FILE_NAME.preprocessor_version 'I-DEAS Master Series 11' engages "
        "the preprocessor-substring auto-detect, PLUS the I-DEAS closing "
        "topology in its ONLY workable encoding: a unit cube whose bottom "
        "and 4 sides form 'main_open_shell' (5 faces, genuinely open) and "
        "whose lid forms 'closing_shell' (1 face) built on FOUR NEW "
        "EDGE_CURVE entities whose names 'e_lid_1'..'e_lid_4' duplicate "
        "the main shell's own top-edge names -- distinct records matched "
        "by name, the real I-DEAS authoring shape, and the only encoding "
        "that reaches the non-manifold-edge registration that the "
        "pure-non-manifold-shell test requires (reusing the SAME "
        "EDGE_CURVE entities, as Lh053 does, short-circuits earlier and "
        "registers nothing). A second unrelated representation item, "
        "'second_item_model', is present because a single-item "
        "representation makes the reader bind the pre-merge per-item shape "
        "and discard the merged compound. Both shells ARE items of the "
        "shape representation via SHELL_BASED_SURFACE_MODEL; never orphaned"
    ),
)

# ── Unit cube, consistently outward-oriented ──────────────────────────────
PTS = [(0., 0., 0.), (1., 0., 0.), (1., 1., 0.), (0., 1., 0.),
       (0., 0., 1.), (1., 0., 1.), (1., 1., 1.), (0., 1., 1.)]
pts = [f.cartesian_point(p) for p in PTS]
vts = [f.vertex_point(p) for p in pts]


def edge(name, a, b, d):
    ln = f.line(pts[a], f.vector(f.direction(d), 1.0))
    return f.edge_curve(vts[a], vts[b], ln, name=name)


e_bot = [
    edge("e_bot_1", 0, 1, (1., 0., 0.)),
    edge("e_bot_2", 1, 2, (0., 1., 0.)),
    edge("e_bot_3", 2, 3, (-1., 0., 0.)),
    edge("e_bot_4", 3, 0, (0., -1., 0.)),
]
e_vert = [
    edge("e_vert_1", 0, 4, (0., 0., 1.)),
    edge("e_vert_2", 1, 5, (0., 0., 1.)),
    edge("e_vert_3", 2, 6, (0., 0., 1.)),
    edge("e_vert_4", 3, 7, (0., 0., 1.)),
]
# Top edges as used by the SIDE faces (main shell).
e_lid_main = [
    edge("e_lid_1", 4, 5, (1., 0., 0.)),
    edge("e_lid_2", 5, 6, (0., 1., 0.)),
    edge("e_lid_3", 6, 7, (-1., 0., 0.)),
    edge("e_lid_4", 7, 4, (0., -1., 0.)),
]


def plane_at(pt_index, axis, ref):
    return f.plane(f.axis2_placement_3d(
        pts[pt_index], f.direction(axis), f.direction(ref)))


def face_of(name, surf, oriented):
    loop = f.edge_loop([f.oriented_edge(e, fwd) for e, fwd in oriented])
    return f.advanced_face([f.face_outer_bound(loop)], surf, name=name)


f_bottom = face_of("bottom", plane_at(0, (0., 0., -1.), (1., 0., 0.)),
                   [(e_bot[3], False), (e_bot[2], False),
                    (e_bot[1], False), (e_bot[0], False)])
f_front = face_of("front", plane_at(0, (0., -1., 0.), (1., 0., 0.)),
                  [(e_bot[0], True), (e_vert[1], True),
                   (e_lid_main[0], False), (e_vert[0], False)])
f_right = face_of("right", plane_at(1, (1., 0., 0.), (0., 1., 0.)),
                  [(e_bot[1], True), (e_vert[2], True),
                   (e_lid_main[1], False), (e_vert[1], False)])
f_back = face_of("back", plane_at(2, (0., 1., 0.), (-1., 0., 0.)),
                 [(e_bot[2], True), (e_vert[3], True),
                  (e_lid_main[2], False), (e_vert[2], False)])
f_left = face_of("left", plane_at(0, (-1., 0., 0.), (0., -1., 0.)),
                 [(e_bot[3], True), (e_vert[0], True),
                  (e_lid_main[3], False), (e_vert[3], False)])

main_shell = f.open_shell([f_bottom, f_front, f_right, f_back, f_left],
                          name="main_open_shell")

# ── THE DEFECT/PATTERN: the lid's four edges are NEW EDGE_CURVE entities
#    carrying the SAME names as the main shell's top edges. ───────────────
e_lid_closing = [
    edge("e_lid_1", 4, 5, (1., 0., 0.)),
    edge("e_lid_2", 5, 6, (0., 1., 0.)),
    edge("e_lid_3", 6, 7, (-1., 0., 0.)),
    edge("e_lid_4", 7, 4, (0., -1., 0.)),
]
f_top = face_of("top_closing", plane_at(4, (0., 0., 1.), (1., 0., 0.)),
                [(e, True) for e in e_lid_closing])
closing_shell = f.open_shell([f_top], name="closing_shell")

sbsm = f.shell_based_surface_model([main_shell, closing_shell],
                                   name="ideas_shells")

# ── Second, unrelated representation item: a single open square face.
#    Required so the representation yields TWO shapes -- a one-shape
#    representation makes the reader bind the pre-merge per-item shape
#    and discard the merged compound entirely. ─────────────────────────────
spts = [f.cartesian_point(p) for p in
        [(5., 0., 0.), (6., 0., 0.), (6., 1., 0.), (5., 1., 0.)]]
svts = [f.vertex_point(p) for p in spts]


def sedge(name, a, b, d):
    ln = f.line(spts[a], f.vector(f.direction(d), 1.0))
    return f.edge_curve(svts[a], svts[b], ln, name=name)


s_edges = [
    sedge("second_item_e1", 0, 1, (1., 0., 0.)),
    sedge("second_item_e2", 1, 2, (0., 1., 0.)),
    sedge("second_item_e3", 2, 3, (-1., 0., 0.)),
    sedge("second_item_e4", 3, 0, (0., -1., 0.)),
]
s_plane = f.plane(f.axis2_placement_3d(
    spts[0], f.direction((0., 0., 1.)), f.direction((1., 0., 0.))))
s_loop = f.edge_loop([f.oriented_edge(e, True) for e in s_edges])
s_face = f.advanced_face([f.face_outer_bound(s_loop)], s_plane,
                         name="second_item_face")
s_shell = f.open_shell([s_face], name="second_item_shell")
sbsm2 = f.shell_based_surface_model([s_shell], name="second_item_model")

f.add_product_chain([sbsm, sbsm2])

# ── The I-DEAS auto-detect gate: FILE_NAME.preprocessor_version must
#    contain the substring "I-DEAS" (STEPControl_ActorRead.cxx:316-334). ──
_base_render = f.render


def _render_with_ideas_header() -> str:
    text = _base_render()
    assert "'cad-research-suite','',''" in text
    return text.replace("'cad-research-suite','',''",
                        "'I-DEAS Master Series 11','',''")


f.render = _render_with_ideas_header  # type: ignore[method-assign]
