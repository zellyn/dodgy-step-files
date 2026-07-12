# TKShHealing — problems OCCT can repair vs corpus coverage

Domain: OCCT Shape Healing toolkit — ShapeFix, ShapeAnalysis, ShapeUpgrade, ShapeExtend, ShapeConstruct, ShapeCustom, ShapeProcess/ShapeProcessAPI.
Source pin: OCCT `V7_8_1` = `bd2a789f15235755ce4d1a3b07379a2e062fdc2e` (see `PIN.md`). Raw material: `OCCT_HEAL_COVERAGE_V3.md` (the TKShHealing slice, ~1,300 of 2,058 branches), every kept evidence line re-verified against the pinned source.

## Headline numbers

| | Count | % |
|---|---:|---:|
| **Distinct problem classes (denominator)** | **60** | |
| COVERED (all needed variants fixtured, verified) | 35 | **58.3%** |
| PARTIAL (some variants missing) | 20 | 33.3% |
| GAP (no genuine fixture) | 5 | 8.3% |
| COVERED-or-PARTIAL | 55 | 91.7% |
| Excluded branches (with reasons, `excluded.json`) | 270 | |
| Distinct catalog fixtures verified as exercising a class | 396 | |

Method: six worker passes (groups A–F in `partial/`) distilled the V3 branches per class-family, verified line citations against the pinned source, and verified fixture candidates by reading catalog records and `.stp` bytes (historical sweeps over-flag; every COVERED verdict rests on at least one byte- or record-level verification). A final cross-group merge pass collapsed 23 duplicate records (detection-vs-fix pairs, wire-level vs face-level vs shape-level drivers of the same defect) and reclassified 9 candidate classes into the excluded list.

## Ranked GAP list (biggest missing repairs first)

1. **`tkshh-splitting-vertex-face`** (`ShapeAnalysis_CheckSmallFace::CheckSplittingVertices` + `ShapeFix_FixSmallFace::FixSplitFace`) — a vertex not belonging to an edge projects onto that edge's interior within tolerance. **The most deceptive gap in the corpus**: ~17 fixtures are *named* after this mechanism, but the four read in depth (Tfa010, Tfa079, Tfa104, Tfa129) all encode the vertex as a genuine shared topological endpoint — which the OCCT check explicitly skips (`V.IsSame(V1)||V.IsSame(V2)`). None demonstrate the actual trigger (an independent, unattached nearby vertex).
2. **`tkshh-solid-unstructured-multishell`** (`ShapeFix_Solid::Perform` → `CreateSolids` shell classification/nesting) — multiple shells with no outer/void structure that must be classified into solids-with-voids. Nearby BREP_WITH_VOIDS fixtures exercise the STEP-schema translator path, not this healer.
3. **`tkshh-sliver-solid`** (`ShapeFix_FixSmallSolid`) — near-zero-volume solid in a compound. The only candidate (Tfa015) is a small *face* on an OPEN_SHELL, which cannot reach `IsValidInput` (requires a `TopoDS_SOLID`).
4. **`tkshh-wire-duplicate-coincident-vertex-instances`** (`ShapeFix_EdgeConnect`) — connected edges referencing distinct but coincident VERTEX instances repaired by global vertex unification (as opposed to the covered wire-local `FixConnected`).
5. **`tkshh-indirect-elementary-surface-axes`** (`ShapeCustom_DirectModification`) — elementary surface on a left-handed axis system (indirect placement) converted to a direct frame. Rare in modern exporters, but a one-fixture win.

## Top PARTIAL holes (missing variants, ranked by how central the repair is)

1. `tkshh-wire-missing-or-bad-degenerated-edge` — missing: degenerated-**torus** apex synthesis (`aPhi=acos(-R/r)`) and **B-spline-surface-pinched-to-a-point** pole synthesis (`ShapeFix_Face`), both in the default face pipeline.
2. `tkshh-face-closed-surface-unsplit-at-seam` — missing: doubly-closed (torus) recursive split, V-closed-only fallback, thin near-full-period trimmed face.
3. `tkshh-wire-nonadjacent-edges-intersect` / `tkshh-face-intersecting-wires` — missing: large (>50%) collinear overlap forcing the 3-edge reconstruction path in `ShapeFix_IntersectionTool` (both self- and cross-wire).
4. `tkshh-wire-small-edge` — missing: small **seam** edge on a periodic face, drop-mode (unmergeable) case, multi-face closed-curve protection (`ShapeFix_Wireframe::MergeSmallEdges`).
5. `tkshh-edge-missing-pcurve` — missing: clean fixture for a seam edge needing **both** period-shifted pcurves synthesized (Gp076 exercises it only entangled with other defects).
6. `tkshh-surface-curve-continuity-below-required` — missing: revolution/extrusion surface whose C0 **basis curve** forces the split; knot-**removal** repair of a geometrically-smooth over-multiplied knot.
7. `tkshh-wire-3d-curve-gap` — missing: gapped **free** wire belonging to no face (`ShapeFix_Wireframe` free-wire traversal).
8. `tkshh-edge-missing-3d-curve` — missing: removal path for a completely geometry-less edge (`ShapeFix_Wire.cxx:744-759`).
9. `tkshh-face-small-area-wire` — missing: `ShapeUpgrade_RemoveInternalWires` cross-face cascade removal.
10. `tkshh-face-wire-of-two-coincident-edges` — Tfa074 has the right defect but on a single-wire face, where `FixWiresTwoCoincEdges` no-ops (`nbWires>=2` gate); needs a multi-wire host face.
11. `tkshh-face-missing-seam-edge` is COVERED, but its sibling `tkshh-face-natural-bound-missing` misses the sphere pole-hole/natural-bound merge; `tkshh-edge-crossing-surface-singularity` misses an edge actually **split** at an interior apex crossing.

Full per-class verdicts, fixture IDs, and missing-variant details: `problems.json`. The remaining PARTIALs: `tkshh-closed-edge-full-period-unsplit`, `tkshh-edge-curve-inconsistent-with-vertex-removed`, `tkshh-face-wires-bound-multiple-disjoint-regions`, `tkshh-near-zero-knot-span-thin-patch-filter`, `tkshh-nonperiodic-bspline-seamlike-edge`, `tkshh-same-curve-fragmented-edges`, `tkshh-shell-free-boundary-gap`.

## Where the denominator judgment was hard

- **Detection vs fix**: ShapeAnalysis checkers and their ShapeFix consumers were folded into single classes (e.g. `CheckSelfIntersection`+`FixSelfIntersection`, `CheckSmallArea`+`FixSmallAreaWire`, `CheckLoop`+`FixLoopWire`). `ShapeAnalysis_Surface::ComputeSingularities` was the hardest call: a cone apex is not malformed input, so singularity *mapping* is excluded infrastructure; only its consuming repairs (degenerated-edge, pcurve-collapse) are counted.
- **Machinery vs repair**: 9 candidate classes from the worker passes were reclassified into `excluded.json` at merge time — Newton-refinement guards, the UV-inversion fallback chain, adaptive sampling density, bbox extrema-sampling, planarity fallbacks for degenerate point sets, parameter-transfer during splits, non-manifold vertex-representation preservation, and the collinear-to-line Bezier simplification. Note: ~40 corpus fixtures deliberately target this machinery (Gs06x–Gs14x, Gn04x–Gn10x families). Those fixtures retain their value — they exercise robustness paths — but the machinery is not counted as "problems OCCT can repair", so they don't inflate this coverage number.
- **Improvement vs repair** (ShapeUpgrade): `UnifySameDomain` (over-fragmented same-domain topology) and continuity splitting (C0 geometry) are counted — both are real translator-output defects. `ConvertCurve2dToBezier`/`ConvertSurfaceToBezierBasis` are downstream-format transformations and mostly excluded, except genuine defect handling (near-zero knot spans).
- **Sibling-domain boundary**: `BRepBuilderAPI_Sewing` (≈200 V3 branches) and `BRepLib` (TKTopAlgo, ≈100 branches incl. `SameParameter`) appear in V3 but are **out of this domain** — sewing belongs to the exchange/reader/sewing sibling; BRepLib is not part of TKShHealing (its `SameParameter` defect surface is represented here via `ShapeFix_Edge::FixSameParameter`). `ShapeUpgrade_ShellSewing` is counted only as a TKShHealing entry point, with the sewing algorithm itself deferred to the sibling.
- **Dead code**: `ShapeFix_FixSmallFace::FixPinFace` is a literal no-op stub, and the whole Pin/Twisted-face detection family in `ShapeAnalysis_CheckSmallFace` is never called by any Fix consumer — excluded rather than counted as repairable problems.

## Line-number verification

V3 was evidently generated against a newer/reformatted OCCT tree: line citations drift systematically, growing with file position (up to −839 in `ShapeFix_Wire.cxx` FixTails, −692 in `ShapeFix_ComposeShell.cxx`, +455 in `ShapeFix_Face.cxx`; `ShapeFix_Shell.cxx` cited at line 1428 in a 1,114-line file). Every evidence line in `problems.json` was re-located and verified at `bd2a789f`. V3 factual errors found and corrected: duplicate faces in `FixFaceOrientation` *are* removed (not merely warned); multi-shell input to `ShapeFix_Solid::Perform` is *not* skipped (dispatches to `CreateSolids`); the `ShapeAnalysis_WireOrder.Perform_at206` branch set is misattributed (that code is `ShapeFix_IntersectionTool::FixSelfIntersectWire`). V3 misses filled from source: `FixShifted`/`FixLacking` bodies, `FixGaps3d/2d` (in `ShapeFix_Wire_1.cxx`, absent from V3), the V-direction knot branch in `SplitSurfaceContinuity`, and the loose-wire block in `MergeSmallEdges`.

## Files

- `problems.json` — 60 problem-class records (`problem_id, domain, description, occt_evidence[], subvariants[], fixture_ids[], coverage_verdict, notes`, plus `source_group`).
- `excluded.json` — 270 excluded branches/classes with one-line reasons.
- `partial/group-{A..F}.json` — the six worker passes (pre-merge), kept for audit.
- `PIN.md` — source pin.
