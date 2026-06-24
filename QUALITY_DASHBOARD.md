# STEP Corpus + Validator — Quality Dashboard

A single-page tour of what's inside, what holds up under adversarial validation, and where to start poking around. For the project overview see [README.md](README.md); for the canonical defect index see [STEP_PROBLEM_CATALOG.md](STEP_PROBLEM_CATALOG.md); for the long-form summary see [validation/VALIDATION_SUMMARY.md](validation/VALIDATION_SUMMARY.md).

## Top-line stats

_Refreshed 2026-06-23. Many "best-effort current" metrics below were
last computed at the noted timestamps; rerun the validators (commands
at the bottom) to recompute._

| Metric | Value |
|---|---:|
| Catalog entries | **3,086** (≈2,355 STEP + **731** mesh entries Me001–Me1182 — 41 mesh waves, 2026-06-23) |
| Active fixtures (`.stp` files) | **2,350** STEP (+ 7 sibling-input fixtures) |
| Quarantined (preserved as evidence; replaced in active corpus) | **150** (84 early-waves + 66 phase_F_boilerplate) |
| Mesh fixtures (§12-14 mesh corpus) | **760** `.mesh.json` fixtures (Me001–Me1182) via Python builder + JSON/OBJ/PLY co-emit + pure-Python oracle — waves 1–41 |
| Adversarial-verification sweep (2026-06-18, full corpus) | **2,280 / 2,309** (98.7 %) verified VALID; 23 CONFIRMED_WEAK; 0 CONFIRMED_INVALID after regen |
| CONFIRMED (Expected-validation line matches live oracle output) | **2337 / 2349** (99.49 %) per `_final_verdict` 2026-06-19; 12 WEAK, 0 ERROR — rerun pending against expanded corpus |
| Expected validation coverage | **2342 / 2347** (99.8 %) for STEP entries — mesh fixtures use separate mesh oracle |
| Q5 stale-assertion fixes (3 sweeps, 2026-06-22/23) | **362** tier-3 / byte assertions refreshed to live-oracle baselines — eliminated all DRIFT in oracle-active subset |
| Machine-checkable **tier-3** assertions in catalog | ≥**2,184** entries (93.1 % coverage; CI ratchet floor at 90 %) |
| Machine-checkable **byte** assertions in catalog | ≥**2,347** across ≥**1,056** entries |
| Total machine-checkable invariants | ≥**4,915** |
| Entries with at least one invariant | **>2,180 / 2,347** (>92 %) |
| Bug-reporter synonyms | **1127** `Synonyms:` lines covering most §12.1-§12.8 entries (improves BM25 recall on natural-language queries) |
| Writer-pathology runtime oracle (`_writer_oracle`) | 34 simulated / 9 skipped = **43 Wr* entries** covered with active byte-level reproduction |
| Category-lint structural-issue ratchet | **0** violations |
| Construction-validity lint (non-unit DIRECTION, parallel axis/refdir) | **0** unexempted violations (9 catalog-claim-IS-defect exempt) |
| Tier-3 placeholder-geometry lint | **0** violators (21 EXEMPT_PLACEHOLDER for non-geometric claims) |
| Schema-vocabulary oracle (FILE_SCHEMA vs entity vocabulary) | **0** unexpected violations · **8** EXEMPT_SCHEMA_MISMATCH (catalog-claim-IS-mismatch) |
| Cross-reference lint (broken `**See also**:` links) | **0** broken · pytest-locked |
| OCC-behavior annotations (catalog-vs-OCC divergence documented) | **975** entries documenting real OCC kernel bugs the catalog now witnesses |
| Provenance tiers explicitly tagged | **37** entries |
| Sibling-input fixtures for `requires-sibling-pair` entries | **7** (Le036, Le049, Le050, Ps011, A074, Pmi090, Wr043) |
| External-kernel cross-validation (pure-Python ISO 10303-21 strict vs OCCT) | **94.7 %** agree-accept; 22 OCC-silently-heals; 8 OCC-stricter-than-spec; 16 spec-clean OCC crashes |
| Manifold-validity oracle (manifold3d on tessellated geometry) | 70 `empty_mesh` (sub-tolerance) · 139 `not_manifold` · 22 segfault-during-tessellation · 769 no-shapes-loaded |
| Silent-empty oracle baseline (evidence = byte-review, not oracle) | **755 / 1282** (~59 %) in legacy cohort; proportion lower in expanded corpus due to more oracle-active STEP entries and separate mesh oracle |
| Oracle-active subset (loads-with-shapes / crashes / rejects / non-silent diagnostic) | **266** STEP (exact rerun pending against 2350-entry corpus) |
| Confirmed OCC segfault fixtures | **25** |
| Structural-mutation detection on silent-empty subset | **9.9 %** detection rate on silent-empty (88 % structurally inert under #N reference swap); mitigated by PRODUCT-wrap; **362 Q5 stale-assertion fixes** tightened oracle-active detection rate |
| Format-invariance test (whitespace/CRLF/comment-strip robust) | **98.0 %** invariant |
| Cross-fixture similarity audit (BM25, threshold 0.6) | 45 high-similarity pairs all linked bidirectionally; **0 unlinked** |
| Catalog claim formalization (auto-extracted outcome tags) | **604** entries tagged with allowed/disallowed outcomes |
| Outcome conformance (live oracle vs catalog `allowed` set) | **248 conform · 931 outside-allowed · 100 violate-disallowed · 3 no-tags** |
| OCCT-API token-hits in scored fields | **0** |
| Distinct §12.x sections | **19** (added §12.14 mesh) |
| Bug-report search regression queries | **340** (last computed; rerun pending) |
| Pytest self-tests | **520** (+19 over the old 501 — solvespace_oracle, tier3_coverage_ratchet, mesh-related) |
| OCAF/XCAF document-level oracle (`_ocaf_oracle`) | tests label/color/transform/assembly persistence on §12.6-assembly entries; 70/102 fixtures load OCAF tree, 30 fail at OCAF reader, 2 segfault (subprocess-isolated) |
| Per-fixture HTML byte highlighting | **2020/2343** byte assertions (86 %) yield positional matches; **961/1318** browse pages render `<mark>`-highlighted defect bytes inline |
| Conformance Kit (curated subset) | **80 entries / 1282** (~3.5 % of current 2313); count predates corpus growth — rerun pending |
| Formal defect-class definitions | **88 definitions** (15 taxonomy + 73 sub-classes) in `DEFECT_CLASS_DEFINITIONS.md` and `browse/defect-classes/`; covers the v0.3 catalog, not yet extended to §12.14 mesh |
| Per-entry **Model impact** annotations | last computed at 1282-entry corpus — rerun pending against current 2313 |
| OCCT path:line citation audit | 49 unique citations verified — 100 % resolve in current OCCT |
| Bug-tracker URL audit | 153 OCCT MANTIS URLs · FreeCAD / IfcOpenShell / CadQuery / sourceforge / GitHub all resolve cleanly |
| GitHub Pages browse site (`/index.html`, `/browse/`, `/browse/by-tag/`) | **1305+ HTML files** (1282 per-fixture + 18 section indexes + 1 catalog browser + 16 by-tag pages). Pages served from repo root via `.nojekyll` |
| Defect-class taxonomy (cross-cutting tags) | **15 tags** auto-derived from existing fields; **1682 tag-entry pairs** across 1282 entries; **0** untagged. Distribution: topology 336, spec-violation 238, silent-loss 144, geometry 131, pmi 130, assembly 114, round-trip 91, crash 90, syntax 90, adversarial 73, units 63, encoding 54, writer 50, interop 44, performance 34. |

**Read CONFIRMED carefully:** it means the codified `**Expected validation**:`
line matches live oracle output. For most fixtures (silent-empty
baseline), both sides are silent regardless of fixture content, so
CONFIRMED on those entries is *catalog-spec consistency*, not
*oracle-independent verification*. Those fixtures get their evidence
from entity-graph adversarial review (forward + reverse). The
non-silent fixtures (reject / segfault / shape-loading) carry stronger
oracle signal.

## Per-section table

Each section maps to one fixture directory under `step-examples/` (or
`mesh-examples/` for §12.14) and one validation report under
`validation/reports/`. Counts refreshed 2026-06-18.

| Section | Section dir | Fixtures |
|---|---|---:|
| §12.1a encoding | 12-1a-encoding | 57 |
| §12.1b header | 12-1b-header | 45 |
| §12.1c syntax | 12-1c-syntax | 46 |
| §12.2a pcurves | 12-2a-pcurves | 163 |
| §12.2b NURBS | 12-2b-nurbs | 167 |
| §12.2c surfaces | 12-2c-surfaces | 177 |
| §12.3a shells | 12-3a-shells | 263 |
| §12.3b wires | 12-3b-wires | 269 |
| §12.3c faces | 12-3c-faces | 259 |
| §12.4 tolerance | 12-4-tolerance | 194 |
| §12.5 units | 12-5-units | 37 |
| §12.6 assembly | 12-6-assembly | 108 |
| §12.7 PMI | 12-7-pmi | 122 |
| §12.8 mixed | 12-8-mixed | 217 |
| §12.10 perf | 12-10-perf | 37 |
| §12.11 adversarial | 12-11-adversarial | 82 |
| §12.12 cross-product | 12-12-cross-product | 44 |
| §12.13 writer-pathology | 12-13-writer-pathology | 63 |
| §12.14 mesh | 12-14-mesh | 760 (Me001–Me1182; waves 1–41) |
| **Total** | | **3,110** STEP+mesh (2,350 STEP + 760 mesh) |

Per-section CONFIRMED/WEAK breakdown last computed under the old
1082-entry corpus; rerun `_final_verdict` to recompute against
the current 2350-STEP-fixture set. The full-corpus adversarial sweep
(2026-06-18) found 2280/2309 (98.7%) VALID; the per-section
distribution of weak fixtures was concentrated in §12.2b NURBS
and §12.2c surfaces (now all regenerated — see DONE.md). Mesh
fixtures (§12.14) use a separate oracle; CONFIRMED metric covers
STEP entries only. 362 Q5 stale-assertion fixes applied 2026-06-22/23.

## Most interesting findings

### 15 OCCT segfaults — kernel actually crashes

Each crashes identically under `occt_heal_on`, `occt_heal_off`, and gmsh's OCCT-backed reader; stderr is empty (the crash happens below `Message_Messenger`'s flush boundary). Catalog: **Ad015, Ad077, Gp001, Gp019, Gn003, Gn004, Gs026, Tsh023, U008, U009, A021, Pmi049, M005, M018, Twi044**. 8 are catalog-consistent ("crashes reader" claims, often citing Mantis 0029478). 6 are *stronger than catalog*: see [SEGFAULT_CHARACTERIZATION.md](validation/SEGFAULT_CHARACTERIZATION.md).

- **[Twi044](step-examples/12-3b-wires/Twi044.stp)**: face contains a 5e-7 mm² inner wire below the global 1e-7 uncertainty ratio. Catalog said "needs healing"; validation says the lack of healing is a hard-failure reproducer. Hypothesized path: NaN propagation through `BRepLib::SameParameter` after `ShapeAnalysis_Wire` collapses sub-tolerance vertices.
- **[U008](step-examples/12-5-units/U008.stp)** / **[U009](step-examples/12-5-units/U009.stp)**: cross-context `MAPPED_ITEM` mixing inch + mm `GEOMETRIC_REPRESENTATION_CONTEXT`s. Catalog framed these as silent mis-scale defects; validation finds `Transfer_TransientProcess` context-cache corruption that escalates to signal 11.
- **[Pmi049](step-examples/12-7-pmi/Pmi049.stp)**: tessellated geometry with no `styled_item`/color where the same `TRIANGULATED_FACE` is shared by multiple `TESSELLATED_SHELL` parents. Crash, not silent-empty as catalog suggested.
- **[A021](step-examples/12-6-assembly/A021.stp)**: heterogeneous CDORSI `style_context` per Saved View component (WR1 violation).
- **[M005](step-examples/12-8-mixed/M005.stp)**: `TRIANGULATED_FACE` with a triangle whose three indices reference the same coordinate.

### Kernel divergence — OCCT and gmsh disagree on shape count

Both kernels load the file but produce different topology: direct evidence that malformed input is interpreted differently by independent implementations. Examples (occt vs gmsh shapes):

- **[Tfa011](step-examples/12-3c-faces/Tfa011.stp)** `shape(1) vs shape(18)`: multiple-outer-wire face. gmsh splits into 18 distinct topological elements, OCCT keeps 1.
- **[Tsh026](step-examples/12-3a-shells/Tsh026.stp)** `shape(1) vs shape(27)`: coincident/duplicate face in shell.
- **[Tsh007](step-examples/12-3a-shells/Tsh007.stp)** `shape(1) vs shape(25)`, **[Tsh019](step-examples/12-3a-shells/Tsh019.stp)** `shape(1) vs shape(21)`, **[Tsh029](step-examples/12-3a-shells/Tsh029.stp)** `shape(1) vs shape(25)`: shell orientation/free-edge cases.
- **[Twi011](step-examples/12-3b-wires/Twi011.stp)** `shape(1) vs shape(11)`, **[Twi043](step-examples/12-3b-wires/Twi043.stp)** `shape(1) vs shape(7)`: wire/loop pathologies.
- **[Pf020](step-examples/12-10-perf/Pf020.stp)** `shape(1) vs shape(9)`: performance-corpus combinatorial.

### 11 unanimous parser rejects — every parser refuses

§12.1 framing/encoding defects so structurally broken that OCCT, gmsh, and ifcopenshell-strict all reject at read. The corpus contains targeted minimal reproducers for each:

- **[Le001](step-examples/12-1a-encoding/Le001.stp)**: UTF-8 BOM before `ISO-10303-21;`. OCCT: `"unexpected QUID, expecting STEP"`.
- **[Le015](step-examples/12-1a-encoding/Le015.stp)**: unterminated string literal at EOF. OCCT: `Line 23: unexpected end of file`.
- **[Le020](step-examples/12-1a-encoding/Le020.stp)**: string exceeds Ed.3 32 769-octet limit (~50 000 octets emitted).
- **[Le031](step-examples/12-1a-encoding/Le031.stp)**: UTF-16 BOM mistaken for ASCII.
- **[Lh002](step-examples/12-1b-header/Lh002.stp)**: missing `END-ISO-10303-21;`.
- **[Lh026](step-examples/12-1b-header/Lh026.stp)**: Ed.3 ANCHOR/REFERENCE/SIGNATURE under strict Ed.2 reader.
- **[Ls020](step-examples/12-1c-syntax/Ls020.stp)**: `ENDSEC` without trailing semicolon.
- **[Ls023](step-examples/12-1c-syntax/Ls023.stp)**: magic-line variants.

### Heal-by-split caught in the act

**[Tfa011](step-examples/12-3c-faces/Tfa011.stp)**: an `ADVANCED_FACE` emitted with two `FACE_OUTER_BOUND` records (one face requires exactly one). OCCT silently invokes `ShapeFix_Face::FixSplitFace` and produces a different topology than the file describes. The corpus confirms this directly: OCCT loads `shape(1)`, gmsh loads `shape(18)` from the same bytes. The "heal" is not cosmetic; it changes downstream face counts and validation properties.

## Sender attribution distribution

Producers cited in catalog `**Sender**:` fields (134 entries explicitly attribute a producer; many more are sender-agnostic). Counts include exact and case-insensitive matches.

```
FreeCAD       ████████████████████  19
SolidWorks    █████████████         13
CATIA         █████████████         13
Creo          ████████████          12
Inventor      ███████████           11
KiCad         █████████              9
OCCT          ██████                 6
NX            ██████                 6
Pro/E         ██████████             10  (PRO/E + Pro/E)
Fusion 360    █████                  5
Rhino         ████                   4
Onshape       ███                    3
HOOPS         ███                    3
TransMagic    ██                     2
SpaceClaim    ██                     2
Parasolid     ██                     2
Solid Edge    █                      1
```

Tail entries include single-cite producers like SolveSpace, Tekla, ICEM Surf, NX-locale exporters; see `STEP_PROBLEM_CATALOG.md` for full attribution.

## Quick-start: 10 fixtures to inspect first

If you want to "see what's going on", start here.

1. **[Le001 — UTF-8 BOM](step-examples/12-1a-encoding/Le001.stp)**: three bytes break the magic line. The minimal possible "weird STEP" file.
2. **[Le015 — unterminated string](step-examples/12-1a-encoding/Le015.stp)**: file ends mid-literal. Every parser rejects with a line number.
3. **[Twi044 — sub-tolerance internal wire](step-examples/12-3b-wires/Twi044.stp)**: 100 mm² square with a 5e-7 mm² triangular hole. Crashes OCCT.
4. **[Tfa011 — two outer wires on one face](step-examples/12-3c-faces/Tfa011.stp)**: heal-by-split caught directly via OCCT/gmsh shape-count divergence.
5. **[Tsh023 — empty EDGE_LOOP](step-examples/12-3a-shells/Tsh023.stp)**: `EDGE_LOOP('empty',())` cascades into ADVANCED_FACE; signal 11.
6. **[U008 — mixed inch/mm MAPPED_ITEM](step-examples/12-5-units/U008.stp)**: two `GEOMETRIC_REPRESENTATION_CONTEXT`s joined naively; crashes OCCT instead of mis-scaling.
7. **[Pmi049 — shared TRIANGULATED_FACE](step-examples/12-7-pmi/Pmi049.stp)**: same tessellated face referenced by two parents.
8. **[Le020 — 50 KB string literal](step-examples/12-1a-encoding/Le020.stp)**: single PERSON.name string ~50 000 octets, well above the Ed.3 32 769 limit.
9. **[Ad015 — fuzzer crash](step-examples/12-11-adversarial/Ad015.stp)**: adversarial input from the §12.11 corpus that catalog explicitly predicts will crash.
10. **[A021 — heterogeneous CDORSI style_context](step-examples/12-6-assembly/A021.stp)**: Saved View per-component styling that violates WR1.

Each file has a top-of-file comment citing its catalog entry and the defect being demonstrated.

## Coverage map

The 16 sub-section directories cover the full §12.x taxonomy from [STEP_PROBLEM_POTENTIAL_SOURCES.md](STEP_PROBLEM_POTENTIAL_SOURCES.md):

| §12.x | Sub-categories covered | Sub-categories not yet covered |
|---|---|---|
| §12.1 lexical | encoding (`Le*`), header (`Lh*`), syntax (`Ls*`) | — |
| §12.2 geometry | pcurves (`Gp*`), NURBS (`Gn*`), surfaces (`Gs*`) | — |
| §12.3 topology | shells (`Tsh*`), wires (`Twi*`), faces (`Tfa*`) | — |
| §12.4 tolerance | covered as one section (`N*`) | — |
| §12.5 units | covered (`U*`) | — |
| §12.6 assembly | covered (`A*`/`P*`); `.stpx`/`.stpz` archives are P012 stub-only | archive-format variants (P012) |
| §12.7 PMI | covered (`Pmi*`) | — |
| §12.8 mixed | tessellation, validation properties, misc (`M*`) | — |
| §12.9 *(reserved)* | — | gap by design (no §12.9 in taxonomy) |
| §12.10 perf | covered (`Pf*`); fixture-scale representatives only | production-scale (gigabyte) inputs intentionally not bundled |
| §12.11 adversarial | covered (`Ad*`) | — |

Two retained CONCERN entries (P009 missing-entity, P026 process-state contamination) are catalog-only by their nature; see VALIDATION_SUMMARY for context.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a catalog entry + matching fixture. The validator runs in roughly 10 minutes on the full corpus (6-worker subprocess pool); CI is split into `.github/workflows/validate-fast.yml` (runs on every push) and `.github/workflows/validate-full.yml` (gated to `[full-ci]` pushes / daily cron / manual dispatch). New entries should target an as-yet-uncovered defect class; the per-section table above is a useful gap finder.
