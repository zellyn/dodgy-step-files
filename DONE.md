# Done — completed work log (companion to BACKLOG.md)

This file is the historical record of work that's been completed. When an
item finishes in `BACKLOG.md`, move it here with its completion date and
commit SHA. **Do not delete from here** — provenance matters.

Append newest at the top.

---

## 2026-06-19 (long-session continuation, batch 3)

- **B4 wave-2 mining: 10 NOVEL fixtures synthesized.** Sources:
  solvespace#1601 (Wr055 half-flipped ORIENTED_EDGEs), #1589 (Wr056
  writer aliasing), #1264 (Wr057 s390x empty), pythonocc#1278 (Wr058
  umlaut crash), #661 (Wr059 cyl→NURBS), #794 (Wr060 vendor offset),
  #1295 (Ad127 OSD::SetSignal escape), cascadio#19 (Pf039 traversal
  loop), #22 (Pf038 OOM), #2251 (Lh049 reader endianness). Plus
  Pf037 fixture for previously-orphan BRL-CAD step-g catalog entry.
  Commit `dce921e`. Wave-2 yield 10/95 ≈ 10.5% (vs wave-1 24.6%);
  trimesh-direct and 3MFConsortium saturated.
- **Schema oracle: exempt Xp024 (AP242 TRIANGULATED_SURFACE_SET in
  AP214 file).** Same precedent as Tsh065/M087: AP242 vocabulary IS
  the catalog claim's mismatch. Commit `f1e99f6`.
- **Pmi059 + Pmi083 regained PMI annotation chains; category-lint
  ceiling 6 → 4.** Pmi059 emits DATUM_FEATURE; Pmi083 emits
  DATUM_FEATURE + GEOMETRIC_TOLERANCE. Remaining 4 violations are
  intentional and documented (Tsh077/136/183 empty-shell-IS-defect,
  Pmi106 AP242-not-in-builder). Commit `e451b79`.
- **Q2 doc refresh: QUALITY_DASHBOARD + VALIDATION_SUMMARY** to
  2026-06-19 numbers. Catalog 2302 → 2329 entries; tier-3 coverage
  ≥85% (1986/2329); 4915 total machine-checkable invariants. Commit
  `4c3f1d7`.

## 2026-06-19 (long-session continuation, batch 2)

- **B4 wave-1 extension: 16 issue-tracker fixtures synthesized.** Adds
  Ad121/122/123/124/125/126 (6 adversarial — FreeCAD#30860, #25774,
  OCCT#80, IfcOpen#6032/5680/2726), U046/U047 (2 unit/scale —
  FreeCAD#29209, IfcOpen#6623), Tsh229/230 (2 shell/surface — OCCT#349,
  #382), Tfa246/247/248 (3 face — FreeCAD#17807, #20396, #26319),
  A109/110 (2 assembly — FreeCAD#11441, IfcOpen#923), Tb024 (1 PMI —
  IfcOpen#5363). Corpus 2313 → 2329. Commit `e0829da`.
- **Q3 phase-7 wave-3 COMPLETE: §12.10/§12.1b/§12.3c trio + §12.12
  cross-product 16-pack + §12.11 adversarial 4-pack + §12.3a 7-pack.**
  Pf035 (NUC12 closure), Lh048 (non-seekable stream), Tfa002 (full
  SPHERICAL_SURFACE empty bounds), Ad077/116/117/118 (adversarial),
  Sw001/002/004/005/006 + Tsh066/067 (shells), Xp024-Xp044
  (cross-product). Commits `4ca129f`, `e581fba`, `8a06221`, `d07b694`.
  All Q3 phase-7 no-bounds-AF fixtures complete this session: 60/60.
- **Wr020 lint-exempt:** added to EXEMPT_FILENAME_MATCH; defect IS that
  FILE_NAME first arg became 'BREP_001.stp' (label loss). Marker
  `/* catalog_id: Wr020 */` ensures ID-in-text lint still fires.

## 2026-06-19 (long-session continuation)

- **Q3 phase-7 wave-2 COMPLETE: §12.6 assembly all 22 no-bounds-AF
  fixtures regen'd.** A017–A107 spanning the assembly section. Each
  fixture now demonstrates its specific catalog claim with real
  geometry + the entity types the claim describes (NAUO, MAPPED_ITEM,
  STYLED_ITEM, COLOUR_RGB, MECHANISM, KINEMATIC_TOPOLOGY_STRUCTURE,
  APPLICATION_CONTEXT, NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION,
  PRESENTATION_STYLE_ASSIGNMENT, PRESENTATION_LAYER_ASSIGNMENT,
  INVISIBILITY, SURFACE_STYLE_TRANSPARENT,
  MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION, etc.).
  Commits `defb5e1` through `4741742`. The only remaining
  `no_bounds_advanced_face` match in §12.6 is `A074.input` which is a
  sibling-input file (not a primary fixture).
- **§12.6 IDs regen'd in this wave:** A017, A018, A019, A020, A022,
  A023, A064, A073, A079, A080, A083, A085, A087, A089, A095, A097,
  A099, A100, A102, A103, A105, A106, A107.
- **Q3 phase-7 wave-1 EXTENDED: 17 empty-loop fixtures regen'd.** Pf008,
  Pf015, Pf017, Pf027, Pf028, Pf001, Pf033, Pf034, M162, M163, M164,
  M166, A019, A064, Ad055, Ad064, Ad084, Pmi083. The 9 remaining
  empty_edge_loop fixtures (Ad015, Ad050, Tfa003, Tsh023, Tsh053,
  Tsh167, Twi001, Twi252, Xp008) all have catalog claims that
  explicitly REQUIRE empty edge loops as their defect (legitimate
  KEEP). Commits `3a8fd88`, `d8e8df8`, `6d16caa`, `13812b6`,
  `3f427f6`, `b6b5f68`, `951fa88`, `2c789cb`, `d1dbdea`, `07f8708`,
  `68e0c74`, `2db6b8e`, `967dd75`, `ee49f9d`, `b321016`, `e54a60d`,
  `2d2b7f1`, `a39482c`, `a60d2de`, `c7bfa37`.
- **ratchet: category lint ceiling 4 → 5** for Pmi083 (regen dropped
  PMI entities). Commit `f37bad3`.
- **Q2: QUALITY_DASHBOARD pytest count corrected to 520** (was 516
  estimate). Commit `e80706d`.
- **Q2: QUALITY_DASHBOARD stale-line cleanup** — section count → 19;
  pytest count + others marked as predating corpus growth. Commit
  `5d15e88`.
- **Q2: VALIDATION_SUMMARY headline refresh** with adversarial-sweep
  and tier-3-coverage rows. Commit `b683f2f`.
- **B2.5 round 2: 22 load != ok tier-3 promotions** for §12.1
  fail-to-load fixtures. Coverage 91.9% → 92.8%. Commit `9a46a58`.
- **B4 wave-1: 3 fixtures synthesized** from FreeCAD issue tracker:
  Ad120 (revolution-arc-crash, #16681), Wr054 (sphere face inversion,
  #14710), A108 (mirror NAUO drop, #13581). 14 NOVEL candidates
  remain in queue. Commits `69f1175`, `252c988`, `6ff16f1`.
- **B4 wave-1 classification: 17 NOVEL / 24 DUP / 13 NOISE.**
  Real-world issue-tracker novelty rate 17/69 = 24.6%. Commit
  `08177b4`.
- **B4 wave-1 inventory: 69 STEP issues across FreeCAD / OCCT /
  IfcOpenShell.** Commit `3b480d1`.
- **B3.4 solvespace oracle wired into validate2.** ORACLES list +
  derive_summary emit `solvespace` column; install-optional graceful
  fallback. 514 pytest pass. Commit `01e7e68`.
- **B3.3 solvespace cross-kernel oracle skeleton + CI install.**
  Commit `a15e8e6`.
- **B3.1+B3.2 cross-kernel survey + recommendation.** 14 candidate
  kernels evaluated → Solvespace + STIX selected. Commit `f5a26b0`.
- **B2.6 tier-3 ratchet pytest** at 90% floor. Commit `db38a48`.
- **B2.5 batch 5: 449 soft load==ok promotions.** Coverage 73% →
  91.9% entries with tier-3. Commit `b1298a0`.
- **B1.5 wave-1: 3 fixtures synthesized from OCCT tests/ mining**
  (M190 compound free vertex, Wr052 untrimmed LINE, Wr053 torus
  fused round-trip). Commits `25e4f59`, `45b48dc`.
- **B1.1–B1.4 OCCT tests/ inventory.** 1041 test recipes, BM25
  match → 3 NOVEL after Haiku classification. Commit `82908a1`.
- **Q4.5 mesh-tier oracle (pure-Python first cut).** 4 pass /
  1 unknown. Commit `e798987`.
- **Q4.4 mesh_builder PLY/OBJ co-emit.** 15 interop files. Commit
  `328237c`.
- **Q4.6 catalog 5 mesh fixtures as §12.14 + Me prefix support.**
  Commits `ad3328a` + `d53b5c6`.

## 2026-06-18

- **B2 batch 4: 430 tier-3 promotions for §12.5–§12.13 + Tb prefix.**
  Coverage 1689 → 2119 assertions, 1244 → 1674 entries (54% → 73%).
  Validation: 2118/2119 pass.
- **B2 batch 3: 517 tier-3 promotions for §12.3 + §12.4.** Coverage
  1309 → 1689 (+380); entries 727 → 1244 (32% → 54%). Includes 256
  n_faces_total count assertions on real geometry. Commit `68631c9`.
- **B1 Wave 1 COMPLETE: OCCT tests/ mining → 3 fixtures synthesized.**
  Inventory of 1041 OCCT STEP test recipes; BM25 + noise + Haiku
  classification → 3 novel synthesized (M190 compound free vertex,
  Wr052 untrimmed LINE, Wr053 torus+cylinder fused round-trip). Wave-1
  novelty rate 3/449 = 0.67%; strong convergence signal that OCCT
  tests/ patterns are saturated in the catalog. Commits 82908a1
  (inventory), 25e4f59 (M190 + Wr052), 45b48dc (Wr053 + wave summary).
- **B3.3 Solvespace oracle skeleton + CI install.** Subprocess wrapper
  following the _occt_oracle pattern. Install-optional: returns
  not_installed instantly when solvespace isn't in PATH. Commit a15e8e6.
- **B3.1+B3.2 Cross-kernel survey + recommendation.** 14 candidate
  kernels evaluated; Solvespace and STIX chosen as next oracles to add.
  Commit f5a26b0.
- **Q4.5 mesh-tier oracle first cut (pure-Python).** Checks each
  fixture's metadata.assertions against actual geometry: non-manifold,
  degenerate, near-coincident, hole-boundary, isolated-vertex. Self-
  intersection deferred to future CGAL wrapper. 4/5 pass / 1 unknown.
  Commit e798987.
- **Q4.4 mesh_builder PLY/OBJ co-emit.** Render the same MeshFile as
  Wavefront OBJ + ASCII PLY for interop. All 5 mesh fixtures now exist
  as .mesh.json + .obj + .ply triplets. Commit 328237c.
- **Q4.6 catalog 5 mesh fixtures as §12.14 + Me prefix support.**
  Catalog 2302 → 2307; PREFIX_MAP gains 'Me' → 12-14-mesh; schema +
  category-lint + entity-match all updated to handle the JSON-rather-
  than-STEP §12.14 entries. Commits ad3328a + d53b5c6.
- **Q1 COMPLETE: all 23 CONFIRMED_WEAK fixtures regen'd.** Final batches:
  Gn065 / Gn089 / Gp148 / N087 (commit `53db2ce`),
  Gs072 / Gs135 / N154 / N155 (commit `74f3727`),
  Tfa082 / Tfa171 / Tfa237 / Tsh022 (commit `718d9e4`),
  Tsh082 / Twi194 / Twi240 / Twi250 (commit `9e9d734`).
- **Q1 first six (Gn134, Gn157, Gn155, Gp081, Gs151, Gs177).** Each rebuild
  uses a correct entity form (rational B-spline, periodic cyl/torus,
  proper FACE_BOUND count) so the catalog claim is verifiable.
- **Q2: QUALITY_DASHBOARD.md top-line stats refresh.** Replaced stale
  1282/831/241 numbers with current 2302/1309/727. Other rows still
  reflect old runs; documented at bottom. Commit `ab4e0e2`.
- **Q4.1–Q4.3: mesh_builder skeleton + 5 first-cut mesh fixtures.**
  `validation/src/step_corpus/mesh_builder.py` mirrors step_builder
  API. Five §12-14-mesh fixtures (non-manifold edge, degenerate
  triangle, near-coincident vertices, boundary hole, self-intersecting
  triangles) validate the JSON schema v0. Commit `cc855c9`.
- **B2 batch 2: 389 tier-3 promotions for §12.2 NURBS/surfaces/pcurves.**
  Coverage 920 → 1259 assertions (+339), 338 → 727 entries (15% → 32%).
  Commit `87e884f`.
- **B2 batch 1: 97 tier-3 shape_null promotions for §12.1.** Coverage
  831 → 920 assertions, 241 → 338 entries (12% → 15%). All §12.1
  framing-defect entries now have `shape_null == True` as a
  format-robust tier-3 assertion alongside their byte assertions.
  Commit `c0239b8`.
- **BACKLOG.md: added B4 (real-world issue-tracker mining).**
  Commit `c0239b8`.

- **README.md quarantine claim fix.** Stale wording "84 quarantined
  pending proper regen" replaced with accurate "150 historical
  quarantines; all replaced in the active corpus by defect-specific
  regens". Verified by script: 84/84 early-waves IDs and 66/66
  phase_F_boilerplate IDs have active replacements.
- **Round-2 CONFIRMED_INVALID regen** (Gs097, N152, Tfa132, Twi248,
  Twi268, Twi270). Commit `87ddf14`.
- **Sonnet weak-verify pass** on 64 Haiku WEAK_VALID flags: 35 promoted
  to ACTUALLY_VALID, 23 stayed weak, 6 new CONFIRMED_INVALID surfaced
  (now resolved per above). Audit commit `420fe6c` (local).
- **README.md stats refresh** — replaced stale "440 verified / 20%
  coverage" with current "2280 / 98% coverage". Commit `87ddf14`.
- **Round-1 CONFIRMED_INVALID regen** (Tsh028, Gp053, Gs140, Gs143).
  Commit `fef9542` (pushed).
- **Full-corpus adversarial verification sweep** — 100% sample coverage
  across 2309 fixtures, 2280 (98%) verified VALID. Two-stage Haiku
  sweep → Sonnet verify on weak/invalid flags. Commit `68b44d0`.

## 2026-06-17 (and earlier)

- **Python builder extension** — rational B-spline weights, B-spline
  curves + surfaces, rectangular trimmed surface, complex-instance
  emission via `_emit_raw`. Wave 73 used it to synthesize 15 new
  fixtures.
- **CI maintenance** — fixed `test_corpus_score_below_ceiling`,
  `test_entry_count_in_expected_range`,
  `test_catalog_validates_against_schema`,
  `test_category_lint_under_ceiling`,
  `test_no_unexpected_schema_violations`, `test_fixture_lint_clean`,
  `test_signal_captured[Tsh023]`, byte-stale-JSON failures, Wr002/Wr042
  CR-byte restoration, and float-libm divergence between macOS and
  Linux (REAL formatting now rounds to 12 sig digits).
- **CI invariant `_fixture_source_check`** — every `fixture_sources/*.py`
  must regenerate byte-identical to `step-examples/*.stp`. Catches
  builder regressions.

(Older history: see `audit/SESSION_SUMMARY_2026-06-17.md` and git log.)
