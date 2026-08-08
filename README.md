# STEP corpus + validator

A catalogued corpus of STEP-file (ISO 10303-21 / -42 / -214 / -242) input pathologies, paired with a multi-tier validator that adversarially confirms each fixture exhibits the defect it claims.

The goal is to give CAD-kernel and STEP-tooling authors a license-clean, citable, reproducible reference for "what real STEP files look like in the wild when they go wrong": BOMs, half-escaped strings, near-period pcurves, knot-vector mistakes, schema mash-ups, unit confusions, PMI corner cases, and adversarial inputs that production parsers grow tolerance for over time.

> ### 👷 Writing a CAD kernel? Start at [**IMPLEMENTERS_ROADMAP.md**](IMPLEMENTERS_ROADMAP.md).
>
> This README describes the repository. The roadmap describes **the work**: the same
> corpus re-cut into the ~170 distinct repair mechanisms it exercises, ordered so the
> failures that hurt users most come first (35 mechanisms have a fixture that *aborts*
> the reference engine), each pointing at the fixtures that prove you got it right.
>
> Two fields do different jobs and it matters which you read:
> `Expected kernel behavior` is the spec for what a **correct** kernel should do;
> `Expected validation` records what **OCCT 7.8.1 was measured doing**, bugs included.

## Repository layout

```
├── README.md                       # this file
├── QUALITY_DASHBOARD.md            # per-section stats, top findings, sender-attribution
├── CONTRIBUTING.md                 # how to add an entry / a fixture
├── CHANGELOG.md                    # release notes
├── STEP_PROBLEM_CATALOG.md         # the canonical catalog (~2,287 entries — see "Aspiration vs current state" below)
├── STEP_PROBLEM_POTENTIAL_SOURCES.md
├── step-examples/                  # ~2,200 license-clean .stp fixtures (one per catalog entry; gaps tracked in audit/)
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
├── validation/                     # multi-tier validator (uv-managed Python package)
│   ├── pyproject.toml
│   ├── README.md
│   ├── VALIDATION_SUMMARY.md       # global verdict matrix + outstanding work
│   ├── SEGFAULT_CHARACTERIZATION.md # 8 unintended-OCCT-segfault fixtures with hypothesised failure paths
│   ├── src/step_corpus/            # validators (validate2 + tier3_geometric + …)
│   ├── tests/                      # pytest self-tests for the validator
│   └── reports/                    # generated per-section reports + triage notes
└── rust/                           # Rust crate that embeds the full corpus + catalog
    ├── Cargo.toml
    ├── README.md
    ├── src/lib.rs                  # Fixture iterator / by_tag / by_section / catalog()
    └── examples/list.rs
```

## Use as a standalone repository

This catalog is designed to live as its own GitHub repository. Documentation and per-fixture HTML pages are served via GitHub Pages from the repository root.

```bash
git clone <repo-url>
```

Everything is in the clone: fixtures, catalog, validator, browse pages. The `browse/` directory holds the GitHub-Pages content (per-fixture HTML pages); `.nojekyll` at the root tells GitHub Pages to serve files raw rather than running them through Jekyll.

## What's in the catalog

`STEP_PROBLEM_CATALOG.md` contains ~2,287 canonical entries (see "Aspiration vs current state" below for what that number does and doesn't mean). Each entry has:

- **ID**: prefixed by §12.x category (`Le001`, `Gn003`, `Tsh017`, `Pmi049`, `Ad027`, …).
- **Category**: taxonomy slot from the §12 hierarchy.
- **Source(s)**: issue tracker citations, source-comment references, public-doc references. We never copy third-party file contents.
- **Sender / Receiver**: producing and consuming CAD tools where the issue was observed (CATIA, NX, Pro/E, SolidWorks, Inventor, Creo, FreeCAD, OCCT, …).
- **Description**: enough detail to construct a reproducer.
- **Reproducer recipe**: the minimal Part-21 form that demonstrates the defect.
- **Expected kernel behavior**: accept / reject-with-error / heal-to-Y (with diagnostic codes where applicable).
- **Notes**: cross-references and validation observations (segfault characterizations, weak-vs-strong manifestation, etc.).
- **Expected validation**: codified validate2 oracle output, e.g. `occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a`. CI compares live output to this spec and emits `DRIFT` on mismatch, so any future kernel update that changes a fixture's behavior is automatically caught.
  - **The two `occt=` values are not independent measurements — do not read a matching pair as corroboration.** They are one reader preference, `read.surfacecurve.mode` 0 vs 3 (prefer the file's pcurves vs ignore them and recompute), and they are **identical for all 2529 fixtures**. That knob is invisible at token granularity: the token reports `n_roots`, which the setting does not move. It is not invisible at *count* granularity — `Gp177` goes from 6 faces to 1 — but the token cannot express that. Treat `occt=` as a single measurement printed twice; the honest second signal is a real healing pass (`ShapeFix`), which is not yet wired in. Tracked in `BACKLOG.md` §(G).

## What's in the corpus

For every canonical catalog entry there is a matching `.stp` file at `step-examples/<section>/<ID>.stp`. The fixtures are:

- **License-clean.** Each file is constructed from scratch from the catalog text. None contains copied third-party STEP exchange data.
- **Minimal.** Each fixture demonstrates one defect class. It includes the entities required to express the defect, plus a wrapping PRODUCT chain only when geometric measurement (face area, edge length, etc.) is needed.
- **Self-describing.** The first non-magic content is a `/* */` comment naming the entry ID, title, defect class, and the catalog claim. The `FILE_NAME` first arg matches the entry ID.
- **Dated 2026-04-26**, with `('auto-generated')` author/org/preprocessor slots so provenance is unambiguous.

See `step-examples/README.md` for the per-section index and `CONTRIBUTING.md` for the fixture style guide.

## Aspiration vs current state

It's easy to look at "thousands of fixtures" and assume this corpus is comprehensive. **It isn't, and it can't be.** This section is the honest calibration.

### What we're aiming at

Twenty-plus years of accumulated CAD-kernel healing knowledge — every BOM, encoding glitch, malformed B-spline, dangling reference, tolerance miscomputation, periodicity edge case, sewing pathology, PMI mash-up, and adversarial input that production parsers have learned to tolerate. The intent is that a new CAD kernel can grade against this corpus and jump much closer to feature parity, instead of waiting for the same defects to filter in through customer bug reports across a decade.

Concretely, the cited surface includes:

- **OCCT TKShHealing**: 327+ methods, 2058+ implementation branches (per `OCCT_HEAL_COVERAGE_V3.md`).
- **MeshFix + CGAL PMP**: separate mesh-repair surface, taxonomy under `MESH_DEFECT_TAXONOMY.md`.
- **CAx Implementor Forum bug history, OCCT issue tracker, HOOPS, JT, IFC ecosystem**: see `CODEBASE_LANDSCAPE.md` and `PHASE4_DEFECT_MINING.md`.

That total problem space is enormous — somewhere in the high thousands of distinct defect classes once fully enumerated.

### Where we actually are (as of 2026-06-18)

| Measure | Count |
|---|---:|
| Catalog entries (distinct defect classes documented) | 2,302 |
| Active fixtures on disk | 2,309 |
| Fixtures with `Part-21 validator: accept` (0 unintentional syntactic errors) | ~all non-framing |
| Fixtures with `reject` matching an intentional defect claim (DanglingRef, GB18030, etc.) | 11 |
| Fixtures with Python builder source under `fixture_sources/` | 82 |
| **Fixtures individually adversarially verified VALID** (do they really demonstrate the claim?) | **2,280 (98%)** |
| Fixtures with weak demonstration (present but not crisp) | 23 |
| Fixtures with claim-vs-geometry mismatch (in regen queue) | 6 |
| Fixtures awaiting individual semantic verification | 0 |
| Historical quarantine (preserved as evidence; replaced in active corpus) | 84 + 66 |

The catalog uses `### ID — title` for each entry. Numbers are best-effort current; re-run `python -m step_corpus._part21_validator --corpus` and `python -m step_corpus._corpus_consistency_lint` from the `validation/` directory to recompute.

### The gap, plainly

- **Mesh defects (CLOSED, 2026-06-19/23)**: previously deferred because STEP isn't a mesh format. The corpus now carries its own mesh-fixture format — `mesh_builder.py` emits `*.mesh.json` files (vertices + triangles + assertions) under `mesh-examples/12-14-mesh/`. §12.14 has ~760 mesh fixtures (Me001–Me1182) covering MeshFix / CGAL PMP / pyvista defect classes. Oracles in place: pymeshfix, pyvista (B3.3b/c). See `MESH_DEFECT_TAXONOMY.md` for the defect catalog and the §12.14 entries in `STEP_PROBLEM_CATALOG.md` for the per-fixture mechanisms.
- **OCCT branch coverage**: the v3 deep-pass enumerates 2058 implementation branches, of which the catalog currently has ~2,287 entries spanning many of them — but a substantial chunk of those entries describe related-or-overlapping defect classes, so true unique-branch coverage is lower than the raw count suggests.
- **Other CAD codebases**: HOOPS, JT, IFC, Parasolid, ACIS — listed in `CODEBASE_LANDSCAPE.md` as worth auditing, mostly not yet deep-passed.
- **Semantic verification gap (CLOSED, 2026-06-18)**: the corpus-wide adversarial sweep ran 100% sample coverage in two-pass Haiku→Sonnet verification. 98% of fixtures (2,280/2,309) demonstrate their claim crisply; the remaining 29 are either weak (23) or claim-vs-geometry mismatches (6 in regen queue at `audit/CONFIRMED_INVALID_REGEN_QUEUE.md`).
- **Sender/receiver attribution**: many entries cite the OCCT method that exhibits the defect, not the producer that wrote the malformed file. Real-world provenance attribution (which CAD tools produce which defects, at what rates) is a separate effort outside this corpus.

### How to read the corpus given the gap

- **Use it as a regression-suite seed**, not as a conformance kit. If your kernel passes every fixture, you've handled a meaningful slice — but expect customer bugs that aren't in here.
- **Treat absence of a defect class as "not yet documented", not "doesn't exist"**. The catalog grows; check git history.
- **Match your interest area to a section**. The §12.3a-shells / §12.3c-faces / §12.3b-wires / §12.2 geometry sections are densest; §12.6-assembly / §12.7-pmi are sparser; §12.5-units is small.
- **The `_quarantine/` directory holds historical-evidence fixtures**. `early-waves/` are pre-template-fix originals (84 IDs); `phase_F_boilerplate/` are the generic-cube versions produced by a misguided regen pass (66 IDs) — both are PRESERVED but REPLACED in the active corpus by defect-specific regens. The IDs themselves are not missing; the active version is at `step-examples/<section>/<ID>.stp`.

### Python builder for new fixtures

Going forward, new fixtures should be authored as Python sources at
`fixture_sources/<section>/<ID>.py` using the minimal builder at
`validation/src/step_corpus/step_builder.py`. The builder takes
responsibility for Part-21 correctness — agents (or humans) write
geometric intent, the builder writes syntax. See
`fixture_sources/README.md` for the API and conventions.

Consumers still read `.stp` files; the `.py` sources are build-time
only.

### Whittling the gap

This README's count tables should be re-checked and updated at every release. Concrete next-work items are tracked in:

- `audit/SESSION_SUMMARY_*.md` — what was found and fixed in each major audit pass
- `audit/lint_rule_candidates.md` — Part-21-validator rules proposed but not yet implemented
- `audit/audit_remaining.txt` — fixture IDs still awaiting individual adversarial verification (currently empty; sweep complete)
- `audit/CONFIRMED_INVALID_REGEN_QUEUE.md` — the small list of fixtures whose geometry doesn't yet match the claim
- `fixture_followups/` — per-fixture notes on weak-or-invalid findings with regen plans

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

Each fixture's catalog entry tells you what the file is *supposed* to provoke; your test harness can either:

- assert your kernel behaves the way the catalog says it should ("heal", "reject", "accept"), or
- pin a snapshot of your kernel's current behavior and use the corpus as a regression suite.

A typical kernel-test workflow: walk the fixtures, look up each id in `STEP_PROBLEM_CATALOG.json` (machine-readable mirror of the catalog markdown), parse with your kernel, and compare your behavior to the entry's `Expected kernel behavior` and `Expected validation` fields. The browse pages at `browse/<id>.html` render each fixture with byte highlighting on the defect site, useful for human triage.

### From Rust

The `rust/` directory ships a crate (`dodgy-step-files`) that embeds the full corpus and catalog. Consume it as a git dependency pinned to a tag:

```toml
[dependencies]
dodgy-step-files = { git = "https://github.com/zellyn/dodgy-step-files", tag = "v1.4.0" }
```

```rust
for f in dodgy_step_files::fixtures() {
    let _ = (f.entry.id.as_str(), f.entry.expected_validation.as_str(), f.step_bytes);
}

for f in dodgy_step_files::by_tag("crash") { /* ... */ }
```

No filesystem setup, no submodule. Adds ~6 MB to your test binary. See [`rust/README.md`](rust/README.md) for the full API.

### From any other language

Walk `step-examples/<section>/<id>.stp` and load metadata from `STEP_PROBLEM_CATALOG.json`. Either vendor a snapshot, add the repo as a git submodule, or download a release tarball from the [releases page](https://github.com/zellyn/dodgy-step-files/releases). The catalog JSON schema is documented in [`schema/`](schema/).

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
| OCCT healing-operation coverage map (API-surface pass) | `OCCT_HEAL_COVERAGE.md` |
| OCCT per-branch deep coverage (v2 — line-by-line implementation pass) | `OCCT_HEAL_COVERAGE_V2.md` |
| OCCT per-branch rich-prose deep coverage (v3 — falsifiable claims + minimal reproducers) | `OCCT_HEAL_COVERAGE_V3.md` |
| Mesh-defect taxonomy + repair-surface survey | `MESH_DEFECT_TAXONOMY.md` |
| Mesh-repair (MeshFix + CGAL PMP) per-method coverage map | `MESH_HEAL_COVERAGE.md` |
| Codebase landscape (codebases worth auditing beyond OCCT/MeshFix/CGAL) | `CODEBASE_LANDSCAPE.md` |
| Plan-of-attack for the comprehensive-curriculum effort | `PLAN_OF_ATTACK.md` |
| Phase 4 defect-class mining results (issue trackers + CAx-IF + HOOPS) | `PHASE4_DEFECT_MINING.md` |
| Coverage policy / what's intentionally out-of-scope | `COVERAGE_POLICY.md` |

## Project status

The catalog covers §12.1–§12.13 (18 distinct sub-sections) with **2,302 canonical entries** as of 2026-06-18. The corpus has roughly one license-clean fixture per entry (2,309 `.stp` files; 150 historical quarantines in `_quarantine/` — 84 early-waves + 66 phase_F_boilerplate — all of which have been replaced in the active corpus by defect-specific regens). See **"Aspiration vs current state"** above for what these numbers do and don't imply.

The Part-21 validator under `validation/src/step_corpus/_part21_validator.py` runs across the corpus in seconds and finds 0 unintentional syntactic errors in non-framing sections. The multi-tier semantic validator runs across all fixtures and produces a verdict matrix with structured fields (provenance_tier, tier3_assertions, byte_assertions).

25 fixtures crash OCCT (signal 11); 11 are unanimously rejected by every parser (OCCT, gmsh, ifcopenshell-strict); a further set produces different shape counts between OCCT and gmsh (heal-by-split caught in the act on shared bytes). See `QUALITY_DASHBOARD.md` for the discoverability tour, `validation/VALIDATION_SUMMARY.md` for the verdict matrix, and `EVIDENCE_MODEL.md` for the per-fixture proof model.


## Contributing

**Please do not open pull requests.** This repository is maintained by a Claude agent that
owns the corpus and synthesizes every fixture itself, so that all `.stp` files stay
license-clean original work and each one is adversarially verified to exhibit the defect it
claims (see "What the validator does" above). Unsolicited PRs can't be merged.

**The way to contribute is to [file an issue](../../issues/new)** describing a problematic
input — a STEP/AP242 file (or class of files) that a real CAD kernel or STEP tool mishandles.
A good issue includes:

- **What goes wrong** — the sender/receiver tools, the symptom (crash, silent wrong result,
  rejection, heal-and-accept), and, if you have it, a citation (issue-tracker link, forum
  thread, spec clause).
- **The input pattern** — describe the offending structure in words (e.g. "a `B_SPLINE_CURVE`
  whose `weights_data` count differs from `control_points_list`", or "two `PRODUCT`s sharing
  one name disambiguated only by NAUO id"). A precise prose description is enough; we
  synthesize the fixture from it.
- **The file itself — only if you have the right to share it.** Attach or paste it *only* when
  it's your own output or otherwise redistributable. **Do not attach proprietary,
  customer, or NDA-covered STEP data.** We never copy third-party file contents into the
  corpus; the maintainer reads your description and builds a fresh, minimal, license-clean
  fixture that reproduces the defect class.

The repo-owner Claude then triages the issue, writes a catalog entry + a Python builder that
emits a byte-stable `.stp`, verifies it against the multi-tier validator, and pushes the
result to `main`. See `CONTRIBUTING.md` for the internal entry format, fixture style guide,
and license-cleanliness rules the maintainer follows.

## License

MIT; see `LICENSE`. The corpus, catalog, validator, and reports are all license-clean original work; nothing is copied from third-party STEP exchange data, so the entire repository can be redistributed under the MIT terms without further attribution requirements.

When citing the corpus or its findings, please reference this repository.
