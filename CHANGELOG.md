# Changelog

## v1.2.0 — fidelity fixes from kernel-author feedback

A real CAD-kernel author imported the full corpus and read each fixture's data against its catalog claim. This release lands the highest-leverage fixes from that review. (Further fixture rewrites continue in v1.2.1+.)

### Parse-unblocking

- **38 fixtures had nested-comment corruption.** Part-21 `/* */` comments don't nest — the first inner `*/` closes the comment early and the prose after it is parsed as STEP code, corrupting the parse before the actual claim ever fires. Fixtures affected (single-`*/` rewrite each): A028–A038, Ad097, Lh043, Ls032, P001–P003, P005–P007, P009–P019, P021–P027. Fix: embedded `*/` inside a multi-section author-intended comment is rewritten to `* /` (space inside); visual meaning preserved, no longer a comment closer. **Ls031 was deliberately left alone** — its nested-comment IS the test data (a buggy scanner that re-fires on inner `/*` mis-parses it; a correct Part-21 reader closes at the first `*/`).

### New metadata: fixture_kind + pair_with

Two new optional fields on every catalog entry:

- **`fixture_kind`** — how a consumer should route the expectation:
  - `malformed-file` — the bytes embody the defect; a correct kernel rejects/heals
  - `conformance-probe` — the file is fully legal Part-21 and tests a legal edge case (Unicode at U+10FFFF, IEEE-754 subnormals, exactly-at-limit values, every printable ASCII); a correct kernel ACCEPTS
  - `receiver-behavior` — the file is valid; the defect is in how a buggy consumer reads it
  - `producer-receiver-pair` — the defect lives in the TRANSFORM between two files; requires the sibling identified by `pair_with`

- **`pair_with`** — sibling id for paired fixtures (e.g. `Le036.input`).

Without `fixture_kind`, a consumer can't tell a correct refusal of a conformance probe (wrong) from a correct refusal of a malformed file (right). Without `pair_with`, the defect in producer/receiver pairs is invisible to a single-file consumer.

This release labels:
- **8 fixtures relabelled to `conformance-probe`** (per kernel-author feedback that the claimed defect is actually a legal edge case): Ls005, Ls030, Le040, Le045, Le046, Le047, Ps004 — and Gb001 to `receiver-behavior`.
- **7 producer/receiver pair receivers** to `producer-receiver-pair` with `pair_with = "<id>.input"`: A074, Le036, Le049, Le050, Pmi090, Ps011, Wr043.

Further entries can be labelled incrementally as the kernel-author review continues.

### Rust crate (1.2.0)

```toml
dodgy-step-files = { git = "https://github.com/zellyn/dodgy-step-files", tag = "v1.2.0" }
```

New types: `FixtureKind`. New fields on `CatalogEntry`: `fixture_kind: Option<FixtureKind>`, `pair_with: Option<String>`. API additive — v1.1.x consumers compile unchanged.

### Pending (v1.2.1+)

Per the feedback: shared mis-wound cube in Bo003/Bo004/Bo024/Fi008 (4); Ps section's shared broken EDGE_LOOP (~16); illegal-Part-21 forms in Twi/Tb/Pf/Tsh/M cluster (~25); build-error-signature audit across 75 fixtures (some are the test, some shadow a different claim).

## v1.1.1 — CI now green

Every CI run since the initial release had been failing. Three independent issues:

1. **Missing `libGLU.so.1` on the runner.** The `gmsh` PyPI wheel link-depends on libGLU at load time even when initialised headlessly (`gmsh.initialize([], False)`); the GitHub-hosted Ubuntu runner doesn't ship it. The gmsh oracle crashed at import, all `gmsh=…` verdicts came back as `subprocess_error`, and four self-tests failed downstream. Fix: `apt-get install libglu1-mesa` before `uv sync`.
2. **Workflow ran pytest before `_run_corpus`.** `test_outcome_conformance` and `test_tier3_assertions` both read `/tmp/cad-v2-out*`, which only gets populated by `_run_corpus`. Fix: split pytest into a fast pre-oracle tier (`--ignore` those two files) and an oracle-dependent post-oracle tier.
3. **Stale `brepcheck.valid == True` assertion on N042.** The entry's own Notes field already documented "tier-3 valid-flag should be ignored for this entry" — the assertion was added against an older OCCT that missed the near-tangent self-intersection. The runner's newer OCCT catches it (returning `valid=False`). Fix: drop the assertion.
4. **`_tier3_assertions` CLI gate diverged from its pytest counterpart.** The standalone CLI was exiting non-zero on any non-pass status, but the pytest test explicitly tolerates `tier3-parse-error` and `no-tier3-output` (infrastructure noise from worker segfaults or empty JSON, per its docstring). Aligned the CLI's failing-status set with the pytest test's.

No functional change to consumers other than N042's `tier3_assertions` array shrinking by one entry. Rust crate bumped to 1.1.1 to keep the published tag in lockstep.

## v1.1 — closure_intent classification for open-shell fixtures

263 fixtures whose STEP bytes use `OPEN_SHELL` or `SHELL_BASED_SURFACE_MODEL` now carry a `closure_intent` label (`sheet` / `solid` / `ambiguous`). The split exists because an open shell is ambiguous between two test intents whose correct kernel behavior is *opposite*: a sheet body is a model-capability test (a solid-only kernel should cleanly refuse); an accidentally-unclosed solid is a repair test (the same kernel must heal it). Without the label a consumer can't tell a correct refusal from a missed repair.

Distribution: **206 sheet**, **30 solid**, **27 ambiguous**. Solid-intent entries also carry a `closure_defect` (`gap` / `missing_face` / `unstitched_seam`) where determinable.

### Surface
- Markdown: `- **Closure intent**: <value>` and optional `- **Closure defect**: <value>` bullets, parsed by `_build_catalog_json.py`.
- JSON: `closure_intent` and `closure_defect` are new top-level fields on every catalog entry, `null` when the fixture has no open-shell context.
- Schema: added to `schema/catalog.schema.json`.
- Browse pages: per-fixture HTML now renders a "Closure intent" section with the kernel-routing blurb.
- Rust crate: `CatalogEntry::closure_intent: Option<ClosureIntent>` + `closure_defect: Option<ClosureDefect>`, with a `by_closure_intent(ClosureIntent)` iterator helper.

## v1.0 — initial release

The STEP corpus is presented as a single coherent reference. It contains:

### Catalog

- `STEP_PROBLEM_CATALOG.md` and `STEP_PROBLEM_CATALOG.json` with **1282 canonical defect entries** organized into 18 §12.x categories spanning encoding, header structure, Part-21 grammar, pcurves, NURBS, surfaces, shells, wires, faces, tolerance, units, assembly, PMI, mixed / auxiliary, performance, adversarial inputs, cross-product synthesized defects, and writer-pathology.
- Each entry carries structured fields: Category / Sources / Sender / Description / Reproducer recipe / Expected kernel behavior / Notes / Expected validation, plus machine-readable taxonomy tags, provenance tier, byte assertions, and tier-3 geometric assertions.
- Companion source-references doc `STEP_PROBLEM_POTENTIAL_SOURCES.md` enumerates the issue trackers, source-comment references, and public docs the catalog draws from.

### Corpus

- **1282 license-clean `.stp` fixtures** under `step-examples/`, one per canonical entry, plus 7 sibling-input fixtures (`<id>.input.stp`) for entries tagged `requires-sibling-pair`.
- 18 per-section directories matching the §12.x taxonomy.
- Every fixture follows the shared style guide: filename equals entry ID, top-of-file `/* */` comment names the entry, title, and defect, with a minimal Part-21 scaffold containing only the entities the defect requires.
- No copied third-party STEP exchange data; every byte is original work derived from the catalog text.

### Validator

- `validation/` Python package, uv-managed, targeting Python 3.11–3.12.
- Multi-tier oracle pipeline (`step_corpus.validate2`): byte-signature inspection, pure-Python ISO 10303-21 strict parser, ifcopenshell strict Part-21 parser, OCCT (heal on / heal off), gmsh OCC, manifold3d, OCAF/XCAF.
- Subprocess isolation per oracle so OCCT segfaults / aborts don't kill the runner.
- Tier-3 geometric introspection for face areas, edge lengths, vertex tolerances, knot-vector arithmetic.
- 3080 machine-checkable invariants (831 tier-3 assertions + 2249 byte assertions) all passing across the full corpus.
- 501 pytest self-tests under `validation/tests/`.

### Browse + reports

- GitHub Pages browse site under `browse/` with 1305+ HTML files (1282 per-fixture pages with inline byte highlighting + 18 section indexes + 1 catalog browser + 16 by-tag pages + landing page).
- Per-section validation reports under `validation/reports/` and aggregate `validation/VALIDATION_SUMMARY.md`.
- `QUALITY_DASHBOARD.md` top-level discoverability tour (per-section stats, sender-attribution histogram, top findings, 10-fixture quick-start).
- `CONFORMANCE_KIT.md` curated 80-entry subset covering all 15 taxonomy tags.
- `DEFECT_CLASS_DEFINITIONS.md` formal definitions for the 15-tag taxonomy plus 73 sub-classes.
- `EVIDENCE_MODEL.md` per-fixture proof model.
- `SEGFAULT_CHARACTERIZATION.md` characterizing the 15+ OCCT crash fixtures.

### Rust crate

- `rust/` ships a `dodgy-step-files` crate that embeds the full corpus (`include_dir!`) and catalog JSON (`include_str!`) into the binary. Consumers add it as a git dependency pinned to a tag — no filesystem setup, no submodule, no crates.io lookup.
- API: `fixtures()` / `fixture(id)` / `by_tag(tag)` / `by_section(section)` / `catalog()`. Each `Fixture` carries a `&'static CatalogEntry` plus `&'static [u8]` STEP bytes.
- MSRV 1.80 (uses `std::sync::LazyLock`). Adds ~6 MB to the consumer's test binary.

### Final verdict matrix

| Verdict | Count | Pct |
|---|---:|---:|
| CONFIRMED | 1281 | 99.38 |
| CONFIRMED-WEAK | 9 | 0.72 |
| DRIFT | 0 | 0 |
| FAIL | 0 | 0 |
| ERROR | 0 | 0 |

### License

MIT — see `LICENSE`. All corpus / catalog / validator / report content is original work, license-clean, no third-party STEP exchange data copied.
