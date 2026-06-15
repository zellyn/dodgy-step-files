# Plan of attack — comprehensive CAD-healing curriculum

> **North star:** a corpus that, used as the test suite for a new CAD kernel,
> lets it jump straight to feature parity with state-of-the-art healing
> libraries rather than taking 20–30 years of incremental customer-bug fixes.
> Any defect that *any* library (open or closed source) is known to fix and
> we don't have a fixture for is a gap.

> **Invariant:** every fixture in the corpus is *prose-laundered* — we read
> upstream source / docs / tickets to learn the *defect class*, then
> synthesise a minimal fixture from our own templates. We never copy code,
> STEP files, mesh files, or test fixtures from any upstream project.

Current self-assessment: **~5% complete.** OCCT API-surface and per-branch
coverage maps exist (75% / 73% respectively on one library); MeshFix has a
taxonomy doc but no fixtures; CGAL PMP is enumerated but unaudited;
proprietary CAD release notes / KB articles / academic surveys: zero.

---

## Phase 0 — In-flight (this session)

- [x] v1.0.0 — initial public release
- [x] v1.0.0 — Rust crate (`include_dir!` + `include_str!`)
- [x] v1.1.0 — `closure_intent` (sheet / solid / ambiguous) on 263 open-shell fixtures
- [x] v1.1.1 — CI fixes (libGLU, pytest ordering, N042 stale assertion, tier3 CLI status alignment)
- [x] v1.2.0 — kernel-author fidelity feedback round 1:
  - [x] 38 nested-comment fixtures
  - [x] `fixture_kind` + `pair_with` fields
  - [x] 7 conformance-probe relabels + 7 producer/receiver-pair labels
  - [x] OCCT API-surface coverage map (`OCCT_HEAL_COVERAGE.md`, 315 ops, 75% covered)
  - [x] Mesh-defect taxonomy doc (`MESH_DEFECT_TAXONOMY.md`)
- [x] v1.2.1 — canonical cube template:
  - [x] Bo003 / Bo004 / Bo024 regenerated via cube generator
  - [x] Ps001 regenerated
  - [x] 6 illegal-Part-21 fixtures cleaned (Twi048/059/060/061/Tsh048/Tb011/Pf017/Twi091)
  - Note: never tagged; folded into v1.2.2
- [ ] v1.2.2 — Ps-section + deep-coverage + Tfa reclassify:
  - [x] Ps003/005/008/013 regenerated
  - [x] Bo004 / Ps013 Expected resynced
  - [x] Ps008 / Ps013 tier3 resynced
  - [x] OCCT per-branch deep coverage (229 branches, 73% covered)
  - [x] Tfa008 / Tfa044 re-tagged `receiver-behavior` (FixPinFace no-op finding)
  - [ ] CI passes (run 27554183171 in flight at time of writing)
  - [ ] Tag v1.2.2 + GitHub release

---

## Phase 1 — Codebase landscape (research)

- [x] Original landscape agent launched (`a302f7b334dab1848`)
- [x] Mandate-extension agent launched (`a7a5297e374232d94`, includes proprietary release notes + KB articles)
- [ ] Receive both reports → consolidated `CODEBASE_LANDSCAPE.md` in the repo
- [ ] Prioritised list: top 10 sources to audit next, with relevance ranking
- [ ] Commit to repo

---

## Phase 2 — OCCT deep-pass v2 (per-method principled chunking)

- [x] Master enumerator launched (`ae0dc2b8c63032a8c`) — produces `/tmp/occt-methods-todo.json` with 200–400 method tuples
- [ ] Receive enumerator output
- [ ] Launch per-method workers in batches of 3:
  - [ ] Worker script per method (input: file URL + line range; output: JSON branch list)
  - [ ] ~200–400 worker invocations, batched 3 at a time
- [ ] Aggregator: merge worker outputs → `OCCT_HEAL_COVERAGE_V2.md`
- [ ] Cross-reference against catalog (regex matching)
- [ ] Identify UNCOVERED branches (expected: several hundred)
- [ ] Reclassify any branches found to be NO-OP STUBS (like `FixPinFace`)
- [ ] Commit `OCCT_HEAL_COVERAGE_V2.md`, replace v1 in `OCCT_HEAL_COVERAGE.md`

---

## Phase 3 — MeshFix + CGAL PMP deep-pass

- [ ] Decision: separate sub-catalog `dodgy-mesh-files` OR new section in this repo? (Default: separate per agent recommendation. Pending user confirmation.)
- [ ] If separate repo: scaffold `github.com/zellyn/dodgy-mesh-files` (Rust crate + validation harness mirrored from this repo)
- [ ] Master enumerator for MeshFix `.cpp` / `.h` files
- [ ] Per-method Haiku workers (batched 3)
- [ ] Master enumerator for CGAL PMP repair headers
- [ ] Per-function workers (CGAL is header-template-heavy; chunking may differ)
- [ ] Aggregated coverage map: `MESH_HEAL_COVERAGE.md`
- [ ] First batch of mesh fixtures (10–15 per `MESH_DEFECT_TAXONOMY.md` Part D)
- [ ] Mesh-fixture format decision: TESSELLATED_* STEP, companion .stl, or both

---

## Phase 4 — Defect mining from non-source enumerated sources

Per the landscape-extension agent's output, sources include OCCT issue tracker, FreeCAD issues, Parasolid release notes, ACIS docs, PTC/Siemens/SolidWorks KB, slicer issue trackers, academic surveys, ISO errata.

- [ ] OCCT GitHub issues — defect-class extractor (one or more sub-agents)
- [ ] FreeCAD GitHub issues — defect-class extractor
- [ ] Parasolid release notes — defect-class extractor
- [ ] ACIS / Spatial docs — defect-class extractor
- [ ] PTC Creo KB — defect-class extractor (where publicly accessible)
- [ ] Siemens NX / Solid Edge KB
- [ ] SolidWorks knowledge base
- [ ] Autodesk Inventor / Fusion 360 release notes
- [ ] Slicer issue trackers (Cura, PrusaSlicer, Bambu Studio)
- [ ] HOOPS Exchange / CAD Exchanger release notes
- [ ] ISO 10303-21 corrigenda + AP242 errata
- [ ] Academic survey papers (Attene 2013 mesh-repair survey, NIST CAD-interop reports, etc.)
- [ ] Each source → list of prose-described defect classes → diff against existing catalog → gap list

---

## Phase 5 — Adversarial-review pipeline (Stage 1–6 from `/tmp/dsf-pipeline-design.md`)

Build the infrastructure to scale fixture authoring to thousands.

- [x] Stage 1 — format-validity check (`_format_check.py` written; not yet committed)
- [ ] Stage 2 — claim-vs-bytes audit (independent agent reads bytes, no catalog text; writes its own defect description; compare adversarially)
- [ ] Stage 3 — dedup against existing entries (semantic-hash on taxonomy + entity counts + Expected triple)
- [ ] Stage 4 — auto-labeling (`closure_intent`, `fixture_kind`, taxonomy)
- [ ] Stage 5 — live-oracle calibration script (run validate2 + tier3 on a single new fixture; emit Expected line + tier3 assertions)
- [ ] Stage 6 — integration: add to markdown, regen JSON, DRIFT check, ratchet update, browse pages
- [ ] Wire the whole pipeline into a single command: `python -m step_corpus.new_fixture <bytes-or-template> <catalog-claim>`

---

## Phase 6 — Fixture synthesis infrastructure

- [x] Cube generator (`_cube_block.py` written; not yet committed)
- [ ] Move pre-merge `_cube_block.py` into validation/ + ship in v1.2.3
- [ ] Cylinder / cone / torus / sphere generators (each with canonical winding)
- [ ] B-spline curve + surface generators (parameterised: control net + knot vector + multiplicity)
- [ ] Sweep / revolution / extrusion generators
- [ ] Fillet generator (for Fi008 and the dozens of fillet-defect classes upcoming)
- [ ] Boolean-output-shape generator (for downstream-of-boolean fixtures)
- [ ] Triangulation / mesh-block generator (for mesh fixtures in `dodgy-mesh-files`)
- [ ] PMI annotation generator (datum, tolerance frame, dimension)
- [ ] Unit-context generator (mm / inches / mixed)
- [ ] Assembly / NAUO generator (for assembly-defect fixtures)
- [ ] Each generator emits *templates* that take a "perturbation parameter" — the perturbation IS the defect

---

## Phase 7 — Backlog from earlier kernel-author feedback (carry-over)

- [ ] Ps007 / Ps009 / Ps011 / Ps012 / Ps014 / Ps015 — bespoke Ps regens
- [ ] A6 build-error audit groups (75 fixtures):
  - [ ] 24 no-bounds ADVANCED_FACE
  - [ ] 23 EDGE_LOOP doesn't chain
  - [ ] 11 Empty EDGE_LOOP
  - [ ] 17 EDGE_CURVE used twice same orientation (minus the 7 already fixed)
- [ ] A067 / N008 / Pmi001 / Pmi087-089 / Tsh041 — bespoke single-cube fixtures with PMI/GVP wrapping
- [ ] M cluster (~17 inline/nested entity constructors — audit which are legal vs illegal)
- [ ] Phase D additions:
  - [ ] Topologically-valid-but-geometrically-degenerate B-reps wrapped in `MANIFOLD_SOLID_BREP`
  - [ ] Periodic-surface seam / pole degeneracies at import (cylinder / cone / sphere / torus seam, degenerate apex edges)
- [ ] Fi008 — real fillet-defect fixture (needs fillet generator first)

---

## Phase 8 — Mesh sub-catalog scaffolding

If user confirms separate-repo direction:

- [ ] Create `github.com/zellyn/dodgy-mesh-files`
- [ ] Mirror layout: README, CHANGELOG, schema/, validation/, rust/, MESH_DEFECT_TAXONOMY.md
- [ ] Mirror fixture format conventions (per-fixture comment header, byte-stable JSON catalog)
- [ ] Author cube-mesh + tetrahedron-mesh + sphere-mesh templates (analogous to STEP cube generator)
- [ ] First batch of 10–15 fixtures from `MESH_DEFECT_TAXONOMY.md` Part D
- [ ] Validator harness wraps MeshFix CLI + CGAL PMP + a manifold-check
- [ ] Rust crate `dodgy-mesh-files` mirroring the STEP crate's API

---

## Phase 9 — Continuous adversarial-review at scale

Once Phases 2–4 land hundreds of UNCOVERED branches → hundreds of new fixtures.

- [ ] Each new fixture batch passes all 6 Stages of Phase 5 pipeline
- [ ] Periodic "audit days" where the existing corpus is re-read adversarially by a fresh agent that has no access to the catalog text
- [ ] Continuous dedup pass — periodically find near-duplicate fixtures and consolidate
- [ ] Coverage metric maintained per release: `(branches covered / branches enumerated)` across the union of audited libraries

---

## Cadence

- Release every batch of fixes / coverage extension as a numbered patch (v1.2.x for fidelity, v1.3.x for new content)
- Tag once CI passes
- Update `OCCT_HEAL_COVERAGE.md`, `MESH_DEFECT_TAXONOMY.md`, and (new) `CODEBASE_LANDSCAPE.md` on each release
- Don't bundle infrastructure with data — data fixes are v1.2.x patches; infrastructure / new generators are minor bumps (v1.3.0)

---

## Open questions for user

- Mesh sub-catalog: separate repo `dodgy-mesh-files`, OR new section in this corpus? (Lean: separate per agent rec.)
- Worker model for per-method passes: Haiku to save cost (mechanical work), or Sonnet to be safe? (Lean: Haiku.)
- Should the Rust crate eventually expose a higher-level "filter by OCCT-branch-id" API once branches have stable ids? Or keep IDs at fixture-id granularity only?
- Stable-ID policy for branch ids (analogous to fixture ids) — never reuse?

---

## Done so far this session

- v1.0 corrupted-fixture diagnosis
- v1.1.0–v1.1.1: CI infrastructure
- v1.2.0: 38 nested comments + metadata + OCCT API coverage + mesh taxonomy
- v1.2.1: cube regens + Part-21 cleanup (folded into v1.2.2)
- v1.2.2: Ps regens + deep-coverage + Tfa reclassify (CI in flight; tag pending)
- Pipeline design doc + format-check script (not yet shipped)
- Cube-block generator module (not yet shipped)
- Landscape research + defect-source extension agents launched
- OCCT deep-pass v2 master enumerator launched
