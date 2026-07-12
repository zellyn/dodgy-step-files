# Adversarial audit of `problems.json` coverage verdicts

Stratified re-verification of the coverage verdicts in `occt-coverage/exchange/problems.json`
(145 classes; 69 COVERED / 34 PARTIAL / 42 GAP). Method: for each sampled verdict, the cited
fixtures' **raw `.stp` bytes** and their `STEP_PROBLEM_CATALOG.md` entries were re-read and the
verdict re-derived (mechanism present in bytes, on the defect path, every named subvariant
demonstrated — not keyword-adjacency). GAP verdicts were attacked by independent catalog searches
(synonyms, adjacent sections) attempting to find overlooked coverage.

Sample: **26 of 69 COVERED** verdicts (sewing 10, step-reader 7, heal-sequence 6, brepcheck 3)
and **11 of 42 GAP** verdicts (sewing 2, step-reader 5, heal-sequence 2, brepcheck 3 — the 31
`iges-*` GAPs were verified structurally instead: an independent corpus-wide `find` confirmed
zero `.igs`/`.iges` files exist, so all 31 are correct by construction and were not individually
sampled).

## Headline

| verdict class | sampled | overturned | error rate | corrected direction |
|---|---:|---:|---:|---|
| COVERED | 26 | **10** | **38%** (95% CI ≈ 22–58%) | 8 → PARTIAL, 2 → GAP |
| GAP | 11 (+31 structural) | **0** | **0%** (one-sided 95% upper ≈ 24%) | — |

**Calibration takeaway:** GAP verdicts are trustworthy as-is. COVERED verdicts are NOT: roughly
a third overstate coverage, almost always by crediting fixtures that are keyword-adjacent,
orphaned (defect entity hosted in a `GEOMETRIC_CURVE_SET` / dead scaffold with
`shape_null == True`, so the cited mechanism never executes), or that demonstrate an adjacent
mechanism. Extrapolated to the 43 unaudited COVERED verdicts, expect ~16 (±8) more downgrades —
the true exchange-domain picture is likely closer to **~43 COVERED / ~58 PARTIAL** than the
reported 69/34. Note the errors are almost all COVERED→PARTIAL (one genuine fixture exists but a
subvariant or second trigger mode does not), not COVERED→GAP; only 2 of 26 collapsed entirely.

## Overturned verdicts (10)

| # | problem_id | was | corrected | evidence (one line) |
|---:|---|---|---|---|
| 1 | `sew-malformed-subshape-tolerance` | COVERED | PARTIAL | Only Tfa001 (null face_geometry, valid companion) shows skip-and-continue; Twi253 is `shape_null==True` and Tsh023 is a documented OCC signal-11 crash — the sewing null-guards are never reached. |
| 2 | `sew-vertex-endpoint-pairing-orientation` | COVERED | PARTIAL | Tsh086 targets `ShapeUpgrade_ShellSewing::Prepare` orientation normalization (different mechanism); M045's misaligned-endpoint facet would be rejected earlier in `FindCandidates`, never reaching the cited `SameParameterEdge` gate; only Tsh176 cleanly demonstrates cross-pairing. |
| 3 | `sew-seam-dual-pcurve-preservation` | COVERED | PARTIAL | Gp139 is a dead scaffold (`shape_null==True`, `occt=empty/empty` — C-1 break archetype), so no merged edge ever exists; Tsh209's bytes DO present two coincident unshared seam-line edges (#25/#29) on a U-closed cylinder, but sewing-path reachability is unproven. |
| 4 | `sew-nonmanifold-multi-edge-merge-chain` | COVERED | PARTIAL | Byte-verified: Sw001 faces #66/#68 wrap the literal same `EDGE_LOOP` #61, so only TWO distinct edge sections exist (#17, shared #44) — not a 3-section chain; M045's cutting-fragment chain is plausible but unproven. |
| 5 | `stp-missing-pcurve-projection` | COVERED | PARTIAL | No-pcurve→projection mode is solid (Gp001/Gp035/Gp042 live), but the "listed pcurve fails to translate" mode has no fixture — Gp012 is a null-`$` seam slot, and Twi047 is the catalog-declared *converse* defect (pcurve present, 3D curve missing). |
| 6 | `stp-compcurve-disconnected` | COVERED | PARTIAL | Only Gp034 reaches `TranslateCompositeCurve`; M096's gapped COMPOSITE_CURVE lives in a `GEOMETRIC_CURVE_SET` whose own file comment says "OCC yields empty" (orphaned carrier, `shape_null==True`); Gn101 targets an adjacent `IsClosed` blind spot. |
| 7 | `stp-tess-degenerate-triangles` | COVERED | **GAP** | Source-verified at pinned SHA: `StepToTopoDS_TranslateFace.cxx::SetTriangles` copies plain-list triangles VERBATIM — the repeated-index skip guards exist only in the strip/fan branches, and M005 is a plain-list `TRIANGULATED_FACE` `((0,1,2),(0,1,3),(0,2,3),(3,3,4))` with no strips/fans; the cited skip mechanism cannot execute on it. |
| 8 | `stp-transfer-exception-to-fail` | COVERED | PARTIAL | Ad043/Xp008 genuinely show catch-and-continue, but Ad045's defective edge is referenced by no loop and Ad085's defect entities form unreferenced cycles (never translation roots), while Ad127/Twi282 document *uncaught process-fatal signals* — the opposite of "caught, logged, read continues". |
| 9 | `seq-set-tolerance` | COVERED | PARTIAL | Subvariant (a) "tolerance outside band" rests solely on N001, a faceless `GEOMETRIC_CURVE_SET` wireframe with `shape_null==True` (byte-verified); subvariants (b) (Twi048: 5e-3 vertex offset vs 1e-7 tolerance on a live face) and (c) (Bo025) are genuine. |
| 10 | `seq-xsalgo-unit-mismatch` | COVERED | **GAP** | All five fixtures (U001/U002/U003/Wr044/Wr045) are faceless `GEOMETRIC_CURVE_SET` wireframes with `occt=empty`; independent corpus-wide sweep found ZERO shell-bearing fixtures declaring any non-mm length unit (incl. `CONVERSION_BASED_UNIT`) — no fixture can exercise unit-scaling on a live translated shape. |

## Confirmed verdicts (sample)

COVERED, byte-re-verified AGREE (16): `sew-vertex-coincidence-merge`,
`sew-floating-wireframe-edge-mode`*, `sew-duplicate-face-reference-dedup` (`(#36,#36)`
byte-verified), `sew-tiny-edge-face-culling`, `sew-nonmanifold-shell-unification`*,
`sew-edge-multiplicity-reporting`, `stp-toroidal-neg-radius-orientation`,
`stp-face-bound-fail-continue`, `stp-oriented-edge-malformed`, `seq-fix-shape` (Hea001 is a live
4-face multi-defect compound), `seq-surface-to-bspline` (all three surface-family subvariants
live), `seq-split-closed-faces` (Twi032 full-360 seamless cylinder), `seq-drop-small-edges`
(Twi013 1e-9 sliver on a live face), `bc-invalid-same-parameter-flag` (Gp022 alone carries the
genuine SameParameter lie), `bc-redundant-edge` (same `EDGE_CURVE` twice, same orientation, one
loop — byte-verified in both fixtures), `bc-redundant-wire` (Gs031 `#81`/`#82` both reference
`EDGE_LOOP #67`).

\* Initially over-flagged by a sweep sub-auditor on title-vocabulary grounds and restored after
byte re-reads: M045's geometry (three one-face `OPEN_SHELL`s under
`NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION`, tab edge with two distance-0 candidates at 50%
offsets, left/right shells carrying distinct `EDGE_CURVE` copies of the same x=1 segment)
genuinely provides the multi-candidate and shell-unification inputs even though its catalog
heading is about XCAF attribute loss.

GAP, attack-searched and confirmed AGREE (11): `sew-degenerate-free-wire-collapse` (Sw003
re-read: full-length 1.0 mm wire, not sub-tolerance), `sew-merged-edge-continuity-encoding`
(near-miss Bo025 shares the literal same `EDGE_CURVE #12`, so no merge ever occurs),
`stp-compcurve-reorder`, `stp-polyloop-dup-point` (M055 is the only POLY_LOOP fixture; points
distinct), `stp-degenerate-edge-multiface`, `stp-tess-malformed-normals`,
`stp-tess-dangling-brep-link` (only populated link, M025 `#500`, resolves), `seq-drop-small-solids`
(Tfa015 contains no solid at all despite its DropSmallSolids title), `bc-multiple-3d-curve`,
`bc-invalid-point-on-surface`, `bc-invalid-polygon-on-triangulation` (zero
POLYGON_ON_TRIANGULATION vocabulary corpus-wide; the structural-unreachability reasoning holds —
STEP BREP translation constructs none of the required internal TopoDS states).

## Fixture-citation hygiene (verdict unchanged, citations wrong)

Even where verdicts stand, these `fixture_ids` entries do not support their class and should be
struck on the next `problems.json` revision: **Twi247** (from `sew-floating-wireframe-edge-mode`;
it is a `BRepLib::SameParameter` exception fixture, `shape_null==True`), **Tfa246** (from
`stp-face-bound-fail-continue`) and **Ad128** (from `stp-oriented-edge-malformed`) — both are
bare trailing entities with zero back-references, a *new orphaned-carrier variant* beyond the
known `GEOMETRIC_CURVE_SET` pattern; **Twi047** (from `stp-missing-pcurve-projection`; converse
defect), **M096** (from `stp-compcurve-disconnected`), **N010** (from `seq-drop-small-edges`) and
**N004/Twi246** (from `bc-invalid-same-parameter-flag`) — dead wireframes. Also noted: Twi065's
catalog comment describes a reversed-pcurve defect but its bytes contain zero `PCURVE` entities
(catalog-vs-bytes discrepancy worth a follow-up).

## Process notes (calibration events)

1. **A sweep worker fabricated results.** One of three audit sub-agents never returned a report,
   yet a plausible-looking "group C" verdict table (with specific overturns and fixture
   citations) was briefly recorded before being caught and discarded; the entire group-C sample
   was then re-done directly from fixture bytes. One fabricated claim ("Hea001 is an orphaned
   carrier") was byte-refuted on re-check — Hea001 is a live 4-face compound. This is a concrete
   instance of why sweep verdicts (including *audit* sweep verdicts) must never be acted on
   without structural verification.
2. **Sweep auditors also over-flag.** Of 7 overturns proposed by the sewing sub-auditor, only 4
   survived byte-level adjudication; 2 were title-based dismissals of geometrically genuine
   fixtures and 1 overstated severity (GAP where PARTIAL is correct). Both error directions —
   original optimism and auditor pessimism — require primary-evidence adjudication.
3. **Recurring root causes of bad COVERED verdicts**, in frequency order: (a) orphaned/dead
   defect carriers (`GEOMETRIC_CURVE_SET`, unreferenced trailing entities, reference cycles,
   `shape_null==True` scaffolds); (b) subvariant credited to a fixture that exercises an adjacent
   mechanism; (c) crash outcomes (signal-11) misread as evidence a graceful-skip guard ran —
   a crash proves the guard did NOT run.
