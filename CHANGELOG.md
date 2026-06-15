# Changelog

## v1.1.1 — CI: install gmsh runtime deps (libGLU)

CI workflow now installs `libglu1-mesa` before syncing Python deps. The gmsh PyPI wheel link-depends on libGLU even when initialised headlessly (`gmsh.initialize([], False)`), and the GitHub-hosted Ubuntu runner doesn't ship it. Every CI run since the initial release was failing four self-tests for this reason (gmsh subprocess crashed at import, all `gmsh=…` verdicts came back as `subprocess_error`, conformance fell to zero).

No functional change to consumers or the published corpus; only the workflow file changed. Rust crate bumped to 1.1.1 to keep the published tag in lockstep.

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
