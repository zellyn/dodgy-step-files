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

**Deferred (need bespoke regen per mechanism — not generic C-1 break):**
- Gp050: SameRange recursive stack overflow (catalog says deg-3 / 10-CP / pcurve mismatch; need specific recipe, not C-1 break in 3D curve)
- Gp061: CheckCurve3dWithPCurve sample-count threshold (defect should be in pcurve bow that 2-sample misses, not in 3D curve)
- Gp062: FixAddPCurve trim-window boundary (endpoint must extend BEYOND v_max trim boundary, not sit on it)
- Gp063: CheckOverlapping false-positive on bounded-curve TRIMMED_CURVE pair (need 2 EDGE_CURVEs sharing 3D LINE with disjoint trim ranges [0,5] and [10,15] — current attempt had neither)
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
- Gn044: ConvertCurve2dToBezier degree-1 skip — degree-1 2D B-spline was placed as a standalone COMPOSITE_CURVE_SEGMENT orphan, not in any PCURVE/EDGE_CURVE chain. Needs the degree-1 B-spline to BE the pcurve of the face's defect edge.
- Gn045: SplitSurface.Init out-of-domain — out-of-domain U=2.0 PCURVE was an orphan with no semantic meaning in STEP (no SplitSurface entity). Recipe TBD — may need TRIMMED_CURVE with out-of-domain U1/U2 wired into face's actual SURFACE_CURVE.
- Gn087: SetUSplitValues neg-zero dedup — defect is pure OCC runtime behavior of SetUSplitValues([-0.0, 0.5, 1.0]); -0.0 cannot be encoded in STEP knot literals (which serialize as "0.0"). The fixture was indistinguishable from a plain flat patch + C-1 driver. No encodable trigger.
- Gn110: ConvertSurfaceToBezierBasis trim-ignored — catalog claims defect is triggered by an inner FACE_BOUND trim at 0.25..0.75, but Sonnet's fixture only emitted FACE_OUTER_BOUND with full extent. Needs explicit inner trim loop on the surface to actually trigger the documented behavior.
- Gn160 (periodic B-spline parameter wrapping): live oracle returns empty/empty but Sonnet's analysis says geometry should load — fixture wires periodic B-spline as edge 3D curve on plane face, OCC rejects but mechanism narrative is unclear. Needs investigation of WHY OCC rejects.
- Gn162 (B-spline interior knot mult=degree+1 Bezier-join): live oracle empty but Sonnet's analysis says tangent-only break should load — fixture wires the discontinuous B-spline as defect 3D curve; OCC rejects for unknown reason. Needs investigation.
- Gn164 (Rational BSpline Closure Detection Bypass): catalog needs the rational B-spline surface to BE the face_geometry, but Sonnet's fixture builds the surface as an orphan alongside a flat-plane face. Recipe: pass the rational B-spline as the `surf` argument to `advanced_face()`, not the pre-built plane.
- Gn165 (Ill-conditioned knot 44:1 ratio): same orphan-surface issue as Gn164. Need B-spline surface IS face_geometry.
- Gn166 (Boundary pole singularity first row): same orphan-surface issue. Need B-spline surface IS face_geometry.
- Logged 2026-06-20 from batch 49 indep verify systemic finding: Sonnet keeps building B-spline surfaces as orphans alongside the face's flat-plane geometry instead of swapping them in. Affects batch 49 final-nurbs trio.
- Ps004, Ps005 (shells): Sonnet attempted post-hoc entity-args mutation (`ent.args[0].append(msb2)`) but ADVANCED_BREP_SHAPE_REPRESENTATION's items arg is stored as a string, not a list. Needs proper builder support for multi-MSB shape representations or a different mechanism encoding.
- Tsh179 (shells): Sonnet used `f.method[index]` syntax (method-not-subscriptable error). Needs retry with proper builder API.
- Logged 2026-06-20 from batch 31 indep verify systemic finding.
- Reason: signal(11) requires engineering a deliberate OCC SIGSEGV; Wave-B Sonnet pipeline doesn't have a template for this yet. Gp001 is the existing reference but is a hand-authored .stp without a fixture_source.py. Need to (a) reverse-engineer Gp001's crash trigger or (b) propose a new builder API for signal-11 fixtures.
- Logged 2026-06-19 from batch 13-18 archetype-aware scans.

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
- [ ] Q5.5 Re-attack the 97 Gp + ~650 other silent-empty entries under new architecture, in small batches with Sonnet verification gating every commit.



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

**Status:** Not started.
**Last touched:** 2026-06-18.

**Plan:**
- [ ] B3.1 Survey kernel landscape: CGAL (Polyhedron + Nef), Geogram,
      OpenSCAD/libfive, Open Cascade Edge (community fork), pythonOCC
      (separate from OCCT?), libIGES. Note: not all read STEP — some
      need bridging via IGES/BREP intermediates.
- [ ] B3.2 Build kernel-availability matrix: which can be installed in the
      Linux CI container (Ubuntu 22.04)? Which need build-from-source?
      Which are Python-bound vs. C/C++ only?
- [ ] B3.3 Pick top-2 kernels to add first based on coverage + ease of
      install (likely CGAL + one other). Implement subprocess-isolated
      oracle wrappers in `validation/src/step_corpus/_kernels/`
      following the existing `_occt_oracle.py` pattern.
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

- [x] `QUALITY_DASHBOARD.md` — refreshed 2026-06-19 to 2329 entries.
      Commit `4c3f1d7`.
- [ ] `CODEBASE_LANDSCAPE.md` — last updated 2026-06-15, hasn't seen the
      corpus-wide adversarial sweep or the builder extensions.
- [x] `validation/VALIDATION_SUMMARY.md` — refreshed 2026-06-19.
      Commit `4c3f1d7`.

### Q3 — Phase 7 backlog (75-fixture A6 audit groups)

Pre-existing task #116. Not blocking but should not be forgotten.

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
