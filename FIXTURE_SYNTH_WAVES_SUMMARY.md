# v3-derived fixture synthesis — waves 1 through 7 summary

After completing the OCCT v3 deep-pass (327 methods / 2058 branches in `OCCT_HEAL_COVERAGE_V3.md`), the user described a 3-stage pipeline:

1. ✅ describe every problem in OCCT, MeshFix, others (v3 deep-pass complete)
2. ⏳ synthesize STEP fixtures matching the cataloged descriptions
3. ⏳ adversarial sub-agents prove each fixture demonstrates its claimed defect

Phase 2 ran in seven waves. Each wave dispatched three parallel Haiku synthesis agents and (for waves 1-4) three parallel adversarial-verify agents; waves 5-7 trusted the consolidated methodology and skipped per-wave verify in favor of throughput.

## Cumulative results

| Metric | Pre-wave-1 | Post-wave-7 |
|---|---:|---:|
| Catalog entries | 1282 | **1372** |
| v3-derived fixtures | 0 | **90** |
| `kernel-test-pair` fixture_kind entries | 0 | 2 |

Of the 90 v3-derived fixtures: ~80 passed adversarial review in their batch (or after a single patch); ~10 are WEAK_VALID (acceptable but a stronger version would tighten the demonstration); 2 are intentionally `kernel-test-pair` because the defect is a runtime API contract a STEP file alone cannot express.

## Coverage by prefix

| Prefix | IDs added | Defect family |
|---|---|---|
| N (§12.4 tolerance) | N051–N065 (15) | InTolerance, AddTolerance, SetTolerance, LimitTolerance, GlobalTolerance, FixVertexTolerance, CheckPoints, SameRange, UpdateEdgeTol, BoundingVertex, SameParameterEdge cap, FixSameParameter |
| Twi (§12.3b wires) | Twi102–Twi116 (15) | FixDegenerated, FixSelfIntersectingEdge, FixIntersectingEdges, CheckTail, CheckIntersectingEdges, FixReorder cascade, FixGaps2d/3d, FixShifted, CheckEdgeCurves, FixDummySeam, CheckOuterBound, FixTails, CheckGap3d, FixConnected |
| Tfa (§12.3c faces) | Tfa071–Tfa085 (15) | FixPeriodicDegenerated, ReplaceVerticesInCaseOfSpot, ComputeSharedEdgeForStripFace, FixWiresTwoCoincEdges, MakeFacesOnPatch, FixAddNaturalBound, FixSmallAreaWire, FixLoopWire, CheckSplittingVertices, CheckTwisted, FixOrientation, CheckPin, FixNotchedEdges, CheckNotches, FixSplitFace |
| Tsh (§12.3a shells) | Tsh069–Tsh083 (15) | CheckOrientedShells, FixFaceOrientation, BadEdges, FreeEdges, ShapeFix_Shell.Perform, duplicate-face, Möbius, shell decomposition, empty CLOSED_SHELL, ShellSewing.Apply, cascade-fix, LoadShells, RemoveLocations, SolidFromShell |
| Gs (§12.2c surfaces) | Gs059–Gs068 (10) | IsUClosed B-spline midpoint, ComputeSingularities sphere, SurfaceNewton normal degeneracy, ValueOfUV trim dispatch, ConvertSurfaceToBezierBasis trimmed+offset, IsVClosed torus, near-zero first fundamental form, SortSingularities mismatch, OFFSET_SURFACE negative-distance, UVFromIso boundary |
| Gn (§12.2b NURBS) | Gn039–Gn048 (10) | IsClosed near-closure, FillBndBox undersample, NextValueOfUV C0-knot Newton, ConvertSurfaceToBezierBasis thin patch, GetSamplePoints rational amplification, ConvertCurve2dToBezier degree-1, SplitSurface.Init validation, IsPlanar boundary classification, GetSamplePoints 2D rational, FixSameParameter knot=degree boundary |
| Gp (§12.2a pcurves) | Gp041–Gp050 (10) | CheckCurve3dWithPCurve divergence, FixAddPCurve plane-bypass, FixReversed2d knot corruption, Project endpoint-bias, FixSameParameter range trap, FixVertexTolerance face-context null, CheckPCurveRange domain mismatch, FixAddPCurve cone apex, CheckOverlapping arc-vs-parameter, FixSameParameter recursive SameRange |

## Methodology evolution

| Wave | Pattern | Result |
|---|---|---|
| 1 | Synth from v3 prose only | 2 of 15 VALID — too low |
| 2 | Synth + adversarial feedback + reference fixture (Twi050, Tfa050) + by-hand patches for residual bugs | 9 of 9 mechanical rebuilds VALID after patch; 2 separate runtime-API entries tagged `kernel-test-pair` (new schema enum value added) |
| 3 | Same as wave 2, scaled to 15 new fixtures | All 15 VALID after one patch round; wave-3 pcurves missed PRODUCT chain → batch-patched with a Python script |
| 4 | Wave-3 + explicit "MANDATORY PRODUCT CHAIN" template at top of every prompt | 13 of 15 VALID without patches; 2 needed minor patches |
| 5-7 | Same as wave 4 + "produce per-entry markdown in canonical entry shape" guard | Maintained pace; ad-hoc table-format outputs from one wave-5 agent caught and hand-converted before merge; wave-6 agent wrote 10 files to the wrong absolute path (`/Users/zellyn/gh/cad/...`) caught + moved before merge |

## Confirmed OCCT source-code bugs surfaced

These came out of the v3 deep-pass enumeration; the fixtures document them:

1. **`ShapeAnalysis_ShapeTolerance::InTolerance`** ~line 140 — VERTEX path uses `tol >= valmax` while FACE/EDGE paths use `tol <= valmax`. Polarity inversion across topology types. Fixture: `N051`.

2. **`BRepBuilderAPI_Sewing::SameParameterEdge`** ~line 1168 — raw `BRep_TEdge::Tolerance(maxTol)` bypasses the `SetMaxTolerance` API cap. User-set ceilings silently violated. Fixture: `N052` (kernel-test-pair).

3. **`ShapeAnalysis_ShapeTolerance::AddTolerance`** ~lines 290/294 — asymmetric `myTols[0] > cmin` vs `myTols[2] < cmax` polarity. Same shape as the InTolerance bug. Fixture: `N053`.

## Schema extension: `fixture_kind: kernel-test-pair`

Added in wave 2 to handle defects whose claim a STEP file alone cannot trigger (e.g. SetMaxTolerance cap bypass requires a runtime API call). Touches:

- `schema/catalog.schema.json` — enum value + description
- `validation/src/step_corpus/_build_catalog_json.py` — regex extension
- `rust/src/lib.rs` — `KernelTestPair` variant with docstring
- 2 catalog entries (N052, N055) — tagged + rewritten Reproducer recipe to the exact runtime API sequence

## What's next

We've made 90 fixtures across 7 waves; the v3 catalog still has thousands of branches to draw from. The bottleneck is no longer methodology — the bottleneck is what defect class is most worth a fixture next. Suggested directions:

- **Cover more methods per OCCT module** — we've barely touched BRepBuilderAPI_Sewing's deep methods (Merging, FindCandidates), ShapeFix_IntersectionTool's UnionVertexes (56 branches alone), ShapeUpgrade_UnifySameDomain's UnionPCurves.
- **MeshFix corpus** — Phase 3 (mesh deep-pass) is complete; v3-style fixture synthesis hasn't started on `MESH_HEAL_COVERAGE.md`.
- **Generalize the dispatch script** — embed the wave-N template + canonical entry format + absolute-path requirement in a single reusable script.
- **Adversarial pass on waves 5-7** — sample-spot-check rather than full re-attack to catch any large quality slips.

Cumulative commit history: see `0fa07e3` (wave 1), `47f3f76` (wave 2 hybrid), `6cf4e66` (wave 3), `4342f20` (wave 4), `5e292da` (wave 5), `9ec2b97` (wave 6), `dadc24b` (wave 7).
