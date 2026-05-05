# STEP corpus + validator

A catalogued corpus of STEP-file (ISO 10303-21 / -42 / -214 / -242) input pathologies, paired with a multi-tier validator that adversarially confirms each fixture exhibits the defect it claims.

The goal is to give CAD-kernel and STEP-tooling authors a license-clean, citable, reproducible reference for "what real STEP files look like in the wild when they go wrong": BOMs, half-escaped strings, near-period pcurves, knot-vector mistakes, schema mash-ups, unit confusions, PMI corner cases, and adversarial inputs that production parsers grow tolerance for over time.

## Repository layout

```
├── README.md                       # this file
├── QUALITY_DASHBOARD.md            # per-section stats, top findings, sender-attribution
├── CONTRIBUTING.md                 # how to add an entry / a fixture
├── CHANGELOG.md                    # release notes
├── STEP_PROBLEM_CATALOG.md         # the canonical catalog (1282 entries)
├── STEP_PROBLEM_POTENTIAL_SOURCES.md
├── step-examples/                  # 1282 license-clean .stp fixtures (one per canonical entry)
│   ├── 12-1a-encoding/             # Le*  — encoding & string-literal defects
│   ├── 12-1b-header/               # Lh*  — header & instance-numbering
│   ├── 12-1c-syntax/               # Ls*  — Part-21 grammar
│   ├── 12-2a-pcurves/              # Gp*  — pcurve defects
│   ├── 12-2b-nurbs/                # Gn*  — NURBS / B-spline
│   ├── 12-2c-surfaces/             # Gs*  — surface / curve degeneracies
│   ├── 12-3a-shells/               # Tsh* — shell / orientation
│   ├── 12-3b-wires/                # Twi* — wire / loop / edge
│   ├── 12-3c-faces/                # Tfa* — face / sewing / free bound
│   ├── 12-4-tolerance/             # N*   — tolerance & numerical precision
│   ├── 12-5-units/                 # U*   — units & coordinate systems
│   ├── 12-6-assembly/              # A*, P* — assembly hierarchy (incl. FreeCAD-origin P)
│   ├── 12-7-pmi/                   # Pmi* — PMI / GD&T
│   ├── 12-8-mixed/                 # M*   — tessellation, validation properties, etc.
│   ├── 12-10-perf/                 # Pf*  — scale & performance
│   ├── 12-11-adversarial/          # Ad*  — parser-robustness
│   ├── 12-12-cross-product/        # Xp*  — cross-product / interop pairs
│   └── 12-13-writer-pathology/     # Wr*  — writer-side defects
├── browse/                         # GitHub-Pages-served per-fixture HTML pages
├── index.html                      # landing page for the GitHub Pages site
├── CONFORMANCE_KIT.md              # curated 80-entry conformance subset
├── DEFECT_CLASS_DEFINITIONS.md     # 88 formal defect-class definitions (15 tags + sub-classes)
└── validation/                     # multi-tier validator (uv-managed Python package)
    ├── pyproject.toml
    ├── README.md
    ├── VALIDATION_SUMMARY.md       # global verdict matrix + outstanding work
    ├── SEGFAULT_CHARACTERIZATION.md # 8 unintended-OCCT-segfault fixtures with hypothesised failure paths
    ├── src/step_corpus/            # validators (validate2 + tier3_geometric + …)
    ├── tests/                      # pytest self-tests for the validator
    └── reports/                    # generated per-section reports + triage notes
```

## Use as a standalone repository

This catalog is designed to live as its own GitHub repository. Documentation and per-fixture HTML pages are served via GitHub Pages from the repository root.

```bash
git clone <repo-url>
```

Everything is in the clone: fixtures, catalog, validator, browse pages. The `browse/` directory holds the GitHub-Pages content (per-fixture HTML pages); `.nojekyll` at the root tells GitHub Pages to serve files raw rather than running them through Jekyll.

## What's in the catalog

`STEP_PROBLEM_CATALOG.md` contains 1282 canonical entries. Each entry has:

- **ID**: prefixed by §12.x category (`Le001`, `Gn003`, `Tsh017`, `Pmi049`, `Ad027`, …).
- **Category**: taxonomy slot from the §12 hierarchy.
- **Source(s)**: issue tracker citations, source-comment references, public-doc references. We never copy third-party file contents.
- **Sender / Receiver**: producing and consuming CAD tools where the issue was observed (CATIA, NX, Pro/E, SolidWorks, Inventor, Creo, FreeCAD, OCCT, …).
- **Description**: enough detail to construct a reproducer.
- **Reproducer recipe**: the minimal Part-21 form that demonstrates the defect.
- **Expected kernel behavior**: accept / reject-with-error / heal-to-Y (with diagnostic codes where applicable).
- **Notes**: cross-references and validation observations (segfault characterizations, weak-vs-strong manifestation, etc.).
- **Expected validation**: codified validate2 oracle output, e.g. `occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a`. CI compares live output to this spec and emits `DRIFT` on mismatch, so any future kernel update that changes a fixture's behavior is automatically caught.

## What's in the corpus

For every canonical catalog entry there is a matching `.stp` file at `step-examples/<section>/<ID>.stp`. The fixtures are:

- **License-clean.** Each file is constructed from scratch from the catalog text. None contains copied third-party STEP exchange data.
- **Minimal.** Each fixture demonstrates one defect class. It includes the entities required to express the defect, plus a wrapping PRODUCT chain only when geometric measurement (face area, edge length, etc.) is needed.
- **Self-describing.** The first non-magic content is a `/* */` comment naming the entry ID, title, defect class, and the catalog claim. The `FILE_NAME` first arg matches the entry ID.
- **Dated 2026-04-26**, with `('auto-generated')` author/org/preprocessor slots so provenance is unambiguous.

See `step-examples/README.md` for the per-section index and `CONTRIBUTING.md` for the fixture style guide.

## What the validator does

The validator under `validation/` is a Python package that runs each fixture through up to four oracles in subprocess isolation and produces a JSON behavior-matrix per file:

- **ifcopenshell strict Part-21 parser**: rejects malformed Part-21 regardless of schema.
- **OCCT with auto-healing on**: what most CAD tools effectively do.
- **OCCT with auto-healing off**: raw OCCT load, exposes whether the file is read clean.
- **gmsh OCC** with `Geometry.OCCAutoFix=0`: independent OCC build with healing knobs.

Tier-3 geometric checks compute face areas, edge lengths, vertex tolerances, knot-vector arithmetic where applicable. The validator emits a per-section report at `validation/reports/<section>-validation.md`.

A fixture is **CONFIRMED** when oracle behavior matches the catalog's expected-kernel-behavior. A fixture is **CONFIRMED-WEAK** when the catalog claims a specific failure mode (e.g., crash) but the validator shows a less specific mismatch (e.g., silent-empty); the defect is real but the cited failure path isn't reached at fixture scale. A fixture is **DRIFT** when its live oracle behavior diverges from the catalog-codified expected spec, usually a kernel update that needs catalog re-baselining. A fixture is **FAIL** when oracle behavior contradicts the catalog claim. CI treats DRIFT and FAIL as errors.

## Quick start

Run the validator self-tests:

```bash
cd validation
uv sync
uv run pytest tests/
```

Run the validator on a single fixture:

```bash
uv run python -m step_corpus.validate2 ../step-examples/12-1a-encoding/Le001.stp --json
```

Run the full-corpus parallel runner (validate2 + tier3_geometric per fixture, ≈10 min on 6 workers):

```bash
uv run python -m step_corpus._run_corpus --workers 6
```

Generate per-section verdicts (CONFIRMED / CONFIRMED-WEAK / DRIFT / FAIL) from the runner output:

```bash
uv run python -m step_corpus._final_verdict
```

Per-section reports land in `validation/reports/`. The global summary lives in `validation/VALIDATION_SUMMARY.md`. Top-level discoverability dashboard: `QUALITY_DASHBOARD.md`.

## Using the corpus in your own project

The corpus is intended to be vendored or git-submoduled into kernel test suites. Each fixture's catalog entry tells you what the file is *supposed* to provoke; your test harness can either:

- assert your kernel behaves the way the catalog says it should ("heal", "reject", "accept"), or
- pin a snapshot of your kernel's current behavior and use the corpus as a regression suite.

A typical kernel-test workflow: walk `step-examples/<section>/<id>.stp`, look up `<id>` in `STEP_PROBLEM_CATALOG.json` (machine-readable mirror of the catalog markdown), parse with your kernel, and compare your behavior to the entry's `Expected kernel behavior` and `Expected validation` fields. The browse pages at `browse/<id>.html` render each fixture with byte highlighting on the defect site, useful for human triage.

## Where to find what

| Question | File |
|---|---|
| What defects exist? | `STEP_PROBLEM_CATALOG.md` (human) / `STEP_PROBLEM_CATALOG.json` (machine) |
| What's a good representative subset to start with? | `CONFORMANCE_KIT.md` (curated 80-entry kit, all 15 taxonomy tags) |
| What does each defect class mean formally? | `DEFECT_CLASS_DEFINITIONS.md` |
| Per-section overview / per-tag browse | `browse/index.html`, `browse/by-tag/`, served from repo root via GitHub Pages |
| Validator output / verdict matrix | `validation/VALIDATION_SUMMARY.md` |
| OCCT crash reproducers with hypothesised paths | `validation/SEGFAULT_CHARACTERIZATION.md` |
| One-page tour of "most interesting findings" | `QUALITY_DASHBOARD.md` |
| Per-fixture proof / evidence schema | `EVIDENCE_MODEL.md` |
| Coverage policy / what's intentionally out-of-scope | `COVERAGE_POLICY.md` |

## Project status

The catalog covers §12.1–§12.13 (18 distinct sub-sections) with **1282 canonical entries**. The corpus has one license-clean fixture per entry (1289 `.stp` files including 7 sibling-input pairs). The multi-tier validator runs across all fixtures and produces a verdict matrix with structured fields (provenance_tier, tier3_assertions, byte_assertions) backing 3080+ machine-checkable invariants.

25 fixtures crash OCCT (signal 11); 11 are unanimously rejected by every parser (OCCT, gmsh, ifcopenshell-strict); a further set produces different shape counts between OCCT and gmsh (heal-by-split caught in the act on shared bytes). See `QUALITY_DASHBOARD.md` for the discoverability tour, `validation/VALIDATION_SUMMARY.md` for the verdict matrix, and `EVIDENCE_MODEL.md` for the per-fixture proof model.


## Contributing

See `CONTRIBUTING.md` for the entry format, fixture style guide, license-cleanliness rules, sender-attribution conventions, and PR review checklist.

## License

MIT; see `LICENSE`. The corpus, catalog, validator, and reports are all license-clean original work; nothing is copied from third-party STEP exchange data, so the entire repository can be redistributed under the MIT terms without further attribution requirements.

When citing the corpus or its findings, please reference this repository.
