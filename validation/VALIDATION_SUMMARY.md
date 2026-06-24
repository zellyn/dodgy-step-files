# STEP Corpus — Validation Summary

_Refreshed 2026-06-23. Subsidiary numbers below partially predate the
corpus expansion; rerun the validators (see commands at the bottom of
`../QUALITY_DASHBOARD.md`) to recompute exact per-section breakdowns._

## Headline

**3,086 catalog entries (2,350 STEP fixtures + 760 mesh [Me001–Me1182, waves 1–41] + 7 sibling-input).**
**Multiple independent confidence signals:**

| Signal | Subset | Result |
|---|---|---|
| Adversarial-verification sweep (Haiku→Sonnet two-pass, 2026-06-18) | 2309 STEP fixtures | **2280 VALID (98.7%)** · 23 weak (all regen'd) · 0 confirmed-invalid after regen |
| Tier-3 assertion coverage | 3086 catalog entries (STEP subset CI-locked) | **≥2,184 STEP entries (93.1%)** carry at least one tier-3 assertion · CI-locked at ≥90% on the §12.1–§12.13 STEP subset via `test_tier3_coverage_ratchet.py`; 362 Q5 stale assertions refreshed 2026-06-22/23 |
| Cross-kernel oracle inventory | full corpus | OCCT (heal on/off), gmsh (autofix on/off), ifcopenshell, part21_strict, manifold, OCAF, **solvespace** (new, install-optional) |
| Catalog ↔ live-oracle agreement (DRIFT detection) | last run on 1082-corpus | 1281 CONFIRMED · 9 CONFIRMED-WEAK · 0 DRIFT (rerun pending against current 2313-corpus) |
| Schema-vocabulary oracle (FILE_SCHEMA vs entity vocabulary) | full corpus | 8 EXEMPT_SCHEMA_MISMATCH (catalog-claim-IS-mismatch, all witnessed) · 0 unexpected · pytest-locked |
| Construction-validity lint (non-unit DIRECTION, parallel axis/refdir) | full corpus | 0 unexempted violations (9 catalog-claim-IS-defect exempt) |
| External-kernel cross-validation (pure-Python ISO 10303-21 vs OCCT) | 960 reviewed | 909 agree (94.7 %); 22 OCC-silently-heals spec violations; 8 OCC-stricter-than-spec; 16 spec-clean OCC crashes |
| Forward adversarial review (bytes support claim) | 960 reviewed | 918 demonstrate · 42 runtime-only · 0 weak after remediation |
| Reverse self-evidence (cold-read description finds canonical entry) | 960 reviewed | 87.4 % top-3 BM25; 16 weak (1.7 %) |

**What CONFIRMED actually means (read this).** CONFIRMED means the
codified `**Expected validation**:` line matches the live oracle output
exactly. For most of the corpus (silent-empty baseline with
`occt=empty/empty gmsh=empty ifc=schema_n/a`), both sides are silent
regardless of fixture content, so CONFIRMED on those entries is asserting
that the oracle is silent, not that the oracle independently verifies the
defect. Their evidence is entity-graph adversarial review, not oracle
differential. The oracle-active subset (~266 fixtures with reject,
segfault, or shape-loading baselines) has CONFIRMED carrying strong oracle
signal.

A mutation test (single-byte flip in DATA section, then re-run validate2)
shows:

- ~10 % detection rate on silent-empty fixtures: by design. The oracle
  is uniformly silent on minimal scaffolds without PRODUCT chains, so
  bytes-level evidence is the real test for these.
- 91.8 % detection rate on oracle-active fixtures (3 mutations per
  fixture; tier-3 fingerprint AND OCCT diagnostic-message signature
  included in the differential). The undetected fixtures are binary-output
  baselines (segfault, parser-reject, process-signal) where random byte
  flips can't change the binary state.

The DRIFT detector compares the codified Expected against future oracle
behavior and fails CI on mismatch; that's its load-bearing role.

## Verdict matrix

_Last full run 2026-06-19 (STEP entries only — rerun pending against 2350-entry corpus). Mesh entries (§12.14) use separate mesh oracle; not included in verdict matrix._

| Verdict | Count | % |
|---|---:|---:|
| CONFIRMED | 2337 | 99.49 |
| CONFIRMED-WEAK | 12 | 0.51 |
| DRIFT | 0 | 0 |
| FAIL | 0 | 0 |
| ERROR | 0 | 0 |

### Verdict semantics

- **CONFIRMED**: validate2 oracle behavior matches the catalog entry's
  `**Expected validation**:` spec, and the catalog's described defect is
  consistent with the kernel mishandling we observe (kernel-mishandling
  IS the defect).
- **CONFIRMED-WEAK**: catalog claims a *specific* failure mode (e.g.
  "kernel crashes") but the validator shows a less-specific mismatch
  (e.g. silent-empty). The defect is real but the cited code path isn't
  reached at fixture scale. By design for §12.10 perf scaled-down
  representatives.
- **DRIFT**: live oracle behavior diverges from the catalog-codified
  `**Expected validation**:` spec. Catalog re-baselining required; CI
  fails the build.
- **FAIL**: validator output contradicts the catalog claim outright.
  Bug in the fixture, the catalog, or the validator.

## CONFIRMED-WEAK breakdown (by design)

| Section | Count | Reason |
|---|---:|---|
| §12.10 perf | 5 | Scaled-down representatives of catastrophic-at-scale defects |
| §12.11 adversarial | 4 | Defects where bytes-level evidence is sufficient but oracle output is silent-empty |
| §12.6 assembly | 2 | Process-state defects (P012 .stpx/.stpz; P026 in-process contamination) |
| §12.2a pcurves | 1 | Pcurve defect manifesting only in tier-3 measurement |
| §12.8 mixed | 1 | Schema mismatch where oracles silently accept |

All carry `**Notes**: Validation observed:` annotations explaining why
fixture-scale silent-empty is the correct manifestation.

## Per-section table

_Fixture counts refreshed 2026-06-23. CONFIRMED/WEAK breakdown is from the
2026-06-19 run (1082-entry corpus basis); rerun `_final_verdict` to update._

| Section | Fixtures (current) | CONFIRMED | WEAK |
|---|---:|---:|---:|
| §12.1a encoding | 57 | 55 | 1 |
| §12.1b header | 45 | 43 | 0 |
| §12.1c syntax | 46 | 45 | 0 |
| §12.2a pcurves | 163 | 31 | 1 |
| §12.2b NURBS | 167 | 30 | 1 |
| §12.2c surfaces | 177 | 49 | 0 |
| §12.3a shells | 263 | 99 | 0 |
| §12.3b wires | 269 | 90 | 0 |
| §12.3c faces | 259 | 76 | 0 |
| §12.4 tolerance | 194 | 70 | 0 |
| §12.5 units | 37 | 31 | 0 |
| §12.6 assembly | 108 | 87 | 2 |
| §12.7 PMI | 122 | 83 | 0 |
| §12.8 mixed | 217 | 117 | 1 |
| §12.10 perf | 37 | 28 | 4 |
| §12.11 adversarial | 82 | 62 | 8 |
| §12.12 cross-product | 44 | 24 | 0 |
| §12.13 writer-pathology | 63 | 44 | 0 |
| §12.14 mesh | 760 (Me001–Me1182) | separate mesh oracle | — |

## Tooling

- `validate2.py`: subprocess-isolated multi-oracle validator
- `_run_corpus.py`: parallel runner (validate2 + tier3); 6 workers, ~10 min on the full corpus
- `_refresh_expected.py`: ground-truth Expected validation lines from `/tmp/cad-v2-out/` JSONL
- `_final_verdict.py`: heuristic classifier with DRIFT detection
- `_bug_search.py`: BM25 bug-report search
- `_api_shape_score.py`: OCCT-API-leak ratchet
- `_byte_assertions.py`: byte-pattern assertion checker
- `_tier3_assertions.py`: tier-3 geometric assertion checker
- `_schema_oracle.py`: FILE_SCHEMA vs entity-vocabulary oracle
- `_writer_oracle.py`: writer-pathology runtime oracle
- `_ocaf_oracle.py`: OCAF/XCAF document-level oracle

## License

MIT; see top-level [`LICENSE`](../LICENSE).
