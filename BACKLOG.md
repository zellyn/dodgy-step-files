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
