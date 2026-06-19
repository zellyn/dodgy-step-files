# Done — completed work log (companion to BACKLOG.md)

This file is the historical record of work that's been completed. When an
item finishes in `BACKLOG.md`, move it here with its completion date and
commit SHA. **Do not delete from here** — provenance matters.

Append newest at the top.

---

## 2026-06-18

- **B2 batch 4: 430 tier-3 promotions for §12.5–§12.13 + Tb prefix.**
  Coverage 1689 → 2119 assertions, 1244 → 1674 entries (54% → 73%).
  Validation: 2118/2119 pass.
- **B2 batch 3: 517 tier-3 promotions for §12.3 + §12.4.** Coverage
  1309 → 1689 (+380); entries 727 → 1244 (32% → 54%). Includes 256
  n_faces_total count assertions on real geometry. Commit `68631c9`.
- **Q1: regen 6 weak fixtures (Gn134, Gn157, Gn155, Gp081, Gs151, Gs177).**
  23 → 17 in queue. Each rebuild uses a correct entity form
  (rational B-spline, periodic cylindrical/toroidal, proper FACE_BOUND
  count) so the catalog claim is actually verifiable from geometry.
- **Q2: QUALITY_DASHBOARD.md top-line stats refresh.** Replaced stale
  1282/831/241 numbers with current 2302/1309/727. Other rows still
  reflect old runs; documented at bottom. Commit `ab4e0e2`.
- **Q4.1–Q4.3: mesh_builder skeleton + 5 first-cut mesh fixtures.**
  `validation/src/step_corpus/mesh_builder.py` mirrors step_builder
  API. Five §12-14-mesh fixtures (non-manifold edge, degenerate
  triangle, near-coincident vertices, boundary hole, self-intersecting
  triangles) validate the JSON schema v0. Commit `cc855c9`.
- **B2 batch 2: 389 tier-3 promotions for §12.2 NURBS/surfaces/pcurves.**
  Coverage 920 → 1259 assertions (+339), 338 → 727 entries (15% → 32%).
  Commit `87e884f`.
- **B2 batch 1: 97 tier-3 shape_null promotions for §12.1.** Coverage
  831 → 920 assertions, 241 → 338 entries (12% → 15%). All §12.1
  framing-defect entries now have `shape_null == True` as a
  format-robust tier-3 assertion alongside their byte assertions.
  Commit `c0239b8`.
- **BACKLOG.md: added B4 (real-world issue-tracker mining).**
  Commit `c0239b8`.

- **README.md quarantine claim fix.** Stale wording "84 quarantined
  pending proper regen" replaced with accurate "150 historical
  quarantines; all replaced in the active corpus by defect-specific
  regens". Verified by script: 84/84 early-waves IDs and 66/66
  phase_F_boilerplate IDs have active replacements.
- **Round-2 CONFIRMED_INVALID regen** (Gs097, N152, Tfa132, Twi248,
  Twi268, Twi270). Commit `87ddf14`.
- **Sonnet weak-verify pass** on 64 Haiku WEAK_VALID flags: 35 promoted
  to ACTUALLY_VALID, 23 stayed weak, 6 new CONFIRMED_INVALID surfaced
  (now resolved per above). Audit commit `420fe6c` (local).
- **README.md stats refresh** — replaced stale "440 verified / 20%
  coverage" with current "2280 / 98% coverage". Commit `87ddf14`.
- **Round-1 CONFIRMED_INVALID regen** (Tsh028, Gp053, Gs140, Gs143).
  Commit `fef9542` (pushed).
- **Full-corpus adversarial verification sweep** — 100% sample coverage
  across 2309 fixtures, 2280 (98%) verified VALID. Two-stage Haiku
  sweep → Sonnet verify on weak/invalid flags. Commit `68b44d0`.

## 2026-06-17 (and earlier)

- **Python builder extension** — rational B-spline weights, B-spline
  curves + surfaces, rectangular trimmed surface, complex-instance
  emission via `_emit_raw`. Wave 73 used it to synthesize 15 new
  fixtures.
- **CI maintenance** — fixed `test_corpus_score_below_ceiling`,
  `test_entry_count_in_expected_range`,
  `test_catalog_validates_against_schema`,
  `test_category_lint_under_ceiling`,
  `test_no_unexpected_schema_violations`, `test_fixture_lint_clean`,
  `test_signal_captured[Tsh023]`, byte-stale-JSON failures, Wr002/Wr042
  CR-byte restoration, and float-libm divergence between macOS and
  Linux (REAL formatting now rounds to 12 sig digits).
- **CI invariant `_fixture_source_check`** — every `fixture_sources/*.py`
  must regenerate byte-identical to `step-examples/*.stp`. Catches
  builder regressions.

(Older history: see `audit/SESSION_SUMMARY_2026-06-17.md` and git log.)
