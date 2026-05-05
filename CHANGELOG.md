# Changelog

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
