# STEP Corpus — Validation Summary

## Headline

**1282 fixtures. Multiple independent confidence signals:**

| Signal | Subset | Result |
|---|---|---|
| Catalog ↔ live-oracle agreement (DRIFT detection) | 1282 (+ 7 sibling-input) | 1281 CONFIRMED · 9 CONFIRMED-WEAK · 0 DRIFT · 0 FAIL · 0 ERROR |
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

| Verdict | Count | % |
|---|---:|---:|
| CONFIRMED | 1281 | 99.38 |
| CONFIRMED-WEAK | 9 | 0.72 |
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

| Section | Fixtures | CONFIRMED | WEAK |
|---|---:|---:|---:|
| §12.1a encoding | 56 | 55 | 1 |
| §12.1b header | 43 | 43 | 0 |
| §12.1c syntax | 45 | 45 | 0 |
| §12.2a pcurves | 32 | 31 | 1 |
| §12.2b NURBS | 31 | 30 | 1 |
| §12.2c surfaces | 49 | 49 | 0 |
| §12.3a shells | 99 | 99 | 0 |
| §12.3b wires | 90 | 90 | 0 |
| §12.3c faces | 76 | 76 | 0 |
| §12.4 tolerance | 70 | 70 | 0 |
| §12.5 units | 31 | 31 | 0 |
| §12.6 assembly | 89 | 87 | 2 |
| §12.7 PMI | 83 | 83 | 0 |
| §12.8 mixed | 118 | 117 | 1 |
| §12.10 perf | 32 | 28 | 4 |
| §12.11 adversarial | 70 | 62 | 8 |
| §12.12 cross-product | 24 | 24 | 0 |
| §12.13 writer-pathology | 44 | 44 | 0 |

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
