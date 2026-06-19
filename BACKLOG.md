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

## Active initiatives

### B1 — Mine OCCT's `tests/` tree for parsing-wisdom coverage

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

**Status:** Substantially done. Coverage 12% → 73% in 4 batches.
**Last touched:** 2026-06-18.

**Plan:**
- [x] B2.1 Enumerate byte assertions. Done (1578 contains / 410 count /
      etc.).
- [x] B2.2 Candidate list. Done.
- [x] B2.3 Existing tier-3 introspection sufficient (shape_null,
      n_faces_total). No extensions needed for the first 1433 promotions.
- [x] B2.4 Batches 1–4 applied (97 + 389 + 517 + 430 = 1433 promotions).
      All validated against live tier3.
- [ ] B2.5 Remaining ~600 entries without tier-3: these mostly have
      catalog claims that don't map to current tier-3 introspection
      (e.g. specific knot multiplicity, byte-level encoding). Either
      extend tier-3 introspection (B2.3 extension) or accept this as
      the ceiling.
- [ ] B2.6 Tier-3 ratchet in `validation/tests/` — fail CI if
      coverage regresses below current 73%.

**Notes:** Pmi125 has one pre-existing tier-3 failure
(`face[0].area > 899` actual 1.0) — predates this work and unrelated.

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

**Status:** Not started.
**Last touched:** 2026-06-18.

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

- [ ] `QUALITY_DASHBOARD.md` — still says 1282 entries, real is 2302.
- [ ] `CODEBASE_LANDSCAPE.md` — last updated 2026-06-15, hasn't seen the
      corpus-wide adversarial sweep or the builder extensions.
- [ ] `validation/VALIDATION_SUMMARY.md` — likely also stale.

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

**Status:** Not started.
**Last touched:** 2026-06-18.

**Plan:**
- [x] Q4.1 Draft `mesh_builder.py` skeleton. Done in cc855c9.
- [x] Q4.2 Define the JSON schema v0. Done in cc855c9.
- [x] Q4.3 First-cut mesh fixtures (Me001–Me005). Done in cc855c9.
- [ ] Q4.4 Optional interop emitters: also write the same mesh as PLY
      and OBJ (where representable, given the format limitations), so
      consumers without our format can still load the unbroken parts.
- [ ] Q4.5 Mesh-tier oracle: subprocess-isolated wrapper around CGAL PMP
      (or MeshFix). Healer reads JSON, attempts repair, reports
      detected-vs-undetected defects. Drops into the same
      multi-tier-validator harness as the STEP oracles.
- [ ] Q4.6 Decide naming + extension: `.mesh.json`? `.stp-mesh`? Note in
      catalog as parallel-to-STEP, not part of it.

**Estimate:** 1-2 days for Q4.1–Q4.3 (skeleton + first 5 fixtures); the
catalog + oracle work scales with how many defect classes we synthesize.

**Hazards:** Risk of bikeshedding the JSON schema. Keep the first cut
narrow — 3-4 defect types — and let real fixtures pull on the schema as
they need it.

---

## Done

See `DONE.md` for completed work history.
