# STEP Corpus Validation

Multi-tier validator for the STEP-defect corpus at `../step-examples/`. 1282 fixtures across 18 §12.x defect categories, each demonstrating a specific input pathology described in `../STEP_PROBLEM_CATALOG.md`. This package adversarially verifies each fixture actually exhibits its claimed defect.

License: **MIT** (see top-level `LICENSE`).

## Why multi-tier

A single oracle isn't enough. OCCT-based kernels silently auto-heal many defects (missing seams, near-period pcurves, negative torus radii); a file we *intend* to be defective gets read as a clean shape, which is correct kernel behavior but doesn't validate the file. Byte-level checks confirm a file contains the defective pattern but don't tell you what a kernel will do with it. The validator therefore runs several oracles in parallel and reports the behavior matrix.

- **Byte / entity-graph signature.** BOM detection, line endings, NUL bytes, file-schema, entity-type histogram. No external tools.
- **ifcopenshell strict Part-21 parser.** Rejects malformed Part-21 regardless of schema.
- **OCCT with auto-healing on / off.** What most CAD tools effectively do, plus a strict-tunables variant for the raw load.
- **gmsh OCC** (autofix on / off). Independent OCC build with healing knobs.
- **Tier-3 geometric introspection.** For fixtures that load, computes face areas, edge lengths, vertex tolerances, knot-vector arithmetic.
- **Catalog ↔ fixture entity-match check.** Verifies fixtures contain the entity types their catalog recipe cites.

Each oracle runs in its own subprocess so OCCT segfaults are reported as `signal(11)` instead of killing the runner.

## Quick start

```bash
cd validation
uv sync

# Run validator self-tests (512 tests, ~110s)
uv run pytest tests/

# Validate one fixture
uv run python -m step_corpus.validate2 ../step-examples/12-1a-encoding/Le001.stp --json

# Tier-3 geometric introspection on one fixture
uv run python -m step_corpus.tier3_geometric ../step-examples/12-3c-faces/Tfa006.stp --json

# Run validate2 + tier3 across the full corpus (parallel; ~10 min on 6 workers)
uv run python -m step_corpus._run_corpus --workers 6

# Generate per-section verdicts (CONFIRMED / CONFIRMED-WEAK / DRIFT / FAIL)
uv run python -m step_corpus._final_verdict

# Lint pass over all fixtures (file-naming, header comments, framing)
uv run python -m step_corpus._fixture_lint

# Search the catalog by bug-report phrasing
uv run python -m step_corpus._bug_search "shell with tiny gap between adjacent faces"

# Browse / show / pick random entries
uv run python -m step_corpus.cli sections
uv run python -m step_corpus.cli show Le001
uv run python -m step_corpus.cli list --section 12.3a
uv run python -m step_corpus.cli random 5

# Run tier-3 geometric assertions encoded in catalog entries
uv run python -m step_corpus._tier3_assertions

# Per-fixture confidence report (aggregates all evidence signals)
uv run python -m step_corpus._confidence_report --top 30

# Mutation-test the oracle-active fixtures (1-byte flips; ~30 min wall time)
uv run python -m step_corpus._mutation_test --oracle-active --all

# Pure-Python ISO 10303-21 strict validator vs OCCT (cross-oracle)
uv run python -m step_corpus._oracle_divergence

# Per-fixture detail pages (one .md per fixture; aggregates all signals)
uv run python -m step_corpus._per_fixture_pages
```

## Verdict semantics

- **CONFIRMED**: validate2 oracle behavior matches the catalog entry's `**Expected validation**:` spec, and the catalog's described defect is consistent with the kernel mishandling we observe.
- **CONFIRMED-WEAK**: catalog claims a *specific* failure mode (e.g., "kernel crashes") but the validator shows a less specific mismatch (e.g., silent-empty). The defect is real but the cited code path isn't reached at fixture scale. By design for §12.10 perf scaled-down representatives.
- **DRIFT**: live oracle behavior diverges from the catalog-codified `**Expected validation**:` spec. Usually a kernel update that needs catalog re-baselining; CI fails the build.
- **FAIL**: validator output contradicts the catalog claim outright. Bug in the fixture, the catalog, or the validator.

Currently 1283 CONFIRMED + 6 CONFIRMED-WEAK + 0 FAIL + 0 DRIFT + 0 ERROR.

## Repository layout

```
validation/
├── pyproject.toml                  # uv-managed deps; MIT license metadata
├── README.md                       # this file
├── VALIDATION_SUMMARY.md           # current verdict matrix + outstanding work
├── SEGFAULT_CHARACTERIZATION.md    # 25 confirmed OCCT segfaults — characterized failure paths
├── src/step_corpus/
│   ├── validate.py                 # legacy v1 validator (in-process)
│   ├── validate2.py                # v2 subprocess-isolated multi-oracle
│   ├── _oracle_workers.py          # per-oracle subprocess workers
│   ├── _run_corpus.py              # parallel runner (validate2 + tier3 per fixture)
│   ├── tier3_geometric.py          # face areas, edge lengths, knot arithmetic
│   ├── tier_entity_match.py        # catalog ↔ fixture entity-citation drift check
│   ├── _final_verdict.py           # heuristic verdict classifier (with DRIFT detection)
│   ├── _fixture_lint.py            # file-naming / header / framing lint
│   ├── _build_catalog_json.py      # markdown → JSON catalog generator
│   ├── catalog.py                  # programmatic catalog API
│   ├── _bug_search.py              # BM25 bug-report search over the catalog
│   ├── _api_shape_score.py         # OCCT-API leak ratchet
│   ├── _refresh_expected.py        # ground-truth Expected validation lines
│   ├── _merge_staging.py           # staging-area → main corpus merger
│   ├── _regen_section_readmes.py   # regenerate per-section README indexes
│   ├── _tier3_assertions.py        # machine-checkable geometric assertions
│   ├── _mutation_test.py           # 1-byte mutation differential
│   ├── _confidence_report.py       # per-fixture evidence aggregator
│   ├── _reverse_eval.py            # reverse-direction self-evidence eval
│   ├── cli.py                      # `step-corpus` browse CLI
│   └── _quick_verdict.py           # legacy fallback classifier
├── tests/
│   └── test_*.py                   # 512 pytest tests
└── reports/                        # generated per-section validation + triage reports
```

## CI

CI is split into two lanes:

**`.github/workflows/validate-fast.yml`** — runs on every push/PR, target <5 min:

1. `uv run pytest tests/` (minus the two oracle-dependent modules): 500+ self-tests (validator + catalog + bug-search + API-shape + schema + dedup audit + taxonomy)
2. `uv run python -m step_corpus._fixture_lint`: fixture style lint
3. `uv run python -m step_corpus._fixture_source_check`: byte-stable builder round-trip
4. `uv run python -m step_corpus._category_lint --strict`
5. `uv run python -m step_corpus._bytes_tier3_audit`
6. `uv run python -m step_corpus._schema_oracle --strict`

**`.github/workflows/validate-full.yml`** — gated (push-to-main with `[full-ci]` in message, daily 07:13 UTC cron, or manual workflow_dispatch):

1. `uv run python -m step_corpus._run_corpus --workers 4`: validate2 + tier3 across every fixture with all oracles
2. `uv run pytest tests/test_outcome_conformance.py tests/test_tier3_assertions.py`: oracle-dependent self-tests
3. `uv run python -m step_corpus._final_verdict`: DRIFT detection classifier
4. `uv run python -m step_corpus._tier3_assertions`: machine-checkable geometric assertions

Any FAIL or DRIFT verdict fails the job. The split exists because the full sweep takes 50-75 min and would otherwise be cancelled by every new push (Wave-B fixture batches push every 3-8 min). See the top-comments in each workflow for the cadence policy.

## License

MIT; see top-level `LICENSE`.
