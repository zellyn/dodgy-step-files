# Backlog — single authoritative work-tracking file

This file is the only authoritative backlog for the corpus. Anything not
captured here is at risk of being forgotten. When picking up work,
**start here, work top-down**. When finishing work, **move the entry to
`DONE.md`** with completion date + commit SHA. This file should contain
ONLY pending work — never edit history into it.

Conventions:
- Each initiative has an **ID** (e.g. `B1`) for cross-reference.
- Subtasks nest beneath. Mark with `[x]` when complete.
- "Status" line tracks freshness; "Last touched" is the date of last
  meaningful update.
- When you start work, prepend the current commit-sha-short to the
  subtask line so resuming is obvious.

---

## Operating principles

- **Quality > completeness, always.** We can pause expansion at any time to chase
  a quality concern. The only requirement: if we defer expansion work, log the
  deferred items here so they aren't forgotten. (User invariant 2026-06-19.)

## Active initiatives

### B5 — New-source mining (2026-07 survey) — IN PROGRESS

**Why:** The STEP/OCCT/CAx-IF/commercial-KB veins are near-saturated. A 2026-07 source
survey (full detail in local `audit/source_survey_2026-07.md`) found new, currently-maintained
frontiers with public issue trackers/forums and license-clean test-file seams. Mine each for
FILE-LEVEL problematic-input classes (a static `.stp`/mesh/container fixture can reproduce it),
synthesize catalog entries + builders, verify via validate2, and push to `main`.

Take these on in parallel (≤3 mining agents at a time per [[feedback_parallelism]]). Order is
"maintainer said you-pick" — sequenced below by tractability × novelty. Mark `[x]` when a source's
candidate-defect list is mined; a second pass synthesizes the confirmed-novel, file-level ones.

**Wave 1 — MINED 2026-07-11 (candidate lists in local audit/mining_*.md):**
- [x] **ruststep** → `audit/mining_ruststep_2026-07.md`. 14 candidates, ~6 novel (rest already covered =
      good saturation signal). Fits EXISTING infra (§12-1b/1c). Strongest: leading-zero instance-name
      aliasing (`#1`≡`#01`), instance-id >u64::MAX overflow, REAL-in-INTEGER slot, empty complex `#1=()`,
      conformant-file-rejected-at-`DATA;`. → SYNTH TASK #490.
- [x] **assimp** → `audit/mining_assimp_2026-07.md`. **26 novel** across 9 formats (glTF/PLY/OBJ/OFF/
      COLLADA/3MF/FBX/STL). NEEDS NEW CATEGORY: **§12.15 "Import-format parser robustness" (`Ip*`)** +
      raw-malformed-file writer — mesh_builder only emits structurally-VALID files, can't express
      header-count lies / OOB indices / dangling refs / truncated multibyte. First glTF/COLLADA/3MF/FBX
      coverage. → INFRA+SYNTH TASK #492 (bigger lift).
- [x] **MBx-IF / NIST** → `audit/mining_nist_mbxif_2026-07.md`. 18 novel; biggest gap = **semantic GD&T
      tolerance vocabulary** (CIRCULAR/TOTAL_RUNOUT, SURFACE/LINE_PROFILE, GEOMETRIC_TOLERANCE_WITH_MODIFIERS
      MMC/LMC, DATUM_REFERENCE_COMPARTMENT) + AP242 tessellation packed-arrays (shared COORDINATES_LIST) +
      saved-view presentation. Fits EXISTING infra (§12-7 Pmi, §12-8 M). → SYNTH TASK #491.
      **Ingestible clean file set:** `https://www.nist.gov/system/files/documents/noindex/2024/06/19/NIST-PMI-STEP-Files.zip`
      (US public-domain, verbatim "no restrictions"). **LICENSE CAVEAT:** only the NIST-authored synthetic
      subset is redistributable; broader CAx-IF (member-production / JAMA / LOTAR) is RESTRICTED — describe-only.

**Synthesis note (all waves):** new fixtures ship with best-guess `Expected validation` lines; the live
occt/gmsh oracle can't be run locally (macOS/CI gmsh platform divergence, [[reference_gmsh_platform_divergence]]),
so let the nightly `validate-full` + `_refresh_expected --apply` rebaseline (established
[[feedback_drift_rebaseline]] workflow). Structural checks (part21, round-trip, byte/tier3, dangling+dup-id
clean) ARE run at synthesis time.

**Wave 1 SYNTHESIS — LANDED on main 2026-07-11 (15 fixtures):** ruststep → Lh051/052, Ls053-056 (6);
NIST GD&T → Pmi156-164 (9, semantic tolerance vocabulary + packed tessellation). All verified (part21,
round-trip 0-drift, byte/tier3/category/fixture lints, dangling+dup clean). Expected lines provisional →
nightly rebaseline. assimp §12.15 still pending (needs new section + raw-file writer, task #492).

**Wave 2 (slicer + viewer STEP streams; OCCT-correlated but attachment-rich, cross-oracle):**
- [ ] **PrusaSlicer** (issues; #11305 malformed-STEP stack overflow, #8998 STEP-vs-STL open-edge divergence)
- [ ] **OrcaSlicer** (highest-volume slicer STEP stream)
- [ ] **Online3DViewer / occt-import-js** (kovacsv; attachment-rich, "opens in X / empty in Y" cross-oracle)

**Wave 2 — MINED 2026-07-11 (low yield, as predicted — OCCT-wrapping slicers corroborate more than diversify):**
- [x] **PrusaSlicer** → `audit/mining_prusaslicer_2026-07.md`. 1 NEW: cyclic `ORIENTED_EDGE.edge_element`
      self-ref → EdgeEnd/EdgeStart recursion stack-overflow DoS (#11305); `#1=ORIENTED_EDGE('',*,*,#1,.F.);`.
      → §12.3b Twi + cross-list §12.11 Ad. Rest corroborate existing OCCT classes.
- [x] **OrcaSlicer** → `audit/mining_orcaslicer_2026-07.md`. 0 NEW (2 sub-cases). Value = cross-oracle
      validator, not a defect source. Do NOT open a fixture wave.
- [x] **Online3DViewer/occt-import-js** → `audit/mining_online3dviewer_2026-07.md`. 3 NEW (viewer exposes
      differentials): (a) OCCT-VERSION differential — conical ADVANCED_FACE dropped by BRepMesh 7.7.x but
      present ≤7.6.1 on VALID bytes (occt-import-js#42 / OCCT#33681) → §12.12 Xp, first version-divergence
      entry; (b) wasm32 32-bit-address-space silent-empty on large valid STEP (#19; iOS-Safari cap sub-case
      #443); (c) far-from-origin float32 three.js vertex collapse (#37/#467), distinct from Tb010/Tb013.
- **Wave-2 synthesizable novel set ≈ 4:** cyclic-ORIENTED_EDGE DoS (Twi/Ad), OCCT-version conical drop (Xp),
      far-origin float32 collapse (Tb/Xp); wasm-address-space is borderline-platform (Pf/Xp or describe-only).
      → SYNTH TASK #496.

**Wave 3 (mesh libraries — malformed-mesh/parser pathologies):**
- [ ] **trimesh + Open3D** (messy-file loaders; RPly failures; trimesh ships an in-repo broken-model corpus)
- [ ] **MeshLab / VCGlib** (`confirmed`-labeled PLY/OBJ crashers)
- [ ] **Draco + fTetWild** (OSS-Fuzz `.drc` crashers; failing Thingi10K STLs)

**Wave 3 — MINED 2026-07-11 (independent mesh kernels → high yield, as predicted):**
- [x] **trimesh + Open3D** → `audit/mining_trimesh_open3d_2026-07.md`. 12 novel (11 §12.15 Ip* parse-layer:
      OBJ backslash line-continuation, face-like-substring-in-name, binary-STL-"solid"-header trap,
      multi-body ASCII STL silent-drop, etc.; 1 §12.14 concave-n-gon fan-triangulation).
- [x] **MeshLab + Draco + fTetWild** → `audit/mining_meshlab_draco_ftetwild_2026-07.md`. 16 novel:
      **8 Draco `.drc` codec/container** (compression-bomb-in-codec, rANS entropy overflow, Edgebreaker
      CLERS OOB, kd-tree point-cloud, integer-overflow size math) — a WHOLE NEW codec surface, zero
      analogue in corpus; 3 §12.15 Ip* (MeshLab OFF/PLY differentials); 5 §12.14 (fTetWild valid-STL
      volumetric-oracle defects).

**CONSOLIDATED SYNTHESIS POOL (Waves 1+3, file-level, mined & ready):**
- **§12.15 `Ip*` parse-layer ≈ 40** (assimp 26 + trimesh 11 + MeshLab 3) — GATED on the §12.15 raw-file
  writer + section scaffold. THE priority unlock. → task #492.
- **Draco `.drc` codec ≈ 8** — needs a BINARY writer (`draco_encoder` + field mutation); own `codec/draco`
  sub-band under §12.15. Heavier tooling; separate sub-track.
- **§12.14 `Me*` ≈ 6** (fTetWild 5 + trimesh 1) — fit existing mesh infra but some need mesh_builder
  n-gon-face / volumetric-oracle support.
- Numerous CORROBORATING (cross-loader confirmation of already-covered classes) — logged in the audit
  files, NOT synthesized; usable as cross-oracle Notes on existing entries.

**§12.15 BUILD — DONE (task #492, 2026-07-12).** Section stood up + 10 fixtures landed & CI-green
(commits faec7b2d, 7a7b61fe, 71a8ccf2). Raw malformed files checked in directly under
`import-examples/12-15-import-formats/` (NOT a Python writer — uses the explicit `Fixture path` catalog
field like §12.14). All 10 independently verified with trimesh 4.12 + pycollada; cross-oracle behavior
recorded per entry. Ip001-010: OBJ/PLY/OFF/glTF/COLLADA across index-OOB, count>body, accessor-overrun,
invalid-enum, negative-index, row-overflow. See [[project_section_12_15_import]].

**§12.15 BATCH 2 — DONE (2026-07-12).** 6 more text-format fixtures (Ip011-016), all independently
verified with trimesh 4.12.2 (+ pycollada 0.9.3 for COLLADA) before catalog write, per the verify-then-ship
discipline. Ip011 glTF node-matrix insufficient backing floats (assimp#6612, raises ValueError reshape);
Ip012 glTF componentType/data-layout mismatch (assimp#5683, silently corrupts all vertices to (0,0,0) —
no exception at all, the worst-case failure mode in the section); Ip013 PLY face index ≥ vertex count kept
UNvalidated on load — load succeeds, only `.triangles` raises IndexError later (deferred-validation gap,
distinct from Ip001/Ip010 which raise immediately); Ip014 COLLADA empty document / no library_geometries
(assimp#110, trimesh+pycollada tolerate cleanly — differential vs assimp's historical crash/hang); Ip015
PLY zero-count face element returns a `PointCloud` instead of `Trimesh` (trimesh's own `points_emptyface.ply`
test-corpus pattern, MIT) — `.faces` raises `AttributeError`, a silent-return-type trap on legitimate input;
Ip016 OFF negative face index kept UNvalidated — `.triangles` silently substitutes the wrong vertex via
Python/NumPy negative-index wraparound instead of erroring (the only variant in the section that neither
raises nor drops the face, but fabricates plausible-looking wrong geometry).

**Candidates tried and DROPPED this batch (documented for the next miner — don't re-attempt without new
tooling)**: OBJ `f` face with <3 vertex-refs / backslash line-continuation / face-like substring in
group-or-comment / vn-vt channel underrun (trimesh's OBJ loader handles all of these gracefully or ignores
vn/vt indices entirely — no observable defect via trimesh); OFF header-glued-magic / leading-comment
tokenization (trimesh parses both correctly); glTF LINE_LOOP<2 indices (confounded — trimesh drops ALL
LINE_LOOP primitives regardless of index count, so the fixture wouldn't isolate the <2-indices defect);
glTF primitive with no `indices` / TRIANGLE_STRIP mode (trimesh correctly reconstructs both topologies);
COLLADA declared-count-exceeds-body (`<float_array count=N>` or `<accessor count=N>` or `<triangles
count=N>` lying vs. actual body) — pycollada always trusts the real array/token length over the declared
XML count, so this whole class doesn't manifest via our available tooling; PLY negative index and PLY
face-list-count-prefix mismatch — technically load without erroring but couldn't get a byte-level
divergence as clean as Ip016's OFF version, so skipped as redundant/weaker.

**§12.15 REMAINING (paused — diminishing returns past ~18; each item below needs new tooling, needs a
loader we don't have (assimp/Open3D/tinygltf), or was tried-and-dropped above):**
- [ ] Remaining assimp classes needing assimp itself (not trimesh) to observe: glTF ExtractData-NULL
      #6609 (glTF 1.0, trimesh doesn't support v1.0 well), animation-channel-target-NULL #6611, degenerate
      UV → tangent-space OOB #6350 (trimesh doesn't compute tangent space), STL count/size #4304 (binary,
      out of this batch's text-only scope), OFF infinite-loop DoS #6604 (hard to pin statically, hang risk).
- [ ] Open3D cross-loader differentials (OBJ vertex-reference disorder, PLY RPly truncation/CRLF) — needs
      an `open3d` dependency, not yet tried; heavier install than trimesh/pycollada.
- [ ] **First FBX coverage** (deep-nesting #6501, PolygonVertexIndex #6635) — needs a minimal ASCII FBX
      that assimp/loaders will actually parse. Medium lift.
- [ ] **First 3MF coverage** (triangle-ref #1128) — needs a ZIP/OPC container writer. Bigger lift.
- [ ] **Draco `.drc` codec ≈ 8** — needs a binary `draco_encoder`-based writer; own sub-track.
- [ ] **PROPOSAL (maintainer decision): permanent §12.15 import oracle.** All 16 fixtures now verified
      with one-shot trimesh/pycollada scripts; a standing `_import_oracle.py` + pytest (loading each Ip*
      and asserting the recorded outcome) would make the section self-guarding like §12.14's mesh oracle.
      Deferred because it adds heavy deps (trimesh/numpy/pycollada) — belongs in the SLOW (validate-full)
      lane, not the fast push-gating lane. Needs your call on dep/CI cost.

**Wave 4 (NEW categories the corpus lacks entirely — need new section/infra):**
- [ ] **lib3mf / 3MF** (ZIP+XML/OPC container defects) — brand-new container-format category; needs new
      section + container-aware builder/validator. Bigger lift; scope separately.
- [ ] **buildingSMART ifc-gherkin-rules** — maintained executable taxonomy of malformed-input classes;
      mine rule names (ShapeFix-style) even if IFC-adjacent.

**Datasets to ingest as filters/seeds (license notes):**
- [ ] **Better STEP (`better-step/abs`)** — use as a FILTER to isolate the ~5% of Fusion360/ABC models
      that fail OCCT meshing (describe-only for the models themselves).
- [ ] **MeshRepairTestModels** — purpose-built broken meshes (small; verify license before ingest).
- [ ] CC3D scan meshes — richer but **describe-only** (signed agreement; do NOT ingest bytes).

**Explicitly deferred / out of scope:** LibreDWG (huge OSS-Fuzz/CVE crasher vein but DWG/DXF, not STEP —
hold unless scope expands to legacy 2D/3D CAD). Concurrency/thread-safety bugs (not encodable as a static file).

**Under-covered buckets these fill:** container-format (ZIP/OPC) defects; adversarial fuzz-crashers WITH
reproducers; independent-parser Part-21 lexical divergences (empty `()`, `DATA;`, non-ASCII); STEP↔mesh
round-trip divergence; PLY/OFF parser pathologies; producer-side degenerate-geometry recipes.

### Q5 — Silent-empty subset strengthening (DEFERRED-IN-PROGRESS)

**Why:** Per QUALITY_DASHBOARD, 88% of the ~755 silent-empty fixtures are
structurally inert under #N reference swap — i.e., random byte-flips look
identical to the catalog's intended defect. Strengthening = adding a
PRODUCT chain + real geometry that demonstrates the specific claim so the
fixture moves into the oracle-active subset.

**Status (2026-06-19):** Pilot of 5 §12-2a-pcurves fixtures pushed (commit
`29c1c03`). Sonnet rigorous verify caught **2/5 weak** (Gp007 FAILS_CLAIM,
Gp008 SLOPPY) — Opus regen'd both per Sonnet recipes; awaiting Sonnet
re-verify. Three Haiku scale-up chunks finished locally (97 more Gp
fixtures) but **discarded** — Haiku's 40% miss rate is unacceptable
under the quality bar; the local file changes were rolled back rather
than committed. New strategy: Sonnet-generates instead of Haiku-generates.
**Last touched:** 2026-06-19.

**Deferred (Q5 recon 2026-06-23 — oracle-active M-fixtures with oracle-invisible defect bytes):**
- M011: GVP inflation defect — the defect bytes are PROPERTY_DEFINITION_REPRESENTATION data (inflated volume=1.5, centroid offset) that OCC never reads during shape load; cube BRep is valid and always loads shape(1)/shape(1); byte mutations to the GVP section are oracle-invisible; only surrounding cube geometry mutations change tier-3 fingerprint. Defect is CONFIRMED in the valid cube + GVP chain (which carries the claim); cannot make the GVP values oracle-visible without adding a GVP checker that rejects on mismatch (OCC doesn't have one). Logged 2026-06-23.
- M014: GISU wrong-representation defect — the defect byte is the GISU.used_representation reference (#520 instead of #620); OCC silently heals/ignores the broken PMI link and loads shape(1)/shape(1); the broken GISU reference (#700 entity) is never checked during BRep load; byte mutations to the GISU or CGR section are oracle-invisible. Same structural limitation as M011: metadata-only, PMI checker would need to reject for mutation to flip. Logged 2026-06-23.

**Deferred (need bespoke regen per mechanism — not generic C-1 break):**
- Gp066: FixSameParameter selection-bias algorithm bug — cannot embed algorithmic selection in static STEP geometry; bytes can only encode the post-bug result (broken curve), not the trigger.
- Logged 2026-06-19 after Sonnet indep verify caught batch-7 mechanism mismatches.

**Deferred (signal(11) archetype — need OCC-crash template):**
- Gp096: CheckCurve3dWithPCurve direction-reversed-but-coincident — Expected occt=signal(11)/signal(11)
- Gp098: CheckOverlapping arc-tangent-to-line — Expected occt=signal(11)/signal(11)
- Gp099: FixSameParameter very-long-edge — Expected occt=signal(11)/signal(11)
- Gp101: CheckCurve3dWithPCurve sample-skip near-endpoint — signal(11)
- Gp102: FixAddPCurve toroidal projection — signal(11)
- Gp104: FixSameParameter offset-curve-3d — signal(11)
- Gp112: FixAddPCurve scaled-surface — signal(11)
- Gp113: CheckOverlapping different-curves-same-geometry — signal(11)
- Gp127: CheckCurve3dWithPCurve missing P-curve (FAIL1) — signal(11)
- Gp131: Confusion tolerance fallback — signal(11)
- Gp140: ShapeFix_ComposeShell.SplitByLine.pcurve-missing-skip — signal(11)
- Gp141: Missing PCurve Extraction Failure — signal(11)
- Gn003: BSpline curve with empty control_points_list — signal(11)
- Gn004: Complex BSpline surface entity with empty knots/multiplicities — signal(11)
- Gn043: nurbs signal(11) — to be addressed with signal(11) work later
- Gn055: nurbs signal(11) — to be addressed with signal(11) work later
- Gn058: nurbs signal(11) — to be addressed with signal(11) work later
- Gs026: surfaces signal(11) — to be addressed with signal(11) work later
- Gs134/136/137/138: surfaces signal(11) — defer to signal(11) work

**Deferred (nurbs Wave-B — mechanism encoded only as orphan entity, not wired into face pipeline):**
- Gn087: SetUSplitValues neg-zero dedup — defect is pure OCC runtime behavior of SetUSplitValues([-0.0, 0.5, 1.0]); -0.0 cannot be encoded in STEP knot literals (which serialize as "0.0"). The fixture was indistinguishable from a plain flat patch + C-1 driver. No encodable trigger.
- Gn110: ConvertSurfaceToBezierBasis trim-ignored — catalog claims defect is triggered by an inner FACE_BOUND trim at 0.25..0.75, but Sonnet's fixture only emitted FACE_OUTER_BOUND with full extent. Needs explicit inner trim loop on the surface to actually trigger the documented behavior.
- Gn160 (periodic B-spline parameter wrapping): live oracle returns empty/empty but Sonnet's analysis says geometry should load — fixture wires periodic B-spline as edge 3D curve on plane face, OCC rejects but mechanism narrative is unclear. Needs investigation of WHY OCC rejects.
- Gn162 (B-spline interior knot mult=degree+1 Bezier-join): live oracle empty but Sonnet's analysis says tangent-only break should load — fixture wires the discontinuous B-spline as defect 3D curve; OCC rejects for unknown reason. Needs investigation.
- Logged 2026-06-20 from batch 49 indep verify systemic finding: Sonnet keeps building B-spline surfaces as orphans alongside the face's flat-plane geometry instead of swapping them in. Affects batch 49 final-nurbs trio.
- Ps004, Ps005 (shells): Sonnet attempted post-hoc entity-args mutation (`ent.args[0].append(msb2)`) but ADVANCED_BREP_SHAPE_REPRESENTATION's items arg is stored as a string, not a list. Needs proper builder support for multi-MSB shape representations or a different mechanism encoding.
- Logged 2026-06-20 from batch 31 indep verify systemic finding.
- Reason: signal(11) requires engineering a deliberate OCC SIGSEGV; Wave-B Sonnet pipeline doesn't have a template for this yet. Gp001 is the existing reference but is a hand-authored .stp without a fixture_source.py. Need to (a) reverse-engineer Gp001's crash trigger or (b) propose a new builder API for signal-11 fixtures.
- Logged 2026-06-19 from batch 13-18 archetype-aware scans.

- Twi047 (wires): Sonnet used `f.axis2_placement_2d()` which doesn't exist in builder. Needs alternative — perhaps `_emit_raw('AXIS2_PLACEMENT_2D(...)')`.

**Deferred (builder API gaps — mechanism can't be encoded in STEP-as-supported):**
- Gp105: CheckOverlapping zero-tolerance-overlap — UNCERTAINTY=0.0 requires injection into the geom_ctx that wraps the shape representation; current builder's add_product_chain hardcodes UNCERTAINTY=1e-7 in the geom_ctx, so a fresh zero-tolerance UNCERTAINTY entity ends up as an orphan and OCCT never sees it. Need builder hook to override geom_ctx UNCERTAINTY.
- Gp108: CheckPCurveRange B-spline-out-of-knot — catalog describes pcurve knots [0,2] used at edge vertex parameters [-1,6]; STEP EDGE_CURVE has no explicit parameter-bounds field, so the out-of-domain claim can't be structurally forced. Need TRIMMED_CURVE wrapper or DEFINED_FUNCTION trick.
- Gp151: CheckPCurveRange periodic_range_semantics — catalog requires pcurve range with first>last (e.g. [5.5, 0.8]) to trigger CheckPCurveRange's wrap-around line 1007; STEP LINE pcurves are monotone by construction (CARTESIAN_POINT + VECTOR), so the non-monotonic range is not encodable as a plain pcurve. Need either explicit TRIMMED_CURVE with U1>U2 (rare in STEP) or COMPOSITE_CURVE_ON_SURFACE workaround.
- Gp165: vertex_tolerance_mismatch_1971 — catalog claims heterogeneous per-vertex tolerances (0.001..0.2 spread) trigger ShapeFix_Edge::FixSameParameter line 1971 unsorted-aTolVerSeq path. Builder has no per-vertex tolerance hook (no VERTEX_TOLERANCE entity emission), and the only global tolerance is via geom_ctx UNCERTAINTY which is uniform. Need builder hook for per-VERTEX tolerance entities.

**Deferred (nurbs Wave-B — OCC heals despite catalog `empty` claim; need stronger triggers):**
- Gn002: RATIONAL_BSPLINE NbWeights ≠ NbControlPoints — Sonnet-built RATIONAL_BSPLINE complex entity with weights row=3 vs CPs row=4; OCC heals to shape(1) instead of expected empty. Recipe: try mismatch in 1D row (curve) only, or use degenerate weights (0.0 or negative) that explicitly violate NURBS evaluation.
- Gn007: undersampled helical thread B-spline — Sonnet-built 16-CP degree-3 helix at radius 5 with 333 turns/span; OCC accepts. Recipe: make CP positions internally contradictory (e.g., consecutive CPs at identical 3D location forcing zero arc-length segment), or use degree-1 polyline with sharp angles.
- Gn008: cusp at mult=degree — Sonnet-built degree-3 with knot mult=3 + 1.5-unit CP gap; OCC heals. Recipe: increase cusp magnitude (5-10 unit gap) or use mult > degree (would also trigger ParseError, not heal).
- Logged 2026-06-19 — OCC heals when interior structural validity (NbCPs, mult sums, monotonicity) holds even with semantic issues. Need defects that break invariants OCC validates at load time.
- Logged 2026-06-19 from batch 14 indep verify SLOPPY verdicts.

**Plan:**
- [x] Q5.0 Pilot: 5 Gp fixtures pushed (`29c1c03`)
- [x] Q5.1 Sonnet verify pilot 5 → 2 STRONG, 1 WEAK_PASS_OK, 1 FAILS, 1 SLOPPY
- [x] Q5.2 Opus regen Gp007 + Gp008 per Sonnet recipes (awaiting re-verify)
- [x] Q5.3 Discard Haiku-generated chunks 1-3 (40% slop rate; rolled back locally, never pushed)
- [ ] Q5.4 Architecture: Sonnet-generates the fixture, Sonnet-self-verifies the bytes match the claim, only commit when STRONG_PASS. Opus regen on STILL_FAILS.
- [x] Q5.6 Pilot 2 (2026-06-25): 3 manual-chain Gp fixtures refactored to add_product_chain — all 3 STRONG_PASS (10/10 mutation detection): Gp074 (FP cliff), Gp078 (near-degenerate), Gp165 (heterogeneous vertex tol, restructured from WIREFRAME to ADVANCED_FACE, oracle shifted to shape(1)/shape(1))
- [ ] Q5.5 Re-attack the remaining manual-chain + unstrengthened silent-empty entries under new architecture, in small batches with Sonnet verification gating every commit.

**Survey note (2026-06-25):** Only 3 candidates remain without add_product_chain in priority sections (Gp074/078/165 — now done). All Twi/Tsh/Gs entries with occt=empty already use add_product_chain. N-tolerance and U-units sections have oracle-invisible defects (tolerance/unit context not read during BRep load) — cannot be made STRONG_PASS via BRep embedding; WEAK at defect-specific byte level.



### B1 — Mine OCCT's `tests/` tree for parsing-wisdom coverage — WAVE 1 DONE

Wave-1 result: 3 / 449 OCCT prose tests synthesized as novel fixtures.
0.67% novelty rate. The OCCT tests/ corpus is **saturated** against our
catalog — further mining waves here are diminishing returns. See
DONE.md and `audit/occt_mining_log.md` for details. Skip remaining
sub-steps; pivot to B4 (issue trackers) for non-saturated sources.

### B1-archive — original B1 plan (now wave-1 complete):

**Why:** OCCT's `tests/de/step/*` and `tests/bug/*` directories are the most
concentrated record of 20+ years of accumulated STEP-parsing healing in
existence. Sampling these and synthesizing pattern-matched fixtures
captures tacit knowledge not surfaced by the v3 method-deep-pass.

**Status:** Not started.
**Last touched:** 2026-06-18.

**Plan:**
- [ ] B1.1 Clone OCCT (or pin a specific commit hash) to a scratch dir under
      `/tmp/occt-mining/`. Verify license is LGPL — we synthesize from
      pattern, never copy bytes.
- [ ] B1.2 Enumerate test files. Catalog directory structure: `tests/de/step/`,
      `tests/bug/`, `tests/parser/`, etc. Count `.stp` and `.step` files,
      record total.
- [ ] B1.3 Build a 30-fixture random-stratified sample across directories.
      For each, extract: (a) the OCCT test recipe (what defect it exercises),
      (b) the entity types involved, (c) the unique structural signature.
- [ ] B1.4 For each sampled fixture, search the existing catalog for an
      already-covered defect. Record match/no-match. Goal: measure
      *novelty rate* = (no-match / total). This tells us the convergence
      signal asked about elsewhere.
- [ ] B1.5 For the non-match subset, synthesize new fixtures via the Python
      builder. Match the defect pattern; do NOT copy any OCCT bytes.
      Add to `step-examples/` + catalog.
- [ ] B1.6 Run the adversarial-verify loop (Haiku → Sonnet) on the new
      fixtures to bring them to the 98%+ VALID bar.
- [ ] B1.7 Record per-wave novelty-rate in `audit/mining_novelty_log.md` so
      we have a trendline.

**Estimate:** 1-2 days for B1.1–B1.4 (mostly exploration); 3-5 days for
B1.5–B1.6 per wave of ~30 fixtures.

**Hazards:** Easy to drift into "interesting" rabbit holes in OCCT source.
Stick to the test corpus, not the implementation. Resist the urge to
also-read `src/ShapeFix/*` while there.

---

### B2 — Tier-3 assertion harvest (byte → runtime promotion)

**Why:** Byte assertions break under formatting normalization; tier-3
invariants survive whitespace/comment changes and are the strongest
evidence the catalog carries. Single biggest crispness lever.

**Status:** Substantially done. Coverage 12% → 85% across 5 batches.
B2.5 deferred (introspection extension would be required to climb
higher; 343 remaining entries don't fit current introspection).
**Last touched:** 2026-06-19.

**Plan:**
- [x] B2.1 Enumerate byte assertions. Done (1578 contains / 410 count /
      etc.).
- [x] B2.2 Candidate list. Done.
- [x] B2.3 Existing tier-3 introspection sufficient (shape_null,
      n_faces_total). No extensions needed for the first 1433 promotions.
- [x] B2.4 Batches 1–4 applied (97 + 389 + 517 + 430 = 1433 promotions).
      All validated against live tier3.
- [x] B2.5 Batch 5: 449 soft load==ok promotions. Coverage 73% → 91.9%
      entries with tier-3. Remaining ~343 entries need tier-3
      introspection extension (e.g. specific knot multiplicity, surface
      type fingerprint) — deferred as B2.5b. Commit `b1298a0`.
- [x] B2.6 Tier-3 ratchet pytest at 90% floor. Commit `db38a48`.
- [ ] B2.5b Extend tier-3 introspection to cover more catalog claims
      (knot vectors, periodicity flags, NURBS rationality, edge-loop
      orientation). Each extension ~1-2 hours of code + tests.

---

### B4 — Mine real-world issue trackers for independent-provenance fixtures

**Why:** The catalog grew from OCCT source + literature + LLM deep-passes —
all *internal* views of what defects exist. Sampling real bug reports from
OSS issue trackers (FreeCAD, Solvespace, OCCT MANTIS, libIGES, py-OCC,
trimesh, etc.) gives independent provenance: *what users actually hit*,
not just what theory or source-code reading predicts. Cross-validates
coverage, sharpens bug-reporter-search vocabulary (already a tracked
metric: 1127 `Synonyms:` lines and 174 BM25 regression queries), stays
LGPL-clean because we synthesize pattern-matched fixtures, not copy bytes.

**Status:** Wave-1 (FreeCAD/OCCT/IfcOpenShell) done — 17 NOVEL synthesized.
Wave-2 (solvespace/pythonocc-core/cascadio/3MFConsortium) done — 10 NOVEL
synthesized; trimesh-direct and 3MFConsortium saturated. Wave-3
(KiCad/CadQuery/OCE/FreeCAD-extended/KiBot/Blender-addon) done — 8 NOVEL
synthesized; 9.3% yield (down from wave-2's 10.5% and wave-1's 24.6%) —
saturation signal. Next: wave-4 pivot to commercial-tracker bug-fix
changelogs (Solid Edge, NX, Inventor) or academic CAD-interop papers —
deferred since FOSS surface is saturating.
**Last touched:** 2026-06-19.

**Plan:**
- [ ] B4.1 Identify target trackers and choose 4-5: FreeCAD GitHub issues,
      Solvespace GitHub, OCCT MANTIS, libIGES, py-OCC, trimesh, pythonOCC,
      blender STEP import bugs. Pick by activity + bug-report quality.
- [ ] B4.2 Build a sampler. For each tracker, fetch 30-50 recent
      STEP-related bug reports (via GitHub API + label filter / MANTIS
      query). Save title + body + attached file links to a local
      `audit/bug_mining/<tracker>/<id>.json`.
- [ ] B4.3 For each sampled report, extract: (a) the defect *pattern*
      described, (b) entities/values implicated, (c) what was wrong from
      the user's perspective. NEVER download attached STEP files — we
      synthesize from pattern, never copy.
- [ ] B4.4 Match against existing catalog. For each report, run the BM25
      bug-search to find the top-3 catalog entries. Tally hit-rate:
      *novelty rate* = (no-good-match / total).
- [ ] B4.5 For non-matches, synthesize new fixtures via the builder.
      Adds entries to `step-examples/` + catalog.
- [ ] B4.6 Run the adversarial-verify loop to bring novelties to the
      98%+ VALID bar.
- [ ] B4.7 Log per-wave novelty-rate in `audit/issue_mining_log.md`.

**Estimate:** B4.1–B4.3 ~1 day (sampling infra); B4.4 ~1 day (match
analysis); B4.5–B4.7 scales with novelty rate. If novelty is ~20% as
expected, 30 reports → ~6 new fixtures per wave.

**Hazards:** Issue-tracker terms-of-service usually require attribution
on direct quotation. We synthesize, don't quote, but record the source
ticket ID in `Sources:` field so provenance is preserved. Watch for
private/customer-confidential reports — skip those.

### B3 — Cross-kernel validation matrix

**Why:** Each fixture currently runs through OCCT + gmsh + ifcopenshell.
Adding CGAL, Geogram, OpenSCAD/libfive, and (eventually) the user's own
kernel produces a differential truth table per fixture. For a kernel-grading
corpus, this is the whole game — disagreements between kernels are the
single most informative signal. Expect surprises: fixtures that demonstrate
*different* defects than intended, "broken" fixtures that no kernel
flags, "clean" fixtures that crash one kernel and not others.

**Status:** B3.1 + B3.2 survey complete 2026-06-24 (see below). B3.3 pending.
**Last touched:** 2026-06-24.

**Plan:**
- [x] B3.1 + B3.2 Kernel landscape survey + install matrix done 2026-06-24
      by Sonnet sub-agent. Verdict: existing matrix already has 2 fully
      independent STEP oracles (OCC + solvespace); next gap is a third
      independent **B-rep** oracle, with a complementary mesh-layer
      oracle as the second add. Ranked top-2:
      - **#1 pilot: BRL-CAD `step-g`** — fully independent STEP reader
        via STEPcode (NIST PDES, not OCC). BSD license. Subprocess
        pattern matches `_solvespace_oracle.py`. macOS: `.dmg` from
        brlcad.org releases; Ubuntu CI: pinned `.tar.bz2` download
        (~5min). No GL dependency. Highest oracle-independence value.
      - **#2: CGAL PMP** — post-tessellation mesh oracle, complementary
        to manifold3d (catches segment-pair self-intersections that
        Euler-characteristic checks miss). `brew install cgal` /
        `apt-get install libcgal-dev`. LGPL-3.0; subprocess-isolated
        so MIT-clean. Requires `cgal_pmp_check.cpp` helper binary.
      Rejected: Geogram (no STEP), OpenSCAD/libfive (OCC-backed STEP),
      OCE/pythonocc-core (duplicate OCC), libIGES/lib3mf (wrong format),
      cascadio (bundles OCC), meshlib (proprietary), pymeshfix (mesh-only,
      duplicates manifold3d's domain).
- [ ] B3.3 Wire BRL-CAD `step-g` first as `_brlcad_oracle.py` following
      `_solvespace_oracle.py` pattern. Output schema:
      `{status, n_regions, n_solids, stderr_tail, duration_ms}`.
      Then wire CGAL PMP as `_cgal_oracle.py` with companion C++ helper.
- [ ] B3.4 Add per-kernel JSON output to validate2 schema. Each oracle
      emits `{loaded, n_faces, n_edges, n_solids, error, error_class}`
      with consistent vocabulary.
- [ ] B3.5 Run the full corpus through both new oracles. Persist results.
- [ ] B3.6 Diff-detection pass: for each fixture, compute a kernel-agreement
      signature `(occt_status, gmsh_status, cgal_status, ...)`. Cluster by
      signature. Surface signatures with N=1 (one kernel disagrees) as
      audit candidates — these are the highest-information fixtures.
- [ ] B3.7 For each high-disagreement cluster, do a manual sanity check:
      which kernel is "right"? Update catalog with cross-kernel notes.
- [ ] B3.8 Add the user's own kernel as a third (later: primary) oracle
      when ready.

**Estimate:** Open-ended. B3.1–B3.4 ~2-3 days; B3.5 is mostly compute time;
B3.6–B3.7 will reveal new work proportional to how many disagreements
surface.

**Hazards:** Installing geometric kernels can be slow + fragile in CI
(libGLU, etc.). Budget for environment debugging. Each new oracle is a
new flaky-CI surface.

---

## Smaller queued items

### Q8 — nightly `validate-full` workflow swallows its own DRIFT list on failure

**Not fixed here** (infra change needs separate review — this is a report-only note per scope
discipline). Found 2026-07-12 while resolving 9 DRIFT fixtures flagged by the nightly run: the
workflow step that prints the DRIFT summary captures the validator's stdout with
`out="$(...)"` while the script has `set -e` active. If the validator's own exit code is
non-zero (which it legitimately is whenever DRIFT entries exist), the `$(...)` command
substitution's failure aborts the script *before* the subsequent `echo "$out"` runs — so the
DRIFT list never reaches the job log, even though the job itself correctly goes red. This is why
today's + this morning's runs both had to be diagnosed from the raw
`/tmp/cad-v2-out*` JSON artifacts rather than the workflow's own summary output.
**Fix** (for whoever picks this up): `out=$(...) || status=$?` to capture the exit code without
tripping `set -e`, *then* `echo "$out"`, *then* `exit "${status:-0}"` (or equivalent) so the
summary always prints regardless of whether the validator found DRIFT. Locate the offending step
in `.github/workflows/` (the nightly `validate-full` job) and apply the same pattern anywhere else
in that workflow captures oracle-script stdout under `set -e` before echoing it.

### Q7 — Mutation-snapshot refresh (oracle-machine chore)
`tests/data/mutation_snapshot.json` (2026-07-02) does not yet cover 14 bytes-only STEP fixtures added
2026-07-11/12 (ruststep Lh051/Ls053-056, NIST Pmi156-164). Not a blocker — `test_bytes_only_are_undetected`
now treats snapshot-missing entries as a non-fatal NOTE (only DETECTED fails), and the 95%-coverage floor
still guards staleness. But the snapshot can only be regenerated on a machine with the live occt oracle
(CI): `cd validation && uv run python -m step_corpus._mutation_test --all --mutations 3 --workers 8 --out
/tmp/qmut_full.json`, then copy to `tests/data/mutation_snapshot.json`. Do on next oracle-machine session.

### Q1 — 23 CONFIRMED_WEAK fixtures, bespoke regens — DONE

### Q2 — Stale-doc refresh

- [x] `QUALITY_DASHBOARD.md` — refreshed 2026-06-19 to 2329 entries
      (commit `4c3f1d7`); re-refreshed 2026-06-24 with mesh+Q5 progress
      (commit `07f37ab`).
- [x] `CODEBASE_LANDSCAPE.md` — coverage-status addendum added 2026-06-24
      noting OCCT v2 + MeshFix/CGAL PMP + B4 mining progress; priority
      #3 (CGAL PMP deeper pass) marked substantively covered.
- [x] `validation/VALIDATION_SUMMARY.md` — refreshed 2026-06-19
      (commit `4c3f1d7`); re-refreshed 2026-06-24 with live
      `_final_verdict` numbers + post-rebaseline verdict matrix.

### Q3 — Phase 7 backlog (75-fixture A6 audit groups) — CLOSED 2026-06-24

Audit complete. Punch list at `audit/A6_audit_groups_punch_list_2026-06-24.md`.

- Group 1 (no-bounds ADVANCED_FACE, spec 24): done — 0 build errors,
  3 intentional KEEPs (Tfa002, Ad015, Tsh229 — all verified).
- Group 2 (EDGE_LOOP doesn't chain, spec 23): 26 fixtures in bytes
  but all are intentional — catalog titles describe wire ordering /
  scrambled edges / FixReorder behavior. Spot-checked Twi003 / Twi078
  / Pf024. KEEPs.
- Group 3 (empty EDGE_LOOP, spec 11): done — 0 build errors, 9 KEEPs.
- Group 4 (EDGE_CURVE twice same orient, spec 17 → 10): 4 fixtures
  in bytes (Bo006, Tfa028, Wr055, Xp012) — all are intentional per
  catalog mechanism claims. KEEPs.

The original 75-fixture spec was a "fix build errors" punch list;
the build errors were fixed during prior Q3 work, and the remaining
structural patterns are by-design defects. Task #116 closed.

### Q4 — Mesh-fixture format (Python builder + JSON serialization)

**Why:** STEP isn't a mesh format and no existing mesh format (OBJ, PLY,
STL, glTF) carries the richness needed to express most MeshFix/CGAL PMP
defects. The Python-builder pattern that worked for STEP fixtures works
just as well here: define a Mesh model that emits **numerically
defective JSON** (a non-manifold mesh has three triangles literally
sharing an edge in the triangle list; a degenerate triangle has its
zero-area indices right there; near-coincident vertices have distinct
entries at sub-tolerance positions). The defect IS in the geometry;
healers don't get a free pass. We invent our own format but it's
deliberately simple and the *real* artifact is the in-memory model.

**Status:** Substantially done. 5 mesh fixtures (Me001-005) +
mesh_builder + PLY/OBJ co-emit + pure-Python oracle in place. Future
work: CGAL PMP / MeshFix wrapper for cross-kernel mesh validation.
**Last touched:** 2026-06-19.

**Plan:**
- [x] Q4.1 Draft `mesh_builder.py` skeleton. Done in cc855c9.
- [x] Q4.2 Define the JSON schema v0. Done in cc855c9.
- [x] Q4.3 First-cut mesh fixtures (Me001–Me005). Done in cc855c9.
- [x] Q4.4 PLY/OBJ co-emit interop. Done in 328237c.
- [x] Q4.5 Pure-Python mesh oracle (`_mesh_oracle.py`). Done in e798987.
      Subprocess-isolated CGAL PMP / MeshFix deferred to v1.4+.
- [x] Q4.6 Naming + extension chosen: `.mesh.json`. Catalog enums
      added. Done in ad3328a + d53b5c6.

**Estimate:** 1-2 days for Q4.1–Q4.3 (skeleton + first 5 fixtures); the
catalog + oracle work scales with how many defect classes we synthesize.

**Hazards:** Risk of bikeshedding the JSON schema. Keep the first cut
narrow — 3-4 defect types — and let real fixtures pull on the schema as
they need it.

---

## Done

See `DONE.md` for completed work history.
- Le059 (encoding): catalog wants raw Latin-1 byte 0xE4 in .stp, but fixture_source_check's UTF-8 read_text round-trip cannot reproduce from a builder-generated render(). Either: (a) update builder write/read to support raw bytes, or (b) exempt Le059 from round-trip check.
- Le031 (encoding): catalog byte assertion `bytes_starts_with(b'\xff\xfe')` requires raw UTF-16 LE BOM bytes which are never produced by UTF-8 encoding in the fixture pipeline. The 0xFF and 0xFE bytes are not valid UTF-8 sequences. Fixture source deferred; requires either a binary-write mode in StepFile or a special exemption in _fixture_source_check. The Le031.stp continues to use the original hand-crafted file (starts with c3 bf c3 be = UTF-8 for ÿþ, not the actual FF FE bytes). The existing byte assertion was already failing before this session.

---

## Mesh-defect §12.14 expansion (deferred 2026-06-21)

§12.14 currently has 4 mesh-defect catalog entries (Me001-004) wrapping
the `mesh_builder` + `mesh-examples/12-14-mesh/*.mesh.json` pipeline.
The `MESH_DEFECT_TAXONOMY.md` source referenced by Me001 enumerates many
more defect classes worth covering: non-manifold edges/vertices (extra),
zero-area triangles, near-coincident vertices, T-junctions, boundary
holes, normal flips, self-intersection, slivers, hanging vertices,
duplicate triangles, inverted winding, etc.

**Target:** expand §12.14 from 4 → ~30-50 entries.

**Tradeoff:** different fixture-kind (JSON not STEP) means the existing
Python tooling/lint/oracle wiring needs to grow to cover it — not just
authoring. `_mesh_oracle.py` exists (Q4.5) but coverage and category-lint
treatment are sparse.

**Why deferred:** the user prefers to land quality (validate2 reconciliation
of the 470 fixtures shipped 2026-06-21) before expanding scope.

**How to apply:** when the kernel needs to be tested against meshing/
tessellation defects, this section is the gap. Treat as a Q5 ticket once
quality work clears.

## Deferred wave-7 items — need oracle verification

### DEF-MM (AP242 Ed.1 kinematic module): REVOLUTE_PAIR + KINEMATIC_JOINT + KINEMATIC_LINK
Two-link mechanism (rectangular prism + shorter prism) connected by revolute joint J1
(axis Z, range ±90°). Requires an AP242 Ed.1 kinematics-capable oracle (HOOPS Exchange
or STEP Tools ST-Developer) to verify Expected validation. OCCT 7.x + FreeCAD only
read the geometry, so encoding without oracle verify would produce speculative Expected
lines. Defer until such an oracle is wired.
Source: FreeCAD issue #19795; OCCT STEP translator docs.

## Deferred wave-9 items — need HOOPS Exchange / ST-Developer / AP242 Ed.4 schema

Wave-9 mining (2026-07-02) sampled 25 defects across AP242 XML Kinematics Recommended Practices
(2021), CAx-IF Round 56J (Aug 2025), AP242 Ed.4 (Aug 2025), and OCCT tracker 2024-2026.
Novelty rate: 22/25 = 88% (record). Full audit: `audit/b4_mining_wave_9_2026-07-02.md`.

All 22 novel items are deferred because they require an AP242 Ed.1/Ed.4 kinematics-capable
oracle (HOOPS Exchange, STEP Tools ST-Developer) or the AP242 Ed.4 EXPRESS schema to verify
Expected validation. OCCT 7.x/8.0 either drops the entities silently (leaving Expected
speculative) or lacks the kinematics module entirely. The wave-7 DEF-MM pattern (deferred
same reason) applies.

- **DEF-FFF/GGG/HHH/III/JJJ** (F01-F05, HIGH): AP242 XML Kinematics receiver-side gaps —
  `spherical_pair_with_pin`, `unconstrained_pair`, `universal_pair`, CV joint, `rolling_curve_pair`.
- **DEF-KKK/LLL/MMM/NNN/OOO/PPP** (F06-F11, HIGH): AP242 XML Kinematics Bugzilla schema holes
  and receiver silent-drops (rolling_surface_pair, KinematicLinkToOccurrenceAssociation cardinality,
  LowOrderKinematicPairWithMotionCoupling link limits, ProductStructureKinematicPathAssociation
  property gap, Substructure reference gap, spherical_pair 3-axis limits).
- **DEF-QQQ/RRR** (F12, F16, HIGH): planar_pair 3-attr limits + EXPRESS SELECT XSD "combined" restriction.
- **DEF-SSS** (F17, HIGH): OCCT #384 tolerance polymorphism — `StepRepr_ReprItemAndLengthMeasureWithUnitAndQRI`
  not recognized as `MEASURE_WITH_UNIT` by 21 tolerance-reader classes. Closed with fix in OCCT 8.0.
- **DEF-TTT..DEF-AAAA** (F13-F15, F18-F25, MEDIUM/LOW): CAx-IF Round 56J validation-property
  partial-match, AP242 Ed.4 STRUCTURAL_JOINT+xMCF fastener, OCCT #430 seam-vertex duplication,
  and other lower-confidence items.

Note: AP242 Ed.3 (2022) was corrective maintenance and added NO kinematics entities.
Kinematics lives in Ed.1 (DEF-MM, already deferred) and Ed.4 (Aug 2025). The wave-8
audit's "AP242 Ed.3 kinematics" hypothesis was wrong; wave-9 confirmed.

## DEF-GMSH-DRIFT — gmsh entity-count platform divergence (2026-07-03, RESOLVED)
Nightly validate-full runs 28575794898 (07-02) and 28653762990 (07-03) both
flagged Gs056 + Twi035 as DRIFT: gmsh entity count (importShapes+synchronize
+OCCAutoFix `getEntities` total) was catalog shape(10) but CI produced
Twi035 shape(5), Gs056 shape(12). OCCT stayed shape(1)/shape(1).

**Diagnosis (investigated, confirmed — NOT nondeterminism):** Ran the exact
production gmsh metric 6× in fresh subprocesses locally (gmsh 4.15.2, ARM
macOS): Gs056 and Twi035 are rock-stable at **10** every run — matching the
original catalog baseline. A spread of controls (Pf001=9, Pf005=15, Pf020=27,
Pf034=9, Pf008=900, Pf033=1296) all matched catalog exactly and were stable.
Both CI nightlies (Linux x86_64, same gmsh 4.15.2) agree at 12/5. So gmsh is
**deterministic per-platform**; the two values differ because OCCAutoFix
healing of these 2 borderline geometries is FP-sensitive across macOS-ARM vs
Linux-x86. The original shape(10) baseline had been set from a local macOS
run; CI (the authoritative nightly env) has consistently been 12/5.

**Fix:** rebaselined Expected to the CI/Linux values (12,5) in 2e0aab1a —
matches both nightlies, so validate-full goes green and stays green.
Recurrence risk is LOW (CI deterministic). Only 2 of 1085 gmsh shape(N>1)
fixtures diverge across platforms — the gmsh oracle is 99.8% platform-stable.

**Latent process note (no action needed now):** gmsh shape(N) baselines must
be sourced from CI-Linux, not local macOS, for borderline-healing geometries.
The other 1083 gmsh fixtures are platform-agnostic.

## DEF-MUT-DEPTH — deeper mutation run saturates bytes-only metric (2026-07-04, RESOLVED: keep depth-3)
Ran the experiment suggested in commit 1c50062f ("bump --mutations 3→10-20
for more stable bytes-only tags"): full-corpus `_mutation_test --all
--mutations 15 --seed 1`. **Result: the metric saturates.** Depth-3 had 138
`undetected`; depth-15 has **0 undetected** (2384 detected, 9 no-target-byte).
A deeper run would reclassify **all 41** `bytes-only` entries as detected →
downgrade to `bytes-sufficient`, erasing the category.

**Why that is WRONG (verified):** `_mutation_test` flips a *random* digit
anywhere in the DATA section and calls it `detected` if any oracle spec
changes. That is a general numeric-sensitivity probe, NOT a test of whether
*this fixture's defect* is oracle-invisible. Example Le004 (`\X\` string-escape
with bad hex, tagged bytes-only): its defect is pure string/metadata OCC never
reads at BRep load (`occt=empty/empty`), yet at depth 15 a random coordinate/
entity-ref flip trivially changes some spec → "detected". That detection is
unrelated to the actual defect. So the 41 bytes-only tags remain CORRECT;
depth-15 detection is noise.

**Decision:** keep the committed depth-3 snapshot + current 41 bytes-only tags
(self-consistent, CI-green). Do NOT bump `--mutations` for bytes-only
validation — it is the wrong lever. This supersedes the 1c50062f note.

**Proper hardening (proposal, do NOT build without sign-off):** a
*defect-targeted* mutation test — mutate a byte *inside each fixture's own
`Byte assertion` region* and confirm no wired oracle notices. That directly
validates the bytes-only claim, unlike random-digit probing. Larger infra
change; propose separately per scope discipline.

## B4 wave-10 mining — 3 fresh seams (2026-07-04, research only; synthesis deferred)
Three parallel research agents mined new sources (OCCT issue tracker, real-world
CAD/exporter forums, ISO-10303 Part-21 e3 conformance). Candidates below are
DEFERRED to fixture synthesis under user quality oversight (Sonnet-gen bar) —
NOT auto-synthesized. Dedup notes from noisy catalog greps; verify at synth time.

### Tier 1 — OCCT tracker minimal reproducers (highest confidence, likely novel)
- **DEF-W10-A**: `DIRECTION('',())` empty direction_ratios → null-deref crash in
  StepGeom_Direction::NbDirectionRatios during TransferRoots. §12.2c/§12.1c.
  Catalog grep 0 hits → NOVEL. (OCCT Mantis 33665)
- **DEF-W10-B**: `TESSELLATED_SHELL('',(),$)` empty required items set → crash in
  STEPCAFControl_Reader. §12.14 mesh (tessellated-entity arity). (OCCT #667)
- **DEF-W10-C**: ORIENTED_EDGE pair with cyclic EdgeStart/EdgeEnd self-reference →
  unbounded reader recursion / stack overflow (DoS topology). §12.3b wires.
  (PrusaSlicer #11305) — distinct from existing wire defects; verify vs cyclic-loop entries.
- **DEF-W10-D**: COMPOUND_REPRESENTATION_ITEM wrapping SET_REPRESENTATION_ITEM of a
  DESCRIPTIVE_REPRESENTATION_ITEM → item_element resolves NULL (silent incomplete
  read). §12.7 PMI. (OCCT #1283)
- **DEF-W10-E**: edge pcurve list where index-0 pcurve is always NULL →
  GlueEdgesWithPCurves/UnifySameDomain silently drops all pcurves (wrong-heal).
  §12.2a pcurves. (OCCT #966)
- **DEF-W10-F**: small-unit body read with xstep.cascade.unit=M → infinite/degenerate
  scale geometry (unit-scale interaction, not just wrong scale). §12.5 units. (OCCT #512)
- **DEF-W10-G**: assembly STEP (Catia/NX-readable) → STEPCAFControl_Reader.Transfer
  never terminates (hang, not crash). §12.6/§12.10. (OCCT #712; Mantis 31711)

### Tier 2 — real-world writer pathologies (CAD forums, med-high novelty)
- **DEF-W10-H**: B_SPLINE knot multiplicity > degree+1 at ends / > degree interior
  (Fusion T-spline→NURBS export). §12.2b nurbs. (Autodesk forum)
- **DEF-W10-I**: elliptical arc revolved 360° with major axis on X → re-imports fused
  with own mirror; Y-axis fine — axis-sign-dependent revolution seam. §12.2c/§12.13.
  (FreeCAD #14447)
- **DEF-W10-J**: closed solid downgraded on export to SHELL_BASED_SURFACE_MODEL /
  loose faces despite watertight source ("imports as surfaces not solid"). §12.3a/§12.13.
  (FreeCAD #20588, #16292)
- **DEF-W10-K**: PRESENTATION_STYLE_ASSIGNMENT with forward/invalid record index →
  "Encountered invalid record index". §12.1c/§12.13. Catalog grep 0 hits → novel.
- **DEF-W10-L**: model far from origin (huge coords) → precision below
  Precision::Confusion, geometry collapses on import. §12.5/§12.4. (OCCT STEP guide)
- **DEF-W10-M**: AP214 root carrying duplicate ADVANCED_FACE copies alongside
  MANIFOLD_SOLID_BREP (redundant top-level faces). §12.13/§12.3a. (dev.occ forum)

### Tier 3 — Part-21 edition-3 structural (novel axis, some prior wave-7/8/9 overlap)
- **DEF-W10-N**: `@`-value-instance refs (`@70`, leading-zero `@023` alias) where `#N`
  expected. §12.1c. Corpus is `#`-centric, 0 "value instance" hits → novel.
- **DEF-W10-O**: named/multi DATA sections `DATA('DS1',('GEOMETRY'));` w/ independent
  populations. §12.1c. Verify vs existing multi-DATA entries.
- **DEF-W10-P**: raw UTF-8 octets embedded directly in string (e3 dual-encoding path)
  vs `\X2\` escaping. §12.1a.
- **DEF-W10-Q**: `\X4\0000F600\X4\0\` 32-bit astral/emoji codepoint escape. §12.1a
  (thin: 5 `\X4\` hits — verify).
- **DEF-W10-R**: SIGNATURE section (base64 CMS/RFC-5652) before ENDSEC. §12.1b.
- **DEF-W10-S**: EXPRESS named-constant refs `#INCH`, `@PI` as attribute values. §12.5.

**Next step (needs user):** pick a Tier-1 batch (the empty-mandatory-aggregate crash
family A/B are the cleanest new class) and run the Sonnet-gen synthesis pipeline with
quality verification. Audit provenance: research agents 2026-07-04.

### Wave-10 Tier-1 reproducibility probe (2026-07-04, verified via validate2; nothing committed)
Built minimal .stp for 4 candidates (base scaffolds Gs001 / Tfa148, one change each),
ran validate2. Results:
- **W10-A `DIRECTION('',())`** → **REPRODUCES: deterministic occt=signal(11)/signal(11),
  gmsh=signal(11)** (2 runs). Clean, isolated, maximally oracle-visible. Confirms OCCT
  Mantis 33665 null-deref. **This is the standout** — and it supplies the long-missing
  **signal(11) reproducer template** (empty mandatory aggregate on an entity referenced by
  the transferred shape). Recommended Expected: `occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a`.
  **RESOLVED — SHIPPED as Ad134** (db61a6d5): signal(11) is an established archetype (175 entries); no greenlight needed. The empty-aggregate crash template is now in the corpus.
- **W10-M duplicate top-level faces** → occt heals identically (shape(1)=base); only gmsh
  degrades 34→9. **occt-INVISIBLE** → weak fixture (the class Q5 moved away from). Skip
  unless reframed.
- **W10-N `@` value-instance ref** → occt rejects as syntax noise (Fails 2→4), heals shape(1);
  gmsh empty; part21_strict accept. Mechanism not honored; only a modest part21/occt/gmsh
  divergence. Low priority.
- **W10-E NULL index-0 pcurve** → no distinct effect (byte-identical outcome to clean base).
  Not synthesizable on this OCCT build. Drop.

**Net:** the empty-mandatory-aggregate crash family (W10-A, and by extension W10-B
TESSELLATED_SHELL) is the genuinely-novel, high-value seam and now has a working template.
The other probed candidates are weak/no-effect. Next synthesis batch should be W10-A once the
signal(11) archetype is greenlit.

### Wave-10 verification round 2 (2026-07-05) — crash-family/knot candidates DEDUP to existing; do NOT synthesize
Probed + deduped a second batch of empty-mandatory-aggregate crash candidates and Tier-2 items
against the live oracle AND existing catalog. Outcome: the family is already well-covered.
- **C1 empty B_SPLINE_CURVE control points** → signal(11) — **DUPLICATE of Gn003** (identical
  reproducer `B_SPLINE_CURVE_WITH_KNOTS('',3,(),...)`, already a shipped signal(11) fixture). Skip.
- **C6 empty B_SPLINE_SURFACE control grid** → signal(11) — **near-duplicate of Gn004** (empty
  bspline-surface aggregate → signal(11), already shipped). Skip.
- **W10-H knot multiplicity > degree+1** → occt shape(1)→empty — **DUPLICATE of Xp042** (interior
  mult exceeds degree+1) and overlaps Gn008. Skip (end-mult variant is marginal novelty at best).
- **C4 empty CARTESIAN_POINT coords** → occt=shape(1)/shape(1) gmsh=empty divergence — no exact
  catalog match, but a low-severity degenerate case in an already-dense occt-heals/gmsh-diverge
  family. OPTIONAL / low priority; not worth a fixture on its own.
- Honest negatives from Tier-2 probe: W10-J (solid→loose-shell) not occt-shape-distinguishable;
  W10-L (far-from-origin) heals identically; W10-K (invalid record index) tolerated (diag-only).

**Conclusion:** Ad134 (empty DIRECTION direction_ratios) was the genuine novel gap in the
empty-aggregate crash family; the bspline/knot/point variants are already in the corpus. The
crash-family expansion has **saturated** against existing coverage. NOTE: the earlier
"signal(11) archetype — need OCC-crash template" / Gn003/Gn004 deferral notes in this file are
STALE (those fixtures were materialized long ago). Future wave-10 synthesis should target the
UNPROBED novel seams instead: Tier-3 Part-21 edition-3 structural (@ value-instances, multi-DATA
populations, SIGNATURE section, raw-UTF-8 dual-encoding) — each needs its own verify+dedup pass.

### Wave-10 arc CLOSED (2026-07-05) — 1 novel fixture shipped, seams saturated
Full wave-10 outcome: 19 candidates mined across 3 fresh seams (OCCT tracker, real-world CAD
forums, ISO-10303 Part-21 e3) → verified + deduped → **exactly ONE genuinely-novel, occt-visible,
synthesizable fixture: Ad134** (empty DIRECTION direction_ratios → signal(11), shipped db61a6d5).
Everything else deduped to existing coverage or was weak:
- Empty-bspline crashes → Gn003/Gn004. Knot-mult overflow → Xp042/Gn008.
- Part-21 e3 structural: @ value-instance → Ls040; multi-DATA → Lh024; SIGNATURE → Lh026;
  raw-UTF-8 → Le002/Le021; ANCHOR/REFERENCE → Lh026/Lh027/Lh028/A014.
- Weak/occt-invisible (skipped): solid→loose-shell, far-from-origin, invalid-record-index,
  duplicate-top-level-faces, empty CARTESIAN_POINT.

**Strategic finding: variant-mining has hit diminishing returns.** The corpus already covers the
mechanisms that OCCT-tracker/forum/conformance mining surfaces — a mining pass now yields ~1 novel
fixture per ~19 candidates. Meaningful further GROWTH needs a different strategy, not more
variant-mining:
  (a) genuinely NEW external sources not yet mined — fuzzing corpora (e.g. OSS-Fuzz OCCT finds),
      academic STEP-robustness papers, other kernels' bug trackers (CGAL/Parasolid/ACIS forums);
  (b) a NEW oracle that sees defects OCCT heals (would make many currently-"weak/occt-invisible"
      candidates like solid→loose-shell become synthesizable) — infra, needs sign-off;
  (c) QUALITY-deepening of existing cases: the defect-targeted mutation validator (mutate within
      each fixture's own Byte-assertion region) to properly harden bytes-only — infra, needs sign-off.

### Wave-11 fresh-source mining (2026-07-05) — saturation CONFIRMED across fresh sources; pause variant-mining
Mined sources wave-10 did NOT touch (OSS-Fuzz/fuzzer OCCT crashes, academic STEP-robustness
taxonomies, other-kernel trackers CGAL/Parasolid/ACIS). The mining agent flagged 3 "HIGH-novelty"
leads; all dedup to existing coverage:
- #1 **cyclic ORIENTED_EDGE recursion** (stack-exhaustion DoS) → already a catalog entry
  (self-referential `ORIENTED_EDGE('',*,*,#N,.T.)` recurses EdgeStart/EdgeEnd until stack exhausts;
  OCCT skips it, valid face loads shape(1)). Plus Twi cyclic-edge entries. DUP.
- #2 **Part-21 e3 anchor/reference/signature** → already saturated (Lh026/Lh027/Lh028/A014/Ls040). DUP.
- #3 **procedural / constructive-geometry model semantics** → covered by A038, M012, M014, M033,
  **M035** (single-item Constructive_Geometry_Representation crashes translator), Wr047. DUP.
- #4-8 (truncation, REAL overflow, duplicate #id, degenerate/tolerance, knot-mult) → all covered.

**DEFINITIVE STRATEGIC CONCLUSION:** variant-mining is saturated — even fresh OSS-Fuzz/academic/
other-kernel sources now yield mechanisms the corpus already covers. Mining agents' novelty
estimates are unreliable (no catalog to dedup against); the real hit rate is ~1 novel fixture per
~19-27 candidates and falling. **Recommend PAUSING autonomous variant-mining.** The genuine next
levers all need a maintainer decision:
  (a) NEW ORACLE that sees defects OCCT heals (turns many "occt-invisible/weak" candidates —
      solid→loose-shell, procedural-semantic, styling refs — into synthesizable oracle-visible
      fixtures). Biggest lever. Infra; needs sign-off.
  (b) defect-targeted mutation validator (harden bytes-only). Infra; needs sign-off.
  (c) a fundamentally new corpus axis (e.g. multi-file assemblies, non-AP242 schemas, time-series
      of a defect across kernel versions) — a scope decision.
Session net (2026-07-03..05): CI DRIFT fixed, mutation-depth saturation documented, CONCERN audit
clean, wave-10/11 mined+verified+deduped, **1 genuinely-novel fixture shipped (Ad134)**.

### fixture_lint 19 warnings — assessed benign (2026-07-05), low priority
`_fixture_lint --strict` reports 19 warnings (0 errors; CI passes — they don't fail the build):
- 16× "no `/* ... */` Part-21 comment block" (Le031, Gp056/058/059/060, Gn055/058,
  Tsh079/080/081/139/140/149/156/158): cosmetic — the mechanism is fully documented in each
  fixture's catalog entry; the inline comment is redundant. Low priority; if ever cleaned, add
  the mechanism description to each .stp header (check for a fixture_source builder first; edit
  the source, not the .stp, if one exists) and re-render the site.
- 3× FILE_NAME/FILE_SCHEMA not found: **Lh004 (FILE_SCHEMA) and Lh046 (FILE_NAME) are §12.1b
  HEADER-DEFECT fixtures that deliberately omit those entities — false-positive warnings; do NOT
  "fix" them.** Tfa126/Tfa131 (FILE_NAME) are minor lint-detection quirks, not real defects.
Conclusion: no action needed; recorded so the benign/intentional ones aren't re-chased.

## Wave-12 REPAIR-CODE mining roadmap (2026-07-06) — the on-thesis vein, NOT saturated
Three parallel gap-mining agents (OCCT source, MeshFix/CGAL source, new-vein search) run against
the coverage maps. Thesis reaffirmed: enumerate problematic-input CLASSES that kernel repair
heuristics exist for (repairs, graceful-tolerate, AND crashes all count). Corrected the earlier
"mining saturated" claim: only bug-tracker/crash mining was exhausted; the repair-code vein has a
tail, and NEW veins are wide open.

### Track A — OCCT ShapeHealing tail (~30-60 fixtures left, then genuinely saturated)
Method: fetch the `.cxx` for each never-mined class, apply COVERAGE_POLICY sub-status rule (one
fixture per input-shape-determined if/else branch). Also mine `BRepCheck_*` as a NEW invariant-
detector family (distinct from Fix* healers; ~5 refs, never per-method mined). Top candidates:
- ShapeConstruct_ProjectCurveOnSurface: AdjustOverDegen (3D edge through degenerate apex, seam-side
  ambiguous) [§12.2a]; sampled-fallback + correctExtremity (projected pcurve endpoint gap) [§12.2a]
- ShapeFix_EdgeProjAux: edge pcurve param-range reversed/zero-length/missing [§12.2a/3b]
- BRepCheck_* family: per-invariant "input violates invariant N" (Face::IntersectWires,
  UnorientableShape, NotClosed, etc.) [§12.3*]
- ShapeCustom_ConvertToBSpline / SweptToElementary / BSplineRestriction rational-drop+continuity-
  downgrade; ShapeUpgrade_ClosedEdgeDivide, FixSmallCurves; ShapeConstruct_Curve::FixEnds;
  ShapeExtend_ComplexCurve C0-gap. (12 total; full list in scratch vein_occt.)

### Track B — Mesh repair tail (near-saturated; 4 strong, existing oracles, no oracle changes)
1. sliver-at-tolerance-boundary (needle-collapse vs cap-flip edge)  2. multi-vertex seam-crack merge
3. out-of-plane spike vertex  4. does_bound_a_volume predicate failure. (+6 lower-conf.)
EXCLUDE n-gon/polygon-soup (unbuildable in triangle-only format).

### Track C — NEW veins (0 coverage — the genuine growth frontier)
- **SASIG PDQ / ISO-PAS 26183** — industry master taxonomy, ~159 coded criteria: 64 geometric +
  **63 NON-geometric/model-structure** (naming, layers, unused/duplicate entities, embedded
  metadata) + drawing/CAE. The non-geometric set is a whole uncovered CATEGORY (possible new
  §12.x). HIGHEST value. Mine via Q-Checker/CADIQ/arXiv 1611.01765 public mirrors. **Needs a
  maintainer call: open a new "model-structure/PDQ" section?**
- **openNURBS/Rhino3dm source** — staged IsValidTopology→IsValidGeometry→IsValidTolerancesAndFlags
  + IsCorrupt; free greppable C++. 0 coverage, immediately minable.
- Parasolid PK_*_state fault codes; IGES-native defects (not OCCT byproduct); 3MF/lib3mf; academic
  taxonomies (Contero arXiv 1611.01765). (full list in scratch vein_new.)

### Execution order (proposed)
1. Harvest ready in-format candidates now (OCCT top-3 + BRepCheck pilots, Mesh top-4) via
   verify→synthesize gate. 2. Enumerate openNURBS + SASIG-PDQ into candidate lists (new mining
   passes). 3. On SASIG non-geometric: decide whether to open a new section before synthesizing.

## Wave-12 execution log + candidate inventory (2026-07-06)
Pipeline PROVEN on the repair-code vein: **Gp173 shipped** (59869b22) — general B-spline 3D edge
on a sphere → OCCT sampled pcurve-projection fallback + correctExtremity REPAIR (occt=shape(1),
runtime-only). On-thesis (a repair heuristic). Dedup skipped 2 of 3 OCCT candidates (Gp005,
Twi085/Gp007). NOTE: synthesis agents must run SERIAL — they all write STEP_PROBLEM_CATALOG.md/.json
+ browse/ + push to main, so parallel synth = git races. Research/enumeration agents can be parallel.

### Ready-to-synthesize candidate inventory (deduped)
**OCCT tail** (~30-60 total; each needs dedup like Gp173 did): ShapeConstruct AdjustOverDegen was
a dup; remaining strong: ShapeCustom_ConvertToBSpline/SweptToElementary, ShapeUpgrade_ClosedEdgeDivide/
FixSmallCurves, ShapeConstruct_Curve::FixEnds, ShapeExtend_ComplexCurve C0-gap, BSplineRestriction
rational-drop/continuity-downgrade, Curve3dToBezier. (BRepCheck family likely dups ShapeFix/Analysis
coverage — dedup hard before attempting.)
**Mesh** (existing oracles, JSON builder — high confidence): 1 sliver-at-tolerance, 2 multi-vertex
seam-crack, 3 out-of-plane spike vertex, 4 does_bound_a_volume predicate failure.
**openNURBS half-wave (~6-8; theme = FLAG-vs-GEOMETRY consistency, novel):** non-unit vertex normal
[§12.14], parallel-array len≠vertex-count [§12.14], under-stated edge tolerance [§12.4], singular-trim
vs non-degenerate edge [§12.2/3], valid-but-unreferenced VERTEX_POINT [§12.3], bound-role mistyping
(2 outers) [§12.3], orient-flag vs vertex-order [§12.3], closed-flag vs distinct-endpoints [§12.3].

### SASIG PDQ — RECOMMENDATION: no big new section
The standard is itself geometry/topology-centric (bulk already covered by §12.2/3/4). Non-geometric
core is small (~15-25). Split: ~7-8 ORACLE-VISIBLE (non-orthonormal AXIS2, tessellation-without-BREP,
isolated wireframe, unresolved external ref, empty assembly/rep, inconsistent units, huge offset) →
**fold into existing §12.5/12.6/12.8 rather than a new section**. ~8-10 PURE-STRUCTURAL (duplicate/
embedded/dangling geometry, blank names, invalid layers) → NO kernel oracle reacts → these are the
concrete motivation for the future **structural-linter oracle** lever (defer until that exists).

## Wave-12 harvest finding (2026-07-06): geometry veins MATURE → pivot to SASIG oracle-visible
Shipped: Gp173 (repair, strong) + Twi281 (VERTEX_LOOP outer bound on flat plane — distinct but
borderline). But the harvest shows the GEOMETRY repair veins are mature at the oracle-active-fixture
level: OCCT ShapeHealing tail pre-screen → 0 strong (3 dups, 2 silent-heal); openNURBS flag-consistency
batch → 1 borderline fixture. Each geometry pass yields ~0-1 novel oracle-active fixtures.
**PIVOT: next batches = SASIG oracle-visible non-geometric** (new problem TYPES, distinguishable OCCT
reactions, fold into existing §12.5/12.6/12.8 — no new section): tessellation-without-BREP,
isolated-wireframe, empty-assembly/rep, inconsistent-units-in-one-rep, non-orthonormal-AXIS2,
unresolved-external-ref. Then mesh 4 (existing oracles). Pure-structural PDQ (dup geom/blank-names/
layers) still awaits the structural-linter oracle lever.

## Wave-12 SASIG pivot RESULT (2026-07-06): oracle-visible non-geometric also near-mature → INFLECTION
Executed the SASIG oracle-visible pivot. Shipped **M191** (isolated wireframe: GEOMETRIC_CURVE_SET of
12 free LINE edges → occt COMPOUND shape(1)/gmsh=shape(12), 0 solids) + **M192** (point-set: 8 bare
CARTESIAN_POINTs → occt COMPOUND shape(1)/gmsh=shape(8), 0 edges) — both §12.8, CONFIRMED, 0 DRIFT.
But the batch **empirically disproved the rest of the oracle-visible list**: non-orthonormal AXIS2
(OCC re-orthonormalizes silently → identical to clean), orphan/empty representation (either segfault-dup
of Ad050/M018 or silently-dropped = invisible), tessellation-without-BREP (dup M002-M021), inconsistent
units (shape_counts don't capture scale → the Q5-quarantine class). Net: 2 of ~7 candidates were
genuinely oracle-visible+novel; the other ~5 collapse to invisible-or-dup.

**INFLECTION (both veins now mature at the shape_counts-oracle level):** geometry/topology AND
oracle-visible-non-geometric are both yielding ~0-2 novel fixtures per full agent pass (~150K tokens
each). The binding constraint is the DISCRIMINATING ORACLE: `shape_counts` (occt/gmsh shape(N)/empty/
reject) cannot see units/scale/orthonormality/external-ref/duplicate-geometry/blank-name defects —
OCCT normalizes or ignores them, so they read identical to a clean solid.

**NEXT REAL LEVER = structural-linter oracle (USER DECISION).** A Part-21-level structural validator
(units-consistency, AXIS2 orthonormality, external-ref resolution, duplicate/dangling entities, name/
layer hygiene) would add a new discriminating dimension and unlock ~15-25 currently-invisible classes
(the SASIG pure-structural core + the oracle-invisible half of the oracle-visible list). This is
validation-INFRA scope → do NOT build unilaterally (feedback_scope_discipline); surface for maintainer.
Until then, low-yield mining is paused; loop pivots to quality/trustworthiness of existing 3158 entries.

### Structural-linter oracle — WORKING PROTOTYPE + decision brief (2026-07-06)
De-risked the lever with a standalone ~90-line spike (session scratchpad:
`structural_linter_spike.py`, NOT committed — awaiting go/no-go). It implements 2 checks with
pure entity parsing (no kernel) and proves discrimination where shape_counts is blind:

    case                   shape_counts        structural-linter
    clean-solid            occt=shape(1)        clean
    inconsistent-units     occt=shape(1) SAME   UNITS_INCONSISTENT (2 distinct length units)
    non-orthonormal-axis   occt=shape(1) SAME   AXIS_NON_ORTHONORMAL (non-unit + non-perpendicular)

**Integration sketch (est. cost, for the go/no-go):**
- Add a `structural` oracle to validate2 alongside occt/gmsh/ifc: input bytes → list[lint-code].
  New Expected-line token, e.g. `struct=UNITS_INCONSISTENT` (or `struct=ok`). ~1 day.
- Check family v1 (each = a new distinguishable class → a new fixture sub-section):
  units-consistency, AXIS2 orthonormality, external-ref resolution, duplicate/coincident entities,
  dangling refs, blank required names, layer/style hygiene. ~7-10 checks.
- Unlocks the ~15-25 currently-INVISIBLE SASIG structural classes + the invisible half of the
  oracle-visible list. This is the only identified vein that reopens meaningful growth.
- Risk: it's a NON-kernel oracle (asserts on spec/structural validity, not OCCT reaction) — a small
  philosophical shift from "what does the kernel do" to "what's malformed". Worth a maintainer nod
  before building. Negative controls (clean inputs → struct=ok) guard against false positives.

**DECISION NEEDED (Zellyn):** build the structural-linter oracle (reopens growth, ~2-3 days infra +
fixtures) or hold the corpus at ~3158 as a geometry/topology/mesh-complete artifact? Prototype proves
feasibility; the shift to a non-kernel oracle is the only judgment call.

## Trust finding 2026-07-06 (robust dangling-ref audit) — assembly boilerplate bug, VERIFIED
Ran a robust string/comment/paren-aware Part-21 tokenizer (scratchpad: dangling.py) over the corpus
to find GENUINE dangling references (referenced #N never defined). Robust count = 147 files (5.7%),
vs the naive ;-split's 569 (22%) — the naive parser's ~422 extra were false positives (missed defs
after /* */ comments, e.g. Gs026's #30). Classification: 52 DOCUMENTED (dangling IS the point —
sentinel #999 etc.), 23 incidental-harmless (broken 90xx scaffold in a fixture whose real defect is on
a separate well-formed subgraph), **72 CONCERNING**.

**71 of the 72 concerning = ONE generator bug** (independently grep-verified on A001): the shared
sub-assembly boilerplate references `#9003`/`#9004`/`#9010` which are NEVER defined; the
plausibly-intended `#9053` (PD_CONTEXT), `#9054` (assembly-root PRODUCT_DEFINITION), `#9060` (GEOM_
REP_CONTEXT) ARE defined. So the NAUO *parent* link (#9004) and rep contexts dangle → the file is not
a valid assembly. These fixtures (54 §12-6-assembly + 8 §12-12 + 5 §12-13 + 4 §12-10-perf; e.g.
A001/A003/A005/A007/P013-018) are meant to demonstrate ONE interop defect (dup instances, color loss,
hierarchy) on an otherwise-valid assembly — but the broken parent/context may confound the claim
(reader could reject/heal for the wrong reason). They're currently CONFIRMED/green, so no CI urgency.
Fix = correct the boilerplate generator (#9003→#9053, #9004→#9054, #9010→#9060, #9022→#9060) and
re-emit 71 fixtures; likely CHANGES occt/gmsh output (valid vs broken assembly) → needs DRIFT
rebaseline. **MAINTAINER DECISION** (71-fixture regen + rebaseline) — do not do unilaterally.
+1 loner: **Ad042** documented as "reference to wrong-TYPE entity" but #9000 is simply undefined
(mechanism drifted to dangling) — individual fix (define #9000 as the intended wrong-type entity).

**v2 DANGLING_REF: viable** on dangling.py (validated vs Gs026 FP + Pf001 TP). Two caveats to fold in:
parse ALL DATA sections + resolve Ed.3 `@section#id` (only 8 multi-DATA files; sole residual FP Lh033),
and keep the `*)`-typo-comment-terminator heuristic scoped to inside comment scans. Full results:
scratchpad final.json / ranked_C.txt.

## Boilerplate fix DONE (2026-07-06) + re-validation Signal-A finding
Fixed 57 of the 71 concerning assembly-boilerplate fixtures (#9003->#9053, #9004->#9054, #9010->#9060):
verified 0 genuine dangling refs remain, structural oracle now `ok`. The fix is ORACLE-INVISIBLE
(occt/gmsh output byte-identical → 0 DRIFT, demonstration preserved) — OCC nulls the missing parent
ref and yields the same stub either way. Branch `fix-assembly-boilerplate-dangling`. **15 DEFERRED**
(non-uniform scaffold, need individual handling): A110, A112, Ad042 (define #9000 as wrong-TYPE),
P011, Pf035/038/039, Wr056/057/062, Xp004/020/029/036/044.

## Re-validation sweep (2026-07-06) — "fixtures that don't demonstrate their claim"
Read-only two-signal sweep (oracle-invisibility via reachability + mutation; claim/content mismatch).
NEW SYSTEMIC CLASS found: **geometry defects on entities UNREACHABLE from the shape-representation
root** — the carrier (bspline/pcurve/surface_curve/surface) is present in bytes but not linked into
any face/shell reachable from SHAPE_REPRESENTATION, so OCC builds a trivial GEOMETRIC_CURVE_SET stub
(shape(1)) and the claimed defect NEVER FIRES. **5 mutation-CONFIRMED** (moving the defect param
changes no oracle output): P014, Gn002, Gn007, Gn008, P022. ~41 more orphan-carrier need review; 135
fixtures have NO byte/structural/tier3 assertion at all (pinning-hygiene gap). CAVEAT: the sweep agent
OVER-FLAGS — Pmi075 was falsely flagged ("no kinematic entities") but actually HAS 3 KINEMATIC
entities and demonstrates its claim; Signal-B (claim/content) is unreliable. So the list is a strong
LEAD requiring per-item verification (structural-grep + mutation) before any fix (feedback_audit_pattern).
Full data: scratchpad SUSPECT_REPORT.md / reach.py / combined_orphan.json.

## Re-validation VERIFIED (2026-07-06): 5 fixtures confirmed not-demonstrating
Double-verified (reachability + mutation-differential, both independent) the orphan-carrier suspects.
**CONFIRMED not-demonstrating (5):** Gn002, Gn007, Gn008 (nurbs), P014, P022 (assembly). Mechanism:
the defect entity sits in a SECOND, unreferenced GEOMETRIC_CURVE_SET('defect_curves',...); the
shape-rep root points only at a 1-vertex stub, so OCC builds shape(1) and never processes the defect.
byte_assertions pass on byte-presence only → green but unreproducible. See feedback_orphaned_defect_carrier.
CLEARED 64 (incl. the sweep's over-flags Pmi075 + M008 — M008 IS reachable, gmsh=shape(27)). UNCLEAR 5
(P027, P017, Pf003/007/014 — perf/structural claims not oracle-demonstrable). Verified data: scratchpad
VERIFICATION_RESULT.txt / final_verdicts.json. FIX = wire each defect into an EDGE_CURVE/ADVANCED_FACE
reachable from the rep root (per feedback_wire_mechanism), then accept-live-oracle — awaiting maintainer go.

## Re-validation COMPLETE (2026-07-06) — 135-unpinned audit + final tally
Audited the 135 non-mesh NO_PINNING fixtures (897 total NO_PINNING but 762 are mesh, validated by the
mesh oracle). Result: **133 DEMONSTRATE_BUT_UNPINNED** (baseline occt=signal(11) crash ×133 or empty ×2,
zero false-clean shape(N); all match Expected exactly; reaction already pinned by Expected+DRIFT — gap is
only a missing byte/mechanism assertion, a hardening nicety). **2 SUSPECT (Hea001, Hea011)** — orphaned
GEOMETRIC_SET carriers like the confirmed-5 but return `empty` (documented value) → lower confidence; fix =
reclassify bytes-sufficient→runtime-only. Data: scratchpad NO_PINNING_AUDIT.md.

**FINAL RE-VALIDATION TALLY (corpus is honest — ~0.3% problematic):**
- NOT-DEMONSTRATING, high-confidence (5): Gn002, Gn007, Gn008, P014, P022 — oracle-invisible quality/spec
  defects; wiring proven insufficient; fix = reclassify OR geometry-quality oracle (MAINTAINER DECISION).
- NOT-DEMONSTRATING, lower-confidence (2): Hea001, Hea011 — reclassify to runtime-only.
- UNDER-ASSERTED but fine (133): optional hygiene — add a mechanism byte-assertion each; NOT a demo failure.
- Everything else verified demonstrating. Coverage: reachability+mutation across all ~2400 STEP fixtures,
  double-verified, over-flags rejected (Pmi075/M008 cleared).

## OCCT problem-coverage remediation queue (2026-07-12)

Adversarial audit of `occt-coverage/{tkshhealing,exchange}/problems.json` found the original
sweep verdicts structurally sound at pass/fail level but with real citation rot and a
COVERED-verdict overturn rate of ~30% in the exchange domain. Corrections applied in
commit that introduces this section (see `occt-coverage/*/VERDICT_AUDIT.md`,
`occt-coverage/tkshhealing/PARTIAL_RESWEEP.md`, `occt-coverage/exchange/COVERED_FULL_REVERIFY.md`
for full evidence). Calibrated tallies: TKShHealing 39/16/5 of 60; exchange 47/47/51 of 145;
combined 86/63/56 of 205 classes; STEP-exercisable (excluding only the structural IGES carve-out,
the audits' own denominator convention) 86/63/25 of 174.

### (a) Ranked GAP worklist — 25 STEP-exercisable gaps

Pulled from `occt-coverage/OCCT_PROBLEM_COVERAGE.md`'s ranked GAP list, tier 0 (STEP-exercisable)
+ tier 1 (detect-only) rows — i.e. every GAP except the 31 structural IGES-carve-out entries.
**Two items are already being worked by a sibling agent right now** (marked below); a third and
fourth in-flight item are fixture-level (not GAP-problem-level) fixes also underway: **Twi065**
(catalog comment claims a reversed-pcurve defect but its bytes contain zero PCURVE entities —
catalog-vs-bytes discrepancy, struck as a bogus citation from `bc-invalid-same-parameter-flag` in
this pass) and **Hea001** (flagged SUSPECT/orphaned in the 2026-07-06 NO_PINNING re-validation
tally above, but VERDICT_AUDIT.md's fresh byte re-read found it IS a live 4-face multi-defect
compound and confirmed it as genuine evidence for `seq-fix-shape` — these two findings conflict;
worth resolving before either fixture is touched further).

1. [ ] `tkshh-indirect-elementary-surface-axes` (TKShHealing): An elementary surface (plane, cylinder, cone, sphere, torus) is defined on a left-handed ('indirect') axis system — its...
2. [ ] `tkshh-sliver-solid` (TKShHealing): A compound/comp-solid contains one or more degenerate 'sliver' solids -- artifacts of Boolean/import operations whose volume is...
3. [ ] `tkshh-solid-unstructured-multishell` (TKShHealing): A shape intended to become a solid is built from more than one shell without pre-established outer-boundary/void nesting -- e.g....
4. [ ] `tkshh-splitting-vertex-face` (TKShHealing): A face contains a vertex that is NOT an endpoint of a given edge of that same face, but whose 3D position projects within... **[IN-FLIGHT: sibling agent authoring a splitting-vertex fixture right now]**
5. [ ] `tkshh-wire-duplicate-coincident-vertex-instances` (TKShHealing): Two or more edges that are topologically connected (consecutive edges in a wire, or arbitrary edges registered as touching)...
6. [ ] `bc-invalid-point-on-surface` (exchange/brepcheck (detect-only)): A vertex's stored 3D point does not actually lie on a surface it is registered against (via a point-on-surface representation),...
7. [ ] `bc-invalid-polygon-on-triangulation` (exchange/brepcheck (detect-only)): An edge's associated polygon-on-triangulation representation (indices into a Poly_Triangulation's node array) is malformed or out...
8. [ ] `bc-multiple-3d-curve` (exchange/brepcheck (detect-only)): An edge carries more than one 3D curve representation, making its geometry ambiguous.
9. [ ] `bc-no-curve-on-surface` (exchange/brepcheck (detect-only)): An edge used as a boundary of a face has no pcurve (2D parametric curve) defined for that face's surface.
10. [ ] `bc-no-surface` (exchange/brepcheck (detect-only)): A face has no underlying surface geometry at all.
11. [ ] `bc-self-intersecting-wire` (exchange/brepcheck (detect-only)): A wire's own edges cross each other in parametric/3D space, making it a non-simple loop.
12. [ ] `seq-drop-small-solids` (exchange/heal-sequence): Solids of negligible size — volume below a threshold or thin-plate/sliver bodies detected via a width-factor criterion —...
13. [ ] `seq-xsalgo-unit-mismatch` (exchange/heal-sequence): The file's declared length unit differs from the session's target (CASCADE) unit, so translated geometry and all repair... **[IN-FLIGHT: sibling agent authoring a unit-mismatch fixture right now]**
14. [ ] `sew-degenerate-free-wire-collapse` (exchange/sewing): After the main merge pass, some free (still-unmatched) boundary edges may form a closed wire loop whose overall size is...
15. [ ] `sew-merged-edge-continuity-encoding` (exchange/sewing): After two faces' edges are merged, downstream consumers (e.g. shading, meshing, or further healing steps) often need to know how...
16. [ ] `stp-compcurve-reorder` (exchange/step-reader): A COMPOSITE_CURVE's list of segments is not given in connected geometric/topological sequence (successive segments don't follow...
17. [ ] `stp-degenerate-edge-multiface` (exchange/step-reader): A degenerate edge (e.g. at a cone apex or sphere pole) is referenced by several faces. A single shared OCCT edge cannot carry the...
18. [ ] `stp-geomset-gri-fallback` (exchange/step-reader): A GEOMETRIC_SET element is none of the directly supported kinds (curve, cartesian point, surface) but is still some geometric...
19. [ ] `stp-missing-geometry-definition` (exchange/step-reader): A topological entity references its underlying geometric definition (a VERTEX_POINT's point, an EDGE_CURVE's curve, or a...
20. [ ] `stp-missing-unit-context-default` (exchange/step-reader): A geometry entity is translated in a context where OCCT cannot locate a governing SHAPE_REPRESENTATION (and hence its...
21. [ ] `stp-polyloop-dup-point` (exchange/step-reader): A FACETED_BREP POLY_LOOP (a faceted polygon boundary given as a flat list of cartesian points) lists the very same point twice in...
22. [ ] `stp-srr-nauo-reversed` (exchange/step-reader): In an assembly, the shape representation relationship attached to a CONTEXT_DEPENDENT_SHAPE_REPRESENTATION relates its two...
23. [ ] `stp-tess-dangling-brep-link` (exchange/step-reader): A tessellated face/shell/solid declares a geometric or topological link to an exact-BRep counterpart that cannot be resolved...
24. [ ] `stp-tess-degenerate-triangles` (exchange/step-reader): Tessellated geometry (TRIANGULATED_FACE / COMPLEX_TRIANGULATED_FACE) whose triangle strips or fans contain index triples that...
25. [ ] `stp-tess-malformed-normals` (exchange/step-reader): A tessellated item's normals table does not have exactly three components per row (not valid XYZ vectors). The normals are...

### (b) PARTIAL upgrade candidates (63)

Every PARTIAL-verdict problem_id across both domains, grouped by sub-domain. Each represents a
genuinely-demonstrated mechanism missing one or more subvariants (see each problem's `notes` field
in `problems.json` for the specific missing subvariant to target) — a smaller, more targeted lift
than a fresh GAP fixture.

#### `TKShHealing` (16)

- [ ] `tkshh-closed-edge-full-period-unsplit`: An edge spans the full period of a closed curve - its start and end vertex coincide (e.g. a full-circle...
- [ ] `tkshh-edge-crossing-surface-singularity`: An edge's curve passes over a surface singularity (cone apex, sphere pole) in its interior, so a single...
- [ ] `tkshh-edge-curve-inconsistent-with-vertex-removed`: An edge carries a 3D curve or a pcurve whose endpoint(s), when evaluated, land farther from the edge's actual...
- [ ] `tkshh-edge-missing-3d-curve`: An edge has no 3D curve (only a pcurve on a surface, or no geometry at all). The 3D curve must be rebuilt...
- [ ] `tkshh-face-closed-surface-unsplit-at-seam`: A face is built directly on a fully closed/periodic surface (full cylinder, cone, torus, or sphere) without...
- [ ] `tkshh-face-intersecting-wires`: Two DIFFERENT wires of the same face intersect each other in UV: a hole boundary crosses the outer boundary,...
- [ ] `tkshh-face-natural-bound-missing`: A face on a closed surface lacks its outer boundary: either the ADVANCED_FACE has no bounds at all (legal...
- [ ] `tkshh-face-small-area-wire`: A face contains a wire that encloses (near-)zero area in UV -- a sliver loop, a collapsed rectangle of width...
- [ ] `tkshh-face-wire-of-two-coincident-edges`: A face (with at least two wires) contains a wire that consists of exactly two edges which are the same edge...
- [ ] `tkshh-near-zero-knot-span-thin-patch-filter`: A curve or surface's knot vector contains near-duplicate/clustered knots (e.g. from an interior knot inserted...
- [ ] `tkshh-nonperiodic-bspline-seamlike-edge`: A closed body is encoded on a B-spline surface that is geometrically closed but NOT declared periodic (e.g....
- [ ] `tkshh-same-curve-fragmented-edges`: A chain of edges joined at degree-2 vertices lies on the same geometric curve — collinear line segments, arcs...
- [ ] `tkshh-surface-curve-continuity-below-required`: A face's boundary curves, pcurves, or its underlying surface have geometric continuity below a required order...
- [ ] `tkshh-wire-missing-or-bad-degenerated-edge`: A wire on a surface with a singularity (cone apex, sphere pole, degenerated torus/revolution row) is missing...
- [ ] `tkshh-wire-nonadjacent-edges-intersect`: Two non-adjacent edges of the same wire cross in parameter space (global self-intersection, e.g. a...
- [ ] `tkshh-wire-small-edge`: A wire contains a geometrically negligible edge: its two endpoint vertices and its curve midpoint all...

#### `exchange/brepcheck` (7)

- [ ] `bc-check-fail`: The underlying geometric evaluation for a specific sub-check (e.g. curve/surface projection, intersection)...
      **Wave-3 packet JL attempt (2026-07-12): NO REPRODUCER FOUND, dropped from that packet's delivery
      (7/8 fixtures shipped instead of 8/8) — quality over count.** Tried live against the pinned
      OCCT 7.8.1 source: near-zero-radius (1e-9..1e-14) circles as outer boundary, as inner hole
      (alone and duplicated), near-zero-radius/major-radius tori, near-zero-radius spheres, extreme
      coordinate magnitude (1e150-1e300) circles round-tripped through STEP, and a nested-solids
      compound at extreme relative scale — all either load cleanly and validate valid, or return a
      clean `IsValid()==False` through ordinary status codes, never a caught exception. Source-level
      read of `BRepCheck_Wire.cxx`/`BRepCheck_Face.cxx`/`BRepCheck_Analyzer.cxx`: the analyzer itself
      has no direct throw sites; every `catch(Standard_Failure)` guards a call into `gp`/`Geom`/
      `Extrema`, and the one unguarded zero-vector-direction construction found
      (`BRepCheck_Wire.cxx:1363`, wire self-intersection-near-vertex path) is already protected by a
      `Distance() <= gp::Resolution()` short-circuit just above it. Also confirmed via
      `_oracle_workers.py`: the harness's own `occt=shape(N)` Expected-validation field never invokes
      `BRepCheck_Analyzer` at all (only `tier3_geometric.py`'s `brepcheck` helper does, and it already
      catches exceptions into a null verdict rather than propagating). Next attempt should try
      solid-level checks (`BRepCheck_Solid` imbrication/void containment) with extreme geometry, or a
      B-spline curve/surface with pathologically near-duplicate knots used as actual edge/face
      geometry reached via STEP (not direct `BRepBuilderAPI` construction, which rejects some of these
      earlier via a different, stricter validation path than the STEP reader).
- [ ] `bc-intersecting-wires`: Two distinct wires bounding the same face cross each other in parametric space.
- [ ] `bc-invalid-degenerated-flag`: An edge marked as 'degenerated' does not actually collapse to a single point (or a genuinely-degenerate edge...
- [ ] `bc-invalid-imbrication-of-shells`: Shell nesting within a solid is topologically inconsistent (shells improperly nested).
- [ ] `bc-invalid-same-range-flag`: An edge's SameRange flag asserts the 3D curve and pcurve share an identical parameter range, but the stored...
- [ ] `bc-invalid-tolerance-value`: A face (or other shape) carries a stored tolerance value that is itself invalid — e.g. inconsistent with...
- [ ] `bc-subshape-not-in-shape`: A parent topological entity references a subshape (vertex/edge/wire/face) that is not actually present/bound...

#### `exchange/heal-sequence` (6)

- [ ] `seq-bspline-restriction`: B-spline curves/surfaces (or geometry convertible to them) whose degree, segment count, continuity class, or...
- [ ] `seq-elementary-to-revolution`: Shapes carrying analytic elementary surfaces (cylinder, cone, sphere, torus) in contexts where the consumer...
- [ ] `seq-set-tolerance`: Tolerance values on the translated shape are unreliable: out of the acceptable band (too tight or too loose...
- [ ] `seq-split-continuity`: Curves, pcurves, or surfaces whose internal smoothness is below the required continuity class (e.g. C0 kinks...
- [ ] `seq-swept-to-elementary`: The inverse mismatch: surfaces encoded as generic sweeps (revolution/extrusion) that are actually elementary...
- [ ] `seq-xsalgo-pcurve-consistency`: A translated edge's parameter-space curve is inconsistent with its 3D data in one of three ways: (a) the...

#### `exchange/sewing` (16)

- [ ] `sew-candidate-tiebreak-reciprocity`: When more than one free edge lies within tolerance of a given reference edge, Sewing must pick exactly one to...
- [ ] `sew-cutting-hanging-vertex-split`: An edge that geometrically passes through or very near a vertex belonging to a different, unrelated free edge...
- [ ] `sew-degenerate-edge-passthrough`: Some edges are legitimately zero-length in parameter space by design (e.g. the edge running along a cone's...
- [ ] `sew-edge-endpoint-tolerance-reconciliation`: Once two edges' endpoints are correctly paired (see sew-vertex-endpoint-pairing-orientation), the two...
- [ ] `sew-free-edge-gap-merge`: Two free (unshared) edges that geometrically represent the same boundary curve but sit a small distance apart...
- [ ] `sew-longest-edge-reference-selection`: When two candidate edges are merged into one, they may not be exactly the same length (e.g. one was trimmed...
- [ ] `sew-malformed-subshape-tolerance`: Corrupt or incomplete sub-shape data supplied as part of the input — a null shape entry in the list of added...
- [ ] `sew-nonmanifold-candidate-disambiguation`: At a non-manifold junction where 3+ free edges all lie within tolerance of each other (e.g. three shells...
- [ ] `sew-nonmanifold-multi-edge-merge-chain`: At a genuinely non-manifold junction, more than two free edges (e.g. three or more shells meeting along a...
- [ ] `sew-pcurve-domain-reconciliation`: Two edges being merged each carry their own 2D pcurve(s), independently parametrized to their own original 3D...
- [ ] `sew-pcurve-parameter-desync-repair`: After a merged edge's 3D curve and 2D pcurve(s) are assembled, they may not walk in lockstep (the...
- [ ] `sew-per-edge-fault-isolation`: Some input edges have geometry pathological enough (e.g. a self-inconsistent 2D/3D curve pairing) that the...
- [ ] `sew-seam-closed-surface-merge`: On a periodic/closed surface (e.g. cylinder, cone, torus, sphere), an edge running along the seam can look...
- [ ] `sew-seam-dual-pcurve-preservation`: A seam edge on a closed/periodic surface (e.g. running along a cylinder's or torus's parametric seam) maps to...
- [ ] `sew-tolerance-budget-acceptance-and-cap`: Perfect 3D/2D parameter synchronization (see sew-pcurve-parameter-desync-repair) cannot always be achieved....
- [ ] `sew-vertex-endpoint-pairing-orientation`: When merging two edges, their two endpoints must be paired up correctly according to the edges' relative...

#### `exchange/step-reader` (18)

- [ ] `stp-compcurve-disconnected`: After segment reordering, adjacent COMPOSITE_CURVE segments' endpoints still do not coincide (a genuine gap...
- [ ] `stp-edge-curve-param-range`: An EDGE_CURVE's 3D-curve trim parameters (as recomputed by projecting the edge's two vertices onto the curve)...
- [ ] `stp-ideas-shell-closing`: An I-DEAS-authored STEP file represents what is really one closed solid boundary as several separate OPEN...
- [ ] `stp-loop-vertex-merge`: Two distinct STEP vertex entities used within the same wire -- either as the (translated) start and end of a...
- [ ] `stp-makeedge-validity-fallback`: Building a proper OCCT edge from the translated 3D curve, its two vertices, and their trim parameters (via...
- [ ] `stp-mapped-item-no-transform`: A MAPPED_ITEM (placing one assembly-component shape representation into a using context) provides neither a...
- [ ] `stp-missing-pcurve-projection`: An edge on a face boundary has no usable 2D (pcurve) representation: the EDGE_CURVE's geometry has no...
- [ ] `stp-nm-shared-entity-reuse`: In a non-manifold STEP model, the same EDGE_CURVE, FaceSurface's underlying surface, or VERTEX entity is...
- [ ] `stp-null-arc-edge-fallback`: An edge's 3D curve cannot be validly trimmed between its two vertex parameters (a 'different points on closed...
- [ ] `stp-partial-assembly-continuation`: A constituent member of a topological container -- a face within a shell/solid, a void shell within a...
- [ ] `stp-pcurve-trim-range-repair`: An edge's 2D (pcurve) trim parameters on a face are inconsistent with the underlying parametric curve or...
- [ ] `stp-seam-pcurve-selection`: An edge lies on a closed surface and is associated with two pcurves (via a SEAM_CURVE, via being referenced...
- [ ] `stp-shell-to-solid-promotion`: A non-manifold-enabled STEP model represents what is topologically a closed, single-volume solid purely as...
- [ ] `stp-srrwt-axis-swap`: In a SHAPE_REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION (used to position one assembly component's shape...
- [ ] `stp-tolerance-ceiling-clamp`: Per-entity repairs elsewhere in the translation pipeline enlarge vertex/edge tolerances to absorb small...
- [ ] `stp-transfer-exception-to-fail`: Translating a piece of STEP geometry (a root shape entity dispatched by type, a wire's per-edge 3D curve...
- [ ] `stp-vertex-tol-gap`: After projecting an edge's declared vertex points onto its 3D curve, the projected point and the vertex's...
- [ ] `stp-vertexloop-bound-mismatch`: A face bound is expressed as a VERTEX_LOOP (a single point, normally meant for degenerate apex-type bounds),...

### (c) Infrastructure follow-ups

- [ ] **Structured `brepcheck_fires` field.** `COVERED_FULL_REVERIFY.md` finding #4: the corpus
      already self-reports non-firing checkers via fifteen fixture-specific "the validity-checker
      does not flag [this]" prose annotations, plus tier-3 `brepcheck.valid` assertions that
      sometimes directly contradict a fixture's own embedded intent comment (Tfa001/Tfa054). Three
      `bc-*` verdicts in this pass hinged on prose-mining these annotations. Proposal: add a
      structured `brepcheck_fires: <status|null>` field per detect-only fixture so this is
      checkable without prose-mining. Needs schema owner sign-off (not done in this pass — out of
      scope, no catalog/fixture edits made here).
- [ ] **`OCC behavior:` prose staleness correction pass.** `COVERED_FULL_REVERIFY.md` finding #5:
      the freeform `OCC behavior:` field in several catalog entries is stale boilerplate
      contradicting the structured `Expected validation` block (confirmed stale on Gs005, Twi001,
      Ad050, Tsh023, M063, Ad123; Ps010/Ps002 claim "passes BRepCheck" contradicted by BRepCheck
      source). Recommendation: trust Expected/tier-3 over prose always, and run a dedicated
      correction pass over the stale `OCC behavior:` prose (catalog edit — out of scope here).
- [ ] **Single-fixture-dependency risk.** Three exchange verdicts now rest on exactly one
      surviving fixture after this pass's pruning — one regression away from PARTIAL/GAP:
      `bc-enclosed-region` (Tsh015 alone), `seq-split-closed-edges` (Twi019 alone),
      `seq-split-common-vertex` (Twi009 alone). Worth a second independent fixture per class as
      insurance before either fixture is ever touched by an unrelated cleanup pass.
- [ ] **17 FixSplitFace-named fixtures have misleading names.** `VERDICT_AUDIT.md`'s
      `tkshh-splitting-vertex-face` GAP investigation read all 18 catalog fixtures named for
      `CheckSplittingVertices`/`FixSplitFace` (Tfa010, Tfa079, Tfa085, Tfa094, Tfa098, Tfa104,
      Tfa117, Tfa118, Tfa129, Tfa136, Tfa145, Tfa149, Tfa163, Tfa169, Tfa173, Tfa183, Tfa210,
      Tfa239) and found every one tests a different `FixSplitFace` code path (multi-zone split,
      NURBS containment bias, non-manifold vertex, etc.) than the actual `CheckSplittingVertices`
      unattached-vertex-onto-edge-interior trigger their shared naming pattern implies.
      Maintainer decision needed: rename for clarity, or leave as-is (the audit's own read
      confirms none of them are wrong, just confusingly grouped).
- [ ] **Orphan-reachability lint idea.** Recurring root cause across both domains' downgrades:
      coverage claims resting on a fixture whose defect entity sits in an unreferenced
      `GEOMETRIC_CURVE_SET` / dead scaffold with `shape_null == True`, so the claimed mechanism
      never executes (feedback_orphaned_defect_carrier — this pass found the same class repeatedly
      under a new "type-dispatch skip" variant: non-GeometricRepresentationItem entities such as
      NAUO/SRR/PRODUCT_DEFINITION or SHAPE_REPRESENTATION stuffed into a `GEOMETRIC_CURVE_SET`,
      silently skipped by `StepToTopoDS_Builder::Init(GeometricSet)`'s GRI-only dispatch — killed
      3 stp-* classes outright). Proposal: an automated lint that cross-references each
      `problems.json` fixture_id against the fixture's own `shape_null` / reachability metadata and
      flags any COVERED/PARTIAL verdict resting entirely on `shape_null==True` fixtures, so this
      class of error is caught mechanically instead of requiring a full manual byte-audit pass.

### Notes on this pass / discrepancies to flag

- **Recount matched exactly.** TKShHealing 39/16/5 of 60 and exchange 47/47/51 of 145 both landed
  exactly on the task's target tallies by direct recount after applying every correction in the
  three audit documents — no forcing needed.
- **`OCCT_PROBLEM_COVERAGE.md`'s own "STEP-exercisable" definition is stricter than the audit
  reports'.** `merge_coverage.py`'s `is_exercisable()` excludes both the IGES carve-out AND
  `detect_only` classes (31 `bc-*` BRepCheck status-code classes), giving 143 classes
  (68/56/19). The two `problems.json` audit reports use a looser "STEP-exercisable (excl. IGES
  only)" denominator — 174 classes, 86/63/25 — which is the number this task's sanity-check target
  was drawn from, and which this pass's corrected `problems.json` reproduces exactly when computed
  that way. This is a pre-existing terminology mismatch between the merge script and the domain
  audit docs, not something introduced by this pass; flagging rather than silently changing
  `merge_coverage.py`'s `is_exercisable()` semantics, since that's a scope decision for whoever
  owns the merge script's contract.
- **Tsh023 contradiction between the two exchange audit documents.** `VERDICT_AUDIT.md` (sampled
  pass) calls Tsh023 "a documented OCC signal-11 crash" (used to downgrade
  `sew-malformed-subshape-tolerance`). `COVERED_FULL_REVERIFY.md` (unaudited-43 pass) calls Tsh023
  live evidence ("wired via FACE_OUTER_BOUND → ADVANCED_FACE into a live OPEN_SHELL, shape(1)") for
  both `stp-edgeloop-empty` and `bc-empty-wire`. Since it's the same fixture file, its actual OCCT
  behavior should be deterministic — these two claims cannot both be right. This pass applied each
  report's finding only to the specific class(es) that report discusses (pruning Tsh023 from
  `sew-malformed-subshape-tolerance`, keeping it in `stp-edgeloop-empty`/`bc-empty-wire`) rather
  than resolving the contradiction unilaterally. **Needs a direct oracle re-run on Tsh023 to
  settle.**
- **Some fixture IDs named in the task's own prompt as prune targets were not found flagged bogus
  in either audit document and were left untouched:** `Hea001` (VERDICT_AUDIT.md explicitly
  confirms it genuine, see above), `Gp059` (cited only in `seq-drop-small-edges`, not mentioned
  anywhere in either report — only its sibling citation `N010` was flagged "dead wireframe" and
  pruned), `N019` (cited only in `seq-surface-to-bspline`, a class VERDICT_AUDIT.md's Confirmed
  list explicitly marks AGREE with no citation issue). Flagging per the task's own instruction to
  "trust the underlying per-class corrections and report the discrepancy rather than forcing" —
  applies to citation-hygiene, not just tallies.
