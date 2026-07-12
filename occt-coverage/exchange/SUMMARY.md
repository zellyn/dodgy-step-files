# OCCT exchange-layer repair taxonomy — coverage summary

Domain: `BRepBuilderAPI_Sewing` + import healing sequence (`XSAlgo`/`ShapeProcess` operators) + STEP reader repair (`StepToTopoDS`/`TransferBRep`/`STEPControl`) + IGES reader repair (`IGESToBRep`/`IGESControl`) + `BRepCheck` validity detection (detect-only).
OCCT pinned at tag `V7_8_1`, commit `bd2a789f15235755ce4d1a3b07379a2e062fdc2e` (verified — see `PIN.md`).
Sibling domain (`TKShHealing`: ShapeFix/ShapeAnalysis/ShapeUpgrade/ShapeExtend/ShapeConstruct/ShapeCustom internals) is covered separately under `occt-coverage/tkshhealing/` and deliberately NOT duplicated here; where this domain's code delegates into those classes, the call site is cited but internal branches are not enumerated.

## Headline

| | classes | COVERED | PARTIAL | GAP |
|---|---:|---:|---:|---:|
| **All exchange-domain problem classes** | **145** | **69 (47.6%)** | **34 (23.4%)** | **42 (29.0%)** |
| sewing (`sew-*`) | 24 | 10 | 12 | 2 |
| STEP reader (`stp-*`) | 39 | 21 | 13 | 5 |
| heal-sequence operators (`seq-*`) | 20 | 15 | 4 | 1 |
| BRepCheck detect-only (`bc-*`) | 31 | 23 | 5 | 3 |
| IGES reader (`iges-*`) | 31 | 0 | 0 | 31 |
| **STEP-exercisable subset (excl. IGES)** | **114** | **69 (60.5%)** | **34 (29.8%)** | **11 (9.6%)** |

A problem counts COVERED only when every named subvariant has a genuinely-verified fixture. Every fixture credited in `problems.json` was verified by reading its catalog entry and, for the load-bearing verdicts, the actual `.stp` bytes (verification agents documented rejected keyword-matches; see "notable rejections" below).

## Ranked GAP list (most important uncovered first)

1. **The entire IGES reader sub-domain (31 classes, `iges-*`)** — structural: the corpus contains zero `.igs`/`.iges` fixtures (verified corpus-wide), so none of OCCT's IGES-side repairs (B-spline knot/degree/weight sanitation, 3D-vs-2D boundary-representation preference, trimmed-surface outer-contour fallback, transform non-similarity rejection, blank-status filtering, …) can be exercised. This is one corpus-format decision, not 31 individual fixture gaps: either add an IGES fixture section or explicitly scope the corpus STEP-only and drop these from the active denominator.
2. **`stp-degenerate-edge-multiface`** — degenerate edge (cone apex / sphere pole) referenced by several faces, forcing per-face retranslation instead of shared-edge reuse. Default STEP path, common in real analytic geometry. Nearest misses: Twi021, Gs189, Tsh035 (all single-face).
3. **`stp-compcurve-reorder`** — COMPOSITE_CURVE whose segments are listed out of connected order (TranslateCompositeCurve reorder repair). All existing disorder fixtures scramble EDGE_LOOP edge lists, a different translation path.
4. **`sew-degenerate-free-wire-collapse`** — post-merge leftover free boundary wire of sub-tolerance extent that sewing collapses. Runs in every reader sew pass. Closest candidate (Sw003) byte-verified NOT to demonstrate it (zero-area but full-length wire).
5. **`sew-merged-edge-continuity-encoding`** — continuity/regularity classification of merged edges (EncodeRegularity family). Zero catalog entries touch regularity vocabulary in a sewing/merge context (Bo025's mis-tagged G1 edge serves the SetTolerance-operator regularity variant, not the post-merge encoding).
6. **`stp-tess-dangling-brep-link`** (3 subvariants: face/shell/solid) — AP242 tessellated entity whose declared exact-BRep link is unresolvable; reader creates a fresh host instead of failing. All tessellated fixtures have `$` or valid links.
7. **`stp-tess-malformed-normals`** — tessellated normals table with rows that aren't 3-component vectors; silently dropped. (Tessellated defect fixtures exist — M005 covers repeated-index degenerate triangles — but none malforms the normals table.)
8. **`stp-polyloop-dup-point`** — POLY_LOOP with the same CARTESIAN_POINT repeated in succession (degenerate-segment skip in TranslatePolyLoop). The corpus's only POLY_LOOP fixture (M055) has distinct points.
9. **`seq-drop-small-solids`** (3 subvariants) — negligible-volume / sliver solid removal (`ShapeFix_FixSmallSolid` operator). Only mesh-domain analogues exist (Me240–248, different oracle). Opt-in operator, so lower urgency than the default-path gaps above.
10. **`bc-multiple-3d-curve`, `bc-invalid-point-on-surface`, `bc-invalid-polygon-on-triangulation`** — detect-only BRepCheck statuses judged STRUCTURALLY-UNREACHABLE from STEP input (they need internal TopoDS states STEP translation never constructs: multiple Curve3D reps on one edge, BRep_PointOnSurface vertex representations, polygon-on-triangulation records). Kept in the denominator as detect-only classes a kernel author must know, but not actionable as STEP fixtures.

High-value PARTIAL clusters (not gaps, but where the next fixtures buy the most):
- **Sewing is the weakest verified area (12/24 PARTIAL)**: recurring missing subvariants are the short-candidate/coverage rejection filters, V-periodic + isoline-fallback seam closure, closed-edge three-point vertex merge, Cutting's split subvariants, and the MaxTolerance cap/retry branches. Systemic finding: the N146–N153 tolerance-wave fixtures are faceless `GEOMETRIC_CURVE_SET` wireframes whose decisive parameters live only in comments — they cannot exercise the face-sewing mechanisms their titles cite (the known orphaned-defect-carrier failure mode).
- **`stp-*` PARTIALs** are mostly one-missing-variant cases (e.g. `stp-vertex-tol-gap` covered for ordinary gaps via Bo030 while its N007 bump-factor fixture is GEOMETRIC_CURVE_SET-hosted; `stp-ideas-shell-closing` has only the header auto-detect trigger (Lh031), no closing-shell topology; M045 — the sole NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION fixture — duplicates rather than shares EDGE_CURVEs across shells, weakening `stp-nm-shared-entity-reuse`).
- **`bc-invalid-same-range-flag` / `bc-invalid-degenerated-flag`**: their direct-target fixtures (Twi082/Twi083) are GEOMETRIC_CURVE_SET-hosted so OCCT translates them to empty shapes — flag defects need face-wired hosts to be observable.

## Where the denominator judgment was hard

1. **BRepCheck dead enum values.** 5 of the 39 `BRepCheck_Status` members (`InvalidPointOnCurve`, `InvalidPointOnCurveOnSurface`, `Invalid3DCurve`, `InvalidWire`, `BadOrientation`) have **no live assignment site** in V7_8_1 (verified by whole-`src/` grep; the `BRepCheck_Vertex::Blind` body that assigned the first two is commented out upstream). They are excluded from the denominator (see `excluded.json`) — an enum value nothing can set is not a problem a kernel must exercise. `NoError` is trivially excluded. The denominator keeps the 31 live statuses.
2. **`bc-check-fail` meta-class.** `CheckFail` is "a checker sub-computation threw"; any other class could present as it. Kept as one class because it is a directly-coded, fixture-targetable behavior (geometry degenerate enough to make evaluation throw); verdict PARTIAL since the corpus's observed throws happen at read/heal time, not inside a check pass.
3. **Heal-sequence operators are one-class-per-operator, and only `FixShape` is default-wired.** The shipped `STEP.exec.op` sequence runs FixShape only; the other operators are opt-in via resource file. Each operator is kept as its own problem class (each targets a distinct input-defect family), but the default/opt-in split is flagged — GAPs in opt-in operators matter less than default-path GAPs. Operator classes capture operator-level *intent*; internal repair mechanics belong to the sibling TKShHealing taxonomy (no double counting).
4. **`seq-split-angle` vs `seq-split-closed-faces` share an input pattern.** A full-period rotational face demonstrates both; kept separate because the operators exist separately (max-angle vs closedness constraints), with the shared-fixture note recorded.
5. **IGES classes in a STEP corpus.** Kept in the denominator (the domain spec includes IGES reader repair) and marked GAP rather than silently dropped — the headline table reports both with-IGES and STEP-exercisable numbers so neither reading misleads.
6. **Multi-level status collapse.** `SubshapeNotInShape` (asserted independently at 6 topological levels) and `BadOrientationOfSubshape` (4 levels) were collapsed to one class each per the dedup rule; `NotClosed` keeps wire-level and shell-level as *subvariants* of one class since the fixture inputs differ materially.
7. **Sewing branch-folding.** The ~1500-line V3 per-branch material for Sewing was collapsed to 24 classes by folding mechanism-supporting branches (map lookups, loop bookkeeping, candidate-array plumbing) into their parent repair decision; 10 excluded-pattern families with examples are in `excluded.json`. Branches whose falsifiable_claim showed a genuine input-defect signature were kept even when their V3 axis tag said `healer-state`/`control_flow_ambiguity` (judged by content, not label).
8. **Verification bar.** "Fixture mentions the same OCCT method" was NOT accepted as coverage. Notable byte-verified rejections: Sw002 ("sliver face" is actually a unit square), Sw004 ("null surface" references a real PLANE), N137 (trivially valid single face), Tsh079 (no actual gap), Tsh141 ("coincident" edges 2.0 apart), Tfa056 ("redundant wire" is actually nested imbrication), Tsh001 (OPEN_SHELL typing ≠ open geometry). Best unexpected find: M045 (an XCAF-attributes fixture) is geometrically the strongest non-manifold sewing input in the corpus and carries four sewing classes that their nominally-dedicated fixtures fail to cover. One sweep verdict was overturned by re-reading bytes: M005's `(3,3,4)` repeated-index triangle covers `stp-tess-degenerate-triangles` (reachable via TESSELLATED_SOLID → shape representation).

## Files

- `problems.json` — 145 classes; fields `problem_id, domain, description, occt_evidence[], subvariants[], fixture_ids[], coverage_verdict, notes` (+ `detect_only: true` on the 31 `bc-*`); merges cleanly with the sibling domain's file.
- `excluded.json` — 52 excluded branch/enum patterns with one-line reasons (5 dead BRepCheck enums, 10 sewing plumbing families, 13 STEP-reader, 24 sequence/IGES).
- `PIN.md` — source pin + verification statement.

All 3197 catalog entries were searchable during verification; every `fixture_ids` entry was validated to exist in `STEP_PROBLEM_CATALOG.json`. Nothing in the catalog or fixtures was modified.
