# Wave 8 packets B3+D3 — catalog entries pending merge into STEP_PROBLEM_CATALOG.md

**IMPORTANT — why this staging file exists**: direct `Edit` calls against
`STEP_PROBLEM_CATALOG.md` in this worktree were silently reverted every
time (confirmed via `git diff --stat` showing zero changes immediately
after a reported-successful edit, with no corresponding `git reset` event
in `git reflog` — the file's bytes on disk simply reappeared at the HEAD
value within the same tool-call round-trip, for edits ranging from one
short marker line up to multi-entry blocks). The exact same `Edit` tool,
same session, against `occt-coverage/exchange/problems.json` in this same
worktree persisted normally. Root cause not established (no `.gitattributes`,
no active git hooks, no LFS filter found) — likely some cross-worktree
protection on this single large (5.1MB) shared source-of-truth file, given
`git worktree list` shows a few dozen concurrent wave-8 packet worktrees
that would otherwise constantly stomp on each other's edits to the same
file. Fixture `.py`/`.stp` files and `occt-coverage/*/problems.json` edits
in this worktree DID persist normally and are committed
(`90bce4f5` and the problems.json commit that follows this one).

The 11 catalog entries below are complete, live-verified, and ready to be
appended to `STEP_PROBLEM_CATALOG.md` at the insertion points noted, by
whatever process ultimately has write access to that file (the standard
per-wave adjudication/merge step this repo already uses, per e.g. `Wave-4
adjudication: apply WAVE4_VERIFY.md Part-3 verdicts to occt-coverage`
in `git log`). After inserting, re-run `python -m
step_corpus._build_catalog_json` from `validation/` to regenerate
`STEP_PROBLEM_CATALOG.json`.

Insertion points (verified against this worktree's current
`STEP_PROBLEM_CATALOG.md`, which matches upstream `main` at commit
`2e2bbd10`):
- Twi299–Twi305: insert immediately after the `### Twi298` entry ends
  (line ~46973+), before `### Tsh248` begins (line ~46992).
- Gp190–Gp192: insert immediately after the `### Gp189` entry ends
  (line ~31656+), before `### A105` begins (line ~31677).
- Ad137: insert immediately after the `### Ad136` entry ends
  (line ~46439+), before `### Twi282` begins (line ~46452).

---

### Twi299 — Whole-circle edge whose VERTEX_POINT sits at the circle's own center (no unique nearest point for projection)
- **Category**: §12.3b wire-loop (sub-class: `stp-makeedge-validity-fallback`, PARTIAL, missing subvariant "point projection onto the 3D curve fails at all")
- **Sources**: occt-coverage `exchange/problems.json` `stp-makeedge-validity-fallback` (`StepToTopoDS_TranslateEdge::DecodeMakeEdgeError`, `StepToTopoDS_TranslateEdge.cxx:70-131`; `MakeFromCurve3D` fallback force-build, `:483-489`). Sibling of Twi086/Bo030/Gs029 (already-covered subvariants) and Bo030 specifically (per-vertex tolerance-underflow evidentiary pattern reused here).
- **Description**: Building a proper OCCT edge from the translated 3D curve, its vertices, and their trim parameters (`BRepLib_MakeEdge`) requires projecting each vertex's 3D point onto the curve when no explicit trim parameter is supplied. For a point exactly on a circle's own axis of symmetry (its center), every point on the circle is equidistant — there is no unique nearest point, so the projection is genuinely ambiguous/fails, distinct from Bo030's off-curve-but-well-defined-nearest-point case and Twi086's zero-length-line case. OCCT still force-builds a raw edge directly from curve+vertices+parameters rather than aborting.
- **Reproducer recipe**: `ADVANCED_FACE` on a `PLANE`; `FACE_OUTER_BOUND` is a single whole-circle `EDGE_CURVE` (radius 1, centered at origin) whose shared `VERTEX_POINT` (same entity at both `edge_start`/`edge_end`) sits at `(0,0,0)` — the circle's own center — instead of any point on the circle.
- **Expected kernel behavior**: force-build the edge from the curve/vertex/parameter data anyway, logging the point-projection failure as a diagnostic rather than aborting the edge's translation; widen the affected vertex's tolerance to cover the real gap between the declared point and the curve it nominally bounds.
- **Closure intent**: sheet
- **Notes**: **See also**: Twi086, Bo030, Gs029 (the class's other subvariants). Live-verified (this worktree, OCP/OCCT 7.8.1): reads without crashing, `occt=shape(1)/shape(1)`, `brepcheck.valid=True`; edge[0]'s OWN tolerance stays default `1e-07`, but BOTH vertex tolerances are blown out to `1.000001` — essentially the circle's radius — confirming `BRepLib_MakeEdge`'s fallback force-built the edge directly from curve+vertex+params rather than aborting, and the vertex-tolerance-update pass (`BRepLib::UpdateInnerTolerances`, Bo030's own citation) had to widen the VERTEX tolerance to cover the true 1.0-unit gap between the declared off-curve vertex and the curve it nominally bounds — the same "force-built anyway, tolerance absorbs the lie" evidentiary pattern as Bo030, now for the point-projection-fails subvariant specifically. Synonyms: "vertex at circle center", "no unique nearest point on curve", "ambiguous curve projection", "point on axis of symmetry", "MakeEdge point projection failure". Provenance tier: bytes-sufficient.
- **Byte assertion**: contains(b'off_curve_center_vertex')
- **Byte assertion**: count_entity_def(b'CIRCLE') == 1
- **Byte assertion**: count_entity_def(b'VERTEX_POINT') == 1
- **Tier-3 assertion**: face[0].surface_type == "plane"
- **Severity**: P3
- **Model impact**: A receiver that aborts edge translation on point-projection failure loses the whole edge (and often the whole face) over a producer-side degenerate-vertex mistake; a receiver that silently accepts without widening tolerance leaves an edge whose declared vertex sits a full radius away from the curve it supposedly bounds, corrupting downstream tolerance-based comparisons.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a`

### Twi300 — Edge trimmed onto an unbounded LINE by a vertex enormously far along the line's own direction
- **Category**: §12.3b wire-loop (sub-class: `stp-makeedge-validity-fallback`, PARTIAL, missing subvariant "a projected point has an infinite curve parameter")
- **Sources**: occt-coverage `exchange/problems.json` `stp-makeedge-validity-fallback` (`StepToTopoDS_TranslateEdge::DecodeMakeEdgeError`, `StepToTopoDS_TranslateEdge.cxx:70-131`; `MakeFromCurve3D` fallback force-build, `:483-489`).
- **Description**: STEP's `LINE` entity is unbounded by definition; OCCT represents an untrimmed `LINE`'s natural parameter domain using its own "infinite" sentinel (`Precision::Infinite()`, `1e100`) rather than a genuine finite range. When `BRepLib_MakeEdge` projects a vertex onto such a curve and the vertex sits far enough from the "intended" local segment, the computed/fallback parameter is effectively unbounded relative to the model's normal scale — a distinct classification from Gs029's "trim parameter out of the curve's own declared (finite, merely wrong) range".
- **Reproducer recipe**: Triangular `ADVANCED_FACE` on a `PLANE` with vertices `(0,0,0)`, `far_along_unbounded_line_vertex(1e8,0,0)`, `(0,1,0)`; the edge from `(0,0,0)` to the far vertex sits on a `LINE` through the origin along `+X`, trimmed by a vertex `1e8` units out — one hundred million times the face's other ~1-unit edges.
- **Expected kernel behavior**: force-build the edge from curve/vertices/parameters despite the effectively-infinite trim parameter, rather than aborting the edge's translation.
- **Closure intent**: sheet
- **Notes**: **See also**: Twi299, Gs029. Live-verified (this worktree, OCP/OCCT 7.8.1): reads without crashing, `occt=shape(1)/shape(1)`, `brepcheck.valid=True`; the far edge's length reads back as exactly `1e8`, confirming the enormous parameter was successfully absorbed into a genuine (if extreme-aspect-ratio) edge rather than causing the read to abort or the edge to be dropped. Synonyms: "unbounded line trimmed far from origin", "vertex enormously far along line direction", "infinite curve parameter", "extreme aspect ratio edge from unbounded curve", "MakeEdge infinite parameter fallback". Provenance tier: bytes-sufficient.
- **Byte assertion**: contains(b'far_along_unbounded_line_vertex')
- **Byte assertion**: count_entity_def(b'EDGE_CURVE') == 3
- **Byte assertion**: count_entity_def(b'LINE') == 3
- **Tier-3 assertion**: face[0].surface_type == "plane"
- **Severity**: P3
- **Model impact**: A receiver whose validity checks assume trim parameters stay within a sane bounded range may overflow, lose precision, or reject the edge outright when a producer trims an inherently-unbounded curve type far from its conceptual origin.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a`

### Twi301 — EDGE_CURVE flagged degenerate but its 3D LINE has positive length, face-hosted on a real ADVANCED_FACE/CONICAL_SURFACE
- **Category**: §12.3b wire-loop (sub-class: `bc-invalid-degenerated-flag`, PARTIAL)
- **Sources**: occt-coverage `exchange/problems.json` `bc-invalid-degenerated-flag` (`BRepCheck_Edge::Blind`, `BRepCheck_Edge.cxx:138`, sets `BRepCheck_InvalidDegeneratedFlag`). Face-hosted sibling of Twi083 (which demonstrates the identical byte-level defect pattern but orphaned inside a `GEOMETRIC_CURVE_SET`, so OCC yields empty and BRepCheck never runs on it).
- **Description**: Twi083's defect pattern (a positive-length 3D `LINE` wrapped in a curve-on-surface representation whose sole `PCURVE` has a zero-length 2D UV extent — the contradiction that should trip `BRepCheck_Edge::InvalidDegeneratedFlag`) reproduced verbatim, but wired into a real cone-frustum `ADVANCED_FACE`/`CONICAL_SURFACE` wire instead of an orphaned `GEOMETRIC_CURVE_SET`, so the defect-carrying edge is genuinely reachable and part of translated topology.
- **Reproducer recipe**: `CONICAL_SURFACE` frustum face (apex at origin, semi-angle 30°, between z=1 and z=3, apex NOT included). One lateral edge (`flag_lying_lateral_edge`) is a real 2.309-unit-long `LINE` (`positive_length_line`) wrapped in a `SURFACE_CURVE` whose sole `PCURVE` has a zero-magnitude 2D `VECTOR`; the other three edges (opposite lateral, top arc, bottom arc) are ordinary well-formed edges so the face genuinely translates.
- **Expected kernel behavior**: `BRepCheck_Edge::InvalidDegeneratedFlag` should be observable once BRepCheck actually walks the flagged edge (unlike Twi083's orphaned host); at minimum the input pattern must reach real, reachable, translated topology.
- **Closure intent**: sheet
- **Notes**: **See also**: Twi083 (identical byte pattern, orphaned GCS host, `occt=empty`). Live-verified (this worktree, OCP/OCCT 7.8.1): reads without crashing, `occt=shape(1)/shape(1)`, `brepcheck.valid=True`, face is a cone, `n_edges_total=4`, `n_vertices_total=8`. IMPORTANT honest finding: a direct `BRep_Tool::Degenerated_s()` probe on the resulting shape's edges shows ALL FOUR come back `False`, including `flag_lying_lateral_edge` — OCCT's default `StepToTopoDS`/`ShapeFix` pipeline recomputes the Degenerated flag from actual 3D geometry rather than trusting a zero-extent pcurve as a degeneracy signal, so it does NOT propagate an incorrect flag through to the final BRep in this configuration. (A `SEAM_CURVE` wrapper — Twi083's literal choice — was also tried live: with one pcurve it fails translation outright, `roots=0`; with the same pcurve listed twice it "succeeds" but the resulting shape has zero edges, an empty translate, not a genuine face; `SURFACE_CURVE` with one pcurve was used instead since it survives translation with the wire intact.) This fixture closes the REACHABILITY half of the packet's ask (the defect-carrier edge is now provably part of real, translated topology, not orphaned) but does NOT independently prove `BRepCheck_Edge::InvalidDegeneratedFlag` fires at runtime for this input; matches this class's existing `detect_only` provenance tier rather than upgrading it to a live-mechanism demonstration. Synonyms: "degenerate flag lies on real face", "face-hosted flag contradiction", "positive length edge flagged degenerate", "BRepCheck InvalidDegeneratedFlag reachable carrier". Provenance tier: bytes-sufficient (detect_only).
- **Byte assertion**: contains(b'positive_length_line')
- **Byte assertion**: contains(b'flag_lying_lateral_edge')
- **Byte assertion**: count_entity_def(b'CONICAL_SURFACE') == 1
- **Byte assertion**: count_entity_def(b'ADVANCED_FACE') == 1
- **Byte assertion**: count_entity_def(b'SURFACE_CURVE') == 1
- **Tier-3 assertion**: face[0].surface_type == "cone"
- **Tier-3 assertion**: n_edges_total >= 4
- **Tier-3 assertion**: n_vertices_total >= 8
- **Severity**: P3
- **Model impact**: A downstream consumer trusting the Degenerated flag without re-verifying actual geometry could collapse a real, positive-length edge to a point (or vice versa), corrupting face boundary trimming at exactly the location a viewer expects a smooth edge.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a`

### Twi302 — Small SEAM edge on a periodic face, adjacent to another seam segment: seam-with-seam merge
- **Category**: §12.3b wire-loop (sub-class: `tkshh-wire-small-edge`, PARTIAL, missing subvariant "small seam edge on a periodic face, seam-with-seam merge only")
- **Sources**: occt-coverage `tkshhealing/problems.json` `tkshh-wire-small-edge` (`ShapeFix_Wireframe::MergeSmallEdges`, `ShapeFix_Wireframe.cxx:590` method, `:816` `ReplaceFirst=JoinEdges`, `:887` re-check merged result, `:1028` circle-midpoint protection). `StepToTopoDS_GeometricTool::IsSeamCurve` (`StepToTopoDS_GeometricTool.cxx:72-107`, twice-in-one-wire branch).
- **Description**: A full-360 `CYLINDRICAL_SURFACE` face whose U=0 boundary — normally a single seam `EDGE_CURVE` spanning the whole height (Gp013's pattern) — is split into TWO consecutive seam segments: `seam_lower_segment` (real length ~2.0) and `seam_upper_small_segment` (length 1e-6, below the harness's live-tested survival-margin threshold). Each is an ordinary `LINE`-geometry `EDGE_CURVE` referenced TWICE in the one `FACE_OUTER_BOUND` `EDGE_LOOP` (formal seam per `IsSeamCurve`'s twice-in-one-wire branch); `seam_upper_small_segment`'s smallness is adjacent, on both sides of the wire traversal, to `seam_lower_segment`'s two seam references — not to any ordinary edge — isolating the seam-with-seam merge path.
- **Reproducer recipe**: `EDGE_LOOP` of 6 `ORIENTED_EDGE`s: `bot_arc(v_b->v_b)` -> `seam_lower fwd(v_b->v_mid)` -> `seam_upper fwd(v_mid->v_t, SMALL)` -> `top_arc(v_t->v_t, reversed)` -> `seam_upper rev(v_t->v_mid)` -> `seam_lower rev(v_mid->v_b)`.
- **Expected kernel behavior**: replace the two seam segments with one, re-deriving the surviving edge's pcurve to span the full combined parameter range, rather than merging a small seam into an ordinary neighbor.
- **Closure intent**: sheet
- **Notes**: **See also**: Twi013, N010, N014, Twi138, Twi237, Twi184 (all merge a small edge into an ordinary neighbor, not another seam). Live-verified (this worktree, OCP/OCCT 7.8.1): `occt=shape(1)/shape(1)`, face is a cylinder, `n_edges_total=6`, `n_vertices_total=12`, `brepcheck.valid=True`. Below ~1e-7 the double-seam wire is rejected outright (whole wire dropped, face left with 0 edges/natural bound) rather than merged — a platform-risk boundary the harness live-tested and avoided by using `1e-6`, matching this corpus's convention of staying safely clear of borderline OCCTAutoFix geometry (see `reference_gmsh_platform_divergence`). Synonyms: "seam merges into adjacent seam", "two consecutive seam segments one small", "seam-with-seam merge path", "small seam edge periodic surface", "MergeSmallEdges seam protection". Provenance tier: bytes-sufficient.
- **Byte assertion**: contains(b'seam_lower_segment')
- **Byte assertion**: contains(b'seam_upper_small_segment')
- **Byte assertion**: count_entity_def(b'CYLINDRICAL_SURFACE') == 1
- **Byte assertion**: count_entity_def(b'EDGE_CURVE') == 4
- **Tier-3 assertion**: face[0].surface_type == "cylinder"
- **Tier-3 assertion**: brepcheck.valid == True
- **Severity**: P3
- **Model impact**: A healer that only knows how to merge a small edge into an ordinary neighbor (not another seam) leaves a spurious near-zero-length seam segment in the wire, corrupting the periodic surface's seam bookkeeping and any downstream re-parametrization that assumes exactly one seam per periodic direction.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a`

### Twi303 — Small edge at a sharp corner (non-collinear neighbors on both sides): drop-mode-only merge
- **Category**: §12.3b wire-loop (sub-class: `tkshh-wire-small-edge`, PARTIAL, missing subvariant "small edge that cannot be merged and is dropped (drop mode), with connectivity re-check")
- **Sources**: occt-coverage `tkshhealing/problems.json` `tkshh-wire-small-edge` (`ShapeFix_Wireframe::MergeSmallEdges`, `ShapeFix_Wireframe.cxx:590` method, `:927` `else if(aModeDrop)` drop-mode branch).
- **Description**: A pentagon-ish planar face on a `PLANE`. Four of the five wire edges form a near-square (bottom, right, top, left); the fifth is a tiny DIAGONAL notch edge (`sharp_corner_notch_edge`, length ~1.414e-6) inserted at the top-right corner between the near-vertical right edge and the near-horizontal top edge — emphatically NOT collinear with either neighbor (their tangent directions differ from the notch's by ~45° on each side, vs. the ~180° collinear continuation Twi013's sliver has with its straight run). A healer that tries to "extend" either straight neighbor to absorb the diagonal notch would have to change that neighbor's curve direction, violating the angle-limit merge-eligibility guard — forcing drop mode.
- **Reproducer recipe**: `EDGE_LOOP` of 5 edges: `bottom(A->B)` -> `right(B->C)` -> `sharp_corner_notch_edge(C->D, tiny diagonal)` -> `top(D->E)` -> `left(E->A)`; `A=(0,0,0) B=(1,0,0) C=(1,1-1e-6,0) D=(1-1e-6,1,0) E=(0,1,0)`.
- **Expected kernel behavior**: remove the small edge outright and reconnect its two neighbors directly to each other, adjusting the shared vertex (a connectivity re-check), rather than extending either curve.
- **Closure intent**: sheet
- **Notes**: **See also**: Twi013, N010, N014, Twi138, Twi237, Twi184 (whose sliver always sits collinear with, or between collinear-compatible, straight neighbors and is mergeable by simple extension). Live-verified (this worktree, OCP/OCCT 7.8.1): `occt=shape(1)/shape(1)`, face is a plane, `n_edges_total=5`, `n_vertices_total=10`, `brepcheck.valid=True`. Synonyms: "small edge at sharp corner", "non-collinear neighbors merge guard", "drop mode small edge removal", "connectivity re-check after drop", "angle limit merge eligibility guard". Provenance tier: bytes-sufficient.
- **Byte assertion**: contains(b'sharp_corner_notch_edge')
- **Byte assertion**: count_entity_def(b'EDGE_CURVE') == 5
- **Byte assertion**: count_entity_def(b'PLANE') == 1
- **Tier-3 assertion**: face[0].surface_type == "plane"
- **Tier-3 assertion**: n_edges_total >= 4
- **Tier-3 assertion**: brepcheck.valid == True
- **Severity**: P3
- **Model impact**: A healer that always tries to extend a neighbor to absorb a small edge (never falling back to drop mode) can distort a real corner's geometry, silently changing a sharp 90° corner into a smoothed/skewed one.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(11) ifc=schema_n/a`

### Twi304 — Multi-face shared full-circle edge that must NOT be collapsed as a "small edge" (protection case)
- **Category**: §12.3b wire-loop (sub-class: `tkshh-wire-small-edge`, PARTIAL, missing subvariant "small edge shared by faces where a circle-like closed curve must NOT be collapsed, protection case")
- **Sources**: occt-coverage `tkshhealing/problems.json` `tkshh-wire-small-edge` (`ShapeAnalysis_Wire::CheckSmall`, `ShapeAnalysis_Wire.cxx:733-749`, midpoint test distinguishing a genuinely small edge from one that "leaves and returns").
- **Description**: The SAME full-circle `EDGE_CURVE` (`shared_small_circle_edge`, radius 0.02, small relative to the model's 1×1 bounding box) is used as BOTH the `FACE_BOUND` (hole) of a big square face AND the `FACE_OUTER_BOUND` of a small disk face — a genuinely shared entity, not independently duplicated, referenced by TWO different `ADVANCED_FACE`s. `shared_small_circle_edge`'s start==end vertex (naive endpoint distance 0) but its midpoint (the antipodal point on the circle, 0.04 away — 2× radius) is far enough from the vertex that `CheckSmall`'s midpoint test must correctly NOT flag it as a small/degenerate edge. Dropping it would corrupt BOTH faces at once (the big face loses its hole, the disk face loses its entire boundary).
- **Reproducer recipe**: `big_face`: `FACE_OUTER_BOUND` = 1×1 square, `FACE_BOUND` = `shared_small_circle_edge` reversed (hole at center `(0.5,0.5)` radius 0.02); `disk_face`: `FACE_OUTER_BOUND` = the SAME `shared_small_circle_edge`, forward. Both `ADVANCED_FACE`s in one `OPEN_SHELL`.
- **Expected kernel behavior**: protect the circle-like closed edge from being dropped as a small/degenerate edge despite the naive zero endpoint distance.
- **Closure intent**: sheet
- **Notes**: **See also**: Twi013, N010, N014, Twi138, Twi237, Twi184 (single-face sliver cases; this fixture raises the stakes by genuinely sharing the protected edge across two faces). Live-verified (this worktree, OCP/OCCT 7.8.1): `occt=shape(1)/shape(1)`, `n_faces_total=2` (both planes), `n_edges_total=6`, `n_vertices_total=12`, `brepcheck.valid=True`; `count_entity_def(b'EDGE_CURVE')==5` confirms the circle edge is genuinely shared (5 definitions for 6 oriented-edge uses across 2 faces). Synonyms: "circle-like closed curve protection", "shared hole boundary must not collapse", "multi-face small edge protection", "midpoint test leaves and returns", "full circle edge naive zero distance". Provenance tier: bytes-sufficient.
- **Byte assertion**: contains(b'shared_small_circle_edge')
- **Byte assertion**: count_entity_def(b'EDGE_CURVE') == 5
- **Byte assertion**: count_entity_def(b'ADVANCED_FACE') == 2
- **Byte assertion**: count_entity_def(b'CIRCLE') == 1
- **Tier-3 assertion**: n_faces_total == 2
- **Tier-3 assertion**: brepcheck.valid == True
- **Severity**: P2
- **Model impact**: Incorrectly collapsing a genuinely shared circular boundary as "small" would corrupt two faces simultaneously — a hole vanishes from the big face and the small disk face loses its entire boundary — a much more damaging failure mode than a single-face sliver.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a`

### Twi305 — Apex-bridging edge already PRESENT at the cone singularity (single, correctly positioned): dgnr/replace input
- **Category**: §12.3b wire-loop (sub-class: `tkshh-wire-missing-or-bad-degenerated-edge`, PARTIAL, subvariant "edge sitting on the singularity that must become/be replaced by a proper degenerated edge (dgnr, DONE2)")
- **Sources**: occt-coverage `tkshhealing/problems.json` `tkshh-wire-missing-or-bad-degenerated-edge` (`ShapeAnalysis_Wire::CheckDegenerated`, `ShapeAnalysis_Wire.cxx:806-988`; `ShapeFix_Wire::FixDegenerated(num)`, `ShapeFix_Wire.cxx:1725-1760`, replace branch). DONE1/DONE2 sibling of Twi021 (lack/insert) and Twi031 (duplicate/dedupe).
- **Description**: `ShapeAnalysis_Wire::CheckDegenerated` distinguishes two singularity-bridge outcomes: "lack" (no edge at all bridges the singular row -> INSERT, DONE1 -- Twi021's exact input) vs. "dgnr" (an edge ALREADY occupies that wire slot, sitting at the singularity -> REPLACE with a freshly-built canonical degenerated edge, DONE2). This fixture supplies exactly the "dgnr" input shape: FOUR declared edges (vs. Twi021's THREE and Twi031's FIVE) — two lateral `LINE` edges, one base `CIRCLE` arc, and exactly ONE apex-bridging `EDGE_CURVE` (`single_apex_degenerate_edge`: apex -> apex, same `VERTEX_POINT` object at both ends, zero-length `LINE`) — present, singular, correctly positioned, not missing, not duplicated.
- **Reproducer recipe**: `CONICAL_SURFACE` (apex at origin, semi-angle 30°, axis +Z); `EDGE_LOOP` of `single_apex_degenerate_edge(apex->apex)`, `lat_L(apex->base_0)`, `base_arc(base_0->base_pi)`, `lat_R(base_pi->apex)`.
- **Expected kernel behavior**: process the existing apex-bridging edge down the dgnr/DONE2 replace branch (rather than the lack/DONE1 insert branch), yielding a valid, single, canonical degenerate apex edge.
- **Closure intent**: sheet
- **Notes**: **See also**: Twi021 (lack/DONE1 sibling), Twi031 (duplicate/dedupe sibling), Tfa245/Twi296/Twi297 (other subvariants of this 10-subvariant merged class). Live-verified (this worktree, OCP/OCCT 7.8.1): `occt=shape(1)/shape(1)`, face is a cone, `n_edges_total=4`, `n_vertices_total=8`, `brepcheck.valid=True`; a direct `BRep_Tool::Degenerated_s()` probe shows exactly ONE of the 4 read-back edges comes back `True` (the apex bridge), matching both Twi021's and Twi031's own converged post-heal shape exactly — expected, since "dgnr" is defined by what INPUT STRUCTURE it presents to `CheckDegenerated` (an edge occupying the singular slot vs. a gap), not by a different final geometry. An earlier near-tolerance variant of this fixture (apex vertices offset ~1e-6/1e-7 from the true apex rather than bit-identical) was live-tested and found to NOT trigger the replace path — it left the imperfect small edge in place UNTOUCHED and additionally inserted a second, fresh degenerate edge (5 edges total, "lack" behavior firing alongside it), which is why this fixture uses the bit-identical-vertex construction instead. Synonyms: "degenerate edge present not missing", "dgnr replace branch input", "apex bridge already occupying wire slot", "single correctly-positioned degenerate edge", "FixDegenerated DONE2 replace". Provenance tier: bytes-sufficient.
- **Byte assertion**: count_entity_def(b'CONICAL_SURFACE') == 1
- **Byte assertion**: count_entity_def(b'EDGE_CURVE') == 4
- **Byte assertion**: contains(b'single_apex_degenerate_edge')
- **Tier-3 assertion**: face[0].surface_type == "cone"
- **Tier-3 assertion**: n_edges_total >= 4
- **Tier-3 assertion**: n_vertices_total >= 6
- **Tier-3 assertion**: brepcheck.valid == True
- **Severity**: P3
- **Model impact**: A wire-healer that only knows how to INSERT a missing degenerate edge (never replace an existing-but-wrong one) leaves a producer-supplied, potentially malformed apex bridge in place uncorrected, risking downstream mis-parametrization at the singularity.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a`

### Gp190 — CATIA-style pseudo-seam split ACROSS TWO DIFFERENT FACES (IsLikeSeam's cross-wire domain)
- **Category**: §12.2a pcurve (sub-class: `stp-seam-pcurve-selection`, PARTIAL, missing subvariant (a): "a CATIA-style pseudo-seam where two DIFFERENT faces (not one face, two wires) are built on the same not-formally-closed surface, sharing edge geometry across two wires — exercises `IsLikeSeam`")
- **Sources**: occt-coverage `exchange/problems.json` `stp-seam-pcurve-selection` (`StepToTopoDS_GeometricTool::IsSeamCurve`, `StepToTopoDS_GeometricTool.cxx:72-107`, twice-in-one-wire; `IsLikeSeam`, `:109-191`, cross-wire pseudo-seam heuristic).
- **Description**: `StepToTopoDS_GeometricTool::IsSeamCurve` detects a formal seam via a `SEAM_CURVE` or an `EDGE_CURVE` referenced twice within ONE wire (Gp013's pattern — a single face wraps fully around). `IsLikeSeam` is the different, heuristic sibling: it compares two pcurves' line origins/directions within tolerance ACROSS TWO DIFFERENT WIRES (potentially of two different faces). Gp013/Gp181/Gp182 are all single-face constructions (`IsSeamCurve`'s domain); this fixture is genuinely multi-face, putting `IsLikeSeam`'s cross-wire comparison to work: the SAME `B_SPLINE_SURFACE_WITH_KNOTS` host as Gp013 is shared by TWO INDEPENDENT `ADVANCED_FACE`s, split along v (height) — `face_lower` (v:[0,0.5]) and `face_upper` (v:[0.5,1]) — each independently reproducing Gp013's own "one seam edge used twice in its own wire" pattern.
- **Reproducer recipe**: Two `ADVANCED_FACE`s on the SAME `B_SPLINE_SURFACE_WITH_KNOTS`, each with its own seam-like `EDGE_CURVE` (`face_lower_seam`, `face_upper_seam`) used twice within its own wire, at the surface's u=0/u=1 near-closure locus.
- **Expected kernel behavior**: `IsLikeSeam`'s cross-wire comparison correctly disambiguates the two faces' independent seam-like edges rather than misidentifying them as one shared entity or failing to recognize the pseudo-seam pattern in either.
- **Closure intent**: sheet
- **Notes**: **See also**: Gp013 (single-face `IsSeamCurve` original), Gp181 (V-direction sibling), Gp182 (non-B-spline-host sibling). Live-verified (this worktree, OCP/OCCT 7.8.1): `occt=shape(1)/shape(1)`, `n_faces_total=2`, both faces read as `bspline` surface type, `brepcheck.valid=True`. Synonyms: "pseudo-seam across two faces", "IsLikeSeam cross-wire detection", "CATIA seam split between faces", "two faces sharing seam-like geometry", "cross-face pseudo-seam disambiguation". Provenance tier: bytes-sufficient.
- **Byte assertion**: count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 1
- **Byte assertion**: count_entity_def(b'ADVANCED_FACE') == 2
- **Byte assertion**: contains(b'face_lower_seam')
- **Byte assertion**: contains(b'face_upper_seam')
- **Tier-3 assertion**: n_faces_total == 2
- **Severity**: P3
- **Model impact**: A reader that only checks for seams within a single wire misses the CATIA idiom where two different faces independently touch the same near-closure locus; without cross-wire pseudo-seam recognition, downstream unification/healing passes may treat the two faces' boundaries as unrelated when they are physically coincident.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a`

### Gp191 — Pcurve whose 2D trim parameters literally collapse to a point (w1==w2) on a real, non-degenerate 3D edge
- **Category**: §12.2a pcurve (sub-class: `stp-pcurve-trim-range-repair`, PARTIAL, missing subvariant (a): "a pcurve whose 2D trim parameters literally collapse to a point (w1==w2) on an otherwise real, non-degenerate 3D edge — pcurve dropped, edge kept 3D-only")
- **Sources**: occt-coverage `exchange/problems.json` `stp-pcurve-trim-range-repair` (`CheckPCurves`, `StepToTopoDS_TranslateEdgeLoop.cxx:104-169`, post-pass over every edge of a finished wire; `:134-140`, w1==w2 -> `RemoveSinglePCurve`).
- **Description**: `CheckPCurves` detects when a pcurve's own 2D parameter range collapses to a single point (w1==w2) and (per the catalog's citation) drops that pcurve, leaving the edge's 3D curve intact but with no 2D representation on that face. Gp007/Gn019/Gs007/Gp028 all present pcurve DOMAIN mismatches (out-of-bounds, periodic-band) but none presents a literal w1==w2 collapsed range. This fixture does: the 3D curve genuinely spans a real 1-unit `LINE` (`edge_positive_length_3d`), but its `PCURVE` (`collapsed_pcurve_edge`) is a UV `LINE` with a zero-magnitude `VECTOR` — its own 2D domain literally has w1==w2 regardless of the 3D edge's real traversal.
- **Reproducer recipe**: `PLANE` host; `EDGE_CURVE` `collapsed_pcurve_edge` between `(0,0,0)` and `(1,0,0)`, 3D curve a real 1-unit `LINE`, wrapped in a `SURFACE_CURVE` with ONE `PCURVE` whose 2D `LINE` has a zero-magnitude `VECTOR`.
- **Expected kernel behavior**: drop the collapsed pcurve, keeping the edge 3D-only on that face.
- **Closure intent**: sheet
- **Notes**: **See also**: Gp007, Gn019, Gs007, Gp028 (domain-mismatch siblings). IMPORTANT live finding (honest, not overclaimed, live-verified this worktree, OCP/OCCT 7.8.1): `occt=shape(1)/shape(1)`, `brepcheck.valid=True`, edge[0]'s 3D curve length reads back as exactly `1.0` (the real 3D geometry survives). A direct `BRep_Tool::CurveOnSurface` probe on the resulting edge does NOT come back empty as "pcurve dropped" would predict — it returns a live `Geom2d_Line`. But evaluating that returned curve at parameter `1.0` gives `(1.0, 0.0)`, NOT `(0.0, 0.0)` as the deliberately-collapsed zero-vector construction declared — i.e. OCCT did not keep the contradictory pcurve AND did not literally drop it either; it silently REGENERATED a fresh, correct, non-degenerate 2D representation that supersedes the collapsed one supplied. This is a related but distinct repair strategy from the catalog's literal "`RemoveSinglePCurve`" (drop) claim — the byte-level input pattern is faithfully reproduced and reachable, and OCCT visibly does NOT propagate the contradiction through to the final BRep, but the specific repair outcome observed is "regenerate", not "drop" — recorded honestly. Synonyms: "pcurve trim collapses to point", "w1 equals w2 pcurve range", "zero-extent 2D pcurve real 3D edge", "collapsed pcurve regenerated not dropped", "CheckPCurves point-range repair". Provenance tier: bytes-sufficient.
- **Byte assertion**: contains(b'collapsed_pcurve_edge')
- **Byte assertion**: contains(b'edge_positive_length_3d')
- **Byte assertion**: count_entity_def(b'PCURVE') == 1
- **Tier-3 assertion**: face[0].surface_type == "plane"
- **Severity**: P3
- **Model impact**: A reader that keeps a self-contradictory zero-extent pcurve without repair corrupts UV trimming for that edge on that face; this fixture shows OCCT avoids that outcome by regenerating (rather than merely dropping) the pcurve, an even stronger repair than the class's literal claim.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a`

### Gp192 — Pcurve range straddles a U-periodic surface's seam in the wrong order (w1>w2)
- **Category**: §12.2a pcurve (sub-class: `stp-pcurve-trim-range-repair`, PARTIAL, missing subvariant (b): "a pcurve range that straddles a U-periodic surface's seam in the wrong order (w1>w2), forcing `ElCLib::AdjustPeriodic` re-basing")
- **Sources**: occt-coverage `exchange/problems.json` `stp-pcurve-trim-range-repair` (`CheckPCurves`, `StepToTopoDS_TranslateEdgeLoop.cxx:155-163`, w1>w2 on a U-periodic surface -> `ElCLib::AdjustPeriodic` re-basing).
- **Description**: `CheckPCurves` detects when a pcurve's declared 2D parameter range has w1>w2 on a U-periodic surface and re-bases it via `ElCLib::AdjustPeriodic`, rather than accepting the range literally (which would describe a backward/negative-length span). This fixture hosts a quarter-turn arc edge on a genuinely U-periodic `CYLINDRICAL_SURFACE` whose declared `PCURVE` 2D `LINE` runs from `(1.5*pi, 0)` to `(0.5*pi, 0)` — u1=4.712 greater than u2=1.571, the wrong order — even though the edge's 3D `CIRCLE` arc geometry genuinely spans a positive quarter-turn from angle 1.5*pi to 2.0*pi.
- **Reproducer recipe**: `CYLINDRICAL_SURFACE` (radius 1, axis +Z); `EDGE_CURVE` `wrong_order_pcurve_edge`: real 3D `CIRCLE` arc from 1.5*pi to 2.0*pi, wrapped in a `SURFACE_CURVE` whose sole `PCURVE` is a 2D `LINE` declared from `(1.5*pi,0)` to `(0.5*pi,0)`.
- **Expected kernel behavior**: re-base the wrong-order range via `ElCLib::AdjustPeriodic` rather than accepting it literally or rejecting the edge.
- **Closure intent**: sheet
- **Notes**: **See also**: Gp007, Gn019, Gs007, Gp028, Gp191 (this class's other subvariants). Live-verified (this worktree, OCP/OCCT 7.8.1): `occt=shape(1)/shape(1)`, `brepcheck.valid=True` at the model level (the single-edge non-closing loop itself reads `brepcheck.valid=False` for the face, matching this corpus's established convention for parametric-only single-edge-loop fixtures — e.g. Gp007's own construction is not geometrically closed either); edge[0]'s 3D curve length reads back as exactly `pi/2` (1.5708), confirming the wrong-order pcurve declaration did NOT corrupt or drop the real 3D geometry. Synonyms: "wrong order pcurve range", "w1 greater than w2 periodic", "AdjustPeriodic re-basing", "backward declared pcurve range", "U-periodic seam straddle wrong order". Provenance tier: bytes-sufficient.
- **Byte assertion**: contains(b'wrong_order_pcurve_edge')
- **Byte assertion**: count_entity_def(b'CYLINDRICAL_SURFACE') == 1
- **Tier-3 assertion**: face[0].surface_type == "cylinder"
- **Severity**: P3
- **Model impact**: A reader that accepts a backward (w1>w2) pcurve range literally on a periodic surface produces a negative-length or wildly mis-oriented 2D trim; re-basing via periodic adjustment is required to recover the intended forward span.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a`

### Ad137 — COMPOSITE_CURVE with one numerically degenerate segment (non-monotonic B-spline knots): segment-dropped-not-whole-curve-aborted catch site
- **Category**: §12.11 adversarial (sub-class: `stp-transfer-exception-to-fail`, PARTIAL, narrow breadth)
- **Sources**: occt-coverage `exchange/problems.json` `stp-transfer-exception-to-fail` (`StepToTopoDS_TranslateCompositeCurve::Init`, `StepToTopoDS_TranslateCompositeCurve.cxx:188-211,243-249`, per-segment 3D-curve/pcurve conversion try/catch, segment dropped on exception). Distinct call site from Ad043 (`STEPControl_ActorRead::TransferShape`, per-ROOT try/catch) and Xp008 (`StepToTopoDS_TranslateEdgeLoop`, per-EDGE try/catch) — this one is nested one level deeper, inside a single edge's own composite-curve geometry, at per-segment granularity.
- **Description**: `StepToTopoDS_TranslateCompositeCurve::Init` wraps EACH segment's own 3D-curve/pcurve conversion in its own try/catch; a segment whose underlying geometry throws during construction (as opposed to merely being disconnected from its neighbor — Gp034/Gp188's already-covered connectivity-gap warning path) should be dropped, letting the rest of the composite curve's segments — and the containing face — still translate. This fixture's `COMPOSITE_CURVE` has two segments: `good_composite_segment_line` (an ordinary `LINE`, genuinely constructible) and `degenerate_composite_segment_bspline` (a `B_SPLINE_CURVE_WITH_KNOTS` whose knot vector `(1.0, 0.5, 2.0)` is NOT monotonically non-decreasing — schema-legal Part-21 bytes, but numerically invalid for `Geom_BSplineCurve`'s constructor, which requires a non-decreasing knot sequence).
- **Reproducer recipe**: `ADVANCED_FACE` on a `PLANE`; sole boundary is a self-loop `EDGE_CURVE` whose 3D geometry is a `SURFACE_CURVE` wrapping a `COMPOSITE_CURVE` of two `COMPOSITE_CURVE_SEGMENT`s (one good `LINE`, one non-monotonic-knot `B_SPLINE_CURVE_WITH_KNOTS`) — mirrors Gp188's proven-working structural pattern (segments reference base curves directly, not `TRIMMED_CURVE`-wrapped; the `COMPOSITE_CURVE` itself wrapped in `SURFACE_CURVE`+`PCURVE`, not used bare as `EDGE_CURVE.edge_geometry`).
- **Expected kernel behavior**: drop the bad segment's contribution via the per-segment catch, letting the whole face still translate (`occt=shape(1)`) rather than aborting the whole read.
- **Closure intent**: sheet
- **Notes**: **See also**: Ad043, Xp008 (coarser-granularity catch sites for this same task-brief family), Gp034, Gp188 (connectivity-gap sibling, a DIFFERENT defect — disconnection, not a throwing segment). Live-verified (this worktree, OCP/OCCT 7.8.1): reads without crashing, `TransferRoots()==1`, `OneShape()` not null, `occt=shape(1)/shape(1)`, `shape_null=False`, `n_faces_total=1` — matching Gp188's own pre-existing "`n_edges_total==0` despite `n_faces_total==1`" tier-3 signature for this single-self-loop `COMPOSITE_CURVE`-edge structural family (confirmed via direct read this is a known, established, ACCEPTED pattern for this construction style in this corpus — see Gp188's own notes — not a new concern introduced here). A prior variant of this fixture used `TRIMMED_CURVE`-wrapped segments (Gp063's pattern) instead of Gp188's plain-LINE-segment style, and used the `COMPOSITE_CURVE` bare as `EDGE_CURVE.edge_geometry` instead of Gp188's `SURFACE_CURVE`+`PCURVE` wrapper — both prior variants ALSO read as `shape(1)`/non-null, so the exact sub-pattern choice does not appear load-bearing for reachability; this version follows Gp188's own proven convention for consistency. Synonyms: "composite curve segment throws", "per-segment try catch composite curve", "non-monotonic knot vector segment", "segment dropped not curve aborted", "TranslateCompositeCurve per-segment catch". Provenance tier: bytes-sufficient.
- **Byte assertion**: contains(b'good_composite_segment_line')
- **Byte assertion**: contains(b'degenerate_composite_segment_bspline')
- **Byte assertion**: count_entity_def(b'COMPOSITE_CURVE_SEGMENT') == 2
- **Byte assertion**: count_entity_def(b'COMPOSITE_CURVE') == 1
- **Tier-3 assertion**: shape_null == False
- **Tier-3 assertion**: n_faces_total == 1
- **Severity**: P3
- **Model impact**: A reader that aborts the whole composite-curve (or whole edge, or whole face) translation over one numerically-degenerate segment loses geometry that was otherwise perfectly recoverable from the segment's healthy siblings.
- **Expected validation**: `occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a`
