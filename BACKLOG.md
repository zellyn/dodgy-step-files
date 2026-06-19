# Backlog — single authoritative work-tracking file

This file is the only authoritative backlog for the corpus. Anything not
captured here is at risk of being forgotten. When picking up work,
**start here, work top-down**. When finishing work, **strike through and
move to `## Done` at bottom; don't delete** — provenance matters.

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

**Why:** 2249 byte assertions across the catalog vs. only 831 tier-3
geometric assertions across 241 entries (~12% coverage). Byte assertions
break under formatting normalization; tier-3 invariants (face[0].area,
edge[2].is_closed, surface.degree_u) survive whitespace/comment changes
and are the strongest evidence the catalog carries. Single biggest
crispness lever.

**Status:** Not started.
**Last touched:** 2026-06-18.

**Plan:**
- [ ] B2.1 Enumerate all byte assertions. Bucket by what they're really
      checking: lexical (e.g. `contains(b'SEAM_CURVE')`), structural
      (e.g. `count_entity_def(b'ADVANCED_FACE') == 2`), value-bearing
      (e.g. `contains(b'1.00000001')`). Tally each bucket.
- [ ] B2.2 For each value-bearing or structural byte assertion, identify
      whether a tier-3 assertion would be a *strictly better* statement of
      the same claim (e.g. `count(ADVANCED_FACE) == 2` ↔
      `len(faces) == 2`). Build a candidate list.
- [ ] B2.3 Implement any missing tier-3 introspections in
      `validation/src/step_corpus/tier3_geometric.py`. Catalog: face.area,
      face.is_planar, edge.is_closed, edge.length, surface.degree_u,
      surface.degree_v, surface.is_periodic_u/v, vertex.distance(other).
- [ ] B2.4 Promote 50 byte assertions in the first batch. Verify each
      tier-3 assertion against live tier3 output via
      `_tier3_assertions`. Lock in the conversion only when the assertion
      passes.
- [ ] B2.5 Iterate to 200 total promotions. Track coverage in
      `audit/tier3_coverage_log.md`.
- [ ] B2.6 Update tier-3 ratchet in `validation/tests/` — once we cross
      a coverage threshold, fail CI if it regresses.

**Estimate:** 1 day for B2.1–B2.2 (analysis); 2-4 days for B2.3–B2.5
(tier-3 introspection extensions + per-assertion promotion).

**Hazards:** Be careful not to weaken the assertion in translation —
"contains the bytes `1.00000001`" is stronger than "vertex at
~(1.00000001, 0, 0)" because the latter might be normalized. Sometimes
both should coexist.

---

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

### Q1 — 23 CONFIRMED_WEAK fixtures, bespoke regens

**Why:** Present but not crisp. These demonstrate the claim weakly — a
better fixture would be a clearer reproducer. Lower priority than the
three Bs above because they're not blocking anything.

**Status:** Listed in `audit/confirmed_weak.txt`.
**Last touched:** 2026-06-18.

**Plan:** Take per-fixture as time permits. Use the same builder pattern
as the round-1 + round-2 INVALID regens. Each fixture: ~30 min.

### Q2 — Stale-doc refresh

- [ ] `QUALITY_DASHBOARD.md` — still says 1282 entries, real is 2302.
- [ ] `CODEBASE_LANDSCAPE.md` — last updated 2026-06-15, hasn't seen the
      corpus-wide adversarial sweep or the builder extensions.
- [ ] `validation/VALIDATION_SUMMARY.md` — likely also stale.

### Q3 — Phase 7 backlog (75-fixture A6 audit groups)

Pre-existing task #116. Not blocking but should not be forgotten.

---

## Done

- [x] Full-corpus adversarial verification sweep (2280/2309 = 98% VALID).
      Two rounds: Haiku sweep → Sonnet verify on weak/invalid flags.
      Completed 2026-06-18.
- [x] Round-1 CONFIRMED_INVALID regen (Tsh028, Gp053, Gs140, Gs143).
      Completed 2026-06-18 in commit fef9542.
- [x] Round-2 CONFIRMED_INVALID regen (Gs097, N152, Tfa132, Twi248,
      Twi268, Twi270). Completed 2026-06-18 in commit 87ddf14.
- [x] README.md refresh — replaced stale 440/20% claims with current
      2280/98%. Completed 2026-06-18 in commit 87ddf14.
- [x] Python builder extension: rational B-spline weights, B-spline
      curves + surfaces, rectangular trimmed surface, complex-instance
      emission via _emit_raw. Completed 2026-06-17/18.
