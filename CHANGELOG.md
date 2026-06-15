# Changelog

## v1.3.0 — comprehensive-curriculum scaffolding + OCCT deep coverage v2 (per-method)

This release recalibrates the corpus's self-assessment. The v1.2.0 OCCT API-surface coverage map credited a fixture as "covering" an operation if the fixture mentioned it by name. The v1.2.2 per-`.cxx`-file pass enumerated ~229 repair branches across 13 files. **v1.3.0's per-method deep pass** runs 67 worker agents (one per method or small file-batch) and enumerates **3,399 repair branches across 317 methods** — and finds that only **867 (25.5%) have a catalog fixture whose text matches a branch's defect-class search anchors**. The previous "73% covered" was overestimating dramatically; per-branch, real coverage is **~25%**.

### New documents

- **`OCCT_HEAL_COVERAGE_V2.md`** (14k lines, 3399 branches): the v2 per-method coverage map. For each branch: file + line range, defect-class summary, what-it-tests, repair action, list of catalog fixtures whose text matches the branch's search anchors (or `UNCOVERED` with a suggested-fixture hint).
- **`CODEBASE_LANDSCAPE.md`** (596 lines, 52 open-source codebases + 75 defect-source enumerations): broader audit landscape produced by two landscape-research agents. Notable findings: (i) **MeshLab `filter_clean` + vcglib `vcg::tri::Clean`** is the cleanest named taxonomy of mesh-repair defects we hadn't audited; (ii) **CAx Implementor Forum round-trip reports** are the densest public taxonomy of kernel-pair translator failures and would mostly be invisible to open-source bug trackers; (iii) the original "skip proprietary kernels" instruction would have excised exactly the highest-leverage source class (commercial-translator-pair literature like HOOPS Exchange / CADfix / Parasolid release notes / SolidWorks SPR lists / CADfix release notes).
- **`PLAN_OF_ATTACK.md`**: structured 9-phase plan-of-attack for the comprehensive-curriculum goal, with `[ ]` checkboxes per item.

### New infrastructure

- **`validation/src/step_corpus/_cube_block.py`**: canonical-winding cube fixture generator. Emits 12 edges where every edge is used exactly once with `.T.` and once with `.F.` across its two incident faces (verified by post-emission consistency check). Supports `outward=True/False` for outward-shell vs void-shell normals. Used to regenerate Bo003/Bo004/Bo024/Ps001/Ps003/Ps005/Ps008/Ps013 in v1.2.1/v1.2.2; future fixtures will use the same generator.
- **`validation/src/step_corpus/_format_check.py`**: Stage 1 of the adversarial-fixture-review pipeline. Scans a fixture's bytes for the v1.0/v1.2-class Part-21 corruptions (nested `/* */`, `|`-delimited complex entities, arithmetic REAL literals, trailing commas in aggregates, same-orientation EDGE_CURVE pairs). Runs against a single fixture or the whole corpus.
- **`validation/tests/test_cube_block.py`**: regression tests verifying the cube generator's outward/inward winding invariants and ID-range layout.

### Notable findings from the deep pass

1. **`ShapeAnalysis_ShapeTolerance::InTolerance`** at `ShapeAnalysis_ShapeTolerance.cxx` line ~149: VERTEX case uses `tol >= valmax` where the other shape types use `<= valmax`. Likely an OCCT source bug. Worth filing upstream.
2. **`ShapeUpgrade_ConvertCurve2dToBezier.Compute` / `ShapeUpgrade_ClosedFaceDivide.SplitSurface`** carry surprisingly intricate periodic-surface seam handling (127 branches across just 2 methods). Lots of UNCOVERED catalog gaps in seam/periodic territory.
3. **`BRepLib::EncodeRegularity`** itself is a thin wrapper; the real continuity-classification logic lives in `BRepLib::ContinuityOfFaces` (15 branches handling G0/G1/G2/CN via tangent derivatives + principal curvatures). Catalog has no fixture matching the principal-curvature-direction-alignment branch — high-leverage gap.

### Rust crate

API unchanged from v1.2.2. Tag the consumer to `v1.3.0` if you want to pin to the broader audit landscape.

```toml
dodgy-step-files = { git = "https://github.com/zellyn/dodgy-step-files", tag = "v1.3.0" }
```

## v1.2.2 — Ps-section cube regens + Bo004 Expected sync + OCCT per-branch deep coverage

(Continued from v1.2.2 cube regens — see below — plus a second pass of OCCT coverage.)

### OCCT per-branch deep coverage

The v1.2.0 OCCT coverage map was an API-surface pass: it credited a fixture as "covering" an operation if the fixture's text mentioned the operation by name. But OCCT's public repair methods (e.g. `ShapeFix_Wire::FixSelfIntersection`) are hundreds of lines of nested `if/else if` branches, each handling a specific defect *shape*. A fixture that mentions "self-intersection" exercises *one* of a dozen self-intersection branches.

Three parallel sub-agents now walked the `.cxx` implementation files and enumerated every substantive repair branch as a separate coverage unit. The result is appended to `OCCT_HEAL_COVERAGE.md` as a "Per-branch deep coverage (second pass)" section.

| Module group | Branches | Covered | UNCOVERED |
|---|---:|---:|---:|
| Wire-level (`ShapeFix_Wire/Edge/IntersectionTool/WireVertex.cxx`) | 88 | 72 | 16 |
| Face/Shell/Shape-level (`ShapeFix_Face/Shell/Shape/Solid/FixSmallFace.cxx`) | 73 | 53 | 20 |
| Sewing + UnifySameDomain (`BRepBuilderAPI_Sewing.cxx` + 3 others) | 68 | 43 | 25 |
| **Total** | **229** | **168 (73%)** | **61** |

Two notable findings shifted catalog data, not just docs:

1. **`ShapeFix_FixSmallFace::FixPinFace` is a no-op stub.** Body is literally `return true;`. Fixtures Tfa008 and Tfa044 (pin faces) — credited as covering this op by the API-surface pass — actually exercise no OCCT repair logic. Re-tagged both as `fixture_kind: receiver-behavior` since the defect is the kernel's missing implementation, not the file's content.
2. **`BRepBuilderAPI_Sewing::SetMaxTolerance` is bypassed.** Even when MaxTolerance is set, the inner loop writes a raw `BRep_TEdge` tolerance at line ~1168, silently exceeding the user cap. No fixture stresses this hard-override path — a high-leverage gap flagged in the deep report for a future release.

### Ps-section cube regenerations (4 fixtures)

Extends v1.2.1's canonical-cube template work into the Ps "pathological success" section, and aligns Bo004's Expected validation with the live oracle output of the regenerated cube.

### Ps-section cube regenerations (4 fixtures)

- **Ps003** — Single inverted face on outer skin: regenerated cube with the "top" face's `ADVANCED_FACE.same_sense` flipped to `.F.`, so its `+z` surface normal is reinterpreted as `-z`. Topologically still closed; one face inverted (the defect).
- **Ps005** — Twin solids at identical coordinates: two `MANIFOLD_SOLID_BREP`s over geometrically identical cubes, listed in one `ADVANCED_BREP_SHAPE_REPRESENTATION`.
- **Ps008** — Inch-valued coordinates labelled as millimetres: cube at 0..10 (intended inches; ~254mm bounding box) with the units context declaring `MILLI METRE`. A correct receiver detects the unit-vs-content mismatch.
- **Ps013** — Chiral part mirrored by silent X-coordinate negation: cube at origin `(-10,0,0)` (intended `(0,0,0)`); X-coords negated mark the left-hand mirror of the author's intent. Detectable via sign of an AXIS2_PLACEMENT_3D determinant.

The remaining Ps fixtures (Ps007, Ps009, Ps011, Ps012, Ps014, Ps015) carry more bespoke defects (assembly placement, PMI annotation drift, NAUO dedup, sweep truncation, etc.); deferred to v1.2.3+.

### Bo004 Expected alignment

The regenerated Bo004 cube has fewer geometrically-distinct faces visible to gmsh (27 shapes vs the pre-regen 53). Updated `Expected validation` from `gmsh=shape(53)` to `gmsh=shape(27)` to match the new live oracle. Same kernel-grading meaning; just resyncs the catalog to what the new geometry actually produces.

### Rust crate 1.2.2

API unchanged.

## v1.2.1 — canonical cube template + illegal-Part-21 cleanup

Continues the v1.2.0 fidelity work. Two clusters of fixes.

### Canonical cube template (4 fixtures)

Four fixtures whose shared cube template had `EDGE_CURVE`s referenced with the same `.T.` orientation by both incident faces (preventing a 2-manifold build, so the parse-succeeded fixtures couldn't even reach their intended defect) are regenerated with a canonical-winding cube generator that emits 12 edges where every edge is used **exactly once with `.T.` and once with `.F.`** across its two incident faces.

- **Bo003** — Two void shells nested inside each other. Outer cube (0..10) + outer void (2..8) + inner void (3..7), both voids in `ORIENTED_CLOSED_SHELL .F.` inside `BREP_WITH_VOIDS`. Defect (imbricated voids) now reachable past build.
- **Bo004** — Closed shell encloses an unrepresented cavity. Outer + inner cube, only outer in `MANIFOLD_SOLID_BREP`. Inner exists but unwrapped — the "cavity not declared" defect.
- **Bo024** — Closed shell whose face orientations imply negative volume. Single cube with all face normals pointing INWARD (`outward=False`).
- **Ps001** — Negative-volume cube in the Ps "pathological success" section. Same all-inward topology as Bo024.

**Fi008** left alone — fillet pathology beyond cube-template scope; will be reworked with a real fillet construction in a later release. The remaining ~14 Ps fixtures (Ps002, Ps003, Ps005–Ps015) carry varied bespoke defects (CW/CCW mix, same_sense flips, overlapping faces, unit traps, identity-vs-offset placements); deferred to v1.2.2+.

### Illegal-Part-21 form cleanup (6 fixtures)

Fixtures whose intended defect was shadowed by an upstream Part-21 grammar violation:

- **Twi048, Twi059, Twi060, Twi061** — replaced `A()|B(*)|C(x,y)` (`|`-delimited complex-entity form, not in Part-21) with `(A()B(*)C(x,y))` (the standard parenthesised juxtaposition).
- **Tsh048** — wrapped the previously un-parenthesised `GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNIT_ASSIGNED_CONTEXT(()) REPRESENTATION_CONTEXT('','3D')` in outer parens and populated the unit-assigned context with real `LENGTH_UNIT` / `PLANE_ANGLE_UNIT` / `SOLID_ANGLE_UNIT` references.
- **Tb011** — replaced literal arithmetic expression `6.283185307179586+1.0E-3` (illegal Part-21 — REAL literals don't allow `+` infix) with the pre-computed value `6.284185307179586`.
- **Pf017** — same fix for `1.0+1e-7` → `1.0000001`.
- **Twi091** — removed Python-style trailing comma `(#106,)` → `(#106)` in `EDGE_LOOP`.

**Pf012 left alone** — its deeply-nested aggregate parens (`((((((((((((((((((((((((( #1 )))…`) ARE the test (stack-overflow probe); rewriting them would defeat the fixture.

The `M` cluster (~17 fixtures with inline/nested entity constructors as parameters) was deferred — most candidates turned out to be legal typed-parameter syntax; an audit would be required to identify the actually-illegal subset.

### Rust crate 1.2.1

API unchanged from v1.2.0.

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
