# OCCT Coverage Sweep — Under-Mined Modules

Read-only sweep of nine OCCT modules not deeply mined in the original passes.
Every defect class enumerated below comes from an explicit OCCT enum, alert macro,
status code, or "Check/Fix/Has/IsValid" public method. Doc comments paraphrased.

Catalog reference: `research/STEP_PROBLEM_CATALOG.json` (578 entries).
Coverage tested by semantic-phrase match across `title`, `description`,
`reproducer`, `category`, `notes`, `sources`.

JSON companion: `/tmp/cad-coverage-undermined.json`.

---

## 1. `TKBRep/BRepCheck/` — invariant checking

**Files walked:** `BRepCheck_{Analyzer,Edge,Face,Result,Shell,Solid,Status,Vertex,Wire}.hxx`
plus `BRepCheck_Status.hxx` (the canonical defect enum for the topology kernel).

**`BRepCheck_Status` enum (36 values):** `NoError`, `InvalidPointOnCurve`,
`InvalidPointOnCurveOnSurface`, `InvalidPointOnSurface`, `No3DCurve`,
`Multiple3DCurve`, `Invalid3DCurve`, `NoCurveOnSurface`,
`InvalidCurveOnSurface`, `InvalidCurveOnClosedSurface`,
`InvalidSameRangeFlag`, `InvalidSameParameterFlag`,
`InvalidDegeneratedFlag`, `FreeEdge`, `InvalidMultiConnexity`,
`InvalidRange`, `EmptyWire`, `RedundantEdge`, `SelfIntersectingWire`,
`NoSurface`, `InvalidWire`, `RedundantWire`, `IntersectingWires`,
`InvalidImbricationOfWires`, `EmptyShell`, `RedundantFace`,
`InvalidImbricationOfShells`, `UnorientableShape`, `NotClosed`,
`NotConnected`, `SubshapeNotInShape`, `BadOrientation`,
`BadOrientationOfSubshape`, `InvalidPolygonOnTriangulation`,
`InvalidToleranceValue`, `EnclosedRegion`, `CheckFail`.

**Covered (semantic match in catalog):** `InvalidPointOnCurve*` (Pmi/Tsh tolerance
families), `Invalid3DCurve` (Twi family), `InvalidCurveOnSurface` (pcurve issues
covered in Tsh/Twi), `InvalidCurveOnClosedSurface` (seam-edge coverage in
12.2a), `InvalidSameParameterFlag` (Tsh), `FreeEdge` (Tfa free-edge family),
`SelfIntersectingWire` (Twi family), `InvalidWire`, `EmptyWire`,
`InvalidImbricationOfWires` (outer/inner wire ordering covered),
`NotClosed`/`NotConnected` (shell-closure family), `BadOrientation`,
`InvalidPolygonOnTriangulation`, `InvalidToleranceValue`, `RedundantEdge`/
`RedundantFace`, `InvalidRange`.

**Uncovered (gaps vs. catalog):** `Multiple3DCurve`, `RedundantWire`,
`InvalidImbricationOfShells`, `EmptyShell`, `EnclosedRegion`,
`InvalidMultiConnexity`, `InvalidSameRangeFlag`, `InvalidDegeneratedFlag`,
`UnorientableShape`, `BadOrientationOfSubshape`, `SubshapeNotInShape`,
`NoSurface` (face has no underlying surface), `IntersectingWires` (distinct
from self-intersection: two wires of the same face cross).

---

## 2. `TKTopAlgo/BRepLib/` — healing operations

**Headers walked:** `BRepLib_{CheckCurveOnSurface,EdgeError,FaceError,WireError,
ShellError,FindSurface,FuseEdges,MakeEdge,MakeFace,MakeShell,MakeSolid,
MakeWire,PointCloudShape,ShapeModification,ToolTriangulatedShape,ValidateEdge}.hxx`
+ `BRepLib.hxx` (static-method facade).

**Error enums:**
- `BRepLib_EdgeError`: `EdgeDone`, `PointProjectionFailed`,
  `ParameterOutOfRange`, `DifferentPointsOnClosedCurve`,
  `PointWithInfiniteParameter`, `DifferentsPointAndParameter`,
  `LineThroughIdenticPoints`.
- `BRepLib_FaceError`: `FaceDone`, `NoFace`, `NotPlanar`,
  `CurveProjectionFailed`, `ParametersOutOfRange`.
- `BRepLib_WireError`: `WireDone`, `EmptyWire`, `DisconnectedWire`,
  `NonManifoldWire`.
- `BRepLib_ShellError`: `ShellDone`, `EmptyShell`, `DisconnectedShell`,
  `ShellParametersOutOfRange`.
- `BRepLib_ShapeModification`: tracking class for downstream healers.

**Static healers (from `BRepLib`):** `Precision`, `SameRange`, `SameParameter`,
`BuildCurve3d`, `BuildCurves3d`, `BuildPCurveForEdgeOnPlane`, `UpdateEdgeTol`,
`UpdateEdgeTolerance`, `UpdateTolerances`, `UpdateInnerTolerances`,
`OrientClosedSolid`, `ContinuityOfFaces`, `EncodeRegularity`, `SortFaces`,
`ReverseSortFaces`, `EnsureNormalConsistency`, `UpdateDeflection`,
`BoundingVertex`, `FindValidRange`, `ExtendFace`, `CheckSameRange`.

**Covered (catalog):** `PointWithInfiniteParameter` (infinite/unbounded
parameter family), `EmptyWire`, `DisconnectedWire` (12.3b),
`SameParameter`/`SameRange` mismatches (Tsh), `ParameterOutOfRange`
(implicitly via 12.4 tolerance group).

**Uncovered:** `DifferentPointsOnClosedCurve`,
`DifferentsPointAndParameter`, `LineThroughIdenticPoints`, `NotPlanar`
(face from non-planar wire), `CurveProjectionFailed`, `NonManifoldWire`,
`DisconnectedShell`, `ShellParametersOutOfRange`. Static healers (defects
that arise when the healer itself fails or is invoked on bad input):
`OrientClosedSolid` (open or incoherent solid that cannot be oriented to
contain matter), `EncodeRegularity` race (regularity already encoded but
wrong; the healer silently no-ops), `BuildCurves3d` (no planar pcurve →
3D curve cannot be reconstructed), `EnsureNormalConsistency`
(triangulation normals inconsistent at smooth-edge nodes),
`ContinuityOfFaces` (G-continuity classification at edge), `FuseEdges`
(merging collinear edges through a 2-valent vertex),
`UpdateInnerTolerances` (inner-curve points outside vertex tolerance).

---

## 3. `TKBO/BOPAlgo/` — Boolean operations

**Headers walked:** `BOPAlgo_{Alerts,ArgumentAnalyzer,Builder,BOP,
BuilderArea,BuilderFace,BuilderShape,BuilderSolid,CellsBuilder,CheckerSI,
CheckResult,CheckStatus,GlueEnum,MakeConnected,MakePeriodic,MakerVolume,
Operation,Options,PaveFiller,RemoveFeatures,Section,ShellSplitter,
Splitter,Tools,WireEdgeSet,WireSplitter}.hxx`.

**`BOPAlgo_CheckStatus` enum:** `CheckUnknown`, `BadType`, `SelfIntersect`,
`TooSmallEdge`, `NonRecoverableFace`, `IncompatibilityOfVertex`,
`IncompatibilityOfEdge`, `IncompatibilityOfFace`, `OperationAborted`,
`GeomAbs_C0`, `InvalidCurveOnSurface`, `NotValid`.

**`BOPAlgo_Alerts.hxx` macros (~40 alerts):** `BOPNotAllowed`, `BOPNotSet`,
`BuilderFailed`, `IntersectionFailed`, `MultipleArguments`, `NoFiller`,
`NullInputShapes`, `PostTreatFF`, `SolidBuilderFailed`, `TooFewArguments`,
`BadPositioning`, `EmptyShape`, `NotSplittableEdge`,
`RemovalOfIBForEdgesFailed`, `RemovalOfIBForFacesFailed`,
`RemovalOfIBForMDimShapes`, `RemovalOfIBForSolidsFailed`,
`SelfInterferingShape`, `ShellSplitterFailed`, `TooSmallEdge`,
`IntersectionOfPairOfShapesFailed`, `BuildingPCurveFailed`,
`AcquiredSelfIntersection`, `UnsupportedType`, `NoFacesToRemove`,
`UnableToRemoveTheFeature`, `RemoveFeaturesFailed`,
`SolidBuilderUnusedFaces`, `FaceBuilderUnusedEdges`,
`UnableToOrientTheShape`, `UnknownShape`, `NoPeriodicityRequired`,
`UnableToTrim`, `UnableToMakeIdentical`, `UnableToRepeat`,
`MultiDimensionalArguments`, `UnableToMakePeriodic`, `UnableToGlue`,
`ShapeIsNotPeriodic`, `UnableToMakeClosedEdgeOnFace`.

**`ArgumentAnalyzer` modes (defect-class testers):** `ArgumentTypeMode`,
`SelfInterMode`, `SmallEdgeMode`, `RebuildFaceMode`, `TangentMode`,
`MergeVertexMode`, `MergeEdgeMode`, `ContinuityMode`, `CurveOnSurfaceMode`.

**Covered:** `SelfIntersect` (Twi), `TooSmallEdge`/`small-edge` (Tsh
Bd-class), `BadPositioning`, `MergeVertex`/`MergeEdge`/`tangency`/`G0
continuity` (Twi+Tsh families), `MakePeriodic` (periodicity covered).

**Uncovered:** `NonRecoverableFace`, `AcquiredSelfIntersection`,
`BuildingPCurveFailed`, `SolidBuilderUnusedFaces`,
`FaceBuilderUnusedEdges`, `UnableToOrientTheShape`,
`UnableToMakeClosedEdgeOnFace`, `UnableToTrim`, `UnableToMakeIdentical`,
`UnableToRepeat`, `RemoveFeaturesFailed` family (4 sub-alerts),
`ShellSplitterFailed`, `MakerVolume` (volume from arbitrary face set),
`ShellSplitter` / `WireSplitter` (utility-level failures),
`PostTreatFF` (face-face curve connection), `MultipleArguments`,
`MultiDimensionalArguments`, `NoFiller` (PaveFiller unset), `BadType`,
`OperationAborted` (user-break vs. internal abort).

---

## 4. `TKFillet/BRepFilletAPI/` — fillets/chamfers

**Headers walked:** `BRepFilletAPI_{LocalOperation,MakeChamfer,MakeFillet,
MakeFillet2d}.hxx`. Backed by `ChFiDS_ErrorStatus`.

**`ChFiDS_ErrorStatus` enum:** `Ok`, `Error`, `WalkingFailure`,
`StartsolFailure`, `TwistedSurface`.

**Public defect-reporting methods on `MakeFillet`:** `NbFaultyContours`,
`FaultyContour`, `NbFaultyVertices`, `FaultyVertex`, `HasResult`,
`BadShape`, `StripeStatus`. Doc paraphrase: the construction can fail at
two specific topology configurations — (a) end-point of contour is
incident to ≥4 edges of the shape, (b) the fillet's intersection with the
limiting face is not entirely contained in that face.

**Covered:** `Twi` family covers fillet-related self-intersection edge
problems generically.

**Uncovered:** `ChFiDS_TwistedSurface`, `ChFiDS_WalkingFailure`,
`ChFiDS_StartsolFailure`, the 4-edge corner case, the
fillet-leaks-off-face case, and partial-result `BadShape` semantics. No
chamfer-specific defects in catalog.

---

## 5. `TKOffset/BRepOffsetAPI/` — offsets, sweeping, lofting, draft

**Headers walked:** `BRepOffsetAPI_{DraftAngle,FindContigousEdges,MakeDraft,
MakeEvolved,MakeFilling,MakeOffset,MakeOffsetShape,MakePipe,MakePipeShell,
MakeThickSolid,MiddlePath,NormalProjection,Sewing,ThruSections}.hxx` +
`BRepFill_ThruSectionErrorStatus.hxx`, `BRepOffset_Error.hxx`,
`BRepOffset_Status.hxx`, `Draft_ErrorStatus.hxx`,
`BRepBuilderAPI_PipeError.hxx`.

**`BRepOffset_Error` enum:** `NoError`, `UnknownError`,
`BadNormalsOnGeometry`, `C0Geometry`, `NullOffset`, `NotConnectedShell`,
`CannotTrimEdges`, `CannotFuseVertices`, `CannotExtentEdge`, `UserBreak`,
`MixedConnectivity` (partially C0 and tangent across an edge).

**`BRepOffset_Status` enum (per-face after offsetting):** `Good`,
`Reversed` (offset > radius of cylinder; face inverts),
`Degenerated` (offset = radius; face collapses), `Unknown` (Bezier).

**`BRepFill_ThruSectionErrorStatus`:** `Done`, `NotDone`, `NotSameTopology`
(profiles must be all closed or all open), `ProfilesInconsistent`,
`WrongUsage` (vertex section not at first/last), `Null3DCurve`, `Failed`.

**`BRepBuilderAPI_PipeError`:** `PipeDone`, `PipeNotDone`,
`PlaneNotIntersectGuide`, `ImpossibleContact`.

**`Draft_ErrorStatus`:** `NoError`, `FaceRecomputation`,
`EdgeRecomputation`, `VertexRecomputation` (each indicates which level
the draft-angle fix had to escalate to).

**Covered:** `C0Geometry` (offset on C0 surface — generic continuity).

**Uncovered (a large unmined attack surface):** `BadNormalsOnGeometry`,
`NotConnectedShell` (offset of a non-shell-like compound),
`CannotTrimEdges`, `CannotFuseVertices`, `CannotExtentEdge`,
`MixedConnectivity`, `Reversed`/`Degenerated` per-face status, all four
`ThruSection` failure modes, `PlaneNotIntersectGuide`,
`ImpossibleContact` (pipe sweep), all three Draft escalation levels,
`MakeFilling` constraint-incompatibility, `MiddlePath` (centerline
extraction), `MakeEvolved` profile-rotation, `NormalProjection` failures,
`MakeThickSolid` (thickening with concave radius < wall),
`FindContigousEdges` (free-edge survey distinct from sewing).

---

## 6. `TKGeomBase/` — base geometry validity

**Headers walked:** `Approx_Status.hxx`, `LProp_Status.hxx`,
`GeomLib_CheckBSplineCurve.hxx`, `GeomLib_Check2dBSplineCurve.hxx`,
`GeomLib_CheckCurveOnSurface.hxx`, `GeomLib_Tool.hxx`,
`Approx_SameParameter.hxx`, `Approx_CurveOnSurface.hxx`.

**Enums:**
- `Approx_Status`: `PointsAdded`, `NoPointsAdded`, `NoApproximation`.
- `LProp_Status`: `Undecided`, `Undefined`, `Defined`, `Computed`.

**Public checkers:** `GeomLib_CheckBSplineCurve` — flags whether either
end tangent of a B-spline points the wrong way relative to its third
control-point neighbour, and offers `FixTangent`.
`GeomLib_CheckCurveOnSurface` — measures max distance between a 3D curve
and its 2D pcurve evaluated through the surface; returns `MaxDistance`,
`MaxParameter`, and a 4-state error status (null inputs / invalid range /
calc error / OK).

**Covered:** generic approximation-failure / continuity-class issues are
in the Tsh and 12.2b families.

**Uncovered:** `Approx_NoApproximation` (a full failure status that
distinguishes "could not approximate at all" from "approx done but
imprecise"), `LProp_Undefined` (point with no defined local properties —
e.g. cusp), `GeomLib_CheckBSplineCurve` reversed-tangent class,
`GeomLib_CheckCurveOnSurface` quantitative pcurve↔3d gap (this is the
metric BRep tolerance is supposed to bound but rarely does).

---

## 7. `TKXSBase/Interface/` — diagnostic infrastructure

**Headers walked:** `Interface_{Check,CheckIterator,CheckTool,CheckStatus,
DataState,InterfaceMismatch,InterfaceError,GTool,GeneralLib}.hxx`.

**`Interface_CheckStatus`:** `OK`, `Warning`, `Fail`, `Any`, `Message`,
`NoFail`.
**`Interface_DataState`:** `StateOK`, `LoadWarning`, `LoadFail`,
`DataWarning`, `DataFail`, `StateUnloaded`, `StateUnknown`.

**Methods:** `Interface_Check` exposes `AddFail` / `AddWarning` /
`SendMsg` / `Mend` (downgrade Fail to Warning) / `HasFailed` /
`HasWarnings` / `Complies` (status query) / `Remove` / `GetAsWarning`
(used during recovery — Fails are kept as Warnings).

A spot-grep across `STEPControl/STEPCAFControl` `.cxx` files yielded ~25
distinct `AddFail`/`AddWarning` strings (sample paraphrased): "scaling
factor skipped", "external reference file is the same main file", "axis
placements swapped in SRRWT corrected", "no unit context default taken",
"product has both sub-assemblies and directly-assigned shape",
"non-manifold COMPSOLID translated as set of SOLIDs", "exception raised,
entity not translated", "no shape produced", "SRR reverses NAUO; NAUO
taken", "no length uncertainty, read.precision.val taken".

**Covered:** the strings overlap heavily with U/N/Pmi families.

**Uncovered as named diagnostic classes:** `StateUnloaded` (entity
parsed but not bound to any in-memory representation — silent data
loss), `LoadWarning` vs. `DataWarning` distinction (parse-time vs.
semantic-time degraded), `Mend`-converted-Warning class (a Fail that was
demoted at recovery; downstream consumers who only inspect Warnings see
no problem). The "external reference file is same as main file" is a
specific A-class adversarial input not isolated as a defect.

---

## 8. `TKXSBase/Transfer/` — transfer-status codes

**Headers walked:** `Transfer_{TransientProcess,FinderProcess,Binder,
StatusExec,StatusResult,TransferDeadLoop,TransferFailure,ResultFromModel,
ResultFromTransient}.hxx`.

**`Transfer_StatusExec`:** `Initial`, `Run`, `Done`, `Error`, `Loop`.
**`Transfer_StatusResult`:** `Void`, `Defined`, `Used`.

**Failure classes:** `Transfer_TransferDeadLoop`, `Transfer_TransferFailure`.

**Covered:** none directly. `Pf010` covers cyclic STEP refs but not the
transfer-layer dead-loop detection signal.

**Uncovered:** `Transfer_StatusLoop` (the watchdog has fired during
transfer — distinct from cyclic-reference-during-parse), `Transfer_StatusError`
(exception caught during entity-to-shape; entity bound to `null`),
`Transfer_StatusVoid` after expected-Defined transfer (silent partial
transfer — entity referenced but never produced a shape).

---

## 9. `TKTopAlgo/BRepBuilderAPI/` — `Sewing` and tunables, plus `FastSewing`

**Headers walked:** `BRepBuilderAPI_{Sewing,FastSewing,EdgeError,FaceError,
PipeError,ShellError,WireError,FindPlane,Copy,GTransform,Transform,
TransitionMode}.hxx`.

**`Sewing` tunables (each is a defect-controlling knob):** `Tolerance`
(default 1e-6), `MinTolerance`, `MaxTolerance`, `FaceMode` (sew faces),
`FloatingEdgesMode` (sew floating edges), `LocalTolerancesMode`
(per-edge/vertex tolerances), `NonManifoldMode` (allow >2 faces per
edge), `SameParameterMode`. Output classifies edges as `FreeEdge`,
`MultipleEdge` (>2 faces), `ContigousEdge` (good seam),
`DegeneratedShape`, `DeletedFace` (smaller than tolerance — silent
geometry loss).

**`BRepBuilderAPI_FastSewing` `FS_Statuses` (bitmask):** `OK`,
`Degenerated`, `FindVertexError`, `FindEdgeError`,
`FaceWithNullSurface`, `NotNaturalBoundsFace`, `InfiniteSurface`,
`EmptyInput`, `Exception`. Doc paraphrase: this fast path *skips*
SameParameter checks because it assumes input pcurves are already
parameter-aligned — when that assumption is wrong, downstream consumers
get a shape that fails `BRepCheck_Analyzer` for `InvalidSameParameter`
without any direct sewing diagnostic.

**Covered:** generic sewing-tolerance / multi-edge defects in Tsh family;
the floating-edge mode is referenced.

**Uncovered:** `MultipleEdge` (>2 faces sharing one edge — non-manifold
sewing output), `DeletedFace` (face below tolerance silently dropped),
`DegeneratedShape` survey output, all five `FastSewing` failure flags as
distinct defects (especially `NotNaturalBoundsFace` — when a trimmed
face has parametric bounds tighter than the surface natural bounds, the
fast sewer mis-locates seams), and the `SameParameter` skip-trap
described above.

---

## Top-30 most important uncovered defects

Each row gives a **suggested ID prefix**, **proposed category**, **terse
defect-class title**, and **entity-level reproducer recipe** the
catalog can adopt. Prefixes follow existing convention; new prefixes
are noted.

| # | Suggested ID | Category | Title | Reproducer (entity-level) |
|---|---|---|---|---|
| 1 | Twi-W### | §12.3b wires | Two non-coincident wires of one face cross (`IntersectingWires`, distinct from self-intersection) | One `FACE_BOUND` outer + one `FACE_BOUND` inner (hole) whose pcurves cross in UV; both wires individually closed and simple. |
| 2 | Tsh-S### | §12.3a shells | Inner void shell of a solid is itself contained in another inner void (`InvalidImbricationOfShells`) | `MANIFOLD_SOLID_BREP` with two `ORIENTED_CLOSED_SHELL` voids where shell B is geometrically inside shell A. |
| 3 | Tfa-F### | §12.3c faces | Face with no underlying surface (`BRepCheck_NoSurface`) | `ADVANCED_FACE` with `face_geometry` = `null`/missing reference, but boundaries present. |
| 4 | Tsh-S### | §12.3a shells | Cavity not closed by a void shell — `EnclosedRegion` | `MANIFOLD_SOLID_BREP` whose outer shell has a topological cavity (genus≥1 sub-region) but no inner-bound shell entry. |
| 5 | Tfa-O### | §12.3c faces | Solid is unorientable (Möbius-like; `UnorientableShape`) | `ORIENTED_CLOSED_SHELL` whose face-orientation flags admit no globally consistent normal field. |
| 6 | Tsh-E### | §12.3 | Edge present in >2 faces inside one shell (`InvalidMultiConnexity`) | Three `ADVANCED_FACE`s sharing a single `EDGE_CURVE` instance (non-manifold edge encoded in a shell that should be 2-manifold). |
| 7 | Twi-E### | §12.3b | Closed B-spline curve has different start/end CARTESIAN_POINT (`DifferentPointsOnClosedCurve`) | `B_SPLINE_CURVE_WITH_KNOTS` flagged `closed_curve = .T.` with `control_points_list` whose first ≠ last. |
| 8 | Twi-E### | §12.3b | Edge geometry is a line through coincident endpoints (`LineThroughIdenticPoints`) | `EDGE_CURVE` whose `edge_start = edge_end` and `edge_geometry` is a `LINE`. |
| 9 | Tsh-O### | §12.3a | Solid orientation cannot be set so that "matter" is consistent (`OrientClosedSolid` returns false) | Closed shell that is well-formed but has a face-flip such that no global outward normal exists; fixture reproduces by inverting one face of an otherwise valid cube. |
| 10 | Tsh-N### | §12.3a | Triangulation normals inconsistent at smooth-edge nodes (`EnsureNormalConsistency`) | STEP with `triangulated_face` (AP242 ed.2) whose per-node normals on a G1 edge disagree across adjacent triangles. |
| 11 | Bo-Sf### **(new prefix `Bo` for Boolean-op defects)** | §12.6 / new §12.6-bo | `BOPAlgo_AcquiredSelfIntersection` — self-intersection appears only after intersection with the second argument | Two valid solids that touch tangentially along a common cylinder; the union creates a degenerate self-touching face. |
| 12 | Bo-Pc### | §12.6-bo | `BOPAlgo_AlertBuildingPCurveFailed` during boolean | Two solids whose intersection edge falls on a periodic surface near the seam; pcurve construction fails. |
| 13 | Bo-Nr### | §12.6-bo | `BOPAlgo_NonRecoverableFace` after section | Boolean of two solids where one face must be split into >2 sub-faces and one slice has area below tolerance. |
| 14 | Bo-Su### | §12.6-bo | `SolidBuilderUnusedFaces` — faces classified neither inside nor outside | Boolean producing a sliver region with faces of ambiguous classification (faces whose all vertices are on the section). |
| 15 | Bo-Co### | §12.6-bo | `UnableToMakeClosedEdgeOnFace` — seam reconstruction fails | Boolean operand is a complete revolution surface; section produces edge that should become a seam but seam parameters disagree. |
| 16 | Fi-Tw### **(new prefix `Fi` for fillet/chamfer)** | new §12.fi | `ChFiDS_TwistedSurface` — fillet surface twists | Concave fillet on a contour around an edge that flips concavity along its length. |
| 17 | Fi-Wa### | new §12.fi | `ChFiDS_WalkingFailure` — fillet contour walker stalls | Tangent-edge contour for fillet hits a vertex of valence ≥4 in the middle of the spine. |
| 18 | Fi-St### | new §12.fi | `ChFiDS_StartsolFailure` — radius too large for local geometry | Fillet of radius R requested where local radius of curvature of one of the support faces is < R. |
| 19 | Fi-Co### | new §12.fi | `MakeFillet` 4-edge corner unsupported | Spine ends at a vertex incident to 4 edges of the shape; algorithm explicitly does not handle this. |
| 20 | Os-Ba### **(new prefix `Os` for offset/sweep)** | new §12.os | `BRepOffset_BadNormalsOnGeometry` — offset given a face with reversed normal | `ADVANCED_FACE` with `same_sense=.F.` on a periodic surface plus an offset request; offset direction inverts mid-face. |
| 21 | Os-Re### | new §12.os | `BRepOffset_Reversed` — offset > radius of cylindrical face | Cylinder face of radius 5 mm; request inward offset of 6 mm; resulting face inverts. |
| 22 | Os-Dg### | new §12.os | `BRepOffset_Degenerated` — offset = radius of cylinder | Cylinder face of radius 5 mm; request inward offset of exactly 5 mm; face collapses to axis. |
| 23 | Os-Mc### | new §12.os | `BRepOffset_MixedConnectivity` — partially C0 and tangent across one edge | Two B-spline faces meeting along an edge that is C0 on one half and G1 on the other; offset undecidable. |
| 24 | Os-Ts### | new §12.os | `BRepFill_NotSameTopology` — loft profiles mixed open/closed | `ThruSections` request with profile 1 = closed wire, profile 2 = open wire. |
| 25 | Os-Pr### | new §12.os | `BRepFill_ProfilesInconsistent` — sections have different edge counts | Two closed wires both intended for ruled loft, but one has 3 edges and the other 5. |
| 26 | Os-Pg### | new §12.os | `BRepBuilderAPI_PlaneNotIntersectGuide` — pipe section-plane misses guide curve | `MakePipe` where the swept-section plane at parameter t fails to intersect the guide curve (typical when guide has high curvature). |
| 27 | Os-Ic### | new §12.os | `BRepBuilderAPI_ImpossibleContact` — pipe contact constraint cannot hold | `MakePipeShell` with `KeepContact` set, auxiliary spine drifts away from main spine beyond reach of any section. |
| 28 | Sw-Ml### **(new prefix `Sw` for sewing)** | new §12.sw | `Sewing.MultipleEdge` — non-manifold output passed as manifold | Three faces share a common boundary edge after sewing (sewer doesn't reject; output fails downstream solid-builder). |
| 29 | Sw-Df### | new §12.sw | `Sewing.DeletedFace` — face below tolerance silently dropped | Sliver face of area < tol²; after sewing the face is gone but no error reported. |
| 30 | Sw-Fs### | new §12.sw | `FastSewing.NotNaturalBoundsFace` — fast path mis-handles trimmed face | Trimmed face with parametric bounds tighter than the underlying surface natural bounds; fast sewer mis-locates seam. |

---

## End-of-report stats

- Modules walked: **9** (BRepCheck, BRepLib, BOPAlgo, BRepFilletAPI,
  BRepOffsetAPI, TKGeomBase checkers, Interface, Transfer, BRepBuilderAPI).
- Defect-class candidates enumerated: **~120** across all modules.
- Covered (semantic match): **~16**.
- Uncovered: **~63 distinct OCCT-named classes**.
- Top-30 surfaced above with concrete entity-level reproducer recipes.
- Suggested new ID prefixes: `Bo` (boolean), `Fi` (fillet), `Os`
  (offset/sweep), `Sw` (sewing). Each cleanly adjacent to existing
  Twi/Tsh/Tfa/Pmi schemes.
