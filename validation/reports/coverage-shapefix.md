# OCCT ShapeFix / ShapeAnalysis coverage in `STEP_PROBLEM_CATALOG.json`

Inputs:
- Sources: `/tmp/cad-occt/src/ModelingAlgorithms/TKShHealing/{ShapeFix,ShapeAnalysis,
  ShapeUpgrade,ShapeBuild,ShapeExtend,ShapeAlgo,ShapeConstruct,ShapeCustom,ShapeProcess,
  ShapeProcessAPI}/`
- Catalog: `research/STEP_PROBLEM_CATALOG.json`
- Generator: `/tmp/parse-occt-fix.py`. Canonical artifact: `/tmp/cad-coverage-gaps.json`.

## Methodology

Parsed every `*.hxx` file under those directories, extracting public methods whose
name matches `Fix.*\(`, `Check.*\(`, or exactly `Perform\(` together with the
immediately preceding `//!` doc block. Excluded data accessors (names ending in
`Mode` / `Status`, or sub-tool factories whose doc starts with `Returns ...Tool` /
`Returns ShapeFix_*`). Overloads on the same class collapse to one record.

A catalog entry covers a method if at least one of:

- the full method name (≥6 chars, excluding generic verbs) appears literally,
- the joined defect-suffix appears literally (e.g. `selfintersectingedge`),
- ≥2 specific defect tokens from the method name appear, or
- 1 specific token plus a defect-class synonym (e.g. `seam` ↔ "seam").

Class-name mentions (`ShapeFix_Wire` etc.) are a tie-breaker only — a single class
mention does not by itself cover the dozens of methods on that class. Generic tokens
(`fix`, `check`, `perform`, `wire`, `edge`, `face`, `shape`, …) do not contribute.

## Totals

- Header files scanned: **114**
- Unique public defect methods: **119**
- Covered (≥1 catalog entry): **46** (39%)
- Uncovered: **73**

## Per-class coverage

| Class | Covered | Total | % |
|---|---:|---:|---:|
| `ShapeAnalysis_CheckSmallFace` | 2 | 9 | 22% |
| `ShapeAnalysis_Edge` | 2 | 7 | 29% |
| `ShapeAnalysis_FreeBoundsProperties` | 0 | 3 | 0% |
| `ShapeAnalysis_ShapeContents` | 0 | 1 | 0% |
| `ShapeAnalysis_Shell` | 0 | 1 | 0% |
| `ShapeAnalysis_TransferParameters` | 0 | 1 | 0% |
| `ShapeAnalysis_TransferParametersProj` | 0 | 1 | 0% |
| `ShapeAnalysis_Wire` | 10 | 24 | 42% |
| `ShapeAnalysis_WireOrder` | 0 | 1 | 0% |
| `ShapeConstruct_Curve` | 0 | 1 | 0% |
| `ShapeConstruct_ProjectCurveOnSurface` | 0 | 1 | 0% |
| `ShapeExtend_ComplexCurve` | 0 | 1 | 0% |
| `ShapeExtend_CompositeSurface` | 0 | 1 | 0% |
| `ShapeFix` | 1 | 1 | 100% |
| `ShapeFix_ComposeShell` | 0 | 1 | 0% |
| `ShapeFix_Edge` | 4 | 7 | 57% |
| `ShapeFix_Face` | 7 | 10 | 70% |
| `ShapeFix_FixSmallFace` | 2 | 7 | 29% |
| `ShapeFix_IntersectionTool` | 0 | 2 | 0% |
| `ShapeFix_Shape` | 0 | 1 | 0% |
| `ShapeFix_Shell` | 1 | 2 | 50% |
| `ShapeFix_Solid` | 0 | 1 | 0% |
| `ShapeFix_SplitCommonVertex` | 0 | 1 | 0% |
| `ShapeFix_Wire` | 13 | 17 | 76% |
| `ShapeFix_WireSegment` | 0 | 1 | 0% |
| `ShapeFix_WireVertex` | 1 | 2 | 50% |
| `ShapeFix_Wireframe` | 3 | 3 | 100% |
| `ShapeProcess` | 0 | 1 | 0% |
| `ShapeProcess_Operator` | 0 | 1 | 0% |
| `ShapeProcess_UOperator` | 0 | 1 | 0% |
| `ShapeUpgrade_FaceDivide` | 0 | 1 | 0% |
| `ShapeUpgrade_FaceDivideArea` | 0 | 1 | 0% |
| `ShapeUpgrade_RemoveInternalWires` | 0 | 1 | 0% |
| `ShapeUpgrade_ShapeConvertToBezier` | 0 | 1 | 0% |
| `ShapeUpgrade_ShapeDivide` | 0 | 1 | 0% |
| `ShapeUpgrade_SplitCurve` | 0 | 1 | 0% |
| `ShapeUpgrade_SplitSurface` | 0 | 1 | 0% |
| `ShapeUpgrade_WireDivide` | 0 | 1 | 0% |

## Covered methods

Method → catalog IDs (top 5, ranked by match score).

| Class | Method | Catalog IDs |
|---|---|---|
| `ShapeAnalysis_CheckSmallFace` | `CheckSplittingVertices` | Gs034 |
| `ShapeAnalysis_CheckSmallFace` | `CheckTwisted` | Gs034 |
| `ShapeAnalysis_Edge` | `CheckPCurveRange` | Gp007 |
| `ShapeAnalysis_Edge` | `CheckSameParameter` | N004, Gp022, Gp027, Twi044, N005 |
| `ShapeAnalysis_Wire` | `CheckConnected` | Gp026, Tsh010, Tsh023, Tsh024, Tsh027 |
| `ShapeAnalysis_Wire` | `CheckCurveGap` | Gp021 |
| `ShapeAnalysis_Wire` | `CheckDegenerated` | Gp005, Gs034, Twi021, N011, M026 |
| `ShapeAnalysis_Wire` | `CheckIntersectingEdges` | Gp030, Gs009 |
| `ShapeAnalysis_Wire` | `CheckOrder` | Twi007 |
| `ShapeAnalysis_Wire` | `CheckOuterBound` | Tfa003 |
| `ShapeAnalysis_Wire` | `CheckSelfIntersectingEdge` | Gs009 |
| `ShapeAnalysis_Wire` | `CheckSelfIntersection` | N008 |
| `ShapeAnalysis_Wire` | `CheckSmall` | Twi013, Gs034 |
| `ShapeAnalysis_Wire` | `CheckSmallArea` | Tsh028, Twi044, Twi045 |
| `ShapeFix` | `FixVertexPosition` | N009 |
| `ShapeFix_Edge` | `FixAddPCurve` | Gp001 |
| `ShapeFix_Edge` | `FixRemovePCurve` | Gp002 |
| `ShapeFix_Edge` | `FixReversed2d` | Gs018 |
| `ShapeFix_Edge` | `FixSameParameter` | Gp022, N004, N006, Gp027, Twi044 |
| `ShapeFix_Face` | `FixLoopWire` | Twi010, Gs009 |
| `ShapeFix_Face` | `FixMissingSeam` | Twi020, Gs002, Twi021, N011 |
| `ShapeFix_Face` | `FixOrientation` | Tsh011, Twi024, Tsh013, Tsh028, Pf025 |
| `ShapeFix_Face` | `FixPeriodicDegenerated` | Gs034, Twi021 |
| `ShapeFix_Face` | `FixSmallAreaWire` | Tsh028, Twi044, Twi045 |
| `ShapeFix_Face` | `FixSplitFace` | Gs034, Tsh013 |
| `ShapeFix_Face` | `FixWiresTwoCoincEdges` | Gs034, Twi033 |
| `ShapeFix_FixSmallFace` | `FixShape` | Ad045, Ad047, Tfa012 |
| `ShapeFix_FixSmallFace` | `FixSplitFace` | Gs034, Tsh013 |
| `ShapeFix_Shell` | `FixFaceOrientation` | Tsh008, Tsh032, Tfa034 |
| `ShapeFix_Wire` | `FixConnected` | Gp026, Twi003, Tsh010, Tsh023, Tsh024 |
| `ShapeFix_Wire` | `FixDegenerated` | Gp005, Twi021, Gs034, N011, M026 |
| `ShapeFix_Wire` | `FixGap2d` | Gp020 |
| `ShapeFix_Wire` | `FixGap3d` | Gp020 |
| `ShapeFix_Wire` | `FixGaps2d` | Gp026 |
| `ShapeFix_Wire` | `FixGaps3d` | N037 |
| `ShapeFix_Wire` | `FixLacking` | Twi036 |
| `ShapeFix_Wire` | `FixReorder` | Twi007, Twi028, Twi038 |
| `ShapeFix_Wire` | `FixSeam` | Gp011, Twi022 |
| `ShapeFix_Wire` | `FixSelfIntersection` | N008 |
| `ShapeFix_Wire` | `FixShifted` | Gp029, Gs007, Gs019, Twi035 |
| `ShapeFix_Wire` | `FixSmall` | Twi013, Gs014, Tsh028, Twi044, Twi045 |
| `ShapeFix_Wire` | `FixTails` | Twi011 |
| `ShapeFix_WireVertex` | `FixSame` | Gp022, N004, N006 |
| `ShapeFix_Wireframe` | `CheckSmallEdges` | Twi013 |
| `ShapeFix_Wireframe` | `FixSmallEdges` | Twi013 |
| `ShapeFix_Wireframe` | `FixWireGaps` | N002 |

## Uncovered methods (gap report)

Defect handlers with no catalog entry referencing them directly or by defect class.
Doc snippets are summarized (≤80 chars) — see `/tmp/cad-coverage-gaps.json` for the
full record (file path, line numbers, original doc, suggested category).

Note: many `Perform()` entries are top-level pipeline runners that delegate to the
specific `Fix*`/`Check*` methods on the same class — they are listed here because
the catalog has no entry referencing each pipeline runner directly.

| Class | Method | Defect summary | Suggested category |
|---|---|---|---|
| `ShapeAnalysis_CheckSmallFace` | `CheckPin` | diagnose a face pin singularity | §12.3 (sub-class: faces) |
| `ShapeAnalysis_CheckSmallFace` | `CheckPinEdges` | diagnose pin-singularity edges | §12.3 (sub-class: edges) |
| `ShapeAnalysis_CheckSmallFace` | `CheckPinFace` | diagnose a face that is a pin | §12.3 (sub-class: faces) |
| `ShapeAnalysis_CheckSmallFace` | `CheckSingleStrip` | diagnose a face that collapses to a single strip | §12.3 (sub-class: faces) |
| `ShapeAnalysis_CheckSmallFace` | `CheckSpotFace` | diagnose a face that collapses to a spot | §12.3 (sub-class: faces) |
| `ShapeAnalysis_CheckSmallFace` | `CheckStripEdges` | diagnose edge pair that forms a strip | §12.3 (sub-class: edges) |
| `ShapeAnalysis_CheckSmallFace` | `CheckStripFace` | diagnose a face that is a strip in U or V | §12.3 (sub-class: faces) |
| `ShapeAnalysis_Edge` | `CheckCurve3dWithPCurve` | diagnose 3D curve vs pcurve mutual orientation | §12.3 (sub-class: edges) |
| `ShapeAnalysis_Edge` | `CheckOverlapping` | diagnose edge overlap | §12.3 (sub-class: edges) |
| `ShapeAnalysis_Edge` | `CheckVertexTolerance` | diagnose vertex tolerance vs curve endpoints | §12.3 (sub-class: edges) |
| `ShapeAnalysis_Edge` | `CheckVerticesWithCurve3d` | diagnose vertex match against 3D curve | §12.3 (sub-class: edges) |
| `ShapeAnalysis_Edge` | `CheckVerticesWithPCurve` | diagnose vertex match against pcurve | §12.3 (sub-class: edges) |
| `ShapeAnalysis_FreeBoundsProperties` | `CheckContours` | diagnose free-bound contours | §12.3 (sub-class: shape-healing) |
| `ShapeAnalysis_FreeBoundsProperties` | `CheckNotches` | diagnose notch features in free bounds | §12.3 (sub-class: shape-healing) |
| `ShapeAnalysis_FreeBoundsProperties` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeAnalysis_ShapeContents` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeAnalysis_Shell` | `CheckOrientedShells` | diagnose shell-orientation manifold condition | §12.3 (sub-class: shells) |
| `ShapeAnalysis_TransferParameters` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeAnalysis_TransferParametersProj` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeAnalysis_Wire` | `CheckClosed` | diagnose wire closure | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckCurveGaps` | diagnose 3D curve gaps along wire | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckEdgeCurves` | diagnose edge geometry consistency (2D/3D) | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckGap2d` | diagnose pcurve gap between adjacent edges | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckGap3d` | diagnose 3D curve gap between adjacent edges | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckGaps2d` | diagnose all pcurve gaps along wire | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckGaps3d` | diagnose all 3D curve gaps along wire | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckLacking` | diagnose missing edges along wire | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckLoop` | diagnose self-loop vertices on wire | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckNotchedEdges` | diagnose notched-edge defect | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckSeam` | diagnose seam pcurve orientation | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckShapeConnect` | diagnose how a wire/edge can attach to existing wire | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `CheckTail` | diagnose wire tail/spike feature | §12.3 (sub-class: wires) |
| `ShapeAnalysis_Wire` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: wires) |
| `ShapeAnalysis_WireOrder` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: wires) |
| `ShapeConstruct_Curve` | `FixKnots` | fix BSpline knot spacing | §12.2 (sub-class: pcurves/curves) |
| `ShapeConstruct_ProjectCurveOnSurface` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: faces) |
| `ShapeExtend_ComplexCurve` | `CheckConnectivity` | diagnose geometrical connectivity of curve/patch composition | §12.2 (sub-class: pcurves/curves) |
| `ShapeExtend_CompositeSurface` | `CheckConnectivity` | diagnose geometrical connectivity of curve/patch composition | §12.3 (sub-class: faces) |
| `ShapeFix_ComposeShell` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shells) |
| `ShapeFix_Edge` | `FixAddCurve3d` | fix (rebuild) missing 3D edge curve | §12.3 (sub-class: edges) |
| `ShapeFix_Edge` | `FixRemoveCurve3d` | fix stale 3D edge curve | §12.3 (sub-class: edges) |
| `ShapeFix_Edge` | `FixVertexTolerance` | fix vertex tolerance to cover curve endpoints | §12.3 (sub-class: edges) |
| `ShapeFix_Face` | `FixAddNaturalBound` | fix face that lacks its natural outer boundary | §12.3 (sub-class: faces) |
| `ShapeFix_Face` | `FixIntersectingWires` | fix face wires that intersect each other | §12.3 (sub-class: wires) |
| `ShapeFix_Face` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: faces) |
| `ShapeFix_FixSmallFace` | `FixFace` | fix small/spot/strip/pin face (umbrella) | §12.3 (sub-class: faces) |
| `ShapeFix_FixSmallFace` | `FixPinFace` | fix face whose vertex pin can be removed | §12.3 (sub-class: faces) |
| `ShapeFix_FixSmallFace` | `FixSpotFace` | fix face collapsed to a spot | §12.3 (sub-class: faces) |
| `ShapeFix_FixSmallFace` | `FixStripFace` | fix face that is a strip | §12.3 (sub-class: faces) |
| `ShapeFix_FixSmallFace` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: faces) |
| `ShapeFix_IntersectionTool` | `FixIntersectingWires` | fix face wires that intersect each other | §12.3 (sub-class: wires) |
| `ShapeFix_IntersectionTool` | `FixSelfIntersectWire` | fix self-intersecting wire on a face | §12.3 (sub-class: wires) |
| `ShapeFix_Shape` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeFix_Shell` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shells) |
| `ShapeFix_Solid` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: solids) |
| `ShapeFix_SplitCommonVertex` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeFix_Wire` | `FixClosed` | fix wire closure (calls FixConnected+FixDegenerated+FixLacking) | §12.3 (sub-class: wires) |
| `ShapeFix_Wire` | `FixEdgeCurves` | fix group: 3D curves and pcurves of edges | §12.3 (sub-class: wires) |
| `ShapeFix_Wire` | `FixNotchedEdges` | fix notched-edge defect on wire | §12.3 (sub-class: wires) |
| `ShapeFix_Wire` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: wires) |
| `ShapeFix_WireSegment` | `CheckPatchIndex` | diagnose patch-index validity for wire-segment edge | §12.3 (sub-class: wires) |
| `ShapeFix_WireVertex` | `Fix` | fix all wire-vertex statuses except 'Disjoined' | §12.3 (sub-class: wires) |
| `ShapeProcess` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeProcess_Operator` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeProcess_UOperator` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeUpgrade_FaceDivide` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: faces) |
| `ShapeUpgrade_FaceDivideArea` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: faces) |
| `ShapeUpgrade_RemoveInternalWires` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: wires) |
| `ShapeUpgrade_ShapeConvertToBezier` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeUpgrade_ShapeDivide` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: shape-healing) |
| `ShapeUpgrade_SplitCurve` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.2 (sub-class: pcurves/curves) |
| `ShapeUpgrade_SplitSurface` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: faces) |
| `ShapeUpgrade_WireDivide` | `Perform` | top-level pipeline runner; delegates to the class's Fix*/Check* methods | §12.3 (sub-class: wires) |

---

Machine-readable gap data: `/tmp/cad-coverage-gaps.json` (list of objects with
`class_name`, `method_name`, `file`, `line`/`lines`, `decl`, `doc`, `suggested_category`).
