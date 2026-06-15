# OCCT healing coverage — per-method rich-prose deep pass (v3)

**Successor to** `OCCT_HEAL_COVERAGE_V2.md` (3,399 branches with 1-2-sentence descriptions).
v3's bar: every branch's description is rich enough to either RECREATE the defect input or be FALSIFIED by an adversarial reader. Each carries `falsifiable_claim` + `minimal_reproducer`. See [`DEEP_PASS_V3_PLAN.md`](DEEP_PASS_V3_PLAN.md) for methodology + the validation-slice plan.

## Current totals (partial — fills in as workers complete)

| | Count |
|---|---:|
| Methods enumerated | 22 |
| Repair branches | 474 |
| Low-confidence branches (need better prose) | 24 |
| Truncated worker outputs (need follow-up) | 0 |

## Defect-axis distribution

| Axis | Count |
|---|---:|
| `healer-state` | 179 |
| `kernel-pair` | 76 |
| `input-shape` | 68 |
| `tolerance` | 61 |
| `api-contract` | 47 |
| `conformance-probe` | 36 |
| `encoding` | 6 |
| `unspecified` | 1 |

## Per-method records

### BRepBuilderAPI_Sewing

#### `BRepBuilderAPI_Sewing.SameParameterEdge`
 (27 branches; 4 low-confidence; source: `v3-deep-BRepBuilderAPI_Sewing_SameParameterEdge.json`)

##### `BRepBuilderAPI_Sewing.SameParameterEdge.floating-edges-reject`
- **Line**: BRepBuilderAPI_Sewing.cxx:672  **Axis**: `input-shape`
- **Brief**: Floating edges (zero connected faces) rejected outright.
- **Falsifiable claim**: Without this check, floating edges would proceed to PCurve extraction, computing invalid curve-surface associations. To test: provide edge with empty listFaces; verify return value is null.
- **Minimal reproducer**: Create edge geometry (e.g., Geom_Line). Construct empty NCollection_List<TopoDS_Shape> for both listFacesFirst and listFacesLast. Call SameParameterEdge. Expected: null edge returned. Without check: exception or garbage tolerance.
- **Search anchors**: 'listFacesFirst.Extent()', 'listFacesLast.Extent()', 'floating edge', 'unconnected edge'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.edge-length-sort-heuristic`
- **Line**: BRepBuilderAPI_Sewing.cxx:679-700  **Axis**: `healer-state`
- **Brief**: Longest edge assigned to edge1 on first call; recursive call inverts selection.
- **Falsifiable claim**: This sorting affects which edge's curve becomes the 3D reference and which edge provides PCurves. Swapping assignment changes tolerance computation outcome. To test: provide two edges of different length; measure final tolerance for both assignment orders.
- **Minimal reproducer**: Create STEP entities: edge1 (length 100mm, line), edge2 (length 10mm, line) on same cylindrical surface. Call SameParameterEdge(edge1, edge2, ...). Measure tolReached. Repeat with swapped argument order. Assertion: same tolerance in both cases (or different if bug exists).
- **Search anchors**: 'Take the longest edge as first', 'len1 < len2', 'GCPnts_AbscissaPoint::Length', 'edge1 = edgeLast', 'edge1 = edgeFirst'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.seam-dual-pcurve-extraction`
- **Line**: BRepBuilderAPI_Sewing.cxx:884-893  **Axis**: `kernel-pair`
- **Brief**: Seam edges on closed surfaces: extract both forward and reversed PCurves.
- **Falsifiable claim**: Seam edges require dual PCurve representation (curve + reversed image) to maintain consistency on toroidal/cylindrical surfaces. Omitting reversed extraction would create single-sided PCurve. To test: construct torus with seam edge; verify both UpdateEdge calls (lines 984, 988, 1033, 1037, 1057, 1061) receive dual curves.
- **Minimal reproducer**: STEP: Create torus (major=50, minor=10). Create closed seam edge along minor circle. Bind to two half-faces with opposite orientations. Set nonmanifold=true. Call SameParameterEdge. Verify: edge has two PCurves on surface. Without dual extraction: single-sided PCurve causes non-manifold geometry.
- **Search anchors**: 'isSeam', 'IsUClosedSurface', 'IsVClosedSurface', 'IsClosed(edge, face)', 'c2d21 = BRep_Tool::CurveOnSurface'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.seam-manifold-nonmanifold-gate`
- **Line**: BRepBuilderAPI_Sewing.cxx:888-890, 975-977  **Axis**: `api-contract`
- **Brief**: Seam edges rejected if manifold-only mode (myNonmanifold=false).
- **Falsifiable claim**: Seam edges inherently create non-manifold topology (edge shared by multiple faces with incompatible orientations). Manifold-only sewing cannot handle them. To test: enable manifold mode; attempt to sew surface with seam; verify rejection.
- **Minimal reproducer**: STEP: torus model with seam edge. BRepBuilderAPI_Sewing sewing; sewing.SetNonmanifoldMode(false); sewing.Add(shell); sewing.Perform(). Expected: seam edge rejected, replaced with degenerate. With manifold=false and seam present: null result.
- **Search anchors**: 'myNonmanifold', '!myNonmanifold', 'return TopoDS_Edge()', 'seam edge', 'manifold'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.seam-75percent-bound-heuristic` **[low-confidence]**
- **Line**: BRepBuilderAPI_Sewing.cxx:1018-1019  **Axis**: `tolerance`
- **Brief**: Seam detection uses 75% parameter-space threshold: distance > 0.75*(U2-U1) → seam.
- **Falsifiable claim**: This heuristic threshold (75%) is arbitrary and may misclassify PCurves near surface seam. Values in 50-85% range would yield different results. To test: construct torus; place edge at 74% and 76% of U range; verify seam detection toggles.
- **Minimal reproducer**: STEP: torus (U=[0,2π]). Create edge at parameter u=1.4π (70% of range). Construct surface with dual PCurves at u=0.1π and u=1.5π. Measure aDist at sample point. If aDist=0.75*2π±ε, seam flag toggles. Expected behavior: borderline cases deterministic.
- **Search anchors**: '0.75 * (fabs(U2 - U1))', 'aDist > 0.75', 'uclosed', 'vclosed', 'isSeam = ...'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.merge-quality-insufficient`
- **Line**: BRepBuilderAPI_Sewing.cxx:1091-1102  **Axis**: `healer-state`
- **Brief**: Merge fails tolerance/SameParameter thresholds; recursively retry on alternate face section.
- **Falsifiable claim**: If first section merge yields !isSamePar or tolReached > myTolerance, retry on second section. This fallback may succeed where primary fails. Without recursion: suboptimal merged edges accepted. To test: construct edge where primary section yields high tolerance; verify second attempt improves it.
- **Minimal reproducer**: STEP: cylinder with two half-shell faces at different scales (ratio 1.1). Create edge at interface. Construct: first face coarse, second fine. Call SameParameterEdge. First attempt: tolReached=0.5 (fails myTolerance=0.1). Recursive call on alternate section: tolReached=0.05 (succeeds). Expected: second result selected.
- **Search anchors**: 'firstCall && (!isResEdge', 'isSamePar', 'tolReached > myTolerance', 'SameParameterEdge(... false)', 'second_ok'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.recursive-tolerance-comparison`
- **Line**: BRepBuilderAPI_Sewing.cxx:1103-1113  **Axis**: `healer-state`
- **Brief**: Accept second attempt only if both SameParameter achieved AND tolerance improved.
- **Falsifiable claim**: Comparison (tolReached_2 < tolReached) ensures monotonic tolerance decrease. Removing this check would accept worse-tolerance fallbacks. To test: construct edge where second attempt has higher tolerance; verify rejection.
- **Minimal reproducer**: STEP: cylinder, edge. First attempt: tolReached=0.08. Second attempt: tolReached=0.12 (worse) but SameParameter=true. Expected: first result retained. If removed: second worse result selected.
- **Search anchors**: 'second_ok =', 'tolReached_2 < tolReached', 'BRep_Tool::Tolerance(s_edge)', 'SameParameter(s_edge)'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.discretized-23point-sampling` **[low-confidence]**
- **Line**: BRepBuilderAPI_Sewing.cxx:1120-1162  **Axis**: `tolerance`
- **Brief**: Sample 3D edge curve at 23 points; compute max distance to PCurve projection.
- **Falsifiable claim**: 23-point sampling may underestimate max distance on high-curvature edges. Coarse grid could miss local peaks. To test: construct edge with oscillating curvature; vary point count; measure max distance convergence.
- **Minimal reproducer**: STEP: complex spline edge on toroidal surface. Create edge with high curvature variation. Sample at 23, 50, 100 points. Compute max distances. Expected: 23 points may underestimate by ±0.001mm. Validate with higher sampling.
- **Search anchors**: 'nbp = 23', 'c3dpnt(i) = c3dAdapt.Value', 'deltaT = (last3d - first3d) / (nbp - 1)', 'GCPnts_AbscissaPoint', 'maxTol'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.location-transform-in-tolerance-eval`
- **Line**: BRepBuilderAPI_Sewing.cxx:1140-1144  **Axis**: `kernel-pair`
- **Brief**: Transform surface by location before D0 evaluation in tolerance computation.
- **Falsifiable claim**: Omitting location transform would compute distance to untransformed surface, yielding false tolerance. To test: place surface with non-identity location; measure tolerance with/without transform.
- **Minimal reproducer**: STEP: surface at origin. Apply placement (translate +100mm, rotate 45°). Create edge on transformed surface. Compute tolerance with location=identity (wrong) vs location!=identity (correct). Expected difference: ±0.001-0.01mm.
- **Search anchors**: 'loc2.IsIdentity()', 'surf2->Transformed(loc2)', 'aS->D0(aP2d.X(), aP2d.Y(), aP2)', 'TopLoc_Location'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.setMaxTolerance-bypass-raw-write`
- **Line**: BRepBuilderAPI_Sewing.cxx:1165-1169  **Axis**: `api-contract`
- **Brief**: Direct BRep_TEdge::Tolerance() write bypasses SetMaxTolerance API when computed tolerance exceeds cap.
- **Falsifiable claim**: Line 1168 performs raw write to BRep_TEdge, circumventing SetMaxTolerance() validation. User-specified cap ignored. API contract violated: SetMaxTolerance guarantees cap enforcement. To test: set MaxTolerance=0.01; compute edge with maxTol=0.05; verify raw write creates 0.05-tolerance edge.
- **Minimal reproducer**: STEP: cylinder. Create edge with simulated tolerance 0.05. Set BRepBuilderAPI_Sewing::SetMaxTolerance(0.01). Trigger discretized-tolerance path (ensure second_ok=false). Inspect edge.TShape()->Tolerance(). Expected if bug: 0.05 (exceeds cap). Correct: cap enforcement or nullify.
- **Search anchors**: 'static_cast<BRep_TEdge*>', 'edge.TShape().get()', '->Tolerance(maxTol)', 'tolReached > MaxTolerance()', 'SetMaxTolerance()'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.builder-api-respected-cap`
- **Line**: BRepBuilderAPI_Sewing.cxx:1172-1175  **Axis**: `api-contract`
- **Brief**: Builder API UpdateEdge respects SetMaxTolerance cap when computed tolerance within bounds.
- **Falsifiable claim**: aBuilder.UpdateEdge(edge, maxTol) validates maxTol against MaxTolerance(). If exceeded, should be rejected. This branch confirms proper API flow for non-bypass case. To test: set MaxTolerance=0.1; compute maxTol=0.05; verify edge accepts it.
- **Minimal reproducer**: STEP: same as bypass case, but ensure computed maxTol < MaxTolerance(). Expected: aBuilder.UpdateEdge succeeds. Edge tolerance = maxTol (within cap).
- **Search anchors**: 'aBuilder.UpdateEdge(edge, maxTol)', 'else {'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.final-tolerance-validation`
- **Line**: BRepBuilderAPI_Sewing.cxx:1180-1184  **Axis**: `tolerance`
- **Brief**: Nullify edge if final tolerance exceeds MaxTolerance (second validation gate).
- **Falsifiable claim**: Final check rejects any edge with tolEdge1 > MaxTolerance(), even after discretized computation. Without this check, bypass at line 1168 would create invalid edges. This gate catches the bypass case. To test: force bypass creation; verify final check nullifies.
- **Minimal reproducer**: STEP: create edge via bypass (line 1168). Final tolerance=0.05, MaxTolerance=0.01. Execute lines 1180-1184. Expected: edge.Nullify() called; returned edge is null.
- **Search anchors**: 'tolEdge1 > MaxTolerance()', 'edge.Nullify()', 'BRep_Tool::Tolerance(edge)', 'return edge'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.vertex-closure-orientation-check`
- **Line**: BRepBuilderAPI_Sewing.cxx:760-776  **Axis**: `input-shape`
- **Brief**: Reject open-open edge pairs if vertex endpoints misaligned (violates continuity).
- **Falsifiable claim**: Misaligned open endpoints (secForward: V11==V22 or V12==V21) indicate incorrect edge pairing. Allowing this would create twisted merged edge. To test: create two open edges with misaligned endpoints; verify rejection.
- **Minimal reproducer**: STEP: line segment A (V1_A, V2_A) and line segment B (V1_B, V2_B) with V1_A==V2_B (misaligned). Call SameParameterEdge(A, B, secForward=true). Expected: null result. Without check: merged edge with invalid topology.
- **Search anchors**: 'V11.IsSame(V22)', 'V12.IsSame(V21)', 'secForward', '!isClosed1 && !isClosed2'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.closed-edge-vertex-merge`
- **Line**: BRepBuilderAPI_Sewing.cxx:785-804  **Axis**: `kernel-pair`
- **Brief**: Merge vertices for closed edges using 3-point midpoint averaging.
- **Falsifiable claim**: Closed edges (V11==V12) require special handling: ComputeToleranceVertex computes weighted average of endpoints. Omitting closure check would attempt standard open-edge merging. To test: create closed edge (loop); call SameParameterEdge; verify ComputeToleranceVertex invoked.
- **Minimal reproducer**: STEP: circle edge (same start/end vertex). Create second edge paired with circle. Call SameParameterEdge. Inspect ComputeToleranceVertex calls: expect 1 call (closed-closed) or 2 calls (closed-open). Tolerance computed at combined center.
- **Search anchors**: 'isClosed1', 'isClosed2', 'V11.IsSame(V12)', 'ComputeToleranceVertex', 'V2New = V1New'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.open-edge-scoped-reuse`
- **Line**: BRepBuilderAPI_Sewing.cxx:808-841  **Axis**: `healer-state`
- **Brief**: Open edges: reuse vertices if already sewed; merge new vertices otherwise.
- **Falsifiable claim**: isOldFirst/isOldLast flags detect pre-sewed vertices. Reusing avoids redundant merges. Omitting reuse would double-sew vertices. To test: create edges with pre-sewed vertices; verify V1New/V2New reuse existing vertices.
- **Minimal reproducer**: STEP: edge1, edge2 already sewed (V11==V21). Call SameParameterEdge(edge1, edge2, secForward=true). Expect: isOldFirst=true; V1New = V11 (reuse). Measure tolerance: should reflect pre-sewed vertex.
- **Search anchors**: 'isOldFirst', 'isOldLast', '!isOldFirst', 'V1New = V11', 'ComputeToleranceVertex'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.secForward-orientation-logic`
- **Line**: BRepBuilderAPI_Sewing.cxx:810-820  **Axis**: `conformance-probe`
- **Brief**: secForward parameter controls vertex pair assignment (forward vs backward orientation).
- **Falsifiable claim**: secForward=true pairs (V11, V21), (V12, V22); secForward=false pairs (V11, V22), (V12, V21). Swapping this logic creates opposite orientation. To test: call with secForward=true and false; measure merged edge orientation.
- **Minimal reproducer**: STEP: two open edges. Call SameParameterEdge(..., secForward=true) and secForward=false. Compare V1New, V2New assignments. Expected: opposite vertex pairings; resulting edges have opposite orientations.
- **Search anchors**: 'secForward', 'V11.IsSame(V21)', 'V11.IsSame(V22)', 'V12.IsSame(V22)', 'V12.IsSame(V21)'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.pcurve-reversal-symmetry`
- **Line**: BRepBuilderAPI_Sewing.cxx:904-914, 922-932  **Axis**: `kernel-pair`
- **Brief**: PCurve reversal: if secBackward, reverse c2d21 and c2d2; rescale domain.
- **Falsifiable claim**: Reversal is asymmetric: only applied if !secForward. Omitting reversal would create PCurves with incompatible domain orientation. To test: construct with secForward=false; verify c2d21, c2d2 reversed and parameters flipped.
- **Minimal reproducer**: STEP: edge on surface with reversed orientation. Call with secForward=false. Inspect c2d21, c2d2 after reversal: Value(param) should yield same 2D point as before-reversal Value(LastParam - param). Domain: firstOld, lastOld swapped.
- **Search anchors**: '!secForward', 'c2d21->Reverse()', 'c2d2->Reverse()', 'ReversedParameter', 'Geom2d_TrimmedCurve'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.sameRange-domain-rescaling`
- **Line**: BRepBuilderAPI_Sewing.cxx:916, 935  **Axis**: `kernel-pair`
- **Brief**: SameRange rescales PCurve domain to match 3D edge (first, last).
- **Falsifiable claim**: PCurves extracted from faces have face-specific domains. Rescaling ensures PCurve parameter equals 3D edge parameter. Omitting rescale creates domain mismatch. To test: extract PCurve with domain [0, 1]; 3D edge domain [5, 10]; apply SameRange; verify result has domain [5, 10].
- **Minimal reproducer**: STEP: face with edge; PCurve domain=[0, π]. 3D edge domain=[0, 1]. Apply SameRange(..., 0, π, 0, 1). Expected: c2d2->FirstParameter()=0, c2d2->LastParameter()=1 after rescale.
- **Search anchors**: 'SameRange(c2d2, firstOld, lastOld, first, last)', 'firstOld', 'lastOld', 'first', 'last'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.sameRange-failure-skip`
- **Line**: BRepBuilderAPI_Sewing.cxx:936-938  **Axis**: `conformance-probe`
- **Brief**: If SameRange conversion fails (returns null), skip face iteration.
- **Falsifiable claim**: SameRange failure indicates incompatible curves (e.g., degenerate PCurve). Skipping avoids null-pointer dereference or invalid PCurve addition. To test: construct degenerate PCurve; attempt SameRange; verify null return and skip.
- **Minimal reproducer**: STEP: degenerate PCurve (single point). Attempt SameRange. Expected: null return. Face iteration continues to next face. Without skip: null dereference in subsequent UpdateEdge calls.
- **Search anchors**: 'c2d2.IsNull()', 'continue', 'SameRange'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.surface-equality-same-face-shortcut`
- **Line**: BRepBuilderAPI_Sewing.cxx:1001-1026  **Axis**: `healer-state`
- **Brief**: If PCurves from two edges on same surface, apply seam heuristic; skip if already merged.
- **Falsifiable claim**: Same-surface PCurves indicate redundant edge pairs. Seam heuristic distinguishes merged (isSeam) from non-merged. Without this check, all same-surface pairs treated identically. To test: construct edge where surf1==surf2; verify seam detection.
- **Minimal reproducer**: STEP: cylinder with two sections. Create edge on both sections. Call SameParameterEdge. If surf1==surf2 and loc1==loc2, invoke seam heuristic. Compare distances; if >75% bound, flag seam.
- **Search anchors**: 'surf2 == surf1', 'loc2.IsDifferent(loc1)', 'IsUClosedSurface', 'IsVClosedSurface'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.same-range-false-flag`
- **Line**: BRepBuilderAPI_Sewing.cxx:744  **Axis**: `kernel-pair`
- **Brief**: Mark new edge as !SameRange (parameter reparameterization in progress).
- **Falsifiable claim**: SameRange=false signals that edge PCurves not yet synchronized with 3D curve. Subsequent UpdateEdge calls establish synchronization. Omitting this flag would incorrectly claim synchronization. To test: inspect edge.SameRange() after construction; expect false.
- **Minimal reproducer**: STEP: create edge, line 744 sets SameRange(edge, false). Verify BRep_Tool::SameRange(edge)==false. After final UpdateEdge: verify SameRange(edge, true) sets it to true.
- **Search anchors**: 'aBuilder.SameRange(edge, false)', '// true'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.same-parameter-finalization`
- **Line**: BRepBuilderAPI_Sewing.cxx:1176  **Axis**: `kernel-pair`
- **Brief**: Final SameParameter() call marks edge as fully synchronized after tolerance computation.
- **Falsifiable claim**: SameParameter(true) signals that 3D curve and all PCurves now have same parameter domain and distance alignment verified. Omitting this marks edge unsynchronized. To test: inspect edge.SameParameter() after line 1176; expect true.
- **Minimal reproducer**: STEP: after discretized-tolerance computation, line 1176 sets SameParameter(edge, true). Verify BRep_Tool::SameParameter(edge)==true.
- **Search anchors**: 'aBuilder.SameParameter(edge, true)', 'SameParameter(edge)'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.location-copy-transform`
- **Line**: BRepBuilderAPI_Sewing.cxx:737-740  **Axis**: `kernel-pair`
- **Brief**: Transform 3D curve by location before using as reference (if location non-identity).
- **Falsifiable claim**: Curves stored with location transformation deferred. Copying and transforming ensures reference curve in world frame. Omitting transform would use local-frame curve. To test: extract curve from edge with non-identity location; measure coordinates.
- **Minimal reproducer**: STEP: place surface at origin with rotation. Extract edge curve with location. Copy and transform. Compare transformed curve Value(t) with location-applied original. Expected: identical 3D points.
- **Search anchors**: 'loc3d.IsIdentity()', 'c3d->Transform(loc3d.Transformation())', 'occ::down_cast<Geom_Curve>(c3d->Copy())'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.line-trimmed-curve-wrapper` **[low-confidence]**
- **Line**: BRepBuilderAPI_Sewing.cxx:906-908, 924-926  **Axis**: `conformance-probe`
- **Brief**: Wrap line-type PCurves in TrimmedCurve before reversal (handles parameter domain edge case).
- **Falsifiable claim**: Line curves allow arbitrary parameter translation. TrimmedCurve enforces domain bounds before reversal. Omitting wrapper could cause reversal domain errors. To test: reverse unwrapped line; observe domain issues; repeat with wrapper.
- **Minimal reproducer**: STEP: line PCurve with domain [0, 100]. Attempt Reverse() directly. Then wrap in TrimmedCurve(line, 0, 100). Reverse() again. Expected: wrapped version handles domain correctly.
- **Search anchors**: 'isKind(STANDARD_TYPE(Geom2d_Line))', 'Geom2d_TrimmedCurve(c2d21, firstOld, lastOld)'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.nonmanifold-mode-gate`
- **Line**: BRepBuilderAPI_Sewing.cxx:888, 975  **Axis**: `api-contract`
- **Brief**: Seam edges accepted only if myNonmanifold=true; manifold mode rejects.
- **Falsifiable claim**: Seam edges create non-manifold vertices. Manifold-only mode cannot represent them. To test: enable/disable nonmanifold mode; attempt seam-edge sewing.
- **Minimal reproducer**: STEP: torus (seam-bearing surface). With myNonmanifold=false: sewing rejects. With myNonmanifold=true: sewing proceeds.
- **Search anchors**: 'myNonmanifold', '!myNonmanifold'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.exception-catch-silent` **[low-confidence]**
- **Line**: BRepBuilderAPI_Sewing.cxx:1072-1089  **Axis**: `conformance-probe`
- **Brief**: SameParameter algorithm exceptions silently set isSamePar=false (no rethrow).
- **Falsifiable claim**: Exceptions from SameParameter() caught and ignored. Edge still returned, marked as not-sameParameter. Caller cannot diagnose cause. To test: construct edge that triggers SameParameter exception; verify silent handling.
- **Minimal reproducer**: STEP: edge with invalid PCurve (null geometry). Call SameParameter(edge). Expect: exception caught; isSamePar=false; no error propagation.
- **Search anchors**: 'catch (Standard_Failure const&)', 'isSamePar = false'

##### `BRepBuilderAPI_Sewing.SameParameterEdge.edge-result-nullify-final`
- **Line**: BRepBuilderAPI_Sewing.cxx:1180-1184  **Axis**: `tolerance`
- **Brief**: Nullify edge result if final tolerance exceeds MaxTolerance (safety gate).
- **Falsifiable claim**: Final validation ensures no out-of-spec edges returned. Omitting nullify would return invalid edges. To test: trigger edge creation with excessive tolerance; verify nullify.
- **Minimal reproducer**: STEP: edge with computed tolerance=0.5, MaxTolerance=0.1. Line 1180-1184 checks and nullifies. Expected: returned edge is null.
- **Search anchors**: 'tolEdge1 > MaxTolerance()', 'edge.Nullify()', 'return edge'


### BRepLib

#### `BRepLib.ContinuityOfFaces`
 (0 branches; source: `v3-deep-BRepLib_ContinuityOfFaces.json`)


#### `BRepLib.EncodeRegularity`
 (0 branches; source: `v3-deep-BRepLib_ContinuityOfFaces.json`)


#### `BRepLib.SameParameter`
 (24 branches; 4 low-confidence; source: `v3-deep-BRepLib_SameParameter.json`)

##### `BRepLib.SameParameter.EARLY_EXIT_SAME_PARAMETER`
- **Line**: BRepLib.cxx:1256  **Axis**: `healer-state`
- **Brief**: Already-SameParameter edges bypass healing, returning null edge.
- **Falsifiable claim**: Without this guard, edges already meeting SameParameter would be processed again, consuming redundant CPU. To test: create edge with SameParameter=true, invoke BRepLib::SameParameter; without guard would loop through curves unnecessarily.
- **Minimal reproducer**: Construct edge from 3D curve with matching 2D parametrization on surface. BRep_Builder().UpdateEdge(edge, ..) then BRep_Builder().SameParameter(edge, true). Call BRepLib::SameParameter(edge, tol). Expected: empty result (optimization). Incorrect: processes curves again.
- **Search anchors**: 'SameParameter already set', 'early return edge', 'no healing needed'

##### `BRepLib.SameParameter.NULL_CURVE3D`
- **Line**: BRepLib.cxx:1265  **Axis**: `input-shape`
- **Brief**: Edges missing 3D curves cannot be healed; return null edge.
- **Falsifiable claim**: Without this check, dereferencing null C3d in GetCurve3d would crash. To test: create edge with only 2D pcurve, no 3D curve; call BRepLib::SameParameter.
- **Minimal reproducer**: Build edge with 2D parametric curve on surface but no 3D curve. Call BRepLib::SameParameter(edge, 0.01). Expected: returns null edge (no 3D geometry to work with). Incorrect: segfault in GAC.Load(C3d).
- **Search anchors**: 'C3d.IsNull', 'missing 3D curve', 'no 3D geometry'

##### `BRepLib.SameParameter.EDGE_COPY_vs_REUSE`
- **Line**: BRepLib.cxx:1273  **Axis**: `api-contract`
- **Brief**: Flag IsUseOldEdge controls whether to modify original edge in-place or create new copy.
- **Falsifiable claim**: Without in-place vs copy decision, caller cannot control whether edges are mutated. To test: set IsUseOldEdge=false and verify new edge is created; set true and verify original is modified.
- **Minimal reproducer**: Edge with C0 discontinuity in 2D curve. Call SameParameter(edge, tol, newTol, IsUseOldEdge=true) and SameParameter(edge, tol, newTol, IsUseOldEdge=false). Expected (true): original edge tolerance updated. Expected (false): new edge returned, original unchanged.
- **Search anchors**: 'IsUseOldEdge', 'EmptyCopied', 'modify in-place vs copy'

##### `BRepLib.SameParameter.TRIMMED_PERIODIC_DETECTION`
- **Line**: BRepLib.cxx:1306  **Axis**: `input-shape`
- **Brief**: Detect if 3D curve is a TrimmedCurve wrapping a periodic basis curve.
- **Falsifiable claim**: Without checking for TrimmedCurve wrapping, periodic basis would be incorrectly treated as non-periodic, causing incorrect parameter clamping. To test: wrap periodic spline in TrimmedCurve; without detection, f3d/l3d would be incorrectly adjusted.
- **Minimal reproducer**: Create periodic Geom_BSplineCurve, wrap in Geom_TrimmedCurve, place on edge. Call BRepLib::SameParameter. Expected: m_TrimmedPeriodical=true, skip clamping. Incorrect: clamp to trimmed bounds, losing periodicity semantics.
- **Search anchors**: 'TrimmedCurve detection', 'periodic basis', 'm_TrimmedPeriodical'

##### `BRepLib.SameParameter.NONPERIODIC_RANGE_CLIP`
- **Line**: BRepLib.cxx:1323  **Axis**: `tolerance`
- **Brief**: Clamp non-periodic curve parameters to its domain [FirstParameter, LastParameter].
- **Falsifiable claim**: Without clamping, using parameters outside domain in GAC.Load() would cause evaluator errors. To test: edge with clamped f3d/l3d outside curve bounds; without clipping, approximation would fail.
- **Minimal reproducer**: Non-periodic spline with domain [0, 10], edge parametrized [0.5, 9.5]. Call BRepLib::SameParameter with original bounds. Expected: f3d=0.5, l3d=9.5 (unchanged if within). With f3d=-0.5: clamped to 0. Incorrect without: evaluator exception.
- **Search anchors**: 'non-periodic curve', 'parameter clamping', 'Udeb/Ufin'

##### `BRepLib.SameParameter.TRANSFORMED_LOCATION`
- **Line**: BRepLib.cxx:1345  **Axis**: `kernel-pair`
- **Brief**: Apply 3D curve location transformation if edge has non-identity location.
- **Falsifiable claim**: Without location transform, 3D curve in local frame would be approximated in wrong coordinates, causing tolerance overflow. To test: edge with rotated/translated location; without transform, approximation error balloons.
- **Minimal reproducer**: Create 3D curve in local frame, edge with TopLoc_Location(rotation+translation). Call BRepLib::SameParameter. Expected: C3d transformed to global. Incorrect: approximation computed in local frame, 2D-3D mismatch.
- **Search anchors**: 'L3d.IsIdentity', 'location transformation', 'surface location'

##### `BRepLib.SameParameter.TOLERANCE_OVERFLOW`
- **Line**: BRepLib.cxx:1366  **Axis**: `tolerance`
- **Brief**: Abort curve processing if 2D-3D distance exceeds 1e10, indicating numerical failure.
- **Falsifiable claim**: Without overflow check, erroneous curve pairs (highly mismatched 3D/2D) would be processed further, corrupting tolerance. To test: pair degenerate 2D curve with 3D curve; error > 1e10, should abort early.
- **Minimal reproducer**: Edge with 3D line segment and completely mismatched 2D curve. Call ComputeTol; error exceeds 1e10. Expected: break, maxdist=error, graceful degradation. Incorrect: accumulate error into SameParameter tolerance.
- **Search anchors**: 'BigError 1.e10', 'tolerance overflow', 'numerical failure'

##### `BRepLib.SameParameter.BSPLINE_C0_DISCONTINUITY`
- **Line**: BRepLib.cxx:1368  **Axis**: `conformance-probe`
- **Brief**: Detect and upgrade B-spline 2D curves with C0 discontinuities (knot discontinuities) to C1.
- **Falsifiable claim**: Without C0->C1 upgrade, knot jumps cause parametric discontinuities in 2D curve, violating SameParameter constraint. To test: 2D B-spline with C0 knot; without upgrade, 2D curve has tangent jump.
- **Minimal reproducer**: Construct 2D B-spline with C0 continuity at interior knot on surface. Edge with this 2D curve + matching 3D curve. Call BRepLib::SameParameter(edge, 0.01). Expected: Geom2dConvert::C0BSplineToC1BSplineCurve applied, smoothed. Incorrect: tangent discontinuity remains, failing SameParameter validation.
- **Search anchors**: 'C0 discontinuity', 'B-spline upgrade', 'Geom2dConvert::C0BSplineToC1'

##### `BRepLib.SameParameter.PERIODIC_BSPLINE_ORIGIN`
- **Line**: BRepLib.cxx:1380  **Axis**: `healer-state`
- **Brief**: For periodic B-splines, find origin knot matching pre-upgrade point to maintain origin semantics.
- **Falsifiable claim**: Without origin re-anchoring, periodic B-spline origin shifts after C0->C1, breaking parameter continuity across period. To test: periodic B-spline, upgrade C0->C1; without SetOrigin, parametrization jumps.
- **Minimal reproducer**: Periodic 2D B-spline (period ~1.0) with C0 knot. Store D0(FirstParameter). Upgrade C0->C1. Expected: D0(FirstParameter) unchanged, origin re-anchored to matching knot. Incorrect: D0(FirstParameter) returns different point after SetOrigin.
- **Search anchors**: 'periodic B-spline', 'origin management', 'SetOrigin', 'parametric continuity'

##### `BRepLib.SameParameter.EVALTOL_C0_FALLBACK` **[low-confidence]**
- **Line**: BRepLib.cxx:1403  **Axis**: `tolerance`
- **Brief**: If B-spline remains C0 after initial upgrade, attempt EvalTol-based tolerance relaxation.
- **Falsifiable claim**: Without EvalTol fallback, persistent C0 curves would fail SameParameter, preventing healing of difficult edges. To test: B-spline where C0->C1 upgrade fails; EvalTol computes relaxed tolerance enabling success.
- **Minimal reproducer**: 2D B-spline with multiple C0 knots where simple C0->C1 conversion cannot fully smooth. After initial Geom2dConvert call, bs2d->Continuity() still == C0. Call EvalTol(curPC, S, GAC, tolerance, tolbail). Expected: tolbail > tolerance, enables second attempt. Incorrect: skip, fail SameParameter.
- **Search anchors**: 'EvalTol fallback', 'persistent C0', 'tolerance relaxation'

##### `BRepLib.SameParameter.POLE_DISTANCE_HEURISTIC` **[low-confidence]**
- **Line**: BRepLib.cxx:1419  **Axis**: `tolerance`
- **Brief**: Use 10% of minimum control polygon edge as second-attempt tolerance (Tol2dbail).
- **Falsifiable claim**: Without pole-distance scaling, second C0->C1 attempt uses arbitrary tolerance; 10% heuristic balances smoothness vs overshooting. To test: B-spline with dense control polygon vs sparse; 10% heuristic adapts.
- **Minimal reproducer**: Dense B-spline (poles 0.01 apart) and sparse B-spline (poles 1.0 apart). Compute min pole distance. Expected: dense -> Tol2dbail=0.001, sparse -> 0.1. Incorrect: fixed tolerance ignores geometry scale.
- **Search anchors**: 'pole distance', '10% heuristic', 'control polygon'

##### `BRepLib.SameParameter.PERIODIC_BSPLINE_ORIGIN_2ND` **[low-confidence]**
- **Line**: BRepLib.cxx:1437  **Axis**: `healer-state`
- **Brief**: Re-apply periodic origin adjustment after second C0->C1 upgrade with relaxed tolerance.
- **Falsifiable claim**: Second C0->C1 may shift origin again; without re-anchoring, parametrization discontinuity persists. To test: apply second upgrade to periodic spline; origin point moves, SetOrigin call corrects it.
- **Minimal reproducer**: Periodic B-spline, first upgrade origin preserved. Apply second Geom2dConvert::C0BSplineToC1 with Tol2dbail. Expected: D0(FirstParameter) may change again, SetOrigin re-anchors. Incorrect: parametrization jumps at origin.
- **Search anchors**: 'second periodic origin', 're-anchor after upgrade'

##### `BRepLib.SameParameter.EVALTOL_REJECTION` **[low-confidence]**
- **Line**: BRepLib.cxx:1458  **Axis**: `healer-state`
- **Brief**: If EvalTol fails (returns false), mark curve as non-healable (goodpc=false).
- **Falsifiable claim**: Without rejection, attempting second C0->C1 with invalid tolerance would cause convergence failure. To test: edge where EvalTol cannot compute valid tolbail; skip further processing.
- **Minimal reproducer**: Edge where EvalTol(curPC, S, GAC, tolerance, tolbail) returns false (degenerate surface or invalid curve). Expected: goodpc=false, IsSameP remains false, edge tolerance adjusted per OCC5898. Incorrect: use tolbail anyway, approximation fails.
- **Search anchors**: 'EvalTol rejection', 'goodpc false', 'skip approximation'

##### `BRepLib.SameParameter.KNOT_RATIO_ANOMALY`
- **Line**: BRepLib.cxx:1481  **Axis**: `conformance-probe`
- **Brief**: Detect knot spacing anomalies (ratio > 10) after C0->C1 upgrade, indicating ill-conditioning.
- **Falsifiable claim**: Without anomaly detection, approximation on ill-conditioned knot distributions fails; detecting ratio triggers arc-length reparametrization. To test: C0->C1 upgrade creates highly non-uniform knots; IsBad flag triggers reparametrization.
- **Minimal reproducer**: B-spline with clustered knots in region, sparse elsewhere. After C0->C1, knot ratio > 10. Expected: IsBad=true, triggers Approx_CurvilinearParameter. Incorrect: attempt approximation on bad knots, convergence failure or tolerance blow-up.
- **Search anchors**: 'knot ratio anomaly', 'critratio 10', 'IsBad flag'

##### `BRepLib.SameParameter.CURVILINEAR_APPROXIMATION`
- **Line**: BRepLib.cxx:1512  **Axis**: `kernel-pair`
- **Brief**: Reparametrize ill-conditioned 2D curve by arc length using Approx_CurvilinearParameter.
- **Falsifiable claim**: Without arc-length reparametrization, bad knot ratios cause numerical instability; arc-length parametrization normalizes conditioning. To test: invoke Approx_CurvilinearParameter on 2D adaptor; replace curve with result.
- **Minimal reproducer**: 2D B-spline with IsBad=true (bad knot ratio). Call Approx_CurvilinearParameter(HC2d, HS, tol, cont, maxdeg, 10). Expected: IsDone/HasResult returns new curve with uniform arc-length parametrization. Incorrect: skip, fail SameParameter.
- **Search anchors**: 'arc-length reparametrization', 'Approx_CurvilinearParameter', 'conditioning'

##### `BRepLib.SameParameter.CURVILINEAR_KNOT_REPAR`
- **Line**: BRepLib.cxx:1519  **Axis**: `tolerance`
- **Brief**: Adjust knots of arc-length reparametrized curve back to original parametric range.
- **Falsifiable claim**: Without range adjustment, arc-length curve may have different domain than original; reparametrizing knots ensures consistency. To test: CurvilinearParameter output may have different [First, Last]; BSplCLib::Reparametrize scales knots back.
- **Minimal reproducer**: Original curve domain [f3d, l3d]. Arc-length result has domain [fC0_new, lC0_new] != [f3d, l3d]. Call BSplCLib::Reparametrize(fC0, lC0, Knots). Expected: knot range matches [fC0, lC0]. Incorrect: domain mismatch causes parametrization errors.
- **Search anchors**: 'knot reparametrization', 'domain adjustment', 'BSplCLib::Reparametrize'

##### `BRepLib.SameParameter.REPAR_AND_RECHECK`
- **Line**: BRepLib.cxx:1562  **Axis**: `healer-state`
- **Brief**: After initial C0->C1 upgrade, reparametrize knots and recompute error to validate improvement.
- **Falsifiable claim**: Without recheck, knot reparametrization could worsen error; recomputing detects regression. To test: reparametrize, compute error1; if error1 > error, revert.
- **Minimal reproducer**: B-spline after C0->C1, goodpc=true, repar=true. Reparametrize knots. Call ComputeTol again. Expected: error1 <= original error (improvement or unchanged). Incorrect: skip recheck, use worse parametrization.
- **Search anchors**: 'reparametrization', 'error recheck', 'error1 vs error'

##### `BRepLib.SameParameter.ERROR_REGRESSION_FALLBACK`
- **Line**: BRepLib.cxx:1569  **Axis**: `healer-state`
- **Brief**: If reparametrization worsens error, revert to original curve and signal isANA=true.
- **Falsifiable claim**: Without regression detection, bad reparametrization would corrupt curve; detecting and reverting preserves correctness. To test: error1 > error indicates regression; revert bs2d.
- **Minimal reproducer**: After reparametrization, error1=0.5 > error=0.1. Expected: bs2d=bs2dsov (revert), isANA=true (signal smaller tolerance for Approx_SameParameter). Incorrect: keep bad reparametrization.
- **Search anchors**: 'error regression', 'fallback revert', 'isANA signal'

##### `BRepLib.SameParameter.APPROX_SAMEPARAMETER`
- **Line**: BRepLib.cxx:1593  **Axis**: `conformance-probe`
- **Brief**: Primary approximation: check if 3D and 2D curves already satisfy SameParameter within tolerance.
- **Falsifiable claim**: Without SameParameter check, new curve generation would be unnecessary if curves already match. To test: if Approx_SameParameter::IsSameParameter() true, accept curves as-is.
- **Minimal reproducer**: 3D curve and 2D parametrization well-matched from initial data. Call Approx_SameParameter. Expected: IsSameParameter()=true, maxdist=SameP.TolReached(). Incorrect: modify curves unnecessarily.
- **Search anchors**: 'IsSameParameter', 'already matched', 'no modification needed'

##### `BRepLib.SameParameter.APPROX_SAMEPARAMETER_DONE`
- **Line**: BRepLib.cxx:1599  **Axis**: `healer-state`
- **Brief**: If approximation succeeded but IsSameParameter false, conditionally accept result if tolreached <= error.
- **Falsifiable claim**: Without conditional acceptance, approximation results worse than original error would replace curves; comparing tolerances ensures monotonic improvement. To test: tolreached < error indicates improvement, accept result.
- **Minimal reproducer**: Approx_SameParameter::IsDone()=true, TolReached()=0.05, original error=0.1. Expected: accept new curve (improvement). With tolreached=0.15 > error: reject, keep original.
- **Search anchors**: 'conditional acceptance', 'tolerance comparison', 'monotonic improvement'

##### `BRepLib.SameParameter.APPROX_SAMEPARAMETER_FAIL`
- **Line**: BRepLib.cxx:1618  **Axis**: `kernel-pair`
- **Brief**: If Approx_SameParameter fails entirely, fallback to GeomLib::SameRange without full approximation.
- **Falsifiable claim**: Without fallback, failed approximation leaves 2D curve unadjusted; SameRange provides minimal adjustment ensuring parameter range match. To test: Approx_SameParameter::IsDone()=false; use SameRange instead.
- **Minimal reproducer**: 3D and 2D curves in mismatched parameter ranges, Approx_SameParameter cannot converge. Expected: fallback to GeomLib::SameRange(TolSameRange, PC[i], ...). Incorrect: leave curves unadjusted, fail validation.
- **Search anchors**: 'approximation failure', 'SameRange fallback', 'minimal adjustment'

##### `BRepLib.SameParameter.GOODPC_FALSE_FALLBACK`
- **Line**: BRepLib.cxx:1636  **Axis**: `healer-state`
- **Brief**: If goodpc=false (curve rejected), mark entire edge as not SameParameter.
- **Falsifiable claim**: Without rejection propagation, single bad curve would not fail overall healing; setting IsSameP=false propagates rejection to tolerance adjustment logic. To test: goodpc=false implies IsSameP=false.
- **Minimal reproducer**: 2D curve marked goodpc=false (e.g., EvalTol rejection). Expected: IsSameP set to false, triggering OCC5898 tolerance relaxation. Incorrect: ignore goodpc, proceed as if all curves ok.
- **Search anchors**: 'rejection propagation', 'goodpc false', 'overall status'

##### `BRepLib.SameParameter.TOLERANCE_RELAXATION_OCC5898`
- **Line**: BRepLib.cxx:1642  **Axis**: `conformance-probe`
- **Brief**: OCC5898 tolerance relaxation: if healing failed but error <= edge_tolerance + curve_precisions, accept current state.
- **Falsifiable claim**: Without relaxation, edges with large intrinsic tolerances would fail even though 3D/2D mismatch is within tolerance budget. To test: error=0.02, edge_tol=0.01, precision=0.015; sum=0.025 >= error, heal succeeds.
- **Minimal reproducer**: Edge with tolerance 0.01, 3D/2D mismatch error 0.02, curve precision 0.015. CurTol=0.025 >= error=0.02. Expected: IsSameP=true (within budget), maxdist=0.01 (use edge tolerance). Incorrect: fail, require tighter curves.
- **Search anchors**: 'OCC5898', 'tolerance relaxation', 'error within budget'

##### `BRepLib.SameParameter.TOLERANCE_REDUCTION`
- **Line**: BRepLib.cxx:1667  **Axis**: `healer-state`
- **Brief**: Reduce edge tolerance from initial value to computed maxdist (smallest mismatch across all curves).
- **Falsifiable claim**: Without reduction, edge retains coarse tolerance even after healing tightens it; reducing to maxdist documents actual precision achieved. To test: initial edge tolerance 0.1, computed maxdist 0.02; set to 0.02.
- **Minimal reproducer**: Edge with tolerance 0.1. After healing, maxdist=0.02 (tightest 3D/2D mismatch). Expected: aNTE->Tolerance(0.02). Incorrect: leave at 0.1, hide improvement.
- **Search anchors**: 'tolerance reduction', 'maxdist update', 'precision documentation'


### MergeSeq

#### `MergeSeq`
 (2 branches; source: `v3-deep-ShapeUpgrade_UnifySameDomain_MergeSeq_MergeSubSeq.json`)

##### `ShapeUpgrade_UnifySameDomain.MergeSeq.merge_edges_predicate_false`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2892  **Axis**: `healer-state`
- **Brief**: Early exit when MergeEdges() fails to find mergeable edge sequences.
- **Falsifiable claim**: Without this predicate check, the kernel would attempt to call myContext->Merge() on uninitialized or invalid subsequence structures. To test: pass an edge sequence containing geometrically identical but topologically non-mergeable edges; expect early false return without context corruption.
- **Minimal reproducer**: Construct an edge sequence containing two parallel coplanar lines with a gap between them but belonging to the same geometric surface (same geometry, different parameter domains). Invoke MergeSeq(). Without check: context enters inconsistent state. With check: returns false gracefully.
- **Search anchors**: 'MergeEdges', 'SeqOfSubsSeqOfEdges', 'if (MergeEdges'

##### `ShapeUpgrade_UnifySameDomain.MergeSeq.null_union_edge_skip`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2896  **Axis**: `healer-state`
- **Brief**: Skips Merge() call when UnionEdges is null, preventing context pollution.
- **Falsifiable claim**: Without this guard, myContext->Merge() would be called with null edges, causing memory access violation or silent state corruption in the context map. To test: construct a case where MergeEdges() initializes some subsequences but leaves UnionEdges as null; without guard, crash or silent corruption occurs.
- **Minimal reproducer**: Build edge sequence where MergeEdges() identifies mergeable groups but fails to construct a valid union edge for the first group (e.g., degenerate geometry). Invoke MergeSeq(). Without null-check: null pointer dereference in Merge(). With check: loop continues safely to next group.
- **Search anchors**: 'UnionEdges.IsNull', 'continue', 'SeqOfSubsSeqOfEdges(i).UnionEdges'


### MergeSubSeq

#### `MergeSubSeq`
 (22 branches; 1 low-confidence; source: `v3-deep-ShapeUpgrade_UnifySameDomain_MergeSeq_MergeSubSeq.json`)

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.degenerate_edge_pair_handler`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2184  **Axis**: `input-shape`
- **Brief**: Special path for merging chains of degenerate edges (zero-length in 3D but valid in 2D topology).
- **Falsifiable claim**: Without this branch, degenerate edge chains would fall through to 3D curve union logic, causing classification errors or incorrect closure detection. To test: pass chain of two degenerate edges on a face; without special handling, incorrect edge classification leads to wrong merge result.
- **Minimal reproducer**: Construct EDGE sequence with two consecutive degenerate edges (parameter equals null 3D curve, valid 2D curve on face). Edges lie on same face with valid 2D parameterization. Invoke MergeSubSeq(). Without special degenerate path: returns false or incorrect edge. With path: constructs correct 2D union edge with proper vertices and parameterization.
- **Search anchors**: 'BRep_Tool::Degenerated', 'FindClosestPoints', 'gp_Pnt2d', 'Degenerated(NewEdge, true)'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.degenerate_closest_points_failure`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2194  **Axis**: `kernel-pair`
- **Brief**: Aborts degenerate edge merging if FindClosestPoints() cannot locate common geometry.
- **Falsifiable claim**: Without this failure check, the method would proceed with uninitialized point arrays and face, leading to undefined 2D curve construction. To test: pass degenerate edges on disjoint faces with no common face in theVFmap; method should return false.
- **Minimal reproducer**: Two degenerate edges on different faces with no shared face relationship in the vertex-face map. Invoke merge path. Without check: reads garbage from uninitialized CommonFace, constructs invalid edge. With check: returns false immediately.
- **Search anchors**: '!FindClosestPoints', 'return false'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.degenerate_orientation_flip_logic`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2216  **Axis**: `encoding`
- **Brief**: Conditionally reverses start/end points of degenerate edge to maintain topology consistency.
- **Falsifiable claim**: Without this orientation-dependent swap, the unified degenerate edge would have inconsistent vertex-parameter associations, violating B-rep consistency. To test: chain of degenerate edges with reversed orientation; without swap, resulting edge has endpoints in wrong parameter positions.
- **Minimal reproducer**: Degenerate edge chain where first edge has REVERSED orientation and IndOnE1==0. Construct expected: swap should occur. Invoke merge. Without swap: vertex parameter updates at line 2230-2231 place vertices at incorrect parameter positions, violating B-rep invariants.
- **Search anchors**: 'OrOfE1OnFace == TopAbs_FORWARD', 'IndOnE1 == 1', 'gp_Pnt2d Tmp', 'swap'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.curve_null_validation`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2249  **Axis**: `conformance-probe`
- **Brief**: Rejects edge chains if 3D curves cannot be extracted, preventing invalid geometry operations.
- **Falsifiable claim**: Without this early null check, the method would attempt curve type classification (IsKind, downcast) on null handles, causing SIGSEGV. To test: edge with missing 3D curve in BRep structure; method should fail fast.
- **Minimal reproducer**: Construct edge with no 3D curve representation (pcurve-only edge, rare but valid in OCCT). Invoke MergeSubSeq on chain. Without null check: segmentation fault during IsKind() call. With check: returns false.
- **Search anchors**: 'c3d1.IsNull()', 'c3d2.IsNull()', 'return false'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.trimmed_curve_unwrap`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2254  **Axis**: `kernel-pair`
- **Brief**: Extracts basis curve from trimmed curve wrappers before geometric classification.
- **Falsifiable claim**: Without unwrapping trimmed curves, type classification (IsKind) would always fail (TrimmedCurve is not Line/Circle), causing false negatives in mergeability detection. To test: edge chain with trimmed line segments; without unwrap, method returns false even though base geometry is mergeable.
- **Minimal reproducer**: Edge sequence where both edges are TrimmedCurve wrappers around Geom_Line basis. Invoke MergeSubSeq(). Without unwrap: IsKind(Geom_Line) returns false, IsUnionOfLinesPossible stays false, method returns false. With unwrap: correctly identifies lines, merges.
- **Search anchors**: 'Geom_TrimmedCurve', 'BasisCurve', 'occ::down_cast'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.line_parallelism_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2268  **Axis**: `tolerance`
- **Brief**: Verifies parallel direction between consecutive lines in chain; non-parallel lines cannot merge.
- **Falsifiable claim**: Without this check, two skew lines with slightly different directions would pass mergeability validation, resulting in topologically invalid merged edge with discontinuous tangent. To test: two lines at angle > tolerance; method should reject merge.
- **Minimal reproducer**: Edge chain of two lines at 5-degree angle (myAngTol typically ~0.017 radians). Invoke MergeSubSeq(). Without angle check: IsUnionOfLinesPossible remains true, returns merged edge with kinked tangent. With check: sets flag false, rejects merge.
- **Search anchors**: '!aDir1.IsParallel', 'myAngTol', 'IsUnionOfLinesPossible = false'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_center_validation`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2283  **Axis**: `tolerance`
- **Brief**: Validates circle centers are coincident before attempting circle chain merge.
- **Falsifiable claim**: Without center check, two concentric circles with large radii would be rejected, but eccentric circles would pass, yielding merged edge with discontinuous curvature. To test: two circles with distinct centers; method should reject.
- **Minimal reproducer**: Two circle arcs: Circle1 center (0,0,0), Circle2 center (1e-3, 0, 0). Distance > Precision::Confusion(). Invoke MergeSubSeq(). Without check: IsUnionOfCirclesPossible stays true, invalid merge. With check: sets false, rejects.
- **Search anchors**: 'P01.Distance(P02)', 'Precision::Confusion', 'IsUnionOfCirclesPossible = false'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.both_possible_contradiction` **[low-confidence]**
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2293  **Axis**: `healer-state`
- **Brief**: Rejects merge if chain validates as both line-mergeable and circle-mergeable (logically inconsistent).
- **Falsifiable claim**: Without contradiction check, chain would proceed to line-merge logic, ignoring that loop validated circle compatibility too. This indicates broken chain assumptions (should be purely lines or circles). To test: fabricate edge with both line and circle properties.
- **Minimal reproducer**: Synthetically impossible: chain where all loop iterations set IsUnionOfLinesPossible=true AND all set IsUnionOfCirclesPossible=true. Invoke merge. Without guard: line-merge proceeds on data that should fail both. With guard: returns false, signaling data corruption.
- **Search anchors**: 'IsUnionOfLinesPossible && IsUnionOfCirclesPossible', 'return false'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.safe_input_mode_vertex_recording`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2307  **Axis**: `api-contract`
- **Brief**: In safe mode, replaces unrec orded vertices in context before updating edge parameterization.
- **Falsifiable claim**: Without safe-mode vertex normalization, vertices shared across multiple edges would cause context state inconsistency when UpdateVertex() is called separately per edge. To test: chain with shared start/end vertex; in unsafe mode after merge, vertex parameter is ambiguous.
- **Minimal reproducer**: Two collinear edges sharing endpoint V. Set mySafeInputMode=true. Invoke MergeSubSeq(). Without context recording: V remains unmapped; UpdateVertex() calls at 2330-2331 update vertices that share identity, causing parametric conflict. With safe mode: vertices replaced with copies, independent updates work.
- **Search anchors**: 'mySafeInputMode', 'myContext->IsRecorded', 'EmptyCopied', 'myContext->Replace'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.zero_length_line_construction`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2323  **Axis**: `input-shape`
- **Brief**: Constructs line from point pair; zero-distance pair yields degenerate line.
- **Falsifiable claim**: If PV1 equals PV2 (collapsed chain), resulting line has zero length, violating B-rep constraints (edge requires distinct vertices). To test: pass chain of edges all at same location; method should fail or produce invalid edge.
- **Minimal reproducer**: Two edges that geometrically collapse to a single point (both edges at same location on surface). Invoke MergeSubSeq(). Line created with gp_Ax1(PV1, Vec) where Vec=(0,0,0); TrimmedCurve(L, 0, 0). Result is degenerate edge. Should validate dist > tolerance before construction.
- **Search anchors**: 'gp_Line(gp_Ax1(PV1, Vec))', 'PV1.Distance(PV2)', 'new Geom_TrimmedCurve'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_closed_chain_identity`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2353  **Axis**: `conformance-probe`
- **Brief**: Detects closed circle chains where start/end vertices are topologically identical.
- **Falsifiable claim**: Without IsSame check, nearly-closed chains (vertices at same spatial location but different topological identity) would be treated as open chains, producing arc instead of full circle. To test: chain where first vertex equals last vertex spatially but are different TopoDS objects.
- **Minimal reproducer**: Circle arc chain: V0 -> ... -> V1 where V0.IsSame(V1)=true (same vertex object). Invoke MergeSubSeq(). With IsSame: isClosed=true, creates full circle. Without: requires spatial distance check fallback (lines 2358-2366).
- **Search anchors**: 'bool isClosed = V[0].IsSame(V[1])', 'if (!isClosed)'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_spatial_closure_tolerance`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2360  **Axis**: `tolerance`
- **Brief**: Fallback closure detection using spatial distance and per-vertex tolerance, overriding topological identity.
- **Falsifiable claim**: Without tolerance-aware spatial check, chain with non-identical but nearby vertices would be treated as open chain. Tolerance threshold ensures closure is respected at precision limit. To test: vertices at different identities but within tolerance distance.
- **Minimal reproducer**: Circle arc: V0, ..., V1 where V0.IsSame(V1)=false but Pnt(V0).Distance(Pnt(V1)) = 1e-8. myTolerance=1e-7. Invoke MergeSubSeq(). Without spatial check: open chain, returns partial arc. With check: isClosed=true, returns full circle.
- **Search anchors**: 'aP0.SquareDistance(aP1)', 'aTol * aTol', 'isClosed = true', 'std::max(BRep_Tool::Tolerance'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_closed_orientation_consistency`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2375  **Axis**: `encoding`
- **Brief**: Normalizes edge orientation based on underlying curve parameterization for closed circle chains.
- **Falsifiable claim**: Without orientation normalization, reversed edges would compute inverted parameter ranges, producing circle with backwards parameterization. To test: reversed circle edge in chain; without check, resulting merged circle has opposite winding.
- **Minimal reproducer**: Closed circle chain where first edge has TopAbs_REVERSED orientation. Invoke closed-chain path (line 2369). Without orientation check: FP/LP computed as reversed interval, resulting circle parameterization is backwards. With check: normalized to forward range.
- **Search anchors**: 'FE.Orientation() == TopAbs_FORWARD', 'adef.FirstParameter()', 'adef.LastParameter()'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_closed_full_circle_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2385  **Axis**: `kernel-pair`
- **Brief**: Uses full original circle if first point is at parameter zero; otherwise reconstructs circle through three points.
- **Falsifiable claim**: Without zero-parameter check, all closed chains would reconstruct circle geometry, potentially introducing numerical drift. When chain starts at parameter 0, original circle is already correct and should be reused. To test: full circle at parameter 0; reuse should preserve geometry.
- **Minimal reproducer**: Full circle edge with parameter range [0, 2π]. First parameter FP ≈ 0. Invoke closed path. Without zero-check: always calls GC_MakeCircle (line 2394), reconstructs geometry. With check: reuses Cir directly, preserving original NURBS representation if applicable.
- **Search anchors**: 'std::abs(FP) < Precision::PConfusion()', 'B.MakeEdge(E, Cir, Precision::Confusion())', 'GC_MakeCircle'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_closed_reconstruction_failure`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2395  **Axis**: `conformance-probe`
- **Brief**: Aborts closed-chain merge if circle reconstruction from three points fails.
- **Falsifiable claim**: Without failure check, MC1.Value() would be called on invalid object, returning garbage circle or crashing. To test: three collinear points on closed chain; GC_MakeCircle fails, method should abort.
- **Minimal reproducer**: Degenerate closed chain with three collinear points (impossible circle). Invoke closed path. Without check: MC1.IsDone()=false, but code calls MC1.Value() anyway (line 2397), undefined behavior. With check: returns false immediately.
- **Search anchors**: 'if (MC1.IsDone())', 'else { return false; }'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_open_chain_parameter_safety`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2432  **Axis**: `tolerance`
- **Brief**: Clamps arc angle span to 7π/8 to avoid ambiguous parameterization in circle construction.
- **Falsifiable claim**: Without angle clamping, large arcs (>π radians) on open chains could produce ambiguous circle parameterization. Constraining to <7π/8 ensures unique point triple for circle reconstruction. To test: arc > π; without clamp, incorrect circle axis.
- **Minimal reproducer**: Open circle arc spanning 150° (2.62 radians). ParamLast-ParamFirst ≈ 2.62. Invoke open path. Without loop (line 2432): uses all three points, may produce circle with different axis due to ambiguity. With loop: repeatedly bisects until span < 7π/8, ensures stable reconstruction.
- **Search anchors**: 'while (std::abs(ParamLast - ParamFirst) > 7 * M_PI / 8)', 'ParamLast = (ParamFirst + ParamLast) / 2'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_open_safe_input_vertex_replication`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2414  **Axis**: `api-contract`
- **Brief**: In safe mode, replaces vertices in context before updating open-circle parameterization, mirroring line-merge logic.
- **Falsifiable claim**: Without safe-mode replication for open circles, shared vertices cause context inconsistency when different edges assign different parameters to the same vertex object. To test: shared vertex between chain and other geometry; without safe mode, vertex parameter is ambiguous post-merge.
- **Minimal reproducer**: Open circle arc sharing start vertex V0 with another edge. mySafeInputMode=true. Invoke open path (line 2408). Without replication: V0 stays unmapped; B.UpdateVertex at line 2456 assigns it one parameter, conflicting with other edge. With replication: V0 replaced with copy, independent parameterization.
- **Search anchors**: 'mySafeInputMode', 'myContext->IsRecorded(V[k])', 'EmptyCopied', 'myContext->Apply'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_open_bisection_parameter_selection`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2434  **Axis**: `kernel-pair`
- **Brief**: Bisects parameter range to find stable intermediate point for circle reconstruction on open arcs.
- **Falsifiable claim**: Without bisection, original ParamLast might be > 7π/8 away from ParamFirst, causing GC_MakeCircle to fail or produce wrong circle. Bisection ensures three well-spaced points define unique circle. To test: large arc; without bisection, reconstruction fails.
- **Minimal reproducer**: Open arc with span 3.2 radians (183°). ParamLast = 3.2, ParamFirst ≈ 0. Invoke open path. Without bisection: loop doesn't execute, three points used directly with suboptimal spacing. With bisection: ParamLast → 1.6, then → 0.8, until stable range achieved.
- **Search anchors**: 'ParamLast = (ParamFirst + ParamLast) / 2', 'adef.Value((FP + LP) * 0.5)', 'GC_MakeCircle'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_open_angle_normalization`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2447  **Axis**: `encoding`
- **Brief**: Normalizes computed arc angle to [0, 2π) range, handling negative angles and ensuring consistent parameterization.
- **Falsifiable claim**: Without normalization, negative angles would be passed to TrimmedCurve constructor, producing backwards-parameterized edge. To test: open arc crossing angle discontinuity; without normalization, lpar < 0, invalid range.
- **Minimal reproducer**: Open circle arc where end point has angle -30° relative to start (e.g., start 350°, end 20° in circle parameter). Invoke open path, line 2446: Dir1.AngleWithRef() returns negative value. Without add-2π: TrimmedCurve(Circle, 0, negative) is invalid. With add: lpar becomes positive.
- **Search anchors**: 'Dir1.AngleWithRef(DirLastInChain, Vdir)', 'if (lpar < 0.)', 'lpar += 2 * M_PI'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.bspline_concatenation_guard`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2463  **Axis**: `api-contract`
- **Brief**: Gates B-spline/Bezier concatenation to chains > 1 edge and myConcatBSplines flag enabled.
- **Falsifiable claim**: Without length and flag checks, single-edge chains would attempt unnecessary B-spline operations, and disabled B-spline mode would still invoke GlueEdgesWith3DCurves. To test: single-edge chain with myConcatBSplines=true; should not attempt concatenation.
- **Minimal reproducer**: Single B-spline edge (chain.Length()=1) with myConcatBSplines=true. Invoke merge. Without length check: NeedUnion loop executes once, line 2496 calls GlueEdgesWith3DCurves on single edge (unnecessary). With check: skips entire B-spline block.
- **Search anchors**: 'theChain.Length() > 1', 'myConcatBSplines', 'if (NeedUnion)'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.bspline_type_screening`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2472  **Axis**: `conformance-probe`
- **Brief**: Iterates chain to verify all edges are B-spline or Bezier curves before attempting concatenation.
- **Falsifiable claim**: Without type screening, mixed-curve chains (e.g., line + B-spline) would invoke GlueEdgesWith3DCurves, which expects B-spline compatible geometry, causing incorrect merge. To test: chain with mixed types; without check, GlueEdges produces wrong result.
- **Minimal reproducer**: Two-edge chain: first is Geom_Line, second is Geom_BSplineCurve. Invoke merge with myConcatBSplines=true. Without screening: NeedUnion stays true, GlueEdgesWith3DCurves called on mixed geometry, incorrect result. With screening: NeedUnion=false at line 2491, block skips, returns false.
- **Search anchors**: 'Geom_BSplineCurve', 'Geom_BezierCurve', 'NeedUnion = false', 'break'

##### `ShapeUpgrade_UnifySameDomain.MergeSubSeq.bspline_null_curve_skip`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:2477  **Axis**: `conformance-probe`
- **Brief**: Skips pcurve-only edges (null 3D curves) during B-spline type verification.
- **Falsifiable claim**: Without null skip, pcurve-only edges would fail IsKind() checks, prematurely setting NeedUnion=false and rejecting valid B-spline chains with some pcurve-only members. To test: B-spline + pcurve-only edge; without skip, type check fails.
- **Minimal reproducer**: Chain: B-spline edge + pcurve-only edge (valid on face). myConcatBSplines=true. Invoke merge. Without skip: BRep_Tool::Curve() returns null, line 2486 IsKind() fails on null, NeedUnion=false, concatenation skipped. With skip: null edges ignored, valid B-splines checked.
- **Search anchors**: 'if (c3d.IsNull())', 'continue'


### ShapeAnalysis_ShapeTolerance

#### `ShapeAnalysis_ShapeTolerance.InTolerance`
 (6 branches; source: `v3-deep-ShapeAnalysis_ShapeTolerance_InTolerance.json`)

##### `ShapeAnalysis_ShapeTolerance.InTolerance.face_tolerance_filtering`
- **Line**: ShapeAnalysis_ShapeTolerance.cxx:107-117  **Axis**: `tolerance`
- **Brief**: FACE iteration: filters faces by tolerance range [valmin, valmax], appending matching ones to result sequence.
- **Falsifiable claim**: Without this branch, no faces would be collected in InTolerance result. To test: call InTolerance(shape_with_faces, 0.001, 0.002, TopAbs_FACE) and verify returned sequence contains faces with tol in [0.001, 0.002].
- **Minimal reproducer**: Construct a shape with two faces: one with tolerance 0.0015 (in-range) and one with 0.003 (out-of-range). Call InTolerance(shape, 0.001, 0.002, TopAbs_FACE). Without branch: empty result. With branch: returns only the 0.0015-tolerance face.
- **Search anchors**: 'BRep_Tool::Tolerance(TopoDS::Face', 'TopAbs_FACE', 'tol >= valmin && (over || (tol <= valmax))'

##### `ShapeAnalysis_ShapeTolerance.InTolerance.edge_tolerance_filtering`
- **Line**: ShapeAnalysis_ShapeTolerance.cxx:119-129  **Axis**: `tolerance`
- **Brief**: EDGE iteration: filters edges by tolerance range [valmin, valmax], appending matching ones to result sequence.
- **Falsifiable claim**: Without this branch, no edges would be collected in InTolerance result. To test: call InTolerance(shape_with_edges, 0.001, 0.002, TopAbs_EDGE) and verify returned sequence contains edges with tol in [0.001, 0.002].
- **Minimal reproducer**: Construct a shape with two edges: one with tolerance 0.0015 (in-range) and one with 0.005 (out-of-range). Call InTolerance(shape, 0.001, 0.002, TopAbs_EDGE). Without branch: empty result. With branch: returns only the 0.0015-tolerance edge.
- **Search anchors**: 'BRep_Tool::Tolerance(TopoDS::Edge', 'TopAbs_EDGE', 'tol >= valmin && (over || (tol <= valmax))'

##### `ShapeAnalysis_ShapeTolerance.InTolerance.vertex_tolerance_filtering_BUGGY`
- **Line**: ShapeAnalysis_ShapeTolerance.cxx:131-141  **Axis**: `tolerance`
- **Brief**: VERTEX iteration uses inverted comparison (tol >= valmax) instead of (tol <= valmax), breaking tolerance range semantics.
- **Falsifiable claim**: VERTEX case with inverted comparison returns wrong vertices. To test: call InTolerance(shape_with_vertices, 0.001, 0.002, TopAbs_VERTEX) and observe it returns vertices with tol >= 0.002 instead of tol <= 0.002, contradicting FACE/EDGE behavior.
- **Minimal reproducer**: Construct a shape with two vertices: one with tolerance 0.0015 (should be in-range) and one with 0.005 (should be out-of-range). Call InTolerance(shape, 0.001, 0.002, TopAbs_VERTEX). Expected: returns only 0.0015 vertex. Actual (buggy): returns only 0.005 vertex due to tol >= valmax inverted check.
- **Search anchors**: 'tol >= valmax', 'TopAbs_VERTEX', 'BRep_Tool::Tolerance(TopoDS::Vertex'

##### `ShapeAnalysis_ShapeTolerance.InTolerance.shell_face_recursion`
- **Line**: ShapeAnalysis_ShapeTolerance.cxx:143-173  **Axis**: `input-shape`
- **Brief**: SHELL iteration: recursively filters faces within each shell using tolerance criteria, collecting matching shells and faces.
- **Falsifiable claim**: Without this branch, shells would never be in result. To test: call InTolerance on a shape with shell-organized faces, verifying shells containing in-range-tolerance faces appear in result.
- **Minimal reproducer**: Construct a shape with a shell containing a face with tolerance 0.0015. Call InTolerance(shape, 0.001, 0.002, TopAbs_SHELL). Without branch: empty result. With branch: returns shell and its in-range face.
- **Search anchors**: 'TopAbs_SHELL', 'mapface', 'iashell', 'Exploration des shells'

##### `ShapeAnalysis_ShapeTolerance.InTolerance.shell_free_face_filtering`
- **Line**: ShapeAnalysis_ShapeTolerance.cxx:175-207  **Axis**: `input-shape`
- **Brief**: SHELL mode: post-processes free (non-shell-bound) faces by tolerance, or recursively includes them if any child edges/vertices match.
- **Falsifiable claim**: Without this branch, free faces in shell mode would be missed. To test: call InTolerance with TopAbs_SHELL on a shape with free faces; verify free in-range-tolerance faces appear in result.
- **Minimal reproducer**: Construct a shape with a free face (not in any shell) with tolerance 0.0015, plus edges in that face with in-range tolerance. Call InTolerance(shape, 0.001, 0.002, TopAbs_SHELL). Without branch: free face omitted. With branch: free face included if tol in-range or contains in-range edges/vertices.
- **Search anchors**: 'Les faces (libres ou sous shell)', 'mapface.Contains', 'iaface'

##### `ShapeAnalysis_ShapeTolerance.InTolerance.SUSPECTED_BUG`
- **Line**: ShapeAnalysis_ShapeTolerance.cxx:140  **Axis**: `?`
- **Brief**: Confirmed OCCT source bug: VERTEX case uses inverted comparison vs other shape types.


### ShapeAnalysis_Wire

#### `ShapeAnalysis_Wire.CheckLoop`
 (12 branches; source: `v3-deep-ShapeAnalysis_Wire_CheckLoop.json`)

##### `ShapeAnalysis_Wire.CheckLoop.unloaded-or-trivial-wire`
- **Line**: ShapeAnalysis_Wire.cxx:2236  **Axis**: `api-contract`
- **Brief**: Method returns false without analysis if wire is unloaded or contains fewer than 2 edges.
- **Falsifiable claim**: Without this branch, the kernel would attempt multi-vertex loop detection on degenerate wires (0-1 edges), causing array access errors or false positives in trivial cases. To test: call CheckLoop on a wire with 1 edge; without the guard, it would incorrectly report loops.
- **Minimal reproducer**: Create a wire with a single edge connecting vertices V1->V2. Call CheckLoop with empty maps. Expected: returns false immediately. Without guard: would iterate and incorrectly classify single-edge wire as a loop if V1==V2.
- **Search anchors**: 'IsLoaded()', 'NbEdges() < 2'

##### `ShapeAnalysis_Wire.CheckLoop.null-vertices`
- **Line**: ShapeAnalysis_Wire.cxx:2245  **Axis**: `kernel-pair`
- **Brief**: Method encodes FAIL2 status and returns false if any edge lacks start or end vertex.
- **Falsifiable claim**: Without this null check, the kernel would dereference null vertex pointers when calling IsSame() and BRep_Tool::Tolerance(), causing segmentation faults or undefined behavior. To test: inject a degenerate edge with null v1 or v2; without: crash.
- **Minimal reproducer**: Construct edge with null V1 or V2 via BRep_Builder. Add to wire. Call CheckLoop. Expected: detects null, returns false with FAIL2 status. Without: dereferences null on IsSame() call.
- **Search anchors**: 'aV1.IsNull()', 'aV2.IsNull()'

##### `ShapeAnalysis_Wire.CheckLoop.seam-edge-classification`
- **Line**: ShapeAnalysis_Wire.cxx:2250  **Axis**: `conformance-probe`
- **Brief**: Seam edges are separated into aMapSeemEdges and excluded from loop detection logic.
- **Falsifiable claim**: Without distinguishing seam edges, the kernel would incorrectly count seam edge endpoints as multi-vertex loop candidates. Seams represent the same parametric edge on both sides of a surface; counting them falsely inflates vertex degree. To test: wire with seam edge at V1; without: V1.Extent()>2 triggers false loop.
- **Minimal reproducer**: Create a wire on a closed surface (e.g., cylinder) with one regular edge E1 and one seam edge S at shared vertex V. E1 connects V->V (degenerate loop). Call CheckLoop. Expected: S is excluded, V loops only on E1. Without seam filter: Extent()=3 (S counted twice + E1), triggers spurious loop detection.
- **Search anchors**: 'myWire->IsSeam(i)', 'aMapSeemEdges.Add(aedge)'

##### `ShapeAnalysis_Wire.CheckLoop.degenerated-edge-filter`
- **Line**: ShapeAnalysis_Wire.cxx:2253  **Axis**: `healer-state`
- **Brief**: Degenerated edges are added to aMapSmallEdges and excluded from loop degree count.
- **Falsifiable claim**: Without filtering degenerated edges, the kernel would count geometrically zero-length edges as real loop participants, inflating vertex degree. A degen edge nominally connects V->V but carries no geometric content. To test: wire with 1 degen edge + 1 regular edge at V; without: V.Extent()=3, spurious loop.
- **Minimal reproducer**: Create degenerated edge (e.g., edge with same 3D point for start/end but valid 2D pcurve). Wire has degen + regular edge both at vertex V. Call CheckLoop. Expected: degen filtered, V.Extent()=1. Without filter: Extent()=3 (degen double-counted + regular), false loop.
- **Search anchors**: 'BRep_Tool::Degenerated(aedge)', 'aMapSmallEdges.Add(aedge)'

##### `ShapeAnalysis_Wire.CheckLoop.self-loop-small-edge`
- **Line**: ShapeAnalysis_Wire.cxx:2256  **Axis**: `tolerance`
- **Brief**: Self-loop edges (V1==V2) below tolerance are classified as small and excluded.
- **Falsifiable claim**: Without CheckSmall() filtering, the kernel would count small self-loop edges (V1==V2, length<<tol) as real loop participants, defeating small-edge removal logic. To test: create V1 with tol=0.1, edge V1->V1 of length 0.05; without: counted in Extent().
- **Minimal reproducer**: Create vertex V1 with tolerance 0.1. Add edge E of length 0.05 connecting V1->V1 (CheckSmall returns true). Wire has E + regular edge at V1. Call CheckLoop. Expected: E filtered, V1 not flagged as loop. Without CheckSmall filter: E counted, Extent()=3, spurious loop.
- **Search anchors**: 'isSame && CheckSmall(i, BRep_Tool::Tolerance(aV1))'

##### `ShapeAnalysis_Wire.CheckLoop.self-loop-binding`
- **Line**: ShapeAnalysis_Wire.cxx:2272  **Axis**: `kernel-pair`
- **Brief**: For self-loop edges (V1==V2), the edge is appended twice to aMapVertexEdges[V1] list.
- **Falsifiable claim**: Without double-append for self-loops, the kernel would undercount degree at self-loop vertices, failing to detect multi-vertex situations. Semantically, V1==V2 edge contributes 2 to degree (out and in); single append loses this. To test: V1 with two self-loop edges; without double-append: only 2 edges in list, extent=2, no loop detection.
- **Minimal reproducer**: Create two self-loop edges E1, E2 both on vertex V1 (E1 and E2 connect V1->V1). Wire has E1, E2. Call CheckLoop. Expected: V1.list=[E1,E1,E2,E2], Extent()=4, isMultiVertex returns true, V1 marked as loop. Without double-append: Extent()=2, isMultiVertex returns false, V1 not flagged.
- **Search anchors**: 'if (isSame)', 'alshape.Append(aedge);', 'alshape.Append(aedge);'

##### `ShapeAnalysis_Wire.CheckLoop.multi-vertex-self-loop-check`
- **Line**: ShapeAnalysis_Wire.cxx:2280  **Axis**: `conformance-probe`
- **Brief**: For self-loop edges, after append, if extent>2 and isMultiVertex passes, vertex added to loop map.
- **Falsifiable claim**: Without this branch, the kernel would fail to detect multi-vertex loops on self-loop edges. A vertex with multiple self-loops (each appended twice) forms a real topological loop. Omitting branch leaves self-loop multi-vertex cases undetected. To test: 3 self-loops at V1; without: V1 not added to aMapLoopVertices.
- **Minimal reproducer**: Create 3 self-loop edges E1, E2, E3 all at V1. After append, V1.list has 6 entries, Extent()=6. Call CheckLoop. Expected: isMultiVertex(6 - skipped)>2 returns true, V1 added to aMapLoopVertices. Without branch: V1 never added, false negative.
- **Search anchors**: 'alshape.Extent() > 2 && isMultiVertex(alshape', 'aMapLoopVertices.Add(aV1)'

##### `ShapeAnalysis_Wire.CheckLoop.dual-vertex-binding`
- **Line**: ShapeAnalysis_Wire.cxx:2290  **Axis**: `kernel-pair`
- **Brief**: For non-self-loop edges, both start (aV1) and end (aV2) vertices get the edge appended.
- **Falsifiable claim**: Without appending to both V1 and V2, the kernel would undercount degree at one endpoint, missing multi-vertex detection. Each edge nominally increases degree of both endpoints by 1. To test: edge V1->V2 in wire with multiple edges at V2; without appending to aV2: V2.Extent() is 1 short.
- **Minimal reproducer**: Create wire with edges E1(V1->V2), E2(V2->V3), E3(V2->V1). For V2: expected list=[E1,E2,E3], Extent()=3. Call CheckLoop. Expected: V2 added to loop map as multi-vertex. Without appending aV2: V2.list=[E1,E3], Extent()=2, V2 not detected as multi-vertex.
- **Search anchors**: 'else {', 'NCollection_List<TopoDS_Shape>& alshape = aMapVertexEdges.ChangeFind(aV1);', 'alshape2'

##### `ShapeAnalysis_Wire.CheckLoop.multi-vertex-v1-check`
- **Line**: ShapeAnalysis_Wire.cxx:2292  **Axis**: `conformance-probe`
- **Brief**: For non-self-loop edges, aV1 is added to loop map if its extent>2 after append.
- **Falsifiable claim**: Without this check, vertices with degree>2 (multi-vertex) in non-self-loop edges would not be flagged. A vertex with >2 distinct edges is topologically exceptional (loop or multiplicity issue). To test: V1 with 3+ distinct edges; without: V1 not marked as loop vertex.
- **Minimal reproducer**: Create wire with edges E1(V0->V1), E2(V1->V2), E3(V1->V3). V1.Extent()=3 after appends. Call CheckLoop. Expected: isMultiVertex returns true, V1 added to aMapLoopVertices. Without check: V1 remains in map, no action taken on multi-vertex condition.
- **Search anchors**: 'alshape.Extent() > 2 && isMultiVertex(alshape, aMapSmallEdges, aMapSeemEdges)', 'aMapLoopVertices.Add(aV1);'

##### `ShapeAnalysis_Wire.CheckLoop.multi-vertex-v2-check`
- **Line**: ShapeAnalysis_Wire.cxx:2298  **Axis**: `conformance-probe`
- **Brief**: For non-self-loop edges, aV2 is added to loop map if its extent>2 after append.
- **Falsifiable claim**: Without this check, the end vertex of non-self-loop edges would not be evaluated for multi-vertex conditions, asymmetrically missing loop vertices. Start vertex (V1) is checked, so end vertex (V2) must also be. To test: V2 with 3+ incident edges; without: V2 not flagged.
- **Minimal reproducer**: Create wire with edges E1(V0->V2), E2(V1->V2), E3(V2->V3). V2.Extent()=3. Call CheckLoop. Expected: isMultiVertex(3 non-skipped)>2 returns true, V2 added to aMapLoopVertices. Without check: V2 silently skipped, loop vertex missed.
- **Search anchors**: 'alshape2.Extent() > 2 && isMultiVertex(alshape2, aMapSmallEdges, aMapSeemEdges)', 'aMapLoopVertices.Add(aV2);'

##### `ShapeAnalysis_Wire.CheckLoop.precision-save-restore`
- **Line**: ShapeAnalysis_Wire.cxx:2239  **Axis**: `healer-state`
- **Brief**: Method saves original precision, sets it to Infinite during analysis, then restores it afterward.
- **Falsifiable claim**: Without precision save/restore, the kernel would leave myPrecision at Infinite() after CheckLoop, affecting all subsequent geometry tolerance checks (edge length, vertex closeness). To test: call CheckLoop, then CheckSmall; without restore: all subsequent checks use Infinite precision.
- **Minimal reproducer**: Set wire precision to 0.01. Call CheckLoop. Then call CheckSmall(i, 0.01). Expected: myPrecision reverted to 0.01 before CheckSmall runs, tolerance checks work correctly. Without restore: myPrecision=Infinite, CheckSmall always returns false (infinite tolerance >> any edge length).
- **Search anchors**: 'double aSavPreci = Precision();', 'SetPrecision(Precision::Infinite());', 'SetPrecision(aSavPreci);'

##### `ShapeAnalysis_Wire.CheckLoop.status-encoding`
- **Line**: ShapeAnalysis_Wire.cxx:2306  **Axis**: `api-contract`
- **Brief**: Method sets myStatus to ShapeExtend_DONE1 and ORs it into myStatusLoop if loops are found.
- **Falsifiable claim**: Without status encoding, the caller would not know whether loop detection succeeded or failed, and would not have persistent record in myStatusLoop. Status encodes correctness for FixWire chains. To test: call CheckLoop on wire with loop; without: myStatus unchanged, loop result unrecorded.
- **Minimal reproducer**: Create multi-vertex wire. Call CheckLoop. Expected: myStatus=ShapeExtend_DONE1, myStatusLoop |= DONE1. Caller queries myStatusLoop and proceeds with FixLoop. Without encoding: myStatus remains OK or FAIL, caller skips FixLoop.
- **Search anchors**: 'myStatus = ShapeExtend::EncodeStatus(ShapeExtend_DONE1);', 'myStatusLoop |= myStatus;'


### ShapeFix_Edge

#### `ShapeFix_Edge.FixAddPCurve`
 (11 branches; source: `v3-deep-ShapeFix_Edge_FixAddPCurve.json`)

##### `ShapeFix_Edge.FixAddPCurve.existing_pcurve_shortcut`
- **Line**: ShapeFix_Edge.cxx:470  **Axis**: `healer-state`
- **Brief**: Early return if PCurve already exists prevents re-projection and redundant state mutations.
- **Falsifiable claim**: Without this check, the kernel would attempt to project and register a new PCurve even when one is already associated with the edge on the surface, potentially duplicating or corrupting the PCurve list via BRep_Builder::UpdateEdge. To test: provide an edge with an existing PCurve on a given face; without the guard, the edge's PCurve would be overwritten or multiplied.
- **Minimal reproducer**: Create a TopoDS_Edge with a 3D curve and an existing PCurve on a cylindrical surface. Call FixAddPCurve(edge, face, false, 0.01). Without the guard: edge PCurves are reprojected and duplicated. With the guard: edge PCurves unchanged, method returns false immediately.
- **Search anchors**: 'HasPCurve', 'IsSeam', 'early return'

##### `ShapeFix_Edge.FixAddPCurve.plane_surface_no_op`
- **Line**: ShapeFix_Edge.cxx:478  **Axis**: `kernel-pair`
- **Brief**: Explicit no-op for planar surfaces avoids wasteful projection since planar PCurves are trivial.
- **Falsifiable claim**: Without this guard, the kernel would invoke the full projection pipeline on planar surfaces, which is numerically redundant (any line in 3D space projects to a line in 2D with known parametrization). To test: provide an edge on a planar face and verify no projection is triggered.
- **Minimal reproducer**: Construct a rectangular planar face (Geom_Plane) and an edge lying on it. Call FixAddPCurve(edge, planarFace, false, prec). Without the guard: myProjector->Perform() called wastefully. With the guard: method returns false, no projection occurs.
- **Search anchors**: 'Geom_Plane', 'planar', 'early return'

##### `ShapeFix_Edge.FixAddPCurve.missing_3d_curve_fail`
- **Line**: ShapeFix_Edge.cxx:497  **Axis**: `api-contract`
- **Brief**: Handles degenerate edge case where 3D curve is absent, blocking projection with explicit error.
- **Falsifiable claim**: Without this check, the kernel would attempt to project a null 3D curve, leading to a downstream segfault or undefined projection result. To test: create an edge without a 3D curve; the method must fail gracefully.
- **Minimal reproducer**: Construct a TopoDS_Edge without a 3D curve representation (e.g., a degenerate edge). Call FixAddPCurve(edge, surface, false, prec). Without the guard: null pointer dereference in myProjector->Perform. With the guard: method returns false and sets FAIL1 status.
- **Search anchors**: 'c3d.IsNull', 'FAIL1', 'missing 3D curve'

##### `ShapeFix_Edge.FixAddPCurve.pcurve_projection_with_tolerances`
- **Line**: ShapeFix_Edge.cxx:515  **Axis**: `tolerance`
- **Brief**: Projection respects vertex tolerances to ensure PCurve endpoints align within acceptable deviation.
- **Falsifiable claim**: Without carrying vertex tolerances (TolFirst, TolLast) into myProjector->Perform, the kernel would project the PCurve without respecting the spatial slack at edge endpoints, potentially creating PCurves that deviate from vertices beyond the acceptable tolerance cone. To test: provide an edge with high vertex tolerance and verify projected PCurve endpoints are constrained.
- **Minimal reproducer**: Create a toroidal surface and an edge with high endpoint tolerances (e.g., 0.1). Construct vertices with TolFirst=0.1, TolLast=0.1. Call FixAddPCurve(edge, toroidalSurf, false, prec). Without tolerance propagation: PCurve endpoints may project outside the tolerance cones. With it: PCurve constrained to vertex tolerance envelopes.
- **Search anchors**: 'TolFirst', 'TolLast', 'Perform', 'vertex tolerance'

##### `ShapeFix_Edge.FixAddPCurve.seam_u_closed_translation`
- **Line**: ShapeFix_Edge.cxx:545  **Axis**: `healer-state`
- **Brief**: For U-closed (but not V-closed) surfaces, seam PCurve is offset by U-parameter range to create distinct representations.
- **Falsifiable claim**: Without this translation, the kernel would register two identical PCurves on a U-closed seam (e.g., a cylindrical surface seam), causing the double-covering representation to collapse to a single curve and corrupting seam topology. To test: verify that dual PCurves differ by exactly (ul - uf, 0) in parameter space.
- **Minimal reproducer**: Construct a cylindrical surface (U-closed, V-open) with a seam edge aligned to the seam parameter U=0. Call FixAddPCurve(edge, cylinderFace, true, prec). Without translation: both PCurves identical, seam topology broken. With translation: c2d2 translated by (ul-uf, 0), creating distinct forward and reverse PCurves.
- **Search anchors**: 'IsUClosed', 'Translate', 'seam', 'ProSTEP'

##### `ShapeFix_Edge.FixAddPCurve.seam_v_closed_translation`
- **Line**: ShapeFix_Edge.cxx:550  **Axis**: `healer-state`
- **Brief**: For V-closed (but not U-closed) surfaces, seam PCurve is offset by V-parameter range.
- **Falsifiable claim**: Without this translation for V-closed surfaces (e.g., conical surface seam), the kernel would fail to create distinct dual PCurves, resulting in incorrect seam representation and topology corruption. To test: verify translation by (0, vl - vf).
- **Minimal reproducer**: Construct a conical surface (V-closed, U-open) with a seam edge. Call FixAddPCurve(edge, conicalFace, true, prec). Without V-translation: both PCurves collapse. With it: c2d2 offset by (0, vl-vf), creating proper seam duality.
- **Search anchors**: 'IsVClosed', 'Translate', 'seam', 'cone'

##### `ShapeFix_Edge.FixAddPCurve.seam_on_doubly_closed_surface`
- **Line**: ShapeFix_Edge.cxx:553  **Axis**: `kernel-pair`
- **Brief**: For doubly-closed surfaces (both U and V closed, e.g., torus), seam PCurve translation delegates to TranslatePCurve to avoid naive parameter-space shifting that would produce topologically invalid seam.
- **Falsifiable claim**: Without TranslatePCurve for doubly-closed surfaces, the kernel would apply a simple parameter translation (e.g., (ul-uf, 0) or (0, vl-vf)), which would project the seam onto a wrong locus on the torus and corrupt the seam edge topology. The correct repair requires geometric analysis of the actual seam path on the doubly-periodic surface. To test: for a toroidal seam edge, verify that the dual PCurve is geometrically distinct and seam-conforming after healing, not merely parameter-shifted.
- **Minimal reproducer**: Construct a toroidal surface (both U and V closed). Create a seam edge aligned to the torus's seam curve (e.g., at U=0 or V=0 parameter, with endpoints at opposite poles). Call FixAddPCurve(edge, toroidalFace, true, prec). Without TranslatePCurve: c2d2 is naively translated by (ul-uf, 0), placing it on the wrong part of the torus's parameter space, breaking seam topology. With TranslatePCurve: the method reconstructs c2d2 geometrically, ensuring it follows the actual seam curve on the torus and maintains proper dual-covering semantics. Observation: check that the two PCurves on the torus correspond to the two halves of the seam in parameter space and in 3D both lie on the actual seam geometric locus.
- **Search anchors**: 'IsUClosed', 'IsVClosed', 'TranslatePCurve', 'Doublement fermee', 'tore'

##### `ShapeFix_Edge.FixAddPCurve.non_seam_single_pcurve`
- **Line**: ShapeFix_Edge.cxx:560  **Axis**: `healer-state`
- **Brief**: For non-seam edges, a single PCurve is registered without duplication or translation.
- **Falsifiable claim**: Without this non-seam branch, the kernel would attempt to create dual-PCurves for all edges, corrupting non-seam edge topology by falsely introducing a second PCurve. To test: verify that a non-seam edge receives exactly one PCurve.
- **Minimal reproducer**: Create a non-seam edge on a cylindrical surface (not at the seam). Call FixAddPCurve(edge, cylinder, false, prec). Without the non-seam branch: edge would incorrectly get two PCurves. With the branch: edge receives single PCurve via UpdateEdge(edge, c2d, ...).
- **Search anchors**: 'UpdateEdge', 'single PCurve', 'non-seam'

##### `ShapeFix_Edge.FixAddPCurve.curve3d_update_on_done3`
- **Line**: ShapeFix_Edge.cxx:567  **Axis**: `healer-state`
- **Brief**: If projector signals DONE3 (3D curve approximation occurred), the edge is updated with the new 3D curve.
- **Falsifiable claim**: Without this update, if the projector had to approximate the input 3D curve (DONE3 status), the edge would retain the original, potentially misaligned 3D curve, causing downstream mismatches between the original and projected PCurve. To test: provide a 3D curve that requires approximation; verify the new 3D curve is written.
- **Minimal reproducer**: Create an edge with a 3D curve that does not project cleanly (e.g., a very high-curvature spline). Call FixAddPCurve with a surface requiring reapproximation. If myProjector sets DONE3: the edge's 3D curve should be replaced. Without the update: edge retains original, misaligned curve. With it: edge updated with approximated curve.
- **Search anchors**: 'DONE3', 'UpdateEdge', 'Curve3d', 'approximation'

##### `ShapeFix_Edge.FixAddPCurve.exception_handling_fail2`
- **Line**: ShapeFix_Edge.cxx:577  **Axis**: `api-contract`
- **Brief**: Catch-all exception handler logs projection failure and sets FAIL2 status to signal healing abort.
- **Falsifiable claim**: Without exception handling, an unexpected numerical failure in projection (e.g., invalid surface, degenerate geometry) would crash the healer. With it, the method gracefully degrades and returns status FAIL2 to allow caller to decide next steps. To test: trigger an exception in myProjector->Perform (e.g., provide invalid surface).
- **Minimal reproducer**: Create a pathological surface (e.g., Geom_Surface subclass with NaN bounds). Call FixAddPCurve(edge, badSurface, false, prec). Without exception handling: process crashes. With it: exception caught, method returns false with FAIL2 status, healing continues on other edges.
- **Search anchors**: 'catch', 'FAIL2', 'exception', 'Standard_Failure'

##### `ShapeFix_Edge.FixAddPCurve.done1_invariant_success`
- **Line**: ShapeFix_Edge.cxx:583  **Axis**: `api-contract`
- **Brief**: Always sets DONE1 status on successful return to signal to caller that method executed.
- **Falsifiable claim**: Without this status, the caller cannot distinguish between 'method was not called' and 'method ran but found nothing to do'. The DONE1 flag ensures consistent state tracking for healing workflows. To test: verify myStatus includes DONE1 after method completes.
- **Minimal reproducer**: Call FixAddPCurve on any valid edge and surface. After return, check myStatus for ShapeExtend_DONE1 flag. Without invariant: status may be ambiguous. With it: status always contains DONE1 on completion.
- **Search anchors**: 'DONE1', 'status', 'invariant'


### ShapeFix_Face

#### `ShapeFix_Face.FixMissingSeam`
 (24 branches; 5 low-confidence; source: `v3-deep-ShapeFix_Face_FixMissingSeam.json`)

##### `ShapeFix_Face.FixMissingSeam.null-surface-guard`
- **Line**: ShapeFix_Face.cxx:1724  **Axis**: `kernel-pair`
- **Brief**: Guard against null surface pointer; returns false immediately if surface is not initialized.
- **Falsifiable claim**: Without this branch, null dereference would occur at line 1729 (mySurf->IsUClosed()). To test: pass face with uninitialized surface handle; without branch crashes with segfault; with branch returns false.
- **Minimal reproducer**: Construct empty TopoDS_Face with null mySurf. Call FixMissingSeam(). Without: null dereference. With: returns false.
- **Search anchors**: 'null surface', 'mySurf.IsNull', 'guard'

##### `ShapeFix_Face.FixMissingSeam.no-closure-early-exit`
- **Line**: ShapeFix_Face.cxx:1732  **Axis**: `conformance-probe`
- **Brief**: Early exit if surface is open in both U and V directions; no seam possible.
- **Falsifiable claim**: Without this branch, open surfaces proceed to wire analysis. To test: construct torus or bspline open in U and V; kernel tries to insert seam on open surface (invalid operation); with branch correctly returns false.
- **Minimal reproducer**: Create BSplineSurface(open-U, open-V) face. Call FixMissingSeam(). Without: attempts seam insertion on non-closed surface. With: returns false.
- **Search anchors**: 'uclosed', 'vclosed', 'no closure'

##### `ShapeFix_Face.FixMissingSeam.context-apply-if-present`
- **Line**: ShapeFix_Face.cxx:1737  **Axis**: `healer-state`
- **Brief**: Applies context transformations to input face if context exists; ensures consistent shape history.
- **Falsifiable claim**: Without this branch, shape-history inconsistency: myFace references original while internal state tracks modified version. To test: FixContext applied prior shape transforms, then FixMissingSeam; without branch old shape used; with branch transformed shape used.
- **Minimal reproducer**: Create face, apply FixContext reshape operation, then FixMissingSeam. Without: myFace != Context()->Apply(myFace). With: myFace synchronized.
- **Search anchors**: 'context', 'apply', 'shape history'

##### `ShapeFix_Face.FixMissingSeam.bspline-non-periodic-rejection`
- **Line**: ShapeFix_Face.cxx:1744  **Axis**: `conformance-probe`
- **Brief**: BSpline surfaces not made periodic are rejected; periodicity is prerequisite for seam insertion.
- **Falsifiable claim**: Without check, non-periodic BSpline seam insertion produces invalid geometry. To test: create non-periodic BSpline closed in knot-space but not periodic; attempt seam insertion without check yields parameter-wrapping errors; with check returns false.
- **Minimal reproducer**: Construct non-periodic BSpline(knots=[0,1,2,3], closed=true in topology). Call FixMissingSeam. Without: invalid seam. With: returns false.
- **Search anchors**: 'BSpline', 'periodic', 'non-periodic rejection'

##### `ShapeFix_Face.FixMissingSeam.infinite-bounds-fallback`
- **Line**: ShapeFix_Face.cxx:1759  **Axis**: `tolerance`
- **Brief**: Handles infinite surface parameter bounds by substituting wire-derived bounds; prevents overflow in range calculations.
- **Falsifiable claim**: Without fallback, infinite bounds propagate into URange/VRange (line 1805), causing arithmetic errors in period-based seam placement. To test: cone or cylinder with infinite bounds; without branch overflow/NaN in seam calc; with branch valid finite bounds used.
- **Minimal reproducer**: Construct Geom_ConicalSurface(infinite bounds) face. Call FixMissingSeam. Without: URange=inf causes NaN in seam calc. With: URange uses wire bounds.
- **Search anchors**: 'infinite bounds', 'Precision::IsInfinite', 'PConfusion'

##### `ShapeFix_Face.FixMissingSeam.non-manifold-wire-filter`
- **Line**: ShapeFix_Face.cxx:1814  **Axis**: `input-shape`
- **Brief**: Filters non-manifold shapes and wires with invalid orientation; only FORWARD/REVERSED wires collected.
- **Falsifiable claim**: Without filter, non-manifold children passed to wire-analysis, causing CheckWire to fail or crash. To test: face with internal non-manifold vertex; without branch error or mismatched result; with branch non-manifold appended separately to aSeqNonManif.
- **Minimal reproducer**: Create face with internal vertex (non-manifold topology). Call FixMissingSeam. Without: invalid wire processing. With: non-manifold separated and reattached later.
- **Search anchors**: 'non-manifold', 'orientation', 'FORWARD', 'REVERSED'

##### `ShapeFix_Face.FixMissingSeam.degenerate-wire-consolidation`
- **Line**: ShapeFix_Face.cxx:1872  **Axis**: `input-shape`
- **Brief**: Removes completely degenerated wires when multiple open wires detected; avoids seam attachment to collapsed geometry.
- **Falsifiable claim**: Without removal, degenerated wires produce degenerated-edge seams with zero 3D extent. To test: face with 3+ wires, all degenerated; without branch degenerated seam added; with branch wires removed and w1/w2 reset.
- **Minimal reproducer**: Create face with 3 degenerated wires (all edges map to point). Call FixMissingSeam. Without: seam on zero-extent geometry. With: degenerated wires removed.
- **Search anchors**: 'degenerated', 'isdeg', 'consolidation'

##### `ShapeFix_Face.FixMissingSeam.degenerated-torus-apex-normalization` **[low-confidence]**
- **Line**: ShapeFix_Face.cxx:1890  **Axis**: `input-shape`
- **Brief**: Degenerated torus (major < minor radius) marked as 'not degenerated' if second wire exists; treats as regular torus.
- **Falsifiable claim**: Degenerated torus with two wires has apex-like region but topology suggests regular closure. Without normalization, apex singularity handling conflicts with two-wire seam logic. To test: torus(major=0.5, minor=1.0) with w2 present; without flag anomalous apex handling; with flag treated as regular closure.
- **Minimal reproducer**: Construct Geom_ToroidalSurface(R=0.5, r=1.0, two boundary wires). Call FixMissingSeam. Without: apex-special-case interferes. With: normal two-wire seam applied.
- **Search anchors**: 'degenerated torus', 'major < minor', 'apex'

##### `ShapeFix_Face.FixMissingSeam.degenerated-torus-apex-edge-synthesis` **[low-confidence]**
- **Line**: ShapeFix_Face.cxx:1909  **Axis**: `input-shape`
- **Brief**: For degenerated torus with single wire: synthesizes degenerated edge at calculated apex; specific for torus major < minor.
- **Falsifiable claim**: Torus apex is singular point; without synthetic degenerated edge, single-wire topology cannot close properly. To test: torus(R=0.5, r=1.0, one wire at equator); without synthetic edge seam incomplete; with synthetic degenerated edge at apex completing second boundary.
- **Minimal reproducer**: Construct Geom_ToroidalSurface(R=0.5, r=1.0) with single equatorial wire. Call FixMissingSeam. Without: single wire remains; with synthetic degenerated edge at aPhi=[acos(-R/r), pi+acos(-R/r)].
- **Search anchors**: 'torus apex', 'degenerated edge', 'aPhi'

##### `ShapeFix_Face.FixMissingSeam.sphere-apex-edge-synthesis` **[low-confidence]**
- **Line**: ShapeFix_Face.cxx:1920  **Axis**: `input-shape`
- **Brief**: For sphere with single wire open in U: synthesizes degenerated edge at pole; completes topology.
- **Falsifiable claim**: Sphere poles are singular; single wire at non-pole latitude cannot close without synthetic pole edge. To test: Geom_SphericalSurface with wire at equator, open in U; without synthetic pole edge seam incomplete; with synthetic degenerated edge at (u=0 or 2π, v=±π/2).
- **Minimal reproducer**: Construct sphere with single wire at v=0.2π (non-pole). Call FixMissingSeam. Without: incomplete topology; with synthetic degenerated edge at north/south pole closing second boundary.
- **Search anchors**: 'sphere', 'apex', 'pole'

##### `ShapeFix_Face.FixMissingSeam.bspline-v-apex-edge-synthesis` **[low-confidence]**
- **Line**: ShapeFix_Face.cxx:1927  **Axis**: `input-shape`
- **Brief**: For BSpline surface open in V: detects apex by distance test (surface pinches at V-boundary); synthesizes degenerated edge.
- **Falsifiable claim**: BSpline cone-like surfaces pinch at one V boundary; without apex detection seam placed on invalid surface region. To test: BSpline cone(apex at v=0, base at v=1) with single wire; distance test mySurf->Value(u, 0) vs Value(u, 0.5); without detection seam applied to apex; with detection synthetic edge at pinch point.
- **Minimal reproducer**: Construct BSpline approximating cone(apex v=SVF). Distance(Value(SUF,SVF), Value(SUF, mid)) < tol indicates pinch. Call FixMissingSeam with single wire. Without: invalid seam; with synthetic edge at pinch.
- **Search anchors**: 'BSpline V-apex', 'cone-like', 'pinch'

##### `ShapeFix_Face.FixMissingSeam.bspline-u-apex-edge-synthesis` **[low-confidence]**
- **Line**: ShapeFix_Face.cxx:1949  **Axis**: `input-shape`
- **Brief**: For BSpline surface open in U: detects apex by distance test; synthesizes degenerated edge at pinch.
- **Falsifiable claim**: BSpline surface may pinch in U direction (e.g., revolution surface); without apex detection seam misplaced. To test: BSpline approximating surface-of-revolution(apex at u=0); without detection seam on apex singular point; with detection synthetic edge at pinch.
- **Minimal reproducer**: Construct BSpline approximating revolution(pinch at u=SUF). Call FixMissingSeam. Without: seam on singular u; with synthetic edge at detected pinch point.
- **Search anchors**: 'BSpline U-apex', 'revolution', 'pinch'

##### `ShapeFix_Face.FixMissingSeam.orientation-correction-partial-closure`
- **Line**: ShapeFix_Face.cxx:2013  **Axis**: `input-shape`
- **Brief**: For partially-closed surfaces (one direction only) or degenerated torus: corrects wire orientation if opposite-sense wires detected.
- **Falsifiable claim**: Cylinder (U-closed, V-open) with opposite-oriented wires produces invalid seam. Without correction, wires traverse U opposite directions. To test: cylinder with w1 forward, w2 reverse; without correction seam fails; with correction wires normalized.
- **Minimal reproducer**: Construct cylinder(U-closed, V-open) with w1 traversing +U, w2 traversing -U. Call FixMissingSeam. Without: seam invalid; with correction both traverse same direction.
- **Search anchors**: 'orientation', 'deltaOther', 'correction'

##### `ShapeFix_Face.FixMissingSeam.wire-replacement-tracking`
- **Line**: ShapeFix_Face.cxx:2043  **Axis**: `healer-state`
- **Brief**: Tracks reordered wires during face reconstruction; replaces original wires with reordered versions to maintain edge connectivity.
- **Falsifiable claim**: FixReorder may reorder edges within wire; without replacement, face reconstructed with original (non-reordered) wire causing edge-connectivity breaks at seam. To test: call FixReorder on w1; without replacement face uses pre-reorder w1; with replacement uses reordered w11.
- **Minimal reproducer**: Create wire with edge order [e1, e2, e3]. FixReorder reorders to [e2, e1, e3]. Reconstruct face without replacement: seam fails to connect. With replacement: seam connects correctly.
- **Search anchors**: 'wire replacement', 'FixReorder', 'w11'

##### `ShapeFix_Face.FixMissingSeam.outer-bound-hole-reversal`
- **Line**: ShapeFix_Face.cxx:2058  **Axis**: `input-shape`
- **Brief**: Non-boundary wires (holes) checked for correct orientation; outer bounds reversed if detected to ensure hole orientation.
- **Falsifiable claim**: Hole incorrectly oriented as outer boundary produces inside-out face. Without check, face with holes may have hole wires exterior-oriented. To test: face with hole wire having outer-boundary orientation; without check hole faces outward; with check hole reversed to inward.
- **Minimal reproducer**: Create face with outer + hole wires, hole wrongly having outer-orientation. Call FixMissingSeam. Without: invalid face topology. With: hole orientation corrected.
- **Search anchors**: 'outer bound', 'hole', 'orientation'

##### `ShapeFix_Face.FixMissingSeam.period-wrapped-wire-adjustment`
- **Line**: ShapeFix_Face.cxx:2071  **Axis**: `healer-state`
- **Brief**: For fully-closed surfaces with non-degenerated torus: adjusts w2 by period along seam direction to minimize edge-splitting.
- **Falsifiable claim**: Without period adjustment, w2 may lie across seam in parameter space, requiring many edge splits. To test: torus(U-closed, V-closed) with w2 offset from w1 by ~period; without shift w2 wraps seam; with shift w2 repositioned to align with w1 side.
- **Minimal reproducer**: Construct torus with w1 at u=0.1, w2 at u=6.2 (wrapped). Call FixMissingSeam. Without: w2 wraps seam, edges split; with AdjustByPeriod shift w2 to u=0.3, no wrap.
- **Search anchors**: 'period', 'AdjustByPeriod', 'shift'

##### `ShapeFix_Face.FixMissingSeam.pcurve-translation-period-sync`
- **Line**: ShapeFix_Face.cxx:2104  **Axis**: `kernel-pair`
- **Brief**: When non-boundary wires require period shift, PCurves translated along shift vector; maintains UV consistency.
- **Falsifiable claim**: Without translation, 3D geometry fixed but UV parameterization uncorrected, causing 3D-UV mismatch. To test: apply period shift to w2, don't translate w2 edges' PCurves; geometry on correct side but UV wraps. With translation: UV follows 3D.
- **Minimal reproducer**: Period shift w2 by vector(1, 0). Without PCurve translation: Point3D correct but Point2D wraps period. With translation: 2D-3D consistent.
- **Search anchors**: 'PCurve', 'translate', 'shift'

##### `ShapeFix_Face.FixMissingSeam.u-seam-optimal-placement`
- **Line**: ShapeFix_Face.cxx:2156  **Axis**: `healer-state`
- **Brief**: For U-closed surfaces: seam placement chosen to coincide with edge-end points, minimizing edge splits.
- **Falsifiable claim**: Arbitrary seam placement splits edges crossing seam; optimal placement at edge-end requires no split. To test: edge with end at u=1.5; seam at u=1.0 requires split; seam at u=1.5 requires no split. Without optimization seam placed sub-optimally; with optimization seam at edge-end.
- **Minimal reproducer**: Edge with PCurve endpoints at [u=0, u=1.5]. Seam placement: optimal at u=1.5 (no split), suboptimal at u=0.5 (split). Algorithm finds u=1.5 as best.
- **Search anchors**: 'seam placement', 'optimal', 'edge-end'

##### `ShapeFix_Face.FixMissingSeam.v-seam-optimal-placement`
- **Line**: ShapeFix_Face.cxx:2170  **Axis**: `healer-state`
- **Brief**: For V-closed surfaces: seam placement chosen to coincide with edge-end points in V direction.
- **Falsifiable claim**: Arbitrary V-seam placement splits edges; optimal placement at V-edge-end avoids split. To test: same as U case but for V-direction.
- **Minimal reproducer**: Edge with PCurve endpoints at [v=0.2, v=2.8]. Optimal seam at v=2.8 (no split) vs v=1.0 (split). Algorithm finds v=2.8.
- **Search anchors**: 'seam placement', 'V-direction', 'optimal'

##### `ShapeFix_Face.FixMissingSeam.dual-wire-seam-point-match`
- **Line**: ShapeFix_Face.cxx:2187  **Axis**: `healer-state`
- **Brief**: Best seam placement is where edge-ends on both w1 and w2 coincide in parameter space; minimizes splits on both wires.
- **Falsifiable claim**: Without matching, seam placed at w1 edge-end but w2 edge-end offset by parameter delta; w2 edge requires split. To test: w1 edge-end u=1.0, w2 edge-end u=1.01; seam at u=1.0 requires w2 split; at u=1.015 (midpoint) both split. Optimal: coinciding point.
- **Minimal reproducer**: w1 edge ends at u=1.0, w2 edge starts at u=1.01 (offset by period-wrapping). Seam at u=1.0: w2 split. Seam at coinciding u: no split. Algorithm prefers coinciding.
- **Search anchors**: 'dual-wire', 'coincide', 'match'

##### `ShapeFix_Face.FixMissingSeam.seam-boundary-clamping`
- **Line**: ShapeFix_Face.cxx:2224  **Axis**: `tolerance`
- **Brief**: Seam location adjusted to lie within surface bounds after optimization; uses AdjustToPeriod to ensure validity.
- **Falsifiable claim**: Optimized seam position may fall outside [SUF, SUL]; clamping ensures within bounds for ComposeShell. To test: surface bounds [0, 2π], optimized seam u=2π+0.1; without clamping out-of-bounds; with clamping adjusted to valid range.
- **Minimal reproducer**: Surface u-bounds [0, 2π]. Optimized seam u=6.3 (outside bounds). Without clamping: out-of-bounds. With AdjustToPeriod: adjusted to ~0.1.
- **Search anchors**: 'seam boundary', 'clamping', 'AdjustToPeriod'

##### `ShapeFix_Face.FixMissingSeam.edge-pcurve-fetch-failure-abort`
- **Line**: ShapeFix_Face.cxx:2254  **Axis**: `input-shape`
- **Brief**: PCurve retrieval failure for any edge causes immediate abort (returns false); corrupted edge data makes seam impossible.
- **Falsifiable claim**: Without early abort, seam insertion proceeds on face with missing PCurves, producing invalid result. To test: face with edge missing PCurve for current face; without abort seam applied; with abort method returns false.
- **Minimal reproducer**: Create face with edge lacking PCurve. Call FixMissingSeam. Without: invalid seam. With: returns false.
- **Search anchors**: 'PCurve', 'fetch failure', 'abort'

##### `ShapeFix_Face.FixMissingSeam.rts-seam-surface-creation`
- **Line**: ShapeFix_Face.cxx:2279  **Axis**: `kernel-pair`
- **Brief**: Seam placed by creating rectangular-trimmed surface from parent surface with new bounds; seam inserted via ComposeShell.
- **Falsifiable claim**: Without RTS wrapper, ComposeShell cannot insert seam on arbitrary surface. RTS reparameterization enables seam injection. To test: ComposeShell expects rectangular surface; without RTS non-rectangular handling fails; with RTS seam inserted.
- **Minimal reproducer**: Create surface with arbitrary bounds. Wrap in RTS(uf, uf+URange, vf, vf+VRange). ComposeShell can now insert seam. Without RTS: incompatible.
- **Search anchors**: 'RectangularTrimmedSurface', 'RTS', 'ComposeShell'

##### `ShapeFix_Face.FixMissingSeam.small-area-wire-cleanup`
- **Line**: ShapeFix_Face.cxx:2309  **Axis**: `healer-state`
- **Brief**: After seam insertion, small-area wires and faces removed to eliminate spurious geometry from ComposeShell.
- **Falsifiable claim**: ComposeShell may create degenerate/small wires at seam; without removal, face contains garbage. To test: face after ComposeShell with small wires; without cleanup small wires present; with FixSmall area removed.
- **Minimal reproducer**: Run ComposeShell seam insertion. Inspect result for small wires. Without cleanup: small wires present. With FixSmall(true): removed.
- **Search anchors**: 'small area', 'cleanup', 'FixSmall'


#### `ShapeFix_Face.FixOrientation`
 (14 branches; source: `v3-deep-ShapeFix_Face_FixOrientation.json`)

##### `ShapeFix_Face.FixOrientation.TinyWireFiltering`
- **Line**: ShapeFix_Face.cxx:1185-1225  **Axis**: `tolerance`
- **Brief**: Filters wires below precision threshold by analyzing 3D curve length via 10-point sampling.
- **Falsifiable claim**: Without this branch, degenerate single-edge wires with near-zero length corrupt orientation analysis by introducing false vertex states during subsequent classification. To test: construct a face with a one-edge wire of length 1e-8; without filtering, classification references such wires; with filtering, they are segregated into VerySmallWires.
- **Minimal reproducer**: STEP: face with outer wire (normal loop) + inner single-edge wire at midpoint with curve length < Precision::Confusion(). Trigger FixOrientation(). Without: wire participates in stb classification, causing sta to become UNKNOWN. With: wire moves to VerySmallWires, excluding it from containment tests.
- **Search anchors**: 'VerySmallWires', 'one-edge', 'null-length', 'NbControl = 10', 'Precision::Confusion()'

##### `ShapeFix_Face.FixOrientation.SingleWireOuterBoundCheck`
- **Line**: ShapeFix_Face.cxx:1237-1247  **Axis**: `healer-state`
- **Brief**: Validates single-wire faces by testing IsOuterBound; reverses if inner.
- **Falsifiable claim**: Without this check, single-wire faces with non-FORWARD orientation are never reversed, allowing inverted inner wires to appear as faces. To test: create face from single inner wire; without: orientation unchanged; with: wire reversed.
- **Minimal reproducer**: STEP: face with one inner wire (not outer boundary per ShapeAnalysis::IsOuterBound). Trigger FixOrientation() with !isAddNaturalBounds. Without: wire retained as-is. With: wire reversed via ShapeExtend_WireData::Reverse(myFace).
- **Search anchors**: 'nb == 1', 'IsOuterBound', 'ShapeExtend_WireData', 'Reverse(myFace)'

##### `ShapeFix_Face.FixOrientation.WireBoundingBoxComputation`
- **Line**: ShapeFix_Face.cxx:1268-1310  **Axis**: `tolerance`
- **Brief**: Constructs 2D bounding boxes for wire containment pre-filtering, with uMiddle/vMiddle normalization on first wire.
- **Falsifiable claim**: Without centering aWireBoxes on first wire's midpoint (uMiddle, vMiddle), periodic surface wrapping shifts become globally inconsistent, causing false containment negatives. To test: torus with two wires; without uMiddle/vMiddle sync, the second wire's box is shifted relative to an unanchored reference; with sync, both boxes are relative to first wire.
- **Minimal reproducer**: STEP: toroidal face with 2+ wires spanning disparate u or v regions. Trigger FixOrientation(). Without: first wire's box set at [aXMin..aXMax]; subsequent wires shifted by AdjustByPeriod(..., 0.5*(new aX), uMiddle_UNINITIALIZED) → undefined reference. With: uMiddle = (firstBox.aXMin + firstBox.aXMax)*0.5; subsequent wires shift relative to this anchor.
- **Search anchors**: 'aWireBoxes', 'isFirst', 'uMiddle', 'vMiddle', 'BndLib_Add2dCurve::Add'

##### `ShapeFix_Face.FixOrientation.PeriodicBoundingBoxShift`
- **Line**: ShapeFix_Face.cxx:1295-1310  **Axis**: `input-shape`
- **Brief**: Adjusts wire bounding boxes for toroidal/cylindrical surfaces via ShapeAnalysis::AdjustByPeriod().
- **Falsifiable claim**: Without periodic shifts, wires wrapping across seams (e.g., in u at torus seam u=0) are classified as non-containing because their 2D boxes fall on opposite sides of the period boundary. To test: torus wire with midpoint near u=0, spanning u=[-eps, +eps]; without shift, box is at [-eps, +eps] relative to unshifted reference; with shift, AdjustByPeriod() maps box to [uRange-eps, uRange+eps] if reference is near uRange.
- **Minimal reproducer**: STEP: toroidal surface (u:0..2π, v:0..π); outer wire midpoint at u≈2π-0.1, inner wire at u≈0.1 (wraps seam). Trigger FixOrientation(). Without: box2 computed at [0.05, ...], box1 at [2π-0.15, ...]; aBox2.IsOut(aBox1)=true spuriously. With: if uclosed, compute xShift=AdjustByPeriod(0.5*(0.05+0.15), uMiddle=2π-0.075, 2π) → shifts box2 to [2π+0.05, ...], IsOut()=false.
- **Search anchors**: 'uclosed', 'vclosed', 'AdjustByPeriod', 'xShift', 'yShift'

##### `ShapeFix_Face.FixOrientation.VertexPeriodicWrap`
- **Line**: ShapeFix_Face.cxx:1335-1350  **Axis**: `input-shape`
- **Brief**: Tests vertex containment on toroidal surfaces via shifted u/v copies when initial PerformInfinitePoint fails.
- **Falsifiable claim**: Without wrapping vertex probes across period boundaries, vertices on toroidal seams are misclassified as UNKNOWN state. To test: vertex at torus seam u=0 with wire outer loop at u≈π; without: stb initially OUT, no seam wrap attempted; with: stb checked at (u+uRange, v) and (u, v+vRange).
- **Minimal reproducer**: STEP: toroidal surface; outer wire encircling meridian at u=π; vertex at seam u=0. Trigger FixOrientation(). Without: stb=clas.Perform(Pnt2d(0,v))=OUT; no further checks if uclosed/vclosed. With: stb==staout, so check clas.Perform(Pnt2d(2π, v)), clas.Perform(Pnt2d(0, v+π)), yielding IN.
- **Search anchors**: 'aSh2.ShapeType() == TopAbs_VERTEX', 'stb == staout', 'uclosed || vclosed', 'p2d.X() + uRange', 'p2d.Y() + vRange'

##### `ShapeFix_Face.FixOrientation.WirePartialClassification`
- **Line**: ShapeFix_Face.cxx:1351-1410  **Axis**: `conformance-probe`
- **Brief**: Classifies each wire via midpoints of constituent edges; detects ambiguity (mixed IN/OUT) as topology error.
- **Falsifiable claim**: Without midpoint-based stb accumulation, wires with edges half-inside and half-outside the parent loop are falsely classified as consistently IN or OUT, creating inverted nested structures. To test: two concentric loops on plane-like surface with one edge of inner loop protruding; without: stb converges to single state; with: stb alternates, sta becomes UNKNOWN.
- **Minimal reproducer**: STEP: planar face with two concentric rectangles; move one edge of inner rectangle outside outer boundary. Trigger FixOrientation(). Without: stb=OUT for first edge, stb==IN for second → condition !(stb==ste) not triggered, sta ≠ UNKNOWN. With: for each edge, ste computed from midpoint; contradictory results cause SI.Bind(aw, 0) and sta=UNKNOWN, triggering warning.
- **Search anchors**: 'stb == TopAbs_UNKNOWN', 'ste == TopAbs_OUT || ste == TopAbs_IN', '!(stb == ste)', 'unp = cw->Value((cf + cl) / 2.)', 'sta = TopAbs_UNKNOWN'

##### `ShapeFix_Face.FixOrientation.ToroidalDiagonalShift`
- **Line**: ShapeFix_Face.cxx:1382-1398  **Axis**: `kernel-pair`
- **Brief**: Attempts 2x2 grid of diagonal period wraps (±uRange, ±vRange) when unary u/v shifts fail on toroidal surfaces.
- **Falsifiable claim**: Without diagonal shift enumeration, wires on toroidal surfaces with both u and v seam-crossing misidentify as non-contained. To test: torus with wire loop near corner (u≈0, v≈0) and inner wire at (u≈2π-ε, v≈π-ε); without: u-shift finds interior, but v-shift then undoes it; diagonal (−uRange, −vRange) succeeds. With: nested loops check ±uRange and ±vRange independently, then ±uRange⊗±vRange if both needed.
- **Minimal reproducer**: STEP: toroidal surface (u:0..2π, v:0..π); outer wire loop at parametric corners u∈[1.9π, 2π], v∈[0.9π, π]; inner wire loop at u∈[0, 0.1π], v∈[0, 0.1π]. Trigger FixOrientation(). Without diagonal loop: unp at outer midpoint ≈(1.95π, 0.95π); single u-shift to (1.95π+2π, 0.95π) → clas.Perform() OUT; single v-shift to (1.95π, 0.95π+π) → clas.Perform() OUT; found=false. With diagonal (dX=+1, dY=+1): unp1=(1.95π-2π, 0.95π-π)=(−0.05π, −0.05π); wraps to equivalent (2π−0.05π, π−0.05π)=(1.95π, 0.95π) in [0,2π)×[0,π); clas.Perform() detects inner loop, found=true, stb flips to IN, wire shifted via Shift2dWire().
- **Search anchors**: '!found && uclosed && vclosed', 'for (double dX = -1.0; dX <= 1.0 && !found; dX += 2.0)', 'for (double dY = -1.0; dY <= 1.0 && !found; dY += 2.0)', 'unp.X() + uRange * dX', 'unp.Y() + vRange * dY'

##### `ShapeFix_Face.FixOrientation.StateFlipAndWireShift`
- **Line**: ShapeFix_Face.cxx:1399-1405  **Axis**: `healer-state`
- **Brief**: Flips stb state (IN↔OUT) and applies 2D coordinate shift via Shift2dWire() after successful diagonal wrap detection.
- **Falsifiable claim**: Without state flip, a wire detected via periodic wrap continues with original stb, inverting the containment relationship. To test: after found=true from diagonal wrap, if stb==IN originally, state must flip to OUT to reflect shifted geometry. To test: shift wire vertices by unp1.XY()-unp.XY(); without: wire remains at original position, violating periodicity consistency.
- **Minimal reproducer**: STEP: toroidal face; after diagonal wrap detects inner wire at shifted position unp1=(−0.05π, −0.05π), original stb=IN. Trigger FixOrientation(). Without state flip: stb remains IN; subsequent containment tests use old stb. With stb flip to OUT and Shift2dWire(bw, myFace, unp1.XY()−unp.XY(), mySurf): all 2D edge coordinates translated; subsequent tests see shifted wire in outer region.
- **Search anchors**: 'if (found)', 'if (stb == TopAbs_IN)', 'stb = TopAbs_OUT', 'else stb = TopAbs_IN', 'Shift2dWire'

##### `ShapeFix_Face.FixOrientation.InfinitePointOuterBoundDetection`
- **Line**: ShapeFix_Face.cxx:1319-1328  **Axis**: `conformance-probe`
- **Brief**: Establishes reference topology via PerformInfinitePoint(); determines if face exterior is IN or OUT in 2D classification space.
- **Falsifiable claim**: Without PerformInfinitePoint(), the algorithm lacks a fixed reference for outer/inner distinction on non-plane surfaces; all wire classifications become relative but unanchored. To test: call FixOrientation() on genus-1 surface; without staout, sta==TopAbs_IN/OUT becomes meaningless; with staout, wire is inner iff sta==staout, outer iff sta≠staout.
- **Minimal reproducer**: STEP: toroidal face with multiple wire loops. Trigger FixOrientation(). Without staout reference: clas.PerformInfinitePoint() not called; for each wire, only (sta==OUT vs. sta==IN) is determined, with no consensus on which boundary is exterior. With staout: If staout=OUT, then wire is contained iff sta!=OUT; if staout=IN, then wire is contained iff sta!=IN.
- **Search anchors**: 'staout = clas.PerformInfinitePoint()', 'sta = TopAbs_OUT', 'if (sta == staout)', 'if (staout == TopAbs_IN)'

##### `ShapeFix_Face.FixOrientation.BoxPrerequistePruning`
- **Line**: ShapeFix_Face.cxx:1360-1365  **Axis**: `healer-state`
- **Brief**: Skips wire containment tests via bounding box disjointness; avoids expensive point-in-polygon for non-overlapping wires.
- **Falsifiable claim**: Without aBox2.IsOut(aBox1) check, every wire pair is tested via edge-midpoint classification even when 2D boxes are disjoint. To test: two concentric circles on a plane; without: inner circle edges tested against outer loop; with: test skipped if boxes disjoint.
- **Minimal reproducer**: STEP: planar face with two widely separated wire loops (e.g., circles at (0,0) and (10,10) with radius 1 each). Trigger FixOrientation(). Without: for each edge of second loop, clas.Perform() called; found/stb updated spuriously. With: aBox2.IsOut(aBox1)=true, inner loop not tested.
- **Search anchors**: 'Bnd_Box2d aBox2', 'aBox2.IsOut(aBox1)', 'continue'

##### `ShapeFix_Face.FixOrientation.ReverseOnOuterContainment`
- **Line**: ShapeFix_Face.cxx:1420-1432  **Axis**: `healer-state`
- **Brief**: Reverses wire if sta==OUT AND staout==IN, indicating outer-boundary wire on inner side of infinite point.
- **Falsifiable claim**: Without this reversal, wires topologically inside the face (sta==OUT, staout==IN) maintain original orientation, inverting the wire-face pair's topology. To test: wire that should be inner boundary; without: kept as-is; with: reversed to proper inner orientation.
- **Minimal reproducer**: STEP: face with wire that test classifies as STA=OUT (all edges outside some region), but PerformInfinitePoint()=IN (outer boundary encloses infinite point). Trigger FixOrientation(). Without reversal: wire not reversed. With: wire reversed via ShapeExtend_WireData::Reverse(myFace); aSeqReversed.Append(i); done=true.
- **Search anchors**: 'sta == TopAbs_OUT', 'staout == TopAbs_IN', 'sewd.Reverse(myFace)', 'aSeqReversed.Append'

##### `ShapeFix_Face.FixOrientation.DeferredReverseOnContainmentPostFact`
- **Line**: ShapeFix_Face.cxx:1443-1475  **Axis**: `healer-state`
- **Brief**: Second pass: reverses wires not in MapIntWires if SI state indicates topological inconsistency (tmpi==2 or tmpi==3).
- **Falsifiable claim**: Without deferred reversal, wires marked SI==2 (contained, staout==OUT) or SI==3 (contained, staout==IN) are not flipped even though they conflict with the global orientation scheme. To test: multi-wire face where first pass establishes consensus but second pass discovers a wire violates it; without: wire kept; with: reversed.
- **Minimal reproducer**: STEP: face with 3+ wires; first two establish sta consensus; third wire's edges all classified as IN but staout==OUT. Trigger FixOrientation(). Without second pass: SI.Find(aw)==2, but no reversal occurs (only SI==0 or SI==1 trigger reversal in first loop). With second pass: tmpi==2, !MapIntWires.Contains(aw), wire is reversed via sewd.Reverse(myFace).
- **Search anchors**: 'for (i = 1; i <= nb; i++)', 'tmpi = SI.Find(aw)', 'if (tmpi > 1)', 'if (!MapIntWires.Contains(aw))', 'if (tmpi == 3)'

##### `ShapeFix_Face.FixOrientation.NaturalBoundsCondensing`
- **Line**: ShapeFix_Face.cxx:1478-1481  **Axis**: `api-contract`
- **Brief**: Suppresses done flag if all reversed wires are natural bounds; avoids redundant face rebuild.
- **Falsifiable claim**: Without this check, faces where all wires are natural bounds but all were reversed trigger unnecessary face rebuilding. To test: natural-bounds-only face with all wires flipped; without: done=true, rebuild occurs; with: done=false, myFace unchanged.
- **Minimal reproducer**: STEP: face with nb==aSeqReversed.Length() and isAddNaturalBounds=true. Trigger FixOrientation(). Without: done remains true if reversals occurred. With: done=false, skipping Face rebuild (lines 1484-1507).
- **Search anchors**: 'isAddNaturalBounds && nb == aSeqReversed.Length()', 'done = false'

##### `ShapeFix_Face.FixOrientation.FaceRebuild`
- **Line**: ShapeFix_Face.cxx:1484-1507  **Axis**: `healer-state`
- **Brief**: Rebuilds face with reoriented wires and re-applies natural bounds/non-wire vertices when done==true.
- **Falsifiable claim**: Without rebuild, myFace retains references to old wire objects even if their edge topology changed; context tracking and downstream operations see stale geometry. To test: reverse wire, don't rebuild; myFace.EmptyCopied() still references original wire; downstream operations reference old edges.
- **Minimal reproducer**: STEP: any face triggering done=true (e.g., single wire reversal). Trigger FixOrientation(). Without rebuild: myFace still references original ws.Value(1) even though it was replaced in ws via sewd.Wire(). With rebuild: S=myFace.EmptyCopied(), B.Add(S, ws.Value(i)) for all i, myFace=TopoDS::Face(S); BRepTools::Update(myFace) ensures topology is current.
- **Search anchors**: 'if (done)', 'TopoDS_Shape S = myFace.EmptyCopied()', 'B.Add(S, ws.Value(i))', 'BRepTools::Update(myFace)'


### ShapeFix_FaceConnect

#### `ShapeFix_FaceConnect.Build`
 (39 branches; source: `v3-deep-ShapeFix_FaceConnect_Build.json`)

##### `ShapeFix_FaceConnect.Build.EDGE_ALREADY_LISTED`
- **Line**: ShapeFix_FaceConnect.cxx:136  **Axis**: `healer-state`
- **Brief**: Duplicate edge detection in free-edge map skips re-binding when edge already exists.
- **Falsifiable claim**: Without this branch, shared edges would be added to free-edge lists multiple times, violating uniqueness invariant. To test: call Build() on shell with degenerate edges; verify free-edge lists contain unique entries.
- **Minimal reproducer**: Construct shell with face containing edge E1 appearing in multiple wires. Trigger Build(). Without: free-edge lists for E1 contain duplicates. With: single entry.
- **Search anchors**: 'if (theIter.Value().IsSame(aSecond))', 'duplicate edge rejection'

##### `ShapeFix_FaceConnect.Build.DEGENERATE_EDGE_FILTER`
- **Line**: ShapeFix_FaceConnect.cxx:105  **Axis**: `kernel-pair`
- **Brief**: Degenerate edges are excluded from free-edge processing; non-degenerate edges only trigger face binding.
- **Falsifiable claim**: Without this branch, degenerate edges would trigger shape-fix operations that assume non-zero edge length. To test: construct face with degenerate edge; verify it's excluded from repair maps.
- **Minimal reproducer**: Create EDGE with zero length in face. Call Build(). Without: degenerate edge enters repair pipeline. With: excluded from myOriFreeEdges.
- **Search anchors**: '!BRep_Tool::Degenerated(TopoDS::Edge(theEdge))'

##### `ShapeFix_FaceConnect.Build.FREE_EDGE_INITIAL_BINDING`
- **Line**: ShapeFix_FaceConnect.cxx:85-91  **Axis**: `healer-state`
- **Brief**: First pass identifies free edges by toggling map entries; second occurrence unbinds, leaving singletons.
- **Falsifiable claim**: Without this toggle logic, edges appearing once and twice would be indistinguishable. To test: shell with E1 in face A only (free) vs. E2 in faces A and B (shared); verify only free edges remain in theFreeEdges map.
- **Minimal reproducer**: Shell with faces: F1 with edges E1,E2; F2 with edge E2. After first pass theFreeEdges map contains E1 (free). After second pass, E2 is removed. Correct: theFreeEdges={E1->F1}.
- **Search anchors**: 'theFreeEdges.UnBind(theEdge)', 'toggle pattern'

##### `ShapeFix_FaceConnect.Build.CONNECTED_FACE_FILTER`
- **Line**: ShapeFix_FaceConnect.cxx:105  **Axis**: `api-contract`
- **Brief**: Only faces registered via Add() method (in myConnected map) trigger free-edge processing.
- **Falsifiable claim**: Without this guard, all free edges would be scheduled for repair, including edges on isolated faces. To test: add F1 to connection list; leave F2 separate. Verify F2's free edges ignored.
- **Minimal reproducer**: Call Add(F1, F3). F2 unconnected. Build() processes only free edges on F1,F3. F2's boundary edges skipped.
- **Search anchors**: 'if (myConnected.IsBound(theFace))'

##### `ShapeFix_FaceConnect.Build.RESULT_EDGE_LIST_INIT`
- **Line**: ShapeFix_FaceConnect.cxx:121-126  **Axis**: `healer-state`
- **Brief**: First reference to original free edge initializes empty lists in result maps.
- **Falsifiable claim**: Without initialization, subsequent appends to myResFreeEdges/myResSharEdges would fail on unbound keys. To test: verify maps contain entry for each original free edge.
- **Minimal reproducer**: Original free edge E1 appears first time: initialize {E1->[]} in myResFreeEdges and myResSharEdges. Subsequent edits append to existing lists.
- **Search anchors**: '!myResFreeEdges.IsBound(theEdge)', 'Initialize empty lists'

##### `ShapeFix_FaceConnect.Build.SELF_CONNECTED_FACE`
- **Line**: ShapeFix_FaceConnect.cxx:233-239  **Axis**: `kernel-pair`
- **Brief**: Faces paired with themselves are detected and logged but not processed (zero faces in sewing array).
- **Falsifiable claim**: Without this guard, self-sewing would corrupt topological state. To test: Add(F, F); verify no sewing occurs, warning logged.
- **Minimal reproducer**: Add(F1, F1). Build(). Warning emitted. theNumOfFacesToSew remains 1 (not set to 2). theSewer receives only F1.
- **Search anchors**: 'if (theFirstFace.IsSame(theSecondFace))', 'Self-connected face warning'

##### `ShapeFix_FaceConnect.Build.PAIR_ALREADY_PROCESSED`
- **Line**: ShapeFix_FaceConnect.cxx:215-228  **Axis**: `healer-state`
- **Brief**: Bidirectional edges are detected; pairs (F1,F2) and (F2,F1) processed only once.
- **Falsifiable claim**: Without deduplication, same edge pair sewed twice with different result states. To test: Add(F1,F2); verify single sewing pass.
- **Minimal reproducer**: Connected list: F1->[F2,F3], F2->[F1]. Process F1-F2, mark in theProcessed(F2). On later iteration F2-F1, skip_pair detected; pair skipped.
- **Search anchors**: 'if (theProcessed.IsBound(theSecondFace))', 'Skip the pair if already processed'

##### `ShapeFix_FaceConnect.Build.SEWING_EXCEPTION_CATCH`
- **Line**: ShapeFix_FaceConnect.cxx:282-290  **Axis**: `kernel-pair`
- **Brief**: Sewing operation wrapped in try-catch to suppress exceptions and gracefully degrade.
- **Falsifiable claim**: Without exception handling, invalid sewing geometry would crash Build(). To test: construct degenerate wire; verify sewing_ok=false on exception.
- **Minimal reproducer**: Create wire with zero-length segments. BRepBuilderAPI_Sewing::Perform() raises Standard_Failure. Exception caught; sewing_ok=false.
- **Search anchors**: 'OCC_CATCH_SIGNALS', 'catch (Standard_Failure const&)'

##### `ShapeFix_FaceConnect.Build.SEWING_NULL_RESULT`
- **Line**: ShapeFix_FaceConnect.cxx:294-297  **Axis**: `kernel-pair`
- **Brief**: Null result from sewer indicates complete failure; recovery discards sewing output.
- **Falsifiable claim**: Without null check, subsequent edge extraction would dereference null; worst case segfault. To test: construct incompatible wires; verify sewing_ok=false.
- **Minimal reproducer**: Wire1, Wire2 with no matching vertices. theSewer.Perform() succeeds but SewedShape().IsNull(). Set sewing_ok=false; skip replacement.
- **Search anchors**: 'if (theSewer.SewedShape().IsNull())', 'Null result check'

##### `ShapeFix_FaceConnect.Build.MODIFIED_EDGE_EXTRACTION`
- **Line**: ShapeFix_FaceConnect.cxx:320-340  **Axis**: `healer-state`
- **Brief**: Sewer tracks modified edges; shared edges detected by double-occurrence in result map.
- **Falsifiable claim**: Without modified tracking, free→shared transitions undetected; edge lists remain incomplete. To test: verify only modified edges enter replacement map.
- **Minimal reproducer**: Original edge E1 sewed to {E1a, E1b}. IsModified(Wire(E1))=true. Extract E1a, E1b into theResultEdges. Second occurrence of E1a (from E2) triggers shared classification.
- **Search anchors**: 'if (theSewer.IsModified(theAuxE))', 'Fill map of result edges'

##### `ShapeFix_FaceConnect.Build.SHARED_EDGE_COLLISION`
- **Line**: ShapeFix_FaceConnect.cxx:329-335  **Axis**: `healer-state`
- **Brief**: When result edge appears in multiple original edges' results, it's classified as shared.
- **Falsifiable claim**: Without collision detection, shared-edge lists would be empty; topology remains incorrectly marked free. To test: sew E1,E2 to common output edge E_shared; verify E_shared in both myResSharEdges[E1] and myResSharEdges[E2].
- **Minimal reproducer**: E1->[E1a,shared_E], E2->[E2a,shared_E]. When processing E2's results, theResultEdges(shared_E)=E1 triggers collision. shared_E moved to myResSharEdges(E1) and myResSharEdges(E2).
- **Search anchors**: 'if (theResultEdges.IsBound(theAuxE))', 'Edge was shared'

##### `ShapeFix_FaceConnect.Build.FREE_EDGE_REMOVAL`
- **Line**: ShapeFix_FaceConnect.cxx:342  **Axis**: `healer-state`
- **Brief**: Modified edges removed from free-list; unmodified edges retained to try later.
- **Falsifiable claim**: Without removal, successful sewing erases incorrect edges; final shell contains wrong topology. To test: verify myResFreeEdges[E].Extent() decreases after sewing.
- **Minimal reproducer**: Original: myResFreeEdges[E1]=[W1]. After Perform(), IsModified(W1)=true. Remove from list. Result: myResFreeEdges[E1]=[].
- **Search anchors**: 'theOldFreeList.Remove(theResultsIter)'

##### `ShapeFix_FaceConnect.Build.EDGE_REPLACEMENT_SCOPE`
- **Line**: ShapeFix_FaceConnect.cxx:415-545  **Axis**: `healer-state`
- **Brief**: Edges replace only if resulting wire is non-empty; identity edges (old==new) skipped.
- **Falsifiable claim**: Without emptywire check, shapeless wires cause ReShape errors. Without identity check, self-loops corrupt geometry. To test: verify no wires with zero edges; no edges replaced by themselves.
- **Minimal reproducer**: Original edge E with no free/shared results: emptywire=true, skip binding. Edge replaced by self: !theAuxE.IsSame(theOldE)=false, skip adding.
- **Search anchors**: 'if (!emptywire)', 'if (!theAuxE.IsSame(theOldE))'

##### `ShapeFix_FaceConnect.Build.VERTEX_PROXIMITY_MATCHING`
- **Line**: ShapeFix_FaceConnect.cxx:467-483  **Axis**: `tolerance`
- **Brief**: New vertices matched to old vertices by minimum Euclidean distance.
- **Falsifiable claim**: Without distance-based matching, vertex associations would be arbitrary; tolerance calculations incorrect. To test: verify theNewV1 closest to theOldP1, not random.
- **Minimal reproducer**: Old edge: V1@(0,0,0)-V2@(1,0,0). New wire vertices: Va@(0.1,0,0), Vb@(0.9,0,0). dist1=0.1 (Va), dist2=0.1 (Vb). Match V1→Va, V2→Vb.
- **Search anchors**: 'if (dist1 < 0 || curdist1 < dist1)', 'Select closest vertex'

##### `ShapeFix_FaceConnect.Build.VERTEX_REPLACEMENT_INIT`
- **Line**: ShapeFix_FaceConnect.cxx:488-511  **Axis**: `healer-state`
- **Brief**: Vertex replacement maps initialized on first old→new association; duplicates rejected.
- **Falsifiable claim**: Without deduplication, same vertex pair would accumulate multiple times; tolerance inflates. To test: verify theRepVertices[V_old] contains each new vertex once.
- **Minimal reproducer**: Match V1_old→V1_new twice (different sewing passes). First: theRepVertices(V1_old)=[V1_new]. Second: check found=true, skip append.
- **Search anchors**: 'if (theRepVertices.IsBound(theOldV1))', 'if (!found)'

##### `ShapeFix_FaceConnect.Build.VERTEX_IDENTITY_SKIP`
- **Line**: ShapeFix_FaceConnect.cxx:486-487  **Axis**: `healer-state`
- **Brief**: Identical old/new vertices skip replacement map entry; no self-mapping.
- **Falsifiable claim**: Without identity check, vertex bounds inflate; ReShape corrupts self-loops. To test: verify no entry in theRepVertices[V]=[V].
- **Minimal reproducer**: Old: V@(0,0,0), New: [V@(0,0,0)]. theOldV1.IsSame(theNewV1)=true. Skip binding.
- **Search anchors**: 'if (!theOldV1.IsSame(theNewV1))'

##### `ShapeFix_FaceConnect.Build.RESHAPE_OK_FALLBACK`
- **Line**: ShapeFix_FaceConnect.cxx:564-569  **Axis**: `api-contract`
- **Brief**: Edge replacement returns ShapeExtend_OK when no edges bound; warning logged.
- **Falsifiable claim**: Without fallback, silent no-op occurs; caller unaware topology unchanged. To test: construct shell with no free edges; verify warning, no crash.
- **Minimal reproducer**: Empty myOriFreeEdges. theRepEdges.IsEmpty()=true. Skip Replace(). Check ShapeExtend_OK status=true.
- **Search anchors**: 'if (theReShape->Status(ShapeExtend_OK))'

##### `ShapeFix_FaceConnect.Build.RESHAPE_FAIL1_FALLBACK`
- **Line**: ShapeFix_FaceConnect.cxx:571-575  **Axis**: `api-contract`
- **Brief**: Edge replacement failure (FAIL1) logged but not thrown; cascade continues.
- **Falsifiable claim**: Without fallback, exception halts Build(); vertex replacement skipped. To test: trigger ReShape failure (invalid edge); verify warning, continue to vertex phase.
- **Minimal reproducer**: theRepEdges contains invalid edge. ReShape::Apply() fails. Status(ShapeExtend_FAIL1)=true. Log error; skip vertex replacement; return result.
- **Search anchors**: 'else if (theReShape->Status(ShapeExtend_FAIL1))'

##### `ShapeFix_FaceConnect.Build.WIRE_ORDER_RESTORATION`
- **Line**: ShapeFix_FaceConnect.cxx:606-622  **Axis**: `healer-state`
- **Brief**: Wire edge ordering corrected after replacement via ShapeAnalysis_WireOrder.
- **Falsifiable claim**: Without reorder, replaced edges create topological discontinuities; wire not valid. To test: verify SAWO.Perform() reconciles wire after edge replacement.
- **Minimal reproducer**: Wire(E1,E2) where E1 replaced by [E1a,E1b]. Order becomes [E1a,E1b,E2]. SAWO recalculates endpoints, reorder applied.
- **Search anchors**: 'ShapeAnalysis_WireOrder SAWO', 'FixReorder'

##### `ShapeFix_FaceConnect.Build.PCURVE_MISSING_SKIP`
- **Line**: ShapeFix_FaceConnect.cxx:612-614  **Axis**: `kernel-pair`
- **Brief**: Edges without parameter curves on face skipped; 3D-only edges bypass fixing.
- **Falsifiable claim**: Without skip, PCurve extraction would fail; wire fixing aborts. To test: edge with no surface parametrization; verify continue skips it.
- **Minimal reproducer**: Edge E with no PCurve on Face F. SAE.PCurve()=false. Continue; skip SAWO.Add() for E. Wire order includes other edges only.
- **Search anchors**: 'if (!SAE.PCurve(...))', 'continue'

##### `ShapeFix_FaceConnect.Build.WIRE_ITERATION_TYPE_CHECK`
- **Line**: ShapeFix_FaceConnect.cxx:599-601  **Axis**: `kernel-pair`
- **Brief**: Only WIRE children processed; other face types skipped.
- **Falsifiable claim**: Without type filter, loops over non-wire elements; incorrect edge fixing applied. To test: verify only TopAbs_WIRE entries enter SFW pipeline.
- **Minimal reproducer**: Face with child SHELLs or FACEs. itw.Value().ShapeType()!=TopAbs_WIRE. Continue; skip fixing.
- **Search anchors**: 'if (itw.Value().ShapeType() != TopAbs_WIRE)', 'continue'

##### `ShapeFix_FaceConnect.Build.FACE_ORIENTATION_FIX`
- **Line**: ShapeFix_FaceConnect.cxx:640-642  **Axis**: `healer-state`
- **Brief**: Face orientation corrected after wire reconstruction via ShapeFix_Face.
- **Falsifiable claim**: Without fix, replaced wires may invert orientation; normal vectors flip. To test: verify SFF.FixOrientation() reconciles outward normal.
- **Minimal reproducer**: Reconstructed face EmpFace with wires in wrong order. FixOrientation(MapWires)=true. Wires reordered; outward normal restored.
- **Search anchors**: 'if (SFF->FixOrientation(MapWires))'

##### `ShapeFix_FaceConnect.Build.TRANSITIVE_VERTEX_MAPPING`
- **Line**: ShapeFix_FaceConnect.cxx:668-695  **Axis**: `healer-state`
- **Brief**: Vertex replacement chains resolved; if V_new→V_interim→V_old, all mapped to V_old.
- **Falsifiable claim**: Without chaining, interim vertices would remain unmapped; final vertex set incomplete. To test: multi-step replacement; verify all endpoints routed to root.
- **Minimal reproducer**: theOldVertices: V2→V1_interim. theRepVertices has V1_interim→V0. Resolve chain: V2→V1_interim, then V1_interim→V0 via theOldVertices(V_interim)=V_old. Result: theNewVertices[V_old]=[...,V0].
- **Search anchors**: 'if (theOldVertices.IsBound(theNew))', 'Transitive mapping'

##### `ShapeFix_FaceConnect.Build.VERTEX_POSITION_AGGREGATION`
- **Line**: ShapeFix_FaceConnect.cxx:707-740  **Axis**: `tolerance`
- **Brief**: New vertex position calculated as midpoint of bounding box across all mapped vertices.
- **Falsifiable claim**: Without aggregation, arbitrary position chosen; merged vertices scatter. To test: map V1@(0,0), V2@(2,0), V3@(4,0) to V_new; verify V_new≈(2,0).
- **Minimal reproducer**: theRV2Iter(V_old)=[V_new@(1,0), V_alt@(3,0)]. LBound=(1,0), RBound=(3,0). Position=(2,0). V_new repositioned to (2,0).
- **Search anchors**: 'thePosition = gp_Pnt((theLBound.XYZ() + theRBound.XYZ()) / 2.)'

##### `ShapeFix_FaceConnect.Build.VERTEX_TOLERANCE_AGGREGATION`
- **Line**: ShapeFix_FaceConnect.cxx:742-759  **Axis**: `tolerance`
- **Brief**: Tolerance of merged vertex inflated to contain all originals plus repositioning error.
- **Falsifiable claim**: Without aggregation, tolerance too tight; repositioning errors exceed bounds. To test: verify final tolerance ≥ max(dist(position, vertex_i) + tol_i).
- **Minimal reproducer**: V1@(0,0) tol=0.01, V2@(0.05,0) tol=0.02. Position=(0.025,0). Max distance 0.025+0.02=0.045. theTolerance=0.045.
- **Search anchors**: 'theTolerance = curtoler'

##### `ShapeFix_FaceConnect.Build.VERTEX_REPLACEMENT_RESHAPE`
- **Line**: ShapeFix_FaceConnect.cxx:764-771  **Axis**: `healer-state`
- **Brief**: Vertex replacement applied via ReShape after edge replacement; oriented forward.
- **Falsifiable claim**: Without reshaping, old vertices remain; new positions ignored. To test: verify ReShape.Apply() substitutes vertices throughout shell.
- **Minimal reproducer**: theOldVertices: V1_old→V1_new. ReShape.Replace(V1_old, V1_new). ReShape.Apply(result). Shell vertices updated.
- **Search anchors**: 'theReShape->Replace(theNVIter.Key()..., theNVIter.Value()...)'

##### `ShapeFix_FaceConnect.Build.VERTEX_RESHAPE_FAILURE`
- **Line**: ShapeFix_FaceConnect.cxx:777-782  **Axis**: `api-contract`
- **Brief**: Vertex replacement failure (FAIL1) logged; result returned unchanged.
- **Falsifiable claim**: Without fallback, exception halts Build(); caller unaware replacement failed. To test: construct invalid vertex replacement; verify warning, return modified shell.
- **Minimal reproducer**: theOldVertices contains degenerate vertex. ReShape.Apply() fails. Status(ShapeExtend_FAIL1)=true. Log error; return result.
- **Search anchors**: 'if (theReShape->Status(ShapeExtend_FAIL1))'

##### `ShapeFix_FaceConnect.Build.EMPTY_RESULT_EDGES`
- **Line**: ShapeFix_FaceConnect.cxx:547  **Axis**: `healer-state`
- **Brief**: No edge replacement performed if theRepEdges map empty after sewing.
- **Falsifiable claim**: Without guard, ReShape.Apply() on empty replacements yields input unchanged; unnecessary work. To test: sew with no successful modifications; verify theRepEdges.IsEmpty()=true, skip ReShape.
- **Minimal reproducer**: All sewing attempts fail or modify nothing. theRepEdges remains empty. IsEmpty()=true; skip entire reshape block.
- **Search anchors**: 'if (!theRepEdges.IsEmpty())'

##### `ShapeFix_FaceConnect.Build.SHELL_CLOSURE_STATE`
- **Line**: ShapeFix_FaceConnect.cxx:646  **Axis**: `kernel-pair`
- **Brief**: Reconstructed shell marked closed if BRep_Tool detects closure.
- **Falsifiable claim**: Without explicit closure marking, kernel may not recognize topologically-closed shells. To test: verify result.Closed() matches BRep_Tool::IsClosed(result).
- **Minimal reproducer**: theShell reconstructed with all boundary edges internal. BRep_Tool::IsClosed()=true. theShell.Closed(true). Subsequent queries return closed=true.
- **Search anchors**: 'theShell.Closed(BRep_Tool::IsClosed(theShell))'

##### `ShapeFix_FaceConnect.Build.EMPTY_VERTICES_REPLACEMENT`
- **Line**: ShapeFix_FaceConnect.cxx:649  **Axis**: `healer-state`
- **Brief**: Vertex replacement skipped if no vertices mapped; rare case avoids unnecessary work.
- **Falsifiable claim**: Without guard, empty ReShape.Apply() performs no-op; returns input unchanged. To test: sew without vertex misalignment; verify theRepVertices.IsEmpty()=true, skip vertex phase.
- **Minimal reproducer**: All vertex matches perfect; theNewV matches theOldV exactly. theRepVertices remains empty. IsEmpty()=true; skip vertex replacement.
- **Search anchors**: 'if (!theRepVertices.IsEmpty())'

##### `ShapeFix_FaceConnect.Build.CONNECTED_FACES_ITERATION`
- **Line**: ShapeFix_FaceConnect.cxx:180-369  **Axis**: `api-contract`
- **Brief**: Process only face pairs registered in myConnected map; unregistered faces ignored.
- **Falsifiable claim**: Without filtering, all free edges in shell would sew together; disconnected faces incorrectly repaired. To test: add only F1,F2 via Add(); verify F3's edges untouched.
- **Minimal reproducer**: Add(F1,F2). Shell has F1,F2,F3. Build() processes F1-F2 sewing. F3's edges skip theFreeEdges map entry because F3 not in myConnected.
- **Search anchors**: 'for (...Iterator theConnectedIter(myConnected))'

##### `ShapeFix_FaceConnect.Build.ORIGINAL_FREE_EDGES_ACCUMULATION`
- **Line**: ShapeFix_FaceConnect.cxx:108-119  **Axis**: `healer-state`
- **Brief**: Original free edges mapped per-face; multiple calls append to existing lists.
- **Falsifiable claim**: Without accumulation, multiple free edges on same face would overwrite; only last edge retained. To test: face with E1,E2 free; verify myOriFreeEdges[F]=[E1,E2].
- **Minimal reproducer**: Face F with free edges E1, E2. First: myOriFreeEdges(F)=[E1]. Second: myOriFreeEdges(F).Append(E2). Result: [E1,E2].
- **Search anchors**: 'myOriFreeEdges(theFace).Append(theEdge)', 'Append free edge to the new list'

##### `ShapeFix_FaceConnect.Build.WIRE_PRECISION_SYNC`
- **Line**: ShapeFix_FaceConnect.cxx:625-626  **Axis**: `tolerance`
- **Brief**: Wire fixer precision set to fixtoler; max tolerance capped at sewtoler.
- **Falsifiable claim**: Without precision sync, wire fixing uses default tolerance; edge curves deviate beyond sewing bounds. To test: verify SFW.SetPrecision(fixtoler); SFW.SetMaxTolerance(sewtoler).
- **Minimal reproducer**: fixtoler=0.001, sewtoler=0.01. SFW->SetPrecision(0.001); SFW->SetMaxTolerance(0.01). Curves adjusted within 0.01 bound.
- **Search anchors**: 'SFW->SetPrecision(fixtoler)', 'SFW->SetMaxTolerance(sewtoler)'

##### `ShapeFix_FaceConnect.Build.WIRE_EDGE_CURVE_FIX`
- **Line**: ShapeFix_FaceConnect.cxx:628  **Axis**: `healer-state`
- **Brief**: Edge curves within wires corrected to match parametric domains.
- **Falsifiable claim**: Without fixing, replaced edges may have parametric discontinuities; subsequent operations fail. To test: verify FixEdgeCurves() applied before self-intersection check.
- **Minimal reproducer**: Wire after replacement has edge with mismatched PCurve. FixEdgeCurves() aligns curve with face parameter space.
- **Search anchors**: 'SFW->FixEdgeCurves()'

##### `ShapeFix_FaceConnect.Build.WIRE_SELF_INTERSECTION_FIX`
- **Line**: ShapeFix_FaceConnect.cxx:629  **Axis**: `healer-state`
- **Brief**: Self-intersecting wires corrected after edge curve fixing.
- **Falsifiable claim**: Without fixing, wires with loops remain; topology invalid. To test: wire with self-crossing edges; verify FixSelfIntersection() removes crossings.
- **Minimal reproducer**: Reconstructed wire has edges crossing. FixSelfIntersection() splits/reorders edges to remove loops.
- **Search anchors**: 'SFW->FixSelfIntersection()'

##### `ShapeFix_FaceConnect.Build.SEWING_WIRE_CONSTRUCTION`
- **Line**: ShapeFix_FaceConnect.cxx:267-272  **Axis**: `healer-state`
- **Brief**: Free edges wrapped in individual wires for sewing; wire-to-edge mapping maintained.
- **Falsifiable claim**: Without wire wrapping, sewer cannot track individual edge modifications. To test: verify each free edge becomes wire; each wire in theSewerWires map.
- **Minimal reproducer**: Original edge E. Create wire W with E. Bind W→E in theSewerWires. Add W to theSewer. Post-sewing, modified wires tracked.
- **Search anchors**: 'theBuilder.MakeWire(theAuxW)', 'theSewerWires.Bind(theAuxE, theAuxW)'

##### `ShapeFix_FaceConnect.Build.AUXILIARY_FACE_WRAPPING`
- **Line**: ShapeFix_FaceConnect.cxx:255  **Axis**: `kernel-pair`
- **Brief**: Empty faces created to contain wires; geometry preserved via EmptyCopied.
- **Falsifiable claim**: Without face wrapping, sewer misses face orientation context; results may be self-intersecting. To test: sewer.Add(Face,Wire) vs. sewer.Add(Wire); verify face context aids.
- **Minimal reproducer**: Face F copied empty. Wires W1,W2 from F's boundary added to empty copy. Both added to sewer along with faces.
- **Search anchors**: 'TopoDS_Shape theFaceToSew = theFacesToSew(i)', 'theAuxF = theFaceToSew.EmptyCopied()'

##### `ShapeFix_FaceConnect.Build.FACE_LIST_INIT`
- **Line**: ShapeFix_FaceConnect.cxx:195  **Axis**: `healer-state`
- **Brief**: Processed face list cleared for each first-face iteration; tracks second-face pairings.
- **Falsifiable claim**: Without per-face list, processed pairs leak across first-face iterations; deduplication fails. To test: verify theProcessedList fresh for each theFirstFace.
- **Minimal reproducer**: F1->[F2,F3], F2->[F1]. Process F1-F2 (added to theProcessedList). Later F2-F1 skipped. F2's list is new (not inherited from F1).
- **Search anchors**: 'NCollection_List<TopoDS_Shape> theProcessedList'

##### `ShapeFix_FaceConnect.Build.NUM_FACES_SEWING_GUARD`
- **Line**: ShapeFix_FaceConnect.cxx:251-277  **Axis**: `healer-state`
- **Brief**: Loop iterates theNumOfFacesToSew (1 or 2); single face passes but does not sew.
- **Falsifiable claim**: Without guard, self-connected faces would still run sewer; topology corrupted. To test: add(F,F); verify loop runs but theNumOfFacesToSew=1, sewer receives single face.
- **Minimal reproducer**: theNumOfFacesToSew=1 (self-connected). Loop i=1: adds F. i=2: condition false, skip. Sewer contains only F; no sewing occurs.
- **Search anchors**: 'for (i = 1; i <= theNumOfFacesToSew; i++)'


### ShapeFix_FixSmallFace

#### `ShapeFix_FixSmallFace.FixPinFace`
 (0 branches; source: `v3-deep-ShapeFix_FixSmallFace_FixPinFace.json`)

**Stub analysis:**
- `is_noop_stub`: `True`
- Body: literal `return true;` with no implementation — accepts parameter `F` but never modifies it or the shape context
- Intended defect class (if implemented): `ShapeFix_FixSmallFace.FixPinFace.UNIMPLEMENTED.pin_face_repair`
- Falsifiable claim: If implemented, this method would remove or repair faces with 'pin' singularities (pole-collapsed NURBS edges where one row of control points degenerates to a point). Currently it returns true without modifying the shape. Calling ShapeFix_FixSmallFace::FixShape processes spot and strip faces but skips all FixPinFace logic — pin-face fixtures in regression catalogs exercise detection (CheckPin/CheckPinFace) but no actual kernel repair. A kernel-grading consumer should treat pin-face test fixtures
- Minimal reproducer: Construct an ADVANCED_FACE with a BSpline surface where one boundary row of poles has collapsed (e.g. all U=umax poles at identical (x,y,z) in 3D space). This represents a topological singularity or 'pin' — the face has infinite curvature at one edge. The face will pass CheckPin()==true and CheckPinFace() will identify the two edges adjacent to the pin. Call ShapeFix_FixSmallFace::FixShape(). Without an implemented FixPinFace: the pin face survives unchanged (only Spot and Strip repairs are appl


### ShapeFix_IntersectionTool

#### `ShapeFix_IntersectionTool.FixSelfIntersectWire`
 (31 branches; 2 low-confidence; source: `v3-deep-ShapeFix_IntersectionTool_FixSelfIntersectWire.json`)

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.null_context_face_validation`
- **Line**: ShapeFix_IntersectionTool.cxx:1038  **Axis**: `api-contract`
- **Brief**: Early exit when context or face is null.
- **Falsifiable claim**: Without this branch, dereferencing myContext or face later would cause null-pointer crash or undefined behavior. To test: call FixSelfIntersectWire with null context or null face, verify early return (false) vs. crash.
- **Minimal reproducer**: Create wire with known self-intersection. Call FixSelfIntersectWire(wire, nullptr, tolerance) or FixSelfIntersectWire(wire, context, TopoDS_Face()) without null checks. Without: segfault on myContext->IsNull(). With: returns false immediately.
- **Search anchors**: 'null check context', 'null face parameter', 'validation guard'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.loop_bounds_split_limit`
- **Line**: ShapeFix_IntersectionTool.cxx:1059  **Axis**: `healer-state`
- **Brief**: Outer loop terminates when NbSplit reaches 30 to prevent runaway iteration.
- **Falsifiable claim**: Without this branch, pathological wires with many self-intersections would undergo unbounded edge splitting, possibly creating >100 edges and consuming memory/time. To test: construct wire with 40+ intersections; count final edges with/without NbSplit<30 gate.
- **Minimal reproducer**: Construct dense self-intersecting wire (e.g., star pattern with 50 ray-edges, many crossing). Trigger FixSelfIntersectWire. Monitor NbSplit counter. Without limit: loop continues indefinitely or creates 100+ edges. With: halts at NbSplit=30, leaving some intersections unresolved.
- **Search anchors**: 'NbSplit < 30', 'split limit 30', 'runaway iteration'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.same_edge_self_intersection_guard`
- **Line**: ShapeFix_IntersectionTool.cxx:1074  **Axis**: `input-shape`
- **Brief**: Skips comparison when edge1 and edge2 refer to the same object.
- **Falsifiable claim**: Without this guard, computing intersections of an edge with itself produces spurious parametric points, leading to false edge splits and topology corruption. To test: wire with a repeated edge reference; observe split behavior.
- **Minimal reproducer**: Create wire where edge E appears twice (e.g., forward then backward). Call FixSelfIntersectWire. Without guard: intersection algorithm reports fake intersection points (e.g., at arbitrary parameters like 0.3 and 0.7). With guard: skips self-comparison, no false splits.
- **Search anchors**: 'edge1.IsSame(edge2)', 'self-comparison guard'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.degenerate_edge_filter`
- **Line**: ShapeFix_IntersectionTool.cxx:1078  **Axis**: `input-shape`
- **Brief**: Excludes degenerate edges (zero-length or collapsed domain) from intersection testing.
- **Falsifiable claim**: Without this filter, degenerate curve intersection algorithms fail or produce NaN parameters, causing crashes in parametric range calculations or infinite loops. To test: wire with degenerate edge (poles, cone apex); verify no crash with guard.
- **Minimal reproducer**: Construct wire with degenerate edge (e.g., BRepBuilderAPI_MakeEdge at cone apex where start==end). Add non-degenerate crossing edge. Call FixSelfIntersectWire. Without filter: NaN parameters or numerical exception. With filter: degenerate edge skipped, no crash.
- **Search anchors**: 'BRep_Tool::Degenerated', 'degenerate curve filter'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.bounding_box_presence_check` **[low-confidence]**
- **Line**: ShapeFix_IntersectionTool.cxx:1082  **Axis**: `healer-state`
- **Brief**: Verifies bounding box metadata exists before spatial intersection tests.
- **Falsifiable claim**: Without this check, accessing non-existent bounding boxes causes exceptions or uses garbage memory, leading to false spatial exclusions or erroneous intersection reports. To test: manually unregister a bounding box; verify crash prevention.
- **Minimal reproducer**: Create wire with edges. Register bounding boxes for all but one edge. Call FixSelfIntersectWire. Without check: exception or undefined behavior when accessing unregistered box. With check: safely skips unregistered edge, no crash.
- **Search anchors**: 'boxes.IsBound', 'bounding box registration'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.spatial_overlap_prefilter`
- **Line**: ShapeFix_IntersectionTool.cxx:1087  **Axis**: `kernel-pair`
- **Brief**: Spatial pre-filter: skips expensive curve intersection if bounding boxes don't overlap.
- **Falsifiable claim**: Without this optimization, all O(n²) non-adjacent edge pairs undergo full curve intersection computation, causing 10x+ slowdown on large wires and potential false positives from numerical noise. To test: large wire with spatially separated edges; measure time.
- **Minimal reproducer**: Construct wire with 20 edges, arranged spatially separated (e.g., box corners). Time FixSelfIntersectWire with/without B1.IsOut(B2) check (simulate by forcing entry). Without prefilter: 10-50x slower, possible false intersections. With prefilter: fast spatial rejection.
- **Search anchors**: 'IsOut bounding box', 'spatial prefilter'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.intersection_algorithm_success_check`
- **Line**: ShapeFix_IntersectionTool.cxx:1099  **Axis**: `kernel-pair`
- **Brief**: Validates that curve intersection algorithm completed successfully before accessing results.
- **Falsifiable claim**: Without this check, accessing NbPoints() or NbSegments() on failed intersection objects causes undefined behavior, crashes, or processes garbage topology. To test: singular or nearly-parallel curves; verify no crash.
- **Minimal reproducer**: Construct wire with nearly-parallel edges (e.g., tangent lines 0.001mm apart) causing intersection algorithm convergence failure. Call FixSelfIntersectWire. Without check: crash or undefined memory access. With check: safely skips failed intersection.
- **Search anchors**: 'Inter.IsDone()', 'intersection validation'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.point_intersection_branch_selector`
- **Line**: ShapeFix_IntersectionTool.cxx:1103  **Axis**: `input-shape`
- **Brief**: Routes to point-intersection handler when NbPoints in range [1,2].
- **Falsifiable claim**: Without this branch, isolated intersection points (most common case) would be misrouted to segment handler, causing incorrect split decisions or missed intersections. To test: wire with 1-2 intersection points; verify correct resolution.
- **Minimal reproducer**: Construct two edges crossing at single point (e.g., line segments X and + in 2D). Call FixSelfIntersectWire. Without branch: segment logic applied incorrectly. With branch: single point detected, correct split at intersection.
- **Search anchors**: 'NbPoints() > 0 && < 3', 'point intersection routing'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.both_curves_interior_intersection`
- **Line**: ShapeFix_IntersectionTool.cxx:1110  **Axis**: `input-shape`
- **Brief**: Detects intersection at interior parameters on both curves (transverse crossing).
- **Falsifiable claim**: Without this branch, transverse interior intersections would be misclassified as endpoint intersections, causing wrong vertex assignments or topology errors. To test: two edges crossing at interior points; verify correct classification.
- **Minimal reproducer**: Create edges E1 (parametric [0,1]) and E2 ([0,1]) intersecting at parameters (0.3, 0.4). Call FixSelfIntersectWire. Without branch: position classification fails, incorrect split. With branch: both-interior correctly identified, proper split at 0.3 and 0.4.
- **Search anchors**: 'PositionOnCurve() == IntRes2d_Middle (both)', 'interior crossing'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.snap_to_existing_vertex_e1`
- **Line**: ShapeFix_IntersectionTool.cxx:1180  **Axis**: `tolerance`
- **Brief**: When intersection near edge1 endpoint but edge2 interior, snap edge1 to existing vertex and split edge2.
- **Falsifiable claim**: Without this branch, vertex merging logic would create redundant new vertices instead of reusing nearby existing ones, increasing vertex count and tolerance stack. To test: intersection near edge endpoint; count vertices.
- **Minimal reproducer**: Create E1 and E2 crossing such that intersection point on E1 is 0.001mm from E1's first vertex V1, and E2 interior at parameter 0.5. Call FixSelfIntersectWire. Without branch: new vertex created even though V1 exists. With branch: V1 reused, E2 split at 0.5 using V1.
- **Search anchors**: 'ModifE1 && !ModifE2', 'snap to existing vertex'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.snap_to_existing_vertex_e2`
- **Line**: ShapeFix_IntersectionTool.cxx:1188  **Axis**: `tolerance`
- **Brief**: When intersection near edge2 endpoint but edge1 interior, snap edge2 to existing vertex and split edge1.
- **Falsifiable claim**: Without this branch, symmetric case (edge2 endpoint vs. edge1 interior) would not be handled, causing asymmetric topology or missed optimizations. To test: swapped roles compared to previous case; verify symmetric behavior.
- **Minimal reproducer**: Create E1 and E2 where E2 endpoint is 0.001mm from intersection, E1 interior. Call FixSelfIntersectWire. Without branch: asymmetric handling or crash. With branch: E2 endpoint reused, E1 split symmetrically.
- **Search anchors**: '!ModifE1 && ModifE2', 'snap to existing vertex (symmetric)'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.create_new_vertex_for_point_intersection`
- **Line**: ShapeFix_IntersectionTool.cxx:1195  **Axis**: `healer-state`
- **Brief**: Creates synthetic vertex at intersection midpoint when neither edge endpoint is within tolerance.
- **Falsifiable claim**: Without this branch, intersections far from endpoints would fail to resolve, leaving self-intersections unhealed or causing topology corruption. To test: interior-interior crossing away from vertices; verify split.
- **Minimal reproducer**: Create E1([0,1] from (0,0) to (1,1)) and E2([0,1] from (1,0) to (0,1)) intersecting at (0.5, 0.5), all far from endpoints. Call FixSelfIntersectWire. Without branch: no split occurs. With branch: new vertex created at (0.5,0.5), both edges split.
- **Search anchors**: 'create new vertex', 'midpoint vertex synthesis'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.first_curve_interior_second_endpoint`
- **Line**: ShapeFix_IntersectionTool.cxx:1215  **Axis**: `input-shape`
- **Brief**: Branch for intersection interior on edge1, at endpoint on edge2.
- **Falsifiable claim**: Without this branch, mixed-position intersections (interior vs. endpoint) would fall through or misroute, causing asymmetric splits or missed merges. To test: asymmetric position intersection; verify correct resolution.
- **Minimal reproducer**: Create E1([0,1]) intersecting E2([0,1]) at parameter (0.5, 0) on E2's start. Call FixSelfIntersectWire. Without branch: misroutes to default handler. With branch: recognizes asymmetry, applies correct endpoint-handling strategy.
- **Search anchors**: 'PositionOnCurve() == IntRes2d_Middle (first) && != (second)', 'asymmetric position'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.second_curve_interior_first_endpoint`
- **Line**: ShapeFix_IntersectionTool.cxx:1229  **Axis**: `input-shape`
- **Brief**: Branch for intersection interior on edge2, at endpoint on edge1 (symmetric to line 1215).
- **Falsifiable claim**: Without this symmetric branch, reversed-position intersections would not be handled, causing topology asymmetry or missed merges. To test: swap edge roles from line 1215 case; verify same correctness.
- **Minimal reproducer**: Create E1([0,1]) and E2([0,1]) intersecting at (0, 0.5), where E1 is at endpoint. Call FixSelfIntersectWire. Without branch: fails to detect symmetric case. With branch: handles symmetrically to line 1215.
- **Search anchors**: 'PositionOnCurve() == IntRes2d_Middle (second) && != (first)', 'symmetric asymmetric position'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.both_curves_at_endpoints`
- **Line**: ShapeFix_IntersectionTool.cxx:1243  **Axis**: `input-shape`
- **Brief**: When both intersection points are at edge endpoints, merge vertices without splitting.
- **Falsifiable claim**: Without this branch, endpoint-endpoint intersections would trigger spurious splits, creating redundant edges and complicating topology. To test: edges meeting at endpoint; verify no extra splits.
- **Minimal reproducer**: Create E1 ending at point P and E2 starting at P (touching at endpoint). Call FixSelfIntersectWire. Without branch: might split both edges unnecessarily. With branch: recognizes endpoint meeting, merges vertices via B.UpdateVertex, no splits.
- **Search anchors**: 'both endpoints intersection', 'vertex merge without split'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.segment_intersection_branch_selector`
- **Line**: ShapeFix_IntersectionTool.cxx:1251  **Axis**: `input-shape`
- **Brief**: Routes to segment-intersection handler when curves have overlapping segments.
- **Falsifiable claim**: Without this branch, overlapping-segment cases would fall through to undefined behavior or be mishandled as point intersections, causing topology corruption. To test: two edges with overlapping segments; verify correct segment resolution.
- **Minimal reproducer**: Create E1 and E2 as collinear line segments with partial overlap (e.g., [0,2] and [1,3]). Call FixSelfIntersectWire. Without branch: misroutes to point handler. With branch: segment overlap detected, both edges split at overlap boundaries.
- **Search anchors**: 'NbSegments() == 1', 'segment intersection routing'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.segment_endpoint_validation` **[low-confidence]**
- **Line**: ShapeFix_IntersectionTool.cxx:1253  **Axis**: `kernel-pair`
- **Brief**: Validates that segment overlap has both endpoints defined.
- **Falsifiable claim**: Without this validation, incomplete segment definitions would cause crashes when accessing segment endpoints or calculating split parameters. To test: degenerate segment; verify no crash.
- **Minimal reproducer**: Construct overlapping segments where segment object lacks defined endpoints. Call FixSelfIntersectWire. Without validation: crash on IS.FirstPoint() access. With validation: safely skips incomplete segment.
- **Search anchors**: 'HasFirstPoint() && HasLastPoint()', 'segment endpoint validation'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.segment_endpoint_tolerance_check`
- **Line**: ShapeFix_IntersectionTool.cxx:1279  **Axis**: `tolerance`
- **Brief**: Rejects segments where computed endpoints deviate excessively from expected geometry.
- **Falsifiable claim**: Without this check, segments with inconsistent endpoints (possibly from numerical errors) would be processed, leading to incorrect splits or topology corruption. To test: segment with endpoint mismatch; verify rejection.
- **Minimal reproducer**: Construct overlapping segment where calculated Pnt11 differs from Pnt21 by >MaxTolVert. Call FixSelfIntersectWire. Without check: processes inconsistent segment, wrong split. With check: rejects segment, no split.
- **Search anchors**: 'Pnt11.Distance(Pnt21) > MaxTolVert', 'segment consistency validation'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.segment_touches_edge1_only`
- **Line**: ShapeFix_IntersectionTool.cxx:1342  **Axis**: `input-shape`
- **Brief**: Segment modifies only edge1; split edge2 using vertices from edge1 intersection.
- **Falsifiable claim**: Without this branch, segments touching only one edge would not be properly resolved, leaving partial intersections unhealed. To test: segment overlapping only one edge; verify only that edge splits.
- **Minimal reproducer**: Create segment overlapping E1([0,2]) fully but not touching E2. Set IsModified1=true, IsModified2=false. Without branch: E2 not split. With branch: E1 used to determine split points on E2.
- **Search anchors**: 'IsModified1 && !IsModified2', 'single-edge segment touch'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.segment_touches_edge2_only`
- **Line**: ShapeFix_IntersectionTool.cxx:1350  **Axis**: `input-shape`
- **Brief**: Segment modifies only edge2; split edge1 using vertices from edge2 intersection.
- **Falsifiable claim**: Without this branch, symmetric case (segment touching only edge2) would not be handled, causing asymmetric healing or missed splits. To test: segment overlapping only edge2; verify correct handling.
- **Minimal reproducer**: Create segment overlapping E2 only, with IsModified1=false, IsModified2=true. Without branch: E1 not split. With branch: E2 intersection determines splits on E1.
- **Search anchors**: '!IsModified1 && IsModified2', 'single-edge segment touch (symmetric)'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.segment_touches_both_edges`
- **Line**: ShapeFix_IntersectionTool.cxx:1358  **Axis**: `input-shape`
- **Brief**: Segment overlaps both edges; triggers major reconstruction logic including large-segment 3-edge split.
- **Falsifiable claim**: Without this branch, segments overlapping both edges would be incompletely resolved, possibly leaving partial intersections or creating degenerate topology. To test: segment overlapping both edges; verify complete resolution.
- **Minimal reproducer**: Create E1([0,2]) and E2([0.5, 2.5]) with segment overlap [0.5, 2]. Set IsModified1=true, IsModified2=true. Without branch: incomplete split. With branch: full 3-edge reconstruction if >50% overlap, else simple 2-edge split.
- **Search anchors**: '!IsModified1 && !IsModified2 (major processing)', 'both-edge segment processing'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.large_segment_overlap_3_edge_split`
- **Line**: ShapeFix_IntersectionTool.cxx:1369  **Axis**: `healer-state`
- **Brief**: Segment exceeds 50% of either edge length; triggers 3-edge reconstruction instead of simple 2-edge split.
- **Falsifiable claim**: Without this branch, large overlaps would be split at only 2 points, leaving significant portions of original geometry unrepaired; with it, intermediate vertices ensure finer control. To test: segment 60% of edge; verify 3-vertex splitting.
- **Minimal reproducer**: Create E1([0,1]) and E2([0,1]) with overlapping segment [0.1, 0.7] (>50% of length). Call FixSelfIntersectWire. Without branch: splits at 0.1 and 0.7 only (2 vertices). With branch: intermediate vertex created, finer reconstruction (3 vertices).
- **Search anchors**: 'std::abs(p12-p11) > std::abs(b1-a1)/2', 'large segment 3-edge split'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.large_segment_vertex_merging`
- **Line**: ShapeFix_IntersectionTool.cxx:1408  **Axis**: `tolerance`
- **Brief**: Within 3-edge split, checks if segment endpoints P01/P02 merge with existing vertices V1/V2.
- **Falsifiable claim**: Without this merging logic, 3-edge reconstruction would create new vertices even when existing ones are nearby, inflating vertex count and tolerance accumulation. To test: large segment with endpoint near existing vertex; count vertices.
- **Minimal reproducer**: Create 3-edge split scenario where P01 (first segment point) is 0.001mm from edge1's first vertex V1. Without branch: NewV1 created as separate vertex. With branch: V1 reused, updated tolerance if needed.
- **Search anchors**: 'P01.Distance(PV1) < tolV1', 'endpoint vertex merging in 3-edge split'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.ambiguous_vertex_rejection`
- **Line**: ShapeFix_IntersectionTool.cxx:1530  **Axis**: `tolerance`
- **Brief**: Rejects reconstruction if a segment endpoint matches multiple existing vertices (akey>1).
- **Falsifiable claim**: Without this check, ambiguous vertex assignments (point near multiple vertices) would cause unpredictable topology or incorrect merges. To test: point equidistant from two vertices; verify rejection.
- **Minimal reproducer**: Create geometry where segment point P01 is 0.01mm from both V1 and V2 (both within tolerance). Call FixSelfIntersectWire. Without check: akey becomes 2, leading to undefined behavior. With check: skipped (continue), segment not processed.
- **Search anchors**: 'akey1 > 1 || akey2 > 1', 'ambiguous vertex detection'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.akey_first_point_new_second_existing`
- **Line**: ShapeFix_IntersectionTool.cxx:1552  **Axis**: `healer-state`
- **Brief**: First segment point is new (P01), second matches existing vertex (P02→V2); split edge1 at P11.
- **Falsifiable claim**: Without this branch, mixed new-existing point cases would misroute to full 2-vertex creation, missing optimization of reusing existing vertex. To test: akey1=0, akey2>0; verify only first point split.
- **Minimal reproducer**: Set up large segment where P01 is new, P02 matches V2 within tolerance. Invoke split logic. Without branch: creates NewV1 and NewV2. With branch: creates only NewV1, uses V2 directly.
- **Search anchors**: 'akey1 == 0 && akey2 > 0', 'first-new second-existing split'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.akey_first_existing_second_new`
- **Line**: ShapeFix_IntersectionTool.cxx:1560  **Axis**: `healer-state`
- **Brief**: First segment point matches existing vertex (P01→V1), second is new (P02); split edge1 at P12.
- **Falsifiable claim**: Without this branch, symmetric case would not be optimized, creating redundant vertices. To test: akey1>0, akey2=0; verify only second point split.
- **Minimal reproducer**: Set P01 matching V1, P02 new. Without branch: creates both NewV1 and NewV2. With branch: creates only NewV2, reuses V1.
- **Search anchors**: 'akey1 > 0 && akey2 == 0', 'first-existing second-new split'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.akey_both_points_new`
- **Line**: ShapeFix_IntersectionTool.cxx:1568  **Axis**: `healer-state`
- **Brief**: Both segment points are new (P01, P02 not matching existing vertices); creates NewV1, NewV2, handles edge crossing.
- **Falsifiable claim**: Without this branch, interior-only segments (no endpoint merges) would not split at both points, leaving partial overlap unresolved. To test: segment interior to both edges; verify both-point splitting.
- **Minimal reproducer**: Create segment [0.2, 0.8] on E1, [0.3, 0.7] on E2, with both points away from any edge endpoint. Without branch: undefined handling. With branch: NewV1 and NewV2 created, edge crossing logic determines if second point splits adjacent edge.
- **Search anchors**: 'akey1 == 0 && akey2 == 0', 'both-new-point split with edge crossing'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.edge_crossing_detection_parameter_bounds`
- **Line**: ShapeFix_IntersectionTool.cxx:1597  **Axis**: `input-shape`
- **Brief**: Determines if split parameter p12 lies outside edge1 bounds, requiring next-edge splitting.
- **Falsifiable claim**: Without this boundary detection, multi-edge overlaps would be split incorrectly (e.g., extending splits beyond segment length), causing topology discontinuities. To test: segment crossing edge boundary; verify correct adjacent-edge split.
- **Minimal reproducer**: Create E1([0,1]) and E2([0,1]) with overlapping segment [0.5, 1.2], where 1.2 exceeds E1's range. Without check: splits at invalid parameter 1.2. With check: detects (a-p12)*(b-p12)>0, splits adjacent edge instead.
- **Search anchors**: '(a - p12) * (b - p12) > 0', 'parameter range crossing detection'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.edge_crossing_detection_second_point`
- **Line**: ShapeFix_IntersectionTool.cxx:1649  **Axis**: `input-shape`
- **Brief**: Determines if second segment endpoint p22 lies outside edge2 bounds, requiring next-edge splitting.
- **Falsifiable claim**: Without this check, multi-segment reconstructions would fail to handle parameter ranges crossing wire loops, leaving topology broken at boundary. To test: segment endpoint beyond current edge; verify adjacent edge split.
- **Minimal reproducer**: Overlapping segment [0.3, 1.1] on E2([0,1]). Without check: parameter 1.1 used directly on E2. With check: detects crossing, applies split to next edge in wire loop.
- **Search anchors**: '(a - p22) * (b - p22) > 0 (second)', 'second-edge parameter crossing'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.multi_split_reconstruction_threshold`
- **Line**: ShapeFix_IntersectionTool.cxx:1659  **Axis**: `healer-state`
- **Brief**: Reapplies 50%-overlap threshold check to determine if current segment requires 3-edge splitting.
- **Falsifiable claim**: Without this secondary threshold check, small overlaps would be treated identically to large ones, losing optimization and potentially over-splitting. To test: 40% overlap vs. 60% overlap; verify different handling.
- **Minimal reproducer**: Create two segments on same edge pair: one 40% overlap, one 60%. Call FixSelfIntersectWire. Without check: both treated same. With check: 40% receives simple 2-vertex split, 60% receives 3-edge reconstruction.
- **Search anchors**: 'std::abs(p12-p11) > std::abs(b1-a1)/2 (multi-split)', 'secondary overlap threshold'

##### `ShapeFix_IntersectionTool.FixSelfIntersectWire.iteration_break_after_modification`
- **Line**: ShapeFix_IntersectionTool.cxx:1686  **Axis**: `healer-state`
- **Brief**: Breaks inner loop after modifying an edge to prevent reprocessing modified geometry.
- **Falsifiable claim**: Without this break, reprocessing modified edges could cause infinite loops or redundant splits. To test: track loop iterations before/after modification; verify count reduction.
- **Minimal reproducer**: Construct multi-edge wire triggering multiple splits in sequence. Without break: inner loop reprocesses newly-split edges, causing O(n³) behavior. With break: breaks after each split, maintaining O(n²).
- **Search anchors**: 'num1--; break', 'loop termination after modification'


### ShapeFix_IntersectionTool::FixIntersectingWires

#### `ShapeFix_IntersectionTool::FixIntersectingWires`
 (50 branches; source: `v3-deep-ShapeFix_IntersectionTool_FixIntersectingWires.json`)

##### `ShapeFix_IntersectionTool.FixIntersectingWires.NULL_CONTEXT_OR_FACE`
- **Line**: ShapeFix_IntersectionTool.cxx:1837  **Axis**: `api-contract`
- **Brief**: Early return if myContext or face is null.
- **Falsifiable claim**: Without this check, null dereference crashes. To test: pass null context or face; should return false immediately.
- **Minimal reproducer**: Invoke FixIntersectingWires with null myContext or null face. Expected: return false. Without: segfault on myContext->Replace().
- **Search anchors**: 'myContext.IsNull()', 'face.IsNull()'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.NON_WIRE_SHAPE_FILTER`
- **Line**: ShapeFix_IntersectionTool.cxx:1849  **Axis**: `input-shape`
- **Brief**: Skip non-WIRE shapes and malformed wire orientations.
- **Falsifiable claim**: Without filtering non-WIRE shapes, algorithm operates on invalid topology. To test: pass face with EDGE/SHELL children instead of WIRE; should isolate to SeqNMShapes.
- **Minimal reproducer**: Create Face with mixed WIRE and EDGE children. Trigger FixIntersectingWires. Verify non-WIRE shapes reach SeqNMShapes at line 2520.
- **Search anchors**: 'iter.Value().ShapeType() != TopAbs_WIRE', 'TopAbs_FORWARD', 'TopAbs_REVERSED'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.MINIMUM_WIRE_COUNT`
- **Line**: ShapeFix_IntersectionTool.cxx:1859  **Axis**: `input-shape`
- **Brief**: Return false if fewer than 2 wires (no pairs to intersect).
- **Falsifiable claim**: Without this check, algorithm runs empty loops. To test: face with 1 wire; should return false immediately.
- **Minimal reproducer**: Create face with single wire. Invoke FixIntersectingWires. Expected: return false (isDone=false). Without: exits after all loops trivially.
- **Search anchors**: 'SeqWir.Length() < 2'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.MAX_VERTEX_TOLERANCE_SEED`
- **Line**: ShapeFix_IntersectionTool.cxx:1864  **Axis**: `tolerance`
- **Brief**: Pre-compute maximum vertex tolerance across all face vertices.
- **Falsifiable claim**: Without capturing MaxTolVert, new vertices (lines 1976, 2244, 2245, 2464) use uninitialized or incorrect tolerance baseline. To test: face with high-tolerance vertices; verify MaxTolVert is updated at line 1977.
- **Minimal reproducer**: Construct face with vertices at tolerance 0.5. Intersect wires; verify MaxTolVert >= 0.5 at line 2247 check.
- **Search anchors**: 'MaxTolVert = 0.0', 'std::max(MaxTolVert, tolV)', 'BRep_Tool::Tolerance'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.WIRE_EDGE_BOXES_CACHING`
- **Line**: ShapeFix_IntersectionTool.cxx:1875  **Axis**: `healer-state`
- **Brief**: Pre-compute 2D bounding boxes for all edges in all wires to accelerate broad-phase intersection tests.
- **Falsifiable claim**: Without caching, algorithm recomputes boxes inside nested loops (performance cliff). To test: face with 10 wires x 100 edges each; measure: with caching is O(n), without is O(n^3) in box computation.
- **Minimal reproducer**: Create face with 5 wires, each 50 edges. Measure execution time with/without aSeqWirEdgeBoxes pre-computation. Expected: linear growth. Without: cubic.
- **Search anchors**: 'aSeqWirEdgeBoxes', 'aSeqWirBoxes', 'CreateBoxes2d'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.WIRE_PAIR_BOUNDING_BOX_CULL`
- **Line**: ShapeFix_IntersectionTool.cxx:1902  **Axis**: `healer-state`
- **Brief**: Skip wire pairs whose 2D bounding boxes do not overlap.
- **Falsifiable claim**: Without this check, algorithm tests all O(n^2) wire pairs. To test: face with 3 wires far apart (no 2D overlap); verify aBox1.IsOut(aBox2) is true, skip pair.
- **Minimal reproducer**: Construct face with 3 non-overlapping wires (e.g., concentric boxes at u=[0,0.1], u=[0.5,0.6], u=[0.9,1]). Trigger FixIntersectingWires. Verify continue at 1904 is executed.
- **Search anchors**: 'aBox1.IsOut(aBox2)', 'continue'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SAME_EDGE_IDENTITY_SKIP`
- **Line**: ShapeFix_IntersectionTool.cxx:1919  **Axis**: `input-shape`
- **Brief**: Skip intersection test if edge1 and edge2 are identical shapes.
- **Falsifiable claim**: Without identity check, algorithm would compute self-intersection of same edge. To test: wire pair where both use same edge instance; should skip at line 1921.
- **Minimal reproducer**: Create two wires sharing a single edge. Invoke FixIntersectingWires. Verify edge1.IsSame(edge2) is true, continue executed.
- **Search anchors**: 'edge1.IsSame(edge2)', 'continue'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.DEGENERATE_EDGE_SKIP`
- **Line**: ShapeFix_IntersectionTool.cxx:1923  **Axis**: `input-shape`
- **Brief**: Skip intersection test if either edge is degenerate (point-like).
- **Falsifiable claim**: Without skipping degenerate edges, algorithm computes invalid intersection geometry. To test: wire with degenerate edge; verify BRep_Tool::Degenerated returns true, skip pair.
- **Minimal reproducer**: Create wire with degenerate edge (start=end). Intersect with normal wire. Expected: skip at 1925. Without: undefined behavior in Geom2dInt_GInter::Perform().
- **Search anchors**: 'BRep_Tool::Degenerated(edge1)', 'BRep_Tool::Degenerated(edge2)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.EDGE_BOX_BINDING_VALIDATION`
- **Line**: ShapeFix_IntersectionTool.cxx:1927  **Axis**: `healer-state`
- **Brief**: Skip if edge boxes were not computed/bound (defensive check).
- **Falsifiable claim**: Without this check, Find() on unbound key causes exception. To test: manipulate boxes map to remove binding; should skip at 1929.
- **Minimal reproducer**: Construct scenario where CreateBoxes2d fails to bind an edge. Verify !boxes1.IsBound(edge1) catches this.
- **Search anchors**: '!boxes1.IsBound(edge1)', '!boxes2.IsBound(edge2)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.EDGE_PAIR_2D_BOUNDING_BOX_OVERLAP`
- **Line**: ShapeFix_IntersectionTool.cxx:1933  **Axis**: `healer-state`
- **Brief**: Check if 2D bounding boxes of two edges overlap before geometry intersection test.
- **Falsifiable claim**: Without 2D box overlap, algorithm wastes CPU on Geom2dInt_GInter for spatially disjoint edges. To test: two edges in same wire with no 2D overlap; should continue at 1935 skipped.
- **Minimal reproducer**: Create face with two edges at disjoint u-ranges ([0, 0.2] and [0.8, 1.0]). Verify B1.IsOut(B2) true, skip geometry test.
- **Search anchors**: '!B1.IsOut(B2)', 'intersection is possible'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.PCURVE_EXTRACTION_EDGE1`
- **Line**: ShapeFix_IntersectionTool.cxx:1938  **Axis**: `input-shape`
- **Brief**: Extract parametric curve for edge1; skip pair if extraction fails.
- **Falsifiable claim**: Without PCurve extraction, algorithm cannot compute 2D intersection. To test: edge with missing PCurve on face; should skip at 1940.
- **Minimal reproducer**: Create edge not properly projected onto face (PCurve missing). Invoke FixIntersectingWires. Expected: continue at 1940. Without: crash in Geom2d intersection.
- **Search anchors**: '!sae.PCurve(edge1, face, Crv1, a1, b1, false)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.PCURVE_EXTRACTION_EDGE2`
- **Line**: ShapeFix_IntersectionTool.cxx:1942  **Axis**: `input-shape`
- **Brief**: Extract parametric curve for edge2; skip pair if extraction fails.
- **Falsifiable claim**: Without PCurve for edge2, Geom2dInt cannot compute intersection. To test: edge2 missing PCurve; should skip at 1944.
- **Minimal reproducer**: Create edge2 without valid PCurve on face. Trigger FixIntersectingWires. Expected: continue at 1944.
- **Search anchors**: '!sae.PCurve(edge2, face, Crv2, a2, b2, false)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.GEOM2D_INTERSECTION_COMPUTATION`
- **Line**: ShapeFix_IntersectionTool.cxx:1950  **Axis**: `kernel-pair`
- **Brief**: Compute 2D intersection of two parametric curves using Geom2dInt_GInter.
- **Falsifiable claim**: Without geometry intersection, algorithm cannot identify overlap regions. To test: two intersecting PCurves; verify Inter.IsDone() true.
- **Minimal reproducer**: Create two wires with PCurves that cross at (0.5, 0.5). Trigger FixIntersectingWires. Verify Inter.IsDone() true, Inter.NbPoints() > 0 or Inter.NbSegments() > 0.
- **Search anchors**: 'Geom2dInt_GInter', 'Inter.Perform', 'tolint = 1.0e-10'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.INTERSECTION_COMPUTATION_VALIDITY`
- **Line**: ShapeFix_IntersectionTool.cxx:1952  **Axis**: `kernel-pair`
- **Brief**: Skip pair if intersection computation failed to converge.
- **Falsifiable claim**: Without validity check, algorithm processes garbage intersection results. To test: pathological PCurves; verify !Inter.IsDone() true, skip.
- **Minimal reproducer**: Create PCurves with numerical instability (e.g., discontinuity at evaluation). Verify Inter.IsDone() returns false, continue at 1954.
- **Search anchors**: '!Inter.IsDone()', 'continue'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.ISOLATED_INTERSECTION_POINT_FILTER`
- **Line**: ShapeFix_IntersectionTool.cxx:1957  **Axis**: `kernel-pair`
- **Brief**: Process isolated intersection points (0-2 points), skip tangencies or complex overlaps.
- **Falsifiable claim**: Without point-count filtering, algorithm mishandles multi-point and segment intersections. To test: tangent curves (NbPoints=1) vs crossing (NbPoints=2); verify branch 1957.
- **Minimal reproducer**: Construct three cases: (1) non-intersecting (NbPoints=0), (2) crossing (NbPoints=1), (3) transverse (NbPoints=2). Verify only case 2-3 processed at 1958-2044.
- **Search anchors**: 'Inter.NbPoints()', 'Inter.NbPoints() < 3', 'Inter.NbSegments() == 1'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.INTERIOR_INTERIOR_INTERSECTION_SPLIT`
- **Line**: ShapeFix_IntersectionTool.cxx:1962  **Axis**: `healer-state`
- **Brief**: If intersection point is in interior of both edges, create new vertex and split both edges.
- **Falsifiable claim**: Without splitting interior intersections, algorithm leaves self-intersecting wires. To test: two edges crossing at interior points; verify new vertex created, both edges split.
- **Minimal reproducer**: Create wires with edges crossing at (0.5, 0.5) on both. Invoke FixIntersectingWires. Verify vertex V created at line 1976, SplitEdge1 called twice (1978, 1984).
- **Search anchors**: 'Tr1.PositionOnCurve() == IntRes2d_Middle', 'Tr2.PositionOnCurve() == IntRes2d_Middle', 'gp_Pnt P0'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.EDGE1_INTERIOR_EDGE2_ENDPOINT`
- **Line**: ShapeFix_IntersectionTool.cxx:1995  **Axis**: `healer-state`
- **Brief**: If intersection is interior to edge1 but endpoint of edge2, find vertex from edge2 and split edge1.
- **Falsifiable claim**: Without endpoint-fusion logic, algorithm creates redundant vertices. To test: edge1 crosses edge2's endpoint; verify FindVertAndSplitEdge called at 2000.
- **Minimal reproducer**: Construct edge1 interior-crossing edge2's start vertex. Invoke FixIntersectingWires. Verify Tr1.PositionOnCurve()=Middle, Tr2!=Middle at line 1996.
- **Search anchors**: 'Tr1.PositionOnCurve() == IntRes2d_Middle', 'Tr2.PositionOnCurve() != IntRes2d_Middle', 'FindVertAndSplitEdge'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.EDGE1_ENDPOINT_EDGE2_INTERIOR`
- **Line**: ShapeFix_IntersectionTool.cxx:2015  **Axis**: `healer-state`
- **Brief**: If intersection is endpoint of edge1 but interior to edge2, find vertex from edge1 and split edge2.
- **Falsifiable claim**: Without symmetry in endpoint handling, algorithm leaves asymmetric repairs. To test: edge2 interior-crossing edge1's endpoint; verify FindVertAndSplitEdge at 2020.
- **Minimal reproducer**: Construct edge2 interior-crossing edge1's endpoint. Invoke FixIntersectingWires. Verify Tr1!=Middle, Tr2=Middle at line 2015.
- **Search anchors**: 'Tr1.PositionOnCurve() != IntRes2d_Middle', 'Tr2.PositionOnCurve() == IntRes2d_Middle', 'FindVertAndSplitEdge'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.BOTH_ENDPOINT_VERTEX_UNION`
- **Line**: ShapeFix_IntersectionTool.cxx:2035  **Axis**: `healer-state`
- **Brief**: If intersection is endpoint of both edges, merge (union) the near-coincident vertices.
- **Falsifiable claim**: Without endpoint fusion, algorithm leaves duplicate nearby vertices. To test: edge1 endpoint ~= edge2 endpoint; verify UnionVertexes called at 2039.
- **Minimal reproducer**: Create two edges with endpoints close (distance < MaxTolVert). Verify Tr1!=Middle, Tr2!=Middle at line 2035, UnionVertexes called.
- **Search anchors**: 'Tr1.PositionOnCurve() != IntRes2d_Middle', 'Tr2.PositionOnCurve() != IntRes2d_Middle', 'UnionVertexes'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_OVERLAP_DETECTION`
- **Line**: ShapeFix_IntersectionTool.cxx:2047  **Axis**: `kernel-pair`
- **Brief**: Detect when two edges have overlapping 2D curves (segment intersection, not isolated points).
- **Falsifiable claim**: Without segment detection, algorithm misses overlapping edge regions. To test: two edges sharing a collinear segment; verify Inter.NbSegments() == 1 at 2047.
- **Minimal reproducer**: Create two edges that overlap on same curve (e.g., two line segments on same line). Verify Inter.NbSegments() returns 1, process at 2048-2481.
- **Search anchors**: 'Inter.NbSegments() == 1', 'IntRes2d_IntersectionSegment', 'IS.HasFirstPoint()'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_ENDPOINT_PRESENCE_CHECK`
- **Line**: ShapeFix_IntersectionTool.cxx:2050  **Axis**: `kernel-pair`
- **Brief**: Verify that overlapping segment has both start and end points defined.
- **Falsifiable claim**: Without endpoint validation, algorithm operates on incomplete segments. To test: segment missing endpoints; skip at 2051.
- **Minimal reproducer**: Construct scenario where IS.HasFirstPoint() or IS.HasLastPoint() is false. Verify condition at 2050 filters this.
- **Search anchors**: 'IS.HasFirstPoint()', 'IS.HasLastPoint()'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_EDGE1_START_VERTEX_ANALYSIS`
- **Line**: ShapeFix_IntersectionTool.cxx:2068  **Axis**: `tolerance`
- **Brief**: Check if overlapping segment start is near edge1's start vertex; if so, consider edge1 as endpoint-constrained.
- **Falsifiable claim**: Without vertex matching, algorithm may split edges incorrectly. To test: segment start near edge1 start; verify distance check at 2073-2084.
- **Minimal reproducer**: Create overlapping segment with Pnt11 within MaxTolVert of V1. Verify maxdist/pdist checks classify this as start-vertex case.
- **Search anchors**: 'dist1 = Pnt11.Distance(PV1)', 'maxdist < MaxTolVert', 'IsModified1 = true'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_EDGE1_END_VERTEX_ANALYSIS`
- **Line**: ShapeFix_IntersectionTool.cxx:2091  **Axis**: `tolerance`
- **Brief**: Check if overlapping segment end is near edge1's end vertex; if so, extend edge1 tolerance or set as endpoint-constrained.
- **Falsifiable claim**: Without end-vertex matching, algorithm leaves overlaps unresolved. To test: segment end near edge1 end; verify distance logic at 2091-2110.
- **Minimal reproducer**: Create segment with Pnt12 within MaxTolVert of V2. Verify conditional at 2104 picks tightest tolerance.
- **Search anchors**: 'dist1 = Pnt11.Distance(PV2)', 'maxdist < MaxTolVert', 'newtol < maxdist'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_EDGE1_CUTTING`
- **Line**: ShapeFix_IntersectionTool.cxx:2111  **Axis**: `healer-state`
- **Brief**: If edge1 is constrained by segment endpoints, cut it to remove overlap.
- **Falsifiable claim**: Without cutting, edge1 still overlaps with edge2 segment. To test: IsModified1=true; verify CutEdge called at 2134.
- **Minimal reproducer**: Set up segment where edge1 is endpoint-constrained. Verify CutEdge called, edge1 parameter range shortened.
- **Search anchors**: 'IsModified1', 'CutEdge(edge1, pend, cut, face, IsCutLine)', 'dista > distb'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_EDGE2_START_VERTEX_ANALYSIS`
- **Line**: ShapeFix_IntersectionTool.cxx:2145  **Axis**: `tolerance`
- **Brief**: Check if overlapping segment start is near edge2's start vertex.
- **Falsifiable claim**: Without vertex matching for edge2, asymmetric repair. To test: segment start near V12; verify distance at 2150-2161.
- **Minimal reproducer**: Construct segment with Pnt21 near edge2's first vertex. Verify maxdist check at 2161.
- **Search anchors**: 'dist1 = Pnt21.Distance(PV12)', 'maxdist < MaxTolVert'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_EDGE2_END_VERTEX_ANALYSIS`
- **Line**: ShapeFix_IntersectionTool.cxx:2167  **Axis**: `tolerance`
- **Brief**: Check if overlapping segment end is near edge2's end vertex.
- **Falsifiable claim**: Without endpoint matching on edge2, algorithm leaves asymmetry. To test: segment end near V22; verify distance logic.
- **Minimal reproducer**: Create segment with Pnt22 near edge2's last vertex. Verify conditional at 2178.
- **Search anchors**: 'dist1 = Pnt21.Distance(PV22)', 'maxdist < MaxTolVert'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_EDGE2_CUTTING`
- **Line**: ShapeFix_IntersectionTool.cxx:2187  **Axis**: `healer-state`
- **Brief**: If edge2 is constrained by segment endpoints, cut it.
- **Falsifiable claim**: Without cutting edge2, overlap persists. To test: IsModified2=true; verify CutEdge at 2210.
- **Minimal reproducer**: Set up scenario where edge2 is endpoint-constrained. Verify CutEdge called.
- **Search anchors**: 'IsModified2', 'CutEdge(edge2, pend, cut, face, IsCutLine)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_BOTH_MODIFIED_RETRY`
- **Line**: ShapeFix_IntersectionTool.cxx:2221  **Axis**: `healer-state`
- **Brief**: If both edges were cut, re-test the same pair with modified ranges.
- **Falsifiable claim**: Without retry, algorithm misses nested overlaps. To test: both IsModified1 and IsModified2 true; verify num2-- at 2225, continue.
- **Minimal reproducer**: Construct scenario where both edges require cutting. Verify num2-- executed, pair re-tested.
- **Search anchors**: 'IsModified1 || IsModified2', 'num2--', 'continue'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_3EDGE_RECONSTRUCTION`
- **Line**: ShapeFix_IntersectionTool.cxx:2232  **Axis**: `healer-state`
- **Brief**: If overlapping segment is large (>50% of either edge), split each edge into 3 parts: [start, overlap_start], [overlap], [overlap_end, end].
- **Falsifiable claim**: Without 3-edge split, algorithm cannot represent large overlaps correctly. To test: segment length > 50% of edge; verify branches at 2310-2346 and 2401-2439 execute.
- **Minimal reproducer**: Create two edges with segment overlap > 50% of edge length. Verify SplitEdge1 called multiple times, tmpE = sewd1->Edge(numseg1), and myContext->Replace(tmpE, SegE) at 2446.
- **Search anchors**: 'std::abs(p12 - p11) > std::abs(b1 - a1) / 2', 'gp_Pnt P01', 'gp_Pnt P02', 'SegE = sewd1->Edge(numseg1)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_START_MATCHES_EDGE1_VERTEX_1`
- **Line**: ShapeFix_IntersectionTool.cxx:2258  **Axis**: `tolerance`
- **Brief**: If overlap segment start P01 matches edge1's start vertex V1, reuse V1 instead of creating new vertex.
- **Falsifiable claim**: Without vertex reuse, algorithm creates duplicate nearby vertices. To test: P01 distance to V1 < MaxTolVert; verify akey1++ at 2265.
- **Minimal reproducer**: Construct segment where P01 == V1 (within tolerance). Verify P01.Distance(PV1) < MaxTolVert, NewV1 = V1, akey1 = 1 at line 2265.
- **Search anchors**: 'P01.Distance(PV1)', 'NewV1 = V1', 'akey1++'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_START_MATCHES_EDGE1_VERTEX_2`
- **Line**: ShapeFix_IntersectionTool.cxx:2267  **Axis**: `tolerance`
- **Brief**: If overlap segment start P01 matches edge1's end vertex V2, reuse V2 instead of creating new vertex.
- **Falsifiable claim**: Without reuse, algorithm creates redundant vertices. To test: P01 distance to V2 < MaxTolVert; verify akey1++ at 2274.
- **Minimal reproducer**: Construct segment where P01 == V2. Verify P01.Distance(PV2) check, NewV1 = V2, akey1 incremented.
- **Search anchors**: 'P01.Distance(PV2)', 'NewV1 = V2', 'akey1++'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_END_MATCHES_EDGE1_VERTEX_1`
- **Line**: ShapeFix_IntersectionTool.cxx:2277  **Axis**: `tolerance`
- **Brief**: If overlap segment end P02 matches edge1's start vertex V1, reuse V1.
- **Falsifiable claim**: Without reuse, duplicate vertices created. To test: P02 == V1; verify akey2++ at 2284.
- **Minimal reproducer**: Construct segment where P02 == V1. Verify P02.Distance(PV1) check, NewV2 = V1, akey2 incremented.
- **Search anchors**: 'P02.Distance(PV1)', 'NewV2 = V1', 'akey2++'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_END_MATCHES_EDGE1_VERTEX_2`
- **Line**: ShapeFix_IntersectionTool.cxx:2286  **Axis**: `tolerance`
- **Brief**: If overlap segment end P02 matches edge1's end vertex V2, reuse V2.
- **Falsifiable claim**: Without reuse, algorithm leaves duplicate vertices. To test: P02 == V2; verify akey2++ at 2293.
- **Minimal reproducer**: Construct segment where P02 == V2. Verify P02.Distance(PV2) check, NewV2 = V2, akey2 incremented.
- **Search anchors**: 'P02.Distance(PV2)', 'NewV2 = V2', 'akey2++'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_AMBIGUOUS_VERTEX_DEGENERATE_EDGE_ABORT`
- **Line**: ShapeFix_IntersectionTool.cxx:2295  **Axis**: `healer-state`
- **Brief**: If both P01 and P02 match the same vertex (akey1>1 or akey2>1), abort segment reconstruction (degenerate edge).
- **Falsifiable claim**: Without this check, algorithm would create degenerate segment edges. To test: P01==V1 and P02==V1; verify akey1>1 at 2295, continue at 2297.
- **Minimal reproducer**: Construct segment where both endpoints match same vertex (e.g., P01=P02=V1). Verify akey1 or akey2 > 1, continue executed.
- **Search anchors**: 'akey1 > 1 || akey2 > 1', 'continue'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_START_NEW_VERTEX_EDGE1_SPLIT`
- **Line**: ShapeFix_IntersectionTool.cxx:2310  **Axis**: `healer-state`
- **Brief**: If segment start P01 is new (akey1==0) but end P02 matches an edge1 vertex (akey2>0), split edge1 at P01.
- **Falsifiable claim**: Without splitting, segment start is not anchored to topology. To test: akey1==0 and akey2>0; verify SplitEdge1 at 2312.
- **Minimal reproducer**: Construct 3-edge case where P01 is new and P02 matches V2. Verify SplitEdge1(sewd1, ..., p11, NewV1, ...) called.
- **Search anchors**: 'akey1 == 0 && akey2 > 0', 'SplitEdge1(sewd1, face, num1, p11, NewV1, tolV1, boxes1)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_END_NEW_VERTEX_EDGE1_SPLIT`
- **Line**: ShapeFix_IntersectionTool.cxx:2318  **Axis**: `healer-state`
- **Brief**: If segment start P01 matches an edge1 vertex (akey1>0) but end P02 is new (akey2==0), split edge1 at P02.
- **Falsifiable claim**: Without splitting, segment end is not anchored. To test: akey1>0 and akey2==0; verify SplitEdge1 at 2320.
- **Minimal reproducer**: Construct 3-edge case where P01 matches V1 but P02 is new. Verify SplitEdge1(sewd1, ..., p12, NewV2, ...) called.
- **Search anchors**: 'akey1 > 0 && akey2 == 0', 'SplitEdge1(sewd1, face, num1, p12, NewV2, tolV2, boxes1)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_BOTH_NEW_VERTICES_EDGE1_DOUBLE_SPLIT`
- **Line**: ShapeFix_IntersectionTool.cxx:2326  **Axis**: `healer-state`
- **Brief**: If both P01 and P02 are new vertices, split edge1 at both points (creating 3 sub-edges).
- **Falsifiable claim**: Without double-split, algorithm cannot isolate segment region in middle. To test: akey1==0 and akey2==0; verify two SplitEdge1 calls at 2329 and 2341.
- **Minimal reproducer**: Construct segment where both endpoints are new. Verify first SplitEdge1 at p11, then SplitEdge1 at p12 (adjusted for num1split2 at 2328-2339).
- **Search anchors**: 'akey1 == 0 && akey2 == 0', 'num1split2 = num1', 'SplitEdge1(sewd1, face, num1split2, p12, NewV2, tolV2, boxes1)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_EXTERNAL_PARAMETER_ADJUSTMENT`
- **Line**: ShapeFix_IntersectionTool.cxx:2336  **Axis**: `healer-state`
- **Brief**: After splitting edge1 at p11, check if p12 is now outside the updated edge parameter range; if so, split the next edge instead.
- **Falsifiable claim**: Without parameter adjustment, algorithm splits wrong edge. To test: p12 external to updated [a,b]; verify num1split2++ at 2338.
- **Minimal reproducer**: Construct case where first split shifts p12 outside parameter range. Verify condition (a - p12) * (b - p12) > 0, num1split2 incremented.
- **Search anchors**: '(a - p12) * (b - p12) > 0', 'num1split2++'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_START_FUSE_EDGE2_FIRST_VERTEX`
- **Line**: ShapeFix_IntersectionTool.cxx:2352  **Axis**: `tolerance`
- **Brief**: If segment start P01 is close to edge2's first vertex PV12, merge them by replacing edge2's first vertex with NewV1.
- **Falsifiable claim**: Without fusion, algorithm creates duplicate nearby vertices on edge2. To test: P01.Distance(PV12) < tolV1; verify vertex replacement at 2356.
- **Minimal reproducer**: Construct case where P01 is near edge2's first vertex. Verify P01.Distance(PV12) < tolV1, edge2 replaced with CopyReplaceVertices at 2357.
- **Search anchors**: 'P01.Distance(PV12) < tolV1', 'sbe.CopyReplaceVertices(edge2, NewV1, V22)', 'akey1 = 1'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_START_FUSE_EDGE2_LAST_VERTEX`
- **Line**: ShapeFix_IntersectionTool.cxx:2364  **Axis**: `tolerance`
- **Brief**: If segment start P01 is close to edge2's last vertex PV22, merge them by replacing edge2's last vertex with NewV1.
- **Falsifiable claim**: Without fusion, duplicate vertices left on edge2. To test: P01.Distance(PV22) < tolV1; verify replacement at 2369.
- **Minimal reproducer**: Construct case where P01 is near edge2's last vertex. Verify P01.Distance(PV22) < tolV1, edge2 replaced.
- **Search anchors**: 'P01.Distance(PV22) < tolV1', 'sbe.CopyReplaceVertices(edge2, V12, NewV1)', 'akey1 = 2'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_END_FUSE_EDGE2_FIRST_VERTEX`
- **Line**: ShapeFix_IntersectionTool.cxx:2376  **Axis**: `tolerance`
- **Brief**: If segment end P02 is close to edge2's first vertex PV12, merge them by replacing edge2's first vertex with NewV2.
- **Falsifiable claim**: Without fusion, algorithm leaves duplicate vertices. To test: P02.Distance(PV12) < tolV2; verify replacement.
- **Minimal reproducer**: Construct case where P02 is near edge2's first vertex. Verify P02.Distance(PV12) < tolV2, edge2 replaced.
- **Search anchors**: 'P02.Distance(PV12) < tolV2', 'sbe.CopyReplaceVertices(edge2, NewV2, V22)', 'akey2 = 1'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_END_FUSE_EDGE2_LAST_VERTEX`
- **Line**: ShapeFix_IntersectionTool.cxx:2388  **Axis**: `tolerance`
- **Brief**: If segment end P02 is close to edge2's last vertex PV22, merge them by replacing edge2's last vertex with NewV2.
- **Falsifiable claim**: Without fusion, duplicate vertices persist on edge2. To test: P02.Distance(PV22) < tolV2; verify replacement.
- **Minimal reproducer**: Construct case where P02 is near edge2's last vertex. Verify P02.Distance(PV22) < tolV2, edge2 replaced.
- **Search anchors**: 'P02.Distance(PV22) < tolV2', 'sbe.CopyReplaceVertices(edge2, V12, NewV2)', 'akey2 = 2'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_START_NEW_VERTEX_EDGE2_SPLIT`
- **Line**: ShapeFix_IntersectionTool.cxx:2402  **Axis**: `healer-state`
- **Brief**: If segment start P01 is new (akey1==0) but matches an edge2 vertex (akey2>0), split edge2 at p21.
- **Falsifiable claim**: Without splitting, segment start is not anchored on edge2. To test: akey1==0 and akey2>0; verify SplitEdge1 at 2404.
- **Minimal reproducer**: Construct case where P01 is new but P02 matches edge2 vertex. Verify SplitEdge1(sewd2, ..., p21, NewV1, ...) called.
- **Search anchors**: 'akey1 == 0 && akey2 > 0', 'SplitEdge1(sewd2, face, num2, p21, NewV1, tolV1, boxes2)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_END_NEW_VERTEX_EDGE2_SPLIT`
- **Line**: ShapeFix_IntersectionTool.cxx:2410  **Axis**: `healer-state`
- **Brief**: If segment start P01 matches an edge2 vertex (akey1>0) but end P02 is new (akey2==0), split edge2 at p22.
- **Falsifiable claim**: Without splitting, segment end is not anchored on edge2. To test: akey1>0 and akey2==0; verify SplitEdge1 at 2412.
- **Minimal reproducer**: Construct case where P01 matches edge2 vertex but P02 is new. Verify SplitEdge1(sewd2, ..., p22, NewV2, ...) called.
- **Search anchors**: 'akey1 > 0 && akey2 == 0', 'SplitEdge1(sewd2, face, num2, p22, NewV2, tolV2, boxes2)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SEGMENT_BOTH_NEW_VERTICES_EDGE2_DOUBLE_SPLIT`
- **Line**: ShapeFix_IntersectionTool.cxx:2418  **Axis**: `healer-state`
- **Brief**: If both P01 and P02 are new on edge2, split edge2 at both points (creating 3 sub-edges).
- **Falsifiable claim**: Without double-split, segment region not isolated on edge2. To test: akey1==0 and akey2==0; verify two SplitEdge1 calls at 2421 and 2434.
- **Minimal reproducer**: Construct segment where both endpoints are new on edge2. Verify first SplitEdge1 at p21, then SplitEdge1 at p22.
- **Search anchors**: 'akey1 == 0 && akey2 == 0', 'num2split2 = num2', 'SplitEdge1(sewd2, face, num2split2, p22, NewV2, tolV2, boxes2)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.LARGE_SEGMENT_OVERLAP_3EDGE_REPLACE_SEGMENT`
- **Line**: ShapeFix_IntersectionTool.cxx:2442  **Axis**: `healer-state`
- **Brief**: After 3-edge reconstruction, replace the segment edge from edge2 with the segment edge from edge1 (ensuring directional consistency).
- **Falsifiable claim**: Without edge substitution, algorithm leaves two overlapping edges. To test: verify orientation check at 2442, SegE.Reverse() if needed, myContext->Replace at 2446.
- **Minimal reproducer**: Construct case where both edges are split into 3. Verify tmpE from edge2 is replaced with SegE from edge1 after orientation sync.
- **Search anchors**: 'tmpE = sewd2->Edge(numseg2)', '!sae.FirstVertex(SegE).IsSame(sae.FirstVertex(tmpE))', 'SegE.Reverse()', 'myContext->Replace(tmpE, SegE)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.SMALL_SEGMENT_OVERLAP_2EDGE_RECONSTRUCTION`
- **Line**: ShapeFix_IntersectionTool.cxx:2451  **Axis**: `healer-state`
- **Brief**: If overlapping segment is small (<50% of edge), split each edge into 2 parts at segment midpoint instead of 3.
- **Falsifiable claim**: Without 2-edge split, algorithm cannot represent small overlaps correctly. To test: segment length <= 50% of edge; verify SplitEdge2 calls at 2468 and 2473.
- **Minimal reproducer**: Create edges with small segment overlap (e.g., 30% of edge). Verify SplitEdge2(sewd2, ..., p21, p22, ...) called, not 3-edge path.
- **Search anchors**: 'std::abs(p12 - p11) <= std::abs(b1 - a1) / 2', 'gp_Pnt P0', 'SplitEdge2(sewd2, face, num2, p21, p22, NewV, tolV, boxes2)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.WIRE_BOX_RECOMPUTATION_AFTER_SPLIT`
- **Line**: ShapeFix_IntersectionTool.cxx:2486  **Axis**: `healer-state`
- **Brief**: After modifying a wire (splits, vertex replacements), recompute its 2D bounding boxes to maintain cache consistency.
- **Falsifiable claim**: Without recomputation, subsequent intersection tests use stale boxes. To test: hasModifWire=true; verify boxes1.Clear() at 2493, CreateBoxes2d at 2494.
- **Minimal reproducer**: Trigger multiple wire modifications (hasModifWire=true). Verify boxes are cleared and recomputed for both wires.
- **Search anchors**: 'if (hasModifWire)', 'boxes1.Clear()', 'CreateBoxes2d(sewd1, face, boxes1)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.FACE_RECONSTRUCTION_FROM_WIRES`
- **Line**: ShapeFix_IntersectionTool.cxx:2507  **Axis**: `healer-state`
- **Brief**: If any wires were modified, reconstruct the face from the modified wires and non-wire shapes.
- **Falsifiable claim**: Without reconstruction, face still references old wires. To test: isDone=true; verify face.EmptyCopied() at 2510, add all wires at 2517-2518.
- **Minimal reproducer**: Trigger modifications (isDone=true). Verify new face created, all modified wires added back, newface.Orientation preserved, myContext->Replace called.
- **Search anchors**: 'if (isDone)', 'face.EmptyCopied()', 'B.Add(newface, wire)', 'newface.Orientation(ori)', 'myContext->Replace(face, newface)'

##### `ShapeFix_IntersectionTool.FixIntersectingWires.MODIFICATION_THRESHOLD_SAFEGUARD`
- **Line**: ShapeFix_IntersectionTool.cxx:1910  **Axis**: `api-contract`
- **Brief**: Abort intersection testing for a wire pair if NbModif >= 30 (safeguard against runaway modifications).
- **Falsifiable claim**: Without modification limit, algorithm may loop infinitely on pathological inputs. To test: force 30+ modifications; verify num1/num2 loop exits.
- **Minimal reproducer**: Create face with highly pathological intersections that trigger many splits. Verify NbModif < 30 check at 1910 and 1915 prevents infinite looping.
- **Search anchors**: 'NbModif < 30', 'for (int num1 = 1; num1 <= sewd1->NbEdges() && NbModif < 30; num1++)'


### ShapeFix_Wire

#### `ShapeFix_Wire.FixSelfIntersection`
 (20 branches; 1 low-confidence; source: `v3-deep-ShapeFix_Wire_FixSelfIntersection.json`)

##### `ShapeFix_Wire.FixSelfIntersection.IsReady_check`
- **Line**: ShapeFix_Wire.cxx:1085  **Axis**: `api-contract`
- **Brief**: Early exit when wire data is not loaded or analyzer not configured.
- **Falsifiable claim**: Without this branch, the kernel would attempt to fix intersections on an uninitialized wire. To test: call FixSelfIntersection on a wire where WireData() returns null or IsReady() is false; observe that method returns false early vs. crashing on null pointer dereference.
- **Minimal reproducer**: Create a ShapeFix_Wire object without calling Load(). Call FixSelfIntersection() directly. Without the branch: null-pointer exception accessing sbwd->NbEdges(). With the branch: returns false cleanly.
- **Search anchors**: 'IsReady', 'myAnalyzer', 'myShape'

##### `ShapeFix_Wire.FixSelfIntersection.RemoveLoopMode_skip`
- **Line**: ShapeFix_Wire.cxx:1093  **Axis**: `healer-state`
- **Brief**: Skips self-intersecting edge fixing entirely when NeedFix returns false (mode disabled).
- **Falsifiable claim**: Without this branch, the kernel would always attempt to fix self-intersecting edges regardless of configuration mode. To test: set FixSelfIntersectingEdgeMode to disabled (-1 or 0); provide a wire with known self-intersections; observe whether fixing is skipped vs. forced.
- **Minimal reproducer**: Create a wire with a self-intersecting edge. Call SetFixSelfIntersectingEdgeMode(0) to disable. Call FixSelfIntersection(). Without the branch: self-intersections would be fixed. With the branch: wire remains unfixed.
- **Search anchors**: 'NeedFix', 'myFixSelfIntersectingEdgeMode'

##### `ShapeFix_Wire.FixSelfIntersection.RemoveLoopMode_less_than_1`
- **Line**: ShapeFix_Wire.cxx:1097  **Axis**: `healer-state`
- **Brief**: Applies self-intersecting edge fix to all edges without dynamic edge count tracking.
- **Falsifiable claim**: Without this branch, when RemoveLoopMode < 1, newly created edges from loop removal would be rechecked. To test: provide wire with edge that splits into N edges; observe whether the new edges are reprocessed vs. skipped.
- **Minimal reproducer**: Create wire with self-intersecting edge that FixSelfIntersectingEdge will split into multiple edges. Set myRemoveLoopMode to 0. Call FixSelfIntersection(). Without the branch: newly generated edges would be visited again. With branch: only original edge count iterated.
- **Search anchors**: 'myRemoveLoopMode', 'FixSelfIntersectingEdge'

##### `ShapeFix_Wire.FixSelfIntersection.RemoveLoopMode_equals_1`
- **Line**: ShapeFix_Wire.cxx:1102  **Axis**: `healer-state`
- **Brief**: Applies self-intersecting edge fix with dynamic decrement to recheck newly generated edges, then calls FixClosed.
- **Falsifiable claim**: Without this branch and its num-- decrement logic, newly created edges from loop removal would not be revalidated. To test: provide wire with edge splitting into multiple fragments; observe whether each fragment is checked for new self-intersections.
- **Minimal reproducer**: Create wire where FixSelfIntersectingEdge on one edge produces 2+ result edges. Set myRemoveLoopMode to 1. Call FixSelfIntersection(). Without the branch: generated edges skip re-check. With branch: num-- ensures next iteration revisits the split point, and FixClosed() validates closure.
- **Search anchors**: 'myRemoveLoopMode', 'num--', 'FixClosed'

##### `ShapeFix_Wire.FixSelfIntersection.FixIntersectingEdges_mode_skip`
- **Line**: ShapeFix_Wire.cxx:1109  **Axis**: `healer-state`
- **Brief**: Skips adjacent edge intersection fixing when mode is disabled.
- **Falsifiable claim**: Without this branch, the kernel would always attempt to fix intersecting edge pairs. To test: set FixIntersectingEdgesMode to disabled; provide wire with two adjacent intersecting edges; observe whether fixing is applied.
- **Minimal reproducer**: Create wire with two consecutive edges that intersect. Set FixIntersectingEdgesMode to 0. Call FixSelfIntersection(). Without the branch: edges would be fixed. With the branch: edges left unfixed.
- **Search anchors**: 'NeedFix', 'myFixIntersectingEdgesMode'

##### `ShapeFix_Wire.FixSelfIntersection.FixIntersectingEdges_closed_mode_start`
- **Line**: ShapeFix_Wire.cxx:1110  **Axis**: `input-shape`
- **Brief**: Selects iteration start: edge 1 for closed wires, edge 2 for open wires.
- **Falsifiable claim**: Without this conditional, closed wires would incorrectly skip checking edge 1 (which wraps around from edge N). To test: create closed wire with intersection at vertex between last and first edge; observe whether it's detected.
- **Minimal reproducer**: Create closed wire (ClosedWireMode=true) where edge N and edge 1 intersect. Without the branch: num starts at 2, missing the first edge's potential intersection with last. With branch: num starts at 1 for closed, catching the wrap-around case.
- **Search anchors**: 'myClosedMode', 'num = '

##### `ShapeFix_Wire.FixSelfIntersection.FixIntersectingEdges_fail_propagation`
- **Line**: ShapeFix_Wire.cxx:1117  **Axis**: `api-contract`
- **Brief**: Propagates FAIL1 and FAIL2 status codes from edge-pair fixing.
- **Falsifiable claim**: Without these branches, caller would not know that intersection fixing failed. To test: provide edges that cannot be fixed (e.g., degenerate intersection); observe whether status is reported vs. silently lost.
- **Minimal reproducer**: Create wire where FixIntersectingEdges(num) returns FAIL1 (e.g., unpaired edges). Call FixSelfIntersection(). Without the branch: myStatusSelfIntersection loses FAIL1 code. With branch: caller sees ShapeExtend_FAIL1 set.
- **Search anchors**: 'ShapeExtend_FAIL1', 'ShapeExtend_FAIL2'

##### `ShapeFix_Wire.FixSelfIntersection.FixIntersectingEdges_done_check`
- **Line**: ShapeFix_Wire.cxx:1126  **Axis**: `healer-state`
- **Brief**: Skips status propagation and edge removal logic when FixIntersectingEdges reported no successful fix.
- **Falsifiable claim**: Without this continue, edge removal would be attempted even when no fix was applied. To test: provide edges with no intersection; observe whether false edge removal is triggered.
- **Minimal reproducer**: Create wire where FixIntersectingEdges(num) finds no intersection (LastFixStatus(DONE) is false). Without the branch: code would fall through to DONE4/DONE3 removal checks. With branch: continue skips to next iteration.
- **Search anchors**: 'ShapeExtend_DONE', 'continue'

##### `ShapeFix_Wire.FixSelfIntersection.FixIntersectingEdges_done_status_propagation`
- **Line**: ShapeFix_Wire.cxx:1130  **Axis**: `api-contract`
- **Brief**: Propagates DONE1, DONE2, DONE6 substatus codes from successful intersection fixes.
- **Falsifiable claim**: Without these branches, caller would not distinguish which type of fix (reordering, trimming, tolerance) was applied. To test: apply various fixes and check status bits.
- **Minimal reproducer**: Create wire with intersecting edges fixable by different strategies (reorder, trim, tolerance adjust). Call FixSelfIntersection(). Without the branches: all fixes report the same status. With branches: DONE1/DONE2/DONE6 distinguish fix type.
- **Search anchors**: 'ShapeExtend_DONE1', 'ShapeExtend_DONE2', 'ShapeExtend_DONE6'

##### `ShapeFix_Wire.FixSelfIntersection.LowEdgeCount_gate`
- **Line**: ShapeFix_Wire.cxx:1142  **Axis**: `input-shape`
- **Brief**: Disables edge removal for wires with < 3 edges to preserve topology.
- **Falsifiable claim**: Without this gate, a 2-edge wire with intersecting edges could be reduced to 1 edge, breaking connectivity. To test: create 2-edge closed wire with intersection; observe whether both edges are preserved vs. removed.
- **Minimal reproducer**: Create closed wire with exactly 2 edges that intersect (e.g., two arcs forming a figure-8). Set nb < 3. Without the branch: DONE4/DONE3 edge removal proceeds, leaving degenerate wire. With branch: edges retained.
- **Search anchors**: 'nb < 3', 'myTopoMode'

##### `ShapeFix_Wire.FixSelfIntersection.RevalidateOnToleranceChange`
- **Line**: ShapeFix_Wire.cxx:1148  **Axis**: `tolerance`
- **Brief**: Re-checks intersection after tolerance was modified to confirm fix validity.
- **Falsifiable claim**: Without this branch, a tolerance-based fix (DONE7) would not be re-validated, risking false fixes. To test: provide edge intersection just beyond tolerance; observe whether re-check is applied after tolerance expansion.
- **Minimal reproducer**: Create intersecting edges with intersection distance equal to current tolerance (boundary case). FixIntersectingEdges returns DONE7 (tolerance adjusted). Without the branch: second call to FixIntersectingEdges() skipped. With branch: re-validates.
- **Search anchors**: 'ShapeExtend_DONE7', 'FixIntersectingEdges(num)'

##### `ShapeFix_Wire.FixSelfIntersection.EdgeRemoval_DONE4_branch`
- **Line**: ShapeFix_Wire.cxx:1154  **Axis**: `healer-state`
- **Brief**: Removes current edge when intersection was fixed by eliminating it (DONE4).
- **Falsifiable claim**: Without this branch, an edge marked for removal (DONE4) would remain in wire, reintroducing the intersection. To test: provide edge that cannot be fixed by trimming/reordering, only removal.
- **Minimal reproducer**: Create wire where FixIntersectingEdges(num) returns DONE4 (remove current edge). Without the branch: sbwd->Remove(num) not called, edge persists. With branch: edge removed, intersection eliminated.
- **Search anchors**: 'ShapeExtend_DONE4', 'sbwd->Remove'

##### `ShapeFix_Wire.FixSelfIntersection.EdgeRemoval_DONE3_branch`
- **Line**: ShapeFix_Wire.cxx:1158  **Axis**: `healer-state`
- **Brief**: Removes previous edge when intersection was fixed by eliminating it (DONE3).
- **Falsifiable claim**: Without this branch, the previous edge marked for removal would persist, leaving degenerate geometry. To test: provide pair of edges where previous must be removed to fix intersection.
- **Minimal reproducer**: Create wire where FixIntersectingEdges(num) returns DONE3 (remove previous). Without the branch: previous edge left in place. With branch: correctly removes num-1 (or wrapped index for num=1).
- **Search anchors**: 'ShapeExtend_DONE3', 'num > 1 ? num - 1 : nb + num - 1'

##### `ShapeFix_Wire.FixSelfIntersection.EdgeRemoval_recovery_loop`
- **Line**: ShapeFix_Wire.cxx:1164  **Axis**: `healer-state`
- **Brief**: Resets iteration pointers after edge removal to rescan from wire start.
- **Falsifiable claim**: Without this reset, iteration state (num, nb) would be inconsistent with the modified wire, causing skipped or out-of-bounds edge checks. To test: remove edge and observe next iteration's bounds.
- **Minimal reproducer**: Create wire where removal of edge N causes iterator to be stale. Without the branch: num and nb not reset, leading to missed or invalid edge accesses. With branch: num reset to 1 (or 2 for open), nb updated.
- **Search anchors**: 'num = (myClosedMode ? 1 : 2)', 'nb = sbwd->NbEdges()'

##### `ShapeFix_Wire.FixSelfIntersection.EdgeRemoval_else_revalidate` **[low-confidence]**
- **Line**: ShapeFix_Wire.cxx:1176  **Axis**: `healer-state`
- **Brief**: Re-validates fixed edge if neither DONE4 nor DONE3 edge removal was applied.
- **Falsifiable claim**: Without this branch, a fix that doesn't remove edges (e.g., trimming in-place) would not be re-validated. To test: fix intersection by trimming bounds; observe whether re-check is applied.
- **Minimal reproducer**: Create wire where FixIntersectingEdges(num) returns DONE1 (reordered) without DONE3/DONE4. Without the branch: no re-validation. With branch: calls FixIntersectingEdges(num) again to confirm.
- **Search anchors**: 'FixIntersectingEdges(num)', 'else'

##### `ShapeFix_Wire.FixSelfIntersection.FixNonAdjacentMode_skip`
- **Line**: ShapeFix_Wire.cxx:1184  **Axis**: `healer-state`
- **Brief**: Skips non-adjacent intersection fixing when mode is disabled.
- **Falsifiable claim**: Without this branch, the kernel would always attempt to fix non-adjacent edge pairs. To test: set FixNonAdjacentIntersectingEdgesMode to disabled; observe whether non-adjacent intersections are still fixed.
- **Minimal reproducer**: Create wire where edge 1 and edge 3 (non-adjacent) intersect. Set FixNonAdjacentIntersectingEdgesMode to 0. Call FixSelfIntersection(). Without the branch: non-adjacent pair fixed. With branch: left unfixed.
- **Search anchors**: 'NeedFix', 'myFixNonAdjacentIntersectingEdgesMode'

##### `ShapeFix_Wire.FixSelfIntersection.IntersectionToolSuccess`
- **Line**: ShapeFix_Wire.cxx:1189  **Axis**: `api-contract`
- **Brief**: Reports DONE5 when ShapeFix_IntersectionTool successfully fixes non-adjacent intersections.
- **Falsifiable claim**: Without this branch, caller would not know that non-adjacent intersections were fixed. To test: provide wire with non-adjacent intersections; observe whether DONE5 is reported.
- **Minimal reproducer**: Create wire with non-adjacent intersecting edges. Call FixSelfIntersection(). If ITool.FixSelfIntersectWire() returns true, without the branch: DONE5 not set. With branch: status updated.
- **Search anchors**: 'ShapeExtend_DONE5'

##### `ShapeFix_Wire.FixSelfIntersection.NonAdjacentEdge_invalidation`
- **Line**: ShapeFix_Wire.cxx:1193  **Axis**: `healer-state`
- **Brief**: Invalidates cached shape when non-adjacent intersection fix modifies wire (split/remove).
- **Falsifiable claim**: Without the nullify, the cached wire shape would become stale, returning wrong geometry on next access. To test: fix non-adjacent intersection and immediately query wire geometry; observe consistency.
- **Minimal reproducer**: Create wire, fix non-adjacent intersection with NbSplit > 0. Without the branch: myShape still references old wire topology. With branch: myShape.Nullify() forces rebuild.
- **Search anchors**: 'myShape.Nullify()'

##### `ShapeFix_Wire.FixSelfIntersection.NonAdjacentRemovalFlag`
- **Line**: ShapeFix_Wire.cxx:1197  **Axis**: `api-contract`
- **Brief**: Sets removal flag when non-adjacent edge fixing removes edges to signal downstream processing.
- **Falsifiable claim**: Without this flag, downstream code would not know that edge removal occurred during non-adjacent fixing. To test: fix non-adjacent intersection with removal; observe whether removal is reported.
- **Minimal reproducer**: Create wire where ShapeFix_IntersectionTool removes edges (NbRemoved > 0). Without the branch: myStatusRemovedSegment not set. With branch: flag signals removal occurred.
- **Search anchors**: 'myStatusRemovedSegment'

##### `ShapeFix_Wire.FixSelfIntersection.NonAdjacentAnalyzerReload`
- **Line**: ShapeFix_Wire.cxx:1202  **Axis**: `healer-state`
- **Brief**: Reloads analyzer when non-adjacent fixing modifies wire to maintain consistent state.
- **Falsifiable claim**: Without this reload, analyzer's internal state would be stale and subsequent fixes might operate on wrong geometry. To test: fix non-adjacent intersection; verify subsequent operations use updated edge list.
- **Minimal reproducer**: Create wire with non-adjacent intersection. After FixSelfIntersectWire() modifies sbwd (NbSplit > 0), without the branch: myAnalyzer still references old sbwd. With branch: Load(sbwd) updates analyzer.
- **Search anchors**: 'myAnalyzer->Load(sbwd)'


### ShapeFix_Wireframe

#### `ShapeFix_Wireframe.FixSmallEdges`
 (10 branches; source: `v3-deep-ShapeFix_Wireframe_FixSmallEdges_FixWireGaps.json`)

##### `ShapeFix_Wireframe.FixSmallEdges.null-shape-early-return`
- **Line**: ShapeFix_Wireframe.cxx:507  **Axis**: `input-shape`
- **Brief**: Early return when input shape is null.
- **Falsifiable claim**: Without this branch, kernel would crash dereferencing null in CheckSmallEdges. To test: call with null shape; verify false returned immediately.
- **Minimal reproducer**: Construct ShapeFix_Wireframe with null TopoDS_Shape. Call FixSmallEdges(). Without: null-deref. With: returns false.
- **Search anchors**: 'if (myShape.IsNull())', 'return false;'

##### `ShapeFix_Wireframe.FixSmallEdges.context-initialization`
- **Line**: ShapeFix_Wireframe.cxx:511  **Axis**: `healer-state`
- **Brief**: Context created if missing; else prior transformations re-applied to myShape.
- **Falsifiable claim**: Without context re-application, prior repairs would be lost. To test: apply FixSmallEdges twice; second call should preserve first's results.
- **Minimal reproducer**: Load shape. FixSmallEdges(). Get Shape(). Load again. FixSmallEdges() again. Without: second call resets shape. With: builds on prior.
- **Search anchors**: 'Context().IsNull()', 'SetContext(new ShapeBuild_ReShape)', 'myShape = Context()->Apply(shape)'

##### `ShapeFix_Wireframe.FixSmallEdges.compound-recursive-dispatch`
- **Line**: ShapeFix_Wireframe.cxx:519  **Axis**: `kernel-pair`
- **Brief**: Recursively processes each sub-solid in COMPOUND separately.
- **Falsifiable claim**: Without recursion, small edges in different sub-solids would merge incorrectly. To test: compound of two solids with different small edge patterns; verify independent processing.
- **Minimal reproducer**: Create COMPOUND with two solids, each with different small edges. Call FixSmallEdges(). Without: edges merged across solids. With: each solid processed independently.
- **Search anchors**: 'myShape.ShapeType() == TopAbs_COMPOUND', 'for (TopoDS_Iterator it(savShape)'

##### `ShapeFix_Wireframe.FixSmallEdges.compound-caching`
- **Line**: ShapeFix_Wireframe.cxx:531  **Axis**: `healer-state`
- **Brief**: Deduplicates identical sub-shapes via shape map to avoid double-processing.
- **Falsifiable claim**: Without caching, identical sub-shapes would be merged multiple times with state divergence. To test: compound with duplicate member; verify single merge result reused.
- **Minimal reproducer**: COMPOUND with same solid added twice. FixSmallEdges(). Without: both edges merged separately. With: second lookup hits cache.
- **Search anchors**: 'cont.IsBound(shape1)', 'cont.Find(shape1)', 'cont.Bind(myShape, res)'

##### `ShapeFix_Wireframe.FixSmallEdges.null-result-skip`
- **Line**: ShapeFix_Wireframe.cxx:548  **Axis**: `input-shape`
- **Brief**: Skips adding null results (completely merged/removed sub-shapes) to compound.
- **Falsifiable claim**: Without null-skip, compound would contain null members causing downstream crashes. To test: small edge that completely collapses; verify not added to output.
- **Minimal reproducer**: COMPOUND where merging small edges completely removes one sub-solid. Call FixSmallEdges(). Without: null added to result. With: null skipped, compound smaller.
- **Search anchors**: 'if (res.IsNull())', 'continue;'

##### `ShapeFix_Wireframe.FixSmallEdges.compound-orientation-preservation`
- **Line**: ShapeFix_Wireframe.cxx:530  **Axis**: `input-shape`
- **Brief**: Orientation of cached sub-shape result is re-oriented to match input.
- **Falsifiable claim**: Without re-orientation, flipped sub-shapes would lose their orientation. To test: add REVERSED sub-solid; verify result carries same orientation.
- **Minimal reproducer**: COMPOUND with FORWARD and REVERSED solids. FixSmallEdges(). Without: orientations normalized. With: orientations preserved.
- **Search anchors**: '.Oriented(shape1.Orientation())', 'shape1.Orientation()'

##### `ShapeFix_Wireframe.FixSmallEdges.compound-location-restoration`
- **Line**: ShapeFix_Wireframe.cxx:527  **Axis**: `input-shape`
- **Brief**: Spatial location is stripped for processing and re-applied post-repair.
- **Falsifiable claim**: Without location restoration, transformed sub-shapes would lose placement. To test: rotated sub-solid; verify position unchanged after small-edge merge.
- **Minimal reproducer**: Solid with translation. Add to COMPOUND. FixSmallEdges(). Without: translation lost. With: translation preserved.
- **Search anchors**: 'shape1.Location(nullLoc)', 'res.Location(L)'

##### `ShapeFix_Wireframe.FixSmallEdges.compound-early-return-success`
- **Line**: ShapeFix_Wireframe.cxx:558  **Axis**: `healer-state`
- **Brief**: Returns immediately after compound processing, skipping CheckSmallEdges on compound.
- **Falsifiable claim**: Without early return, compound members would be checked twice (once recursively, once in CheckSmallEdges). To test: verify no double status bits set.
- **Minimal reproducer**: COMPOUND with small edges. FixSmallEdges(). Check status. Without: bits duplicated. With: set once from recursion.
- **Search anchors**: 'return StatusSmallEdges(ShapeExtend_DONE);'

##### `ShapeFix_Wireframe.FixSmallEdges.check-and-merge-dispatch`
- **Line**: ShapeFix_Wireframe.cxx:560  **Axis**: `kernel-pair`
- **Brief**: Dispatches to CheckSmallEdges to identify small edges, then MergeSmallEdges to fix them.
- **Falsifiable claim**: Without this dispatch, small edges would not be detected or merged. To test: shape with small edge below tolerance; verify edge merged.
- **Minimal reproducer**: Create EDGE with length < Precision::Confusion(). Add to face/solid. FixSmallEdges(). Without: edge remains. With: merged with adjacent.
- **Search anchors**: 'CheckSmallEdges(theSmallEdges', 'MergeSmallEdges(theSmallEdges'

##### `ShapeFix_Wireframe.FixSmallEdges.unconditional-success-return`
- **Line**: ShapeFix_Wireframe.cxx:563  **Axis**: `api-contract`
- **Brief**: Always returns true (StatusSmallEdges(ShapeExtend_DONE)) after CheckSmallEdges and MergeSmallEdges.
- **Falsifiable claim**: Without unconditional return, failure cases in CheckSmallEdges/MergeSmallEdges might be lost. To test: verify return is true regardless of merge success.
- **Minimal reproducer**: Shape with/without small edges. FixSmallEdges(). Always returns true. Status bits indicate if actual work done.
- **Search anchors**: 'return StatusSmallEdges(ShapeExtend_DONE);'


#### `ShapeFix_Wireframe.FixWireGaps`
 (23 branches; source: `v3-deep-ShapeFix_Wireframe_FixSmallEdges_FixWireGaps.json`)

##### `ShapeFix_Wireframe.FixWireGaps.null-shape-early-return`
- **Line**: ShapeFix_Wireframe.cxx:99  **Axis**: `input-shape`
- **Brief**: Early return when input shape is null.
- **Falsifiable claim**: Without this branch, the kernel would attempt to dereference a null shape in downstream explorers. To test: call FixWireGaps with null shape and verify false is returned immediately.
- **Minimal reproducer**: Construct ShapeFix_Wireframe with null TopoDS_Shape. Call FixWireGaps(). Without branch: null-deref crash. With: returns false.
- **Search anchors**: 'if (myShape.IsNull())', 'return false;'

##### `ShapeFix_Wireframe.FixWireGaps.context-initialization`
- **Line**: ShapeFix_Wireframe.cxx:103  **Axis**: `healer-state`
- **Brief**: Context is lazily created if missing; else re-applies prior transformations.
- **Falsifiable claim**: Without the context re-application branch, prior repairs in the context would not propagate to myShape. To test: apply FixWireGaps twice; second call should see results of first.
- **Minimal reproducer**: Create ShapeFix_Wireframe with valid shape. FixWireGaps(). Call Shape() to get modified. Load that shape again and FixWireGaps() again. Without: old state replayed. With: new state built upon.
- **Search anchors**: 'Context().IsNull()', 'SetContext(new ShapeBuild_ReShape)', 'myShape = Context()->Apply(shape)'

##### `ShapeFix_Wireframe.FixWireGaps.compound-recursive-dispatch`
- **Line**: ShapeFix_Wireframe.cxx:111  **Axis**: `kernel-pair`
- **Brief**: Recursive FixWireGaps call for each sub-solid when input is COMPOUND.
- **Falsifiable claim**: Without this branch, compound solids would be processed as monolithic, losing per-sub-solid repair. To test: create compound of two solids with different gap patterns; verify both are fixed independently.
- **Minimal reproducer**: Construct COMPOUND with two solid members, each with 3d/2d wire gaps in different patterns. Call FixWireGaps(). Without: only first gap pattern fixed. With: both patterns independently repaired.
- **Search anchors**: 'myShape.ShapeType() == TopAbs_COMPOUND', 'for (TopoDS_Iterator it(savShape)'

##### `ShapeFix_Wireframe.FixWireGaps.compound-caching-deduplication`
- **Line**: ShapeFix_Wireframe.cxx:123  **Axis**: `healer-state`
- **Brief**: Deduplicates identical sub-shapes within compound using shape map to avoid redundant repairs.
- **Falsifiable claim**: Without caching, identical sub-shapes would be repaired multiple times with potential state divergence. To test: create compound with duplicate refs; verify status coalesces.
- **Minimal reproducer**: Construct COMPOUND with same solid added twice. Load into ShapeFix_Wireframe. Call FixWireGaps(). Without: both entries repaired separately. With: second lookup hits cache, single repair result used.
- **Search anchors**: 'cont.IsBound(shape1)', 'cont.Find(shape1)', 'cont.Bind(myShape, res)'

##### `ShapeFix_Wireframe.FixWireGaps.compound-orientation-preservation`
- **Line**: ShapeFix_Wireframe.cxx:122  **Axis**: `input-shape`
- **Brief**: Orientation of sub-shape is preserved even when using cached result.
- **Falsifiable claim**: Without orientation re-application, flipped orientations in compound would be lost. To test: add reversed sub-shape; verify result carries same orientation.
- **Minimal reproducer**: Create COMPOUND with one solid FORWARD, one REVERSED. Call FixWireGaps(). Without: orientations normalized. With: original orientations maintained.
- **Search anchors**: '.Oriented(shape1.Orientation())', 'shape1.Orientation()'

##### `ShapeFix_Wireframe.FixWireGaps.compound-location-restoration`
- **Line**: ShapeFix_Wireframe.cxx:119  **Axis**: `input-shape`
- **Brief**: Spatial location (transformation) is stripped for processing and re-applied post-repair.
- **Falsifiable claim**: Without location re-application, transformed sub-shapes would lose their placement. To test: add rotated/translated sub-shape; verify spatial position unchanged after repair.
- **Minimal reproducer**: Create solid with translation gp_Trsf. Add to COMPOUND. Load and FixWireGaps(). Without: translation lost. With: translation preserved.
- **Search anchors**: 'shape1.Location(nullLoc)', 'res.Location(L)'

##### `ShapeFix_Wireframe.FixWireGaps.compound-return-early-success`
- **Line**: ShapeFix_Wireframe.cxx:136  **Axis**: `healer-state`
- **Brief**: Returns immediately after compound processing without processing non-compound faces.
- **Falsifiable claim**: Without early return, compound members would be repaired twice (once recursively, once in face loop). To test: verify no double-healing on compound.
- **Minimal reproducer**: Create COMPOUND with one solid. Call FixWireGaps(). Check status bits. Without: status OR'd twice. With: status set once from recursive call.
- **Search anchors**: 'return StatusWireGaps(ShapeExtend_DONE);'

##### `ShapeFix_Wireframe.FixWireGaps.precision-selection`
- **Line**: ShapeFix_Wireframe.cxx:112  **Axis**: `tolerance`
- **Brief**: Uses caller-provided precision if positive; falls back to Precision::Confusion().
- **Falsifiable claim**: Without fallback, zero/negative precision would cause downstream healing failures. To test: call with Precision()=-1 and verify Confusion() is used.
- **Minimal reproducer**: Load shape. Set Precision(-1). Call FixWireGaps(). Inspect sfw->Precision(). Without: undefined behavior. With: Confusion() substituted.
- **Search anchors**: '(Precision() > 0.) ? Precision() : Precision::Confusion()'

##### `ShapeFix_Wireframe.FixWireGaps.face-orientation-normalization`
- **Line**: ShapeFix_Wireframe.cxx:149  **Axis**: `input-shape`
- **Brief**: Face orientation is normalized to FORWARD before wire processing.
- **Falsifiable claim**: Without normalization, REVERSED faces might cause inconsistent gap-fixing orientation. To test: use REVERSED face; verify orientation corrected for healing.
- **Minimal reproducer**: Create FACE with REVERSED orientation containing wire with gaps. Call FixWireGaps(). Verify internal processing used FORWARD; result orientation preserved externally.
- **Search anchors**: 'if (face.Orientation() == TopAbs_REVERSED)', 'face.Orientation(TopAbs_FORWARD)'

##### `ShapeFix_Wireframe.FixWireGaps.wire-type-check`
- **Line**: ShapeFix_Wireframe.cxx:157  **Axis**: `input-shape`
- **Brief**: Skips non-WIRE sub-elements within faces using type filter.
- **Falsifiable claim**: Without type check, SHELL/SOLID sub-elements would cause unexpected behavior in wire healing. To test: malformed face with shell sub-element; verify skipped.
- **Minimal reproducer**: Construct Face with both WIRE and SHELL children. Call FixWireGaps(). Without: shell passed to sfw->Init, crash. With: shell skipped, only wires processed.
- **Search anchors**: 'if (itw.Value().ShapeType() != TopAbs_WIRE)', 'continue;'

##### `ShapeFix_Wireframe.FixWireGaps.context-apply-transitive`
- **Line**: ShapeFix_Wireframe.cxx:152  **Axis**: `healer-state`
- **Brief**: Context is re-applied to shape before using it (accounts for mutations by other fixers).
- **Falsifiable claim**: Without context re-application, prior shape modifications (e.g., from other repair steps) would be discarded. To test: modify shape via context; verify mutations carried forward.
- **Minimal reproducer**: Create Context. Modify wire via Context()->Replace(). Load shape into fixer. FixWireGaps(). Without: Replace lost. With: Replace visible in fixer.
- **Search anchors**: 'Context()->Apply(anExpf1.Current())', 'tmpF = Context()->Apply'

##### `ShapeFix_Wireframe.FixWireGaps.fix-gaps-3d-dispatch`
- **Line**: ShapeFix_Wireframe.cxx:163  **Axis**: `kernel-pair`
- **Brief**: Invokes ShapeFix_Wire.FixGaps3d() on each wire; status bits OR'd into myStatusWireGaps.
- **Falsifiable claim**: Without this dispatch, 3d gap defects would not be detected or fixed. To test: wire with 3d gap; verify gap closed and status DONE1 set.
- **Minimal reproducer**: Create WIRE with disconnected endpoints in 3d (gap > tolerance). Add to FACE. Call FixWireGaps(). Without: endpoints remain disconnected. With: gap closed, status DONE1.
- **Search anchors**: 'sfw->FixGaps3d()', 'myStatusWireGaps |= ShapeExtend::EncodeStatus(ShapeExtend_DONE1)'

##### `ShapeFix_Wireframe.FixWireGaps.fix-gaps-3d-failure-capture`
- **Line**: ShapeFix_Wireframe.cxx:167  **Axis**: `conformance-probe`
- **Brief**: Captures FixGaps3d failure status and propagates as FAIL1 in myStatusWireGaps.
- **Falsifiable claim**: Without failure capture, gap-closing errors would be silent. To test: wire with gap unsolvable in 3d; verify FAIL1 status set.
- **Minimal reproducer**: Create WIRE with pathological 3d gap (e.g., in degenerate surface). Call FixWireGaps(). Without: failure not reported. With: StatusWireGaps(ShapeExtend_FAIL1) true.
- **Search anchors**: 'if (sfw->StatusGaps3d(ShapeExtend_FAIL))', 'myStatusWireGaps |= ShapeExtend::EncodeStatus(ShapeExtend_FAIL1)'

##### `ShapeFix_Wireframe.FixWireGaps.fix-gaps-2d-dispatch`
- **Line**: ShapeFix_Wireframe.cxx:170  **Axis**: `kernel-pair`
- **Brief**: Invokes FixGaps2d() to close gaps in parameter space (2d curves).
- **Falsifiable claim**: Without 2d gap closing, wires could have parametrically disconnected curves even after 3d closure. To test: wire with 3d close but 2d far; verify 2d gap closed.
- **Minimal reproducer**: Create WIRE where 3d endpoints close but 2d endpoints distant (e.g., near seam). Call FixWireGaps(). Without: 2d mismatch remains. With: 2d gap repaired, status DONE2.
- **Search anchors**: 'sfw->FixGaps2d()', 'ShapeExtend_DONE2'

##### `ShapeFix_Wireframe.FixWireGaps.fix-gaps-2d-failure-capture`
- **Line**: ShapeFix_Wireframe.cxx:174  **Axis**: `conformance-probe`
- **Brief**: Captures FixGaps2d failure status as FAIL2.
- **Falsifiable claim**: Without failure capture, 2d healing failures would silently pass. To test: surface with bad parametrization where 2d gap cannot close; verify FAIL2 set.
- **Minimal reproducer**: Create FACE with badly parametrized PCURVE on wire. Call FixWireGaps(). Without: 2d failure not flagged. With: StatusWireGaps(ShapeExtend_FAIL2) true.
- **Search anchors**: 'if (sfw->StatusGaps2d(ShapeExtend_FAIL))', 'ShapeExtend_FAIL2'

##### `ShapeFix_Wireframe.FixWireGaps.warning-emission-on-repair`
- **Line**: ShapeFix_Wireframe.cxx:179  **Axis**: `api-contract`
- **Brief**: Emits warning message when any gap (3d or 2d) is actually fixed.
- **Falsifiable claim**: Without warning, users would not be notified of gap corrections. To test: fix gap and check warning message sent.
- **Minimal reproducer**: Create WIRE with gap. Enable message logging. Call FixWireGaps(). Without: no warning emitted. With: 'FixWireframe.FixFixWireGaps.MSG0' warning visible.
- **Search anchors**: 'SendWarning(itw.Value()', 'FixWireframe.FixFixWireGaps.MSG0'

##### `ShapeFix_Wireframe.FixWireGaps.free-wire-3d-gap-dispatch`
- **Line**: ShapeFix_Wireframe.cxx:193  **Axis**: `input-shape`
- **Brief**: Processes wires not on any face (free 3d wires) using TopExp_Explorer with TopAbs_FACE filter.
- **Falsifiable claim**: Without this branch, orphaned 3d wires (not members of any face) would not be healed. To test: create free WIRE with 3d gap; verify gap closed.
- **Minimal reproducer**: Create WIRE standalone (not in any FACE). Add to shape. Call FixWireGaps(). Without: gap remains. With: gap fixed via free-wire handling.
- **Search anchors**: 'TopExp_Explorer expw(myShape, TopAbs_WIRE, TopAbs_FACE)', 'expw.More()'

##### `ShapeFix_Wireframe.FixWireGaps.conditional-post-processing`
- **Line**: ShapeFix_Wireframe.cxx:213  **Axis**: `healer-state`
- **Brief**: Post-processing (SameParameter, FixSelfIntersection, FixVertexTolerance) only runs if any gap was actually fixed.
- **Falsifiable claim**: Without conditional check, unnecessary post-processing would degrade performance on already-valid shapes. To test: shape with no gaps; verify post-processing skipped.
- **Minimal reproducer**: Create valid SHAPE with no gaps. Call FixWireGaps(). Measure post-processing time. Without: post-processing always runs. With: skipped if no fixes needed.
- **Search anchors**: 'if (StatusWireGaps(ShapeExtend_DONE))'

##### `ShapeFix_Wireframe.FixWireGaps.same-parameter-sync`
- **Line**: ShapeFix_Wireframe.cxx:217  **Axis**: `kernel-pair`
- **Brief**: Calls ShapeFix::SameParameter to synchronize 3d and 2d curve parametrizations.
- **Falsifiable claim**: Without SameParameter call, 3d/2d misalignment would persist after gap closure. To test: verify same-parameter property holds post-repair.
- **Minimal reproducer**: Wire with gap and parametrization mismatch. Call FixWireGaps(). Without: SameParameter property not enforced. With: 3d/2d param aligned.
- **Search anchors**: 'ShapeFix::SameParameter(myShape, false)'

##### `ShapeFix_Wireframe.FixWireGaps.self-intersection-fix`
- **Line**: ShapeFix_Wireframe.cxx:232  **Axis**: `kernel-pair`
- **Brief**: Fixes self-intersections of wires that may have been introduced by gap closure.
- **Falsifiable claim**: Without self-intersection removal, gap closure could create loops/crossings. To test: gap closure that creates crossing; verify removed.
- **Minimal reproducer**: WIRE with gap where closure would self-intersect. Call FixWireGaps(). Without: self-intersection remains. With: FixSelfIntersection called, crossing removed.
- **Search anchors**: 'sfw->FixSelfIntersection()'

##### `ShapeFix_Wireframe.FixWireGaps.vertex-tolerance-fixup`
- **Line**: ShapeFix_Wireframe.cxx:234  **Axis**: `tolerance`
- **Brief**: Adjusts vertex tolerances on all edges to ensure they accommodate endpoint geometry.
- **Falsifiable claim**: Without tolerance adjustment, vertices could fall outside their edges' tolerance bounds. To test: verify vertex tolerance >= max distance to edge endpoints.
- **Minimal reproducer**: WIRE after gap closure where vertices too tight. Call FixWireGaps(). Without: vertices may be out of tolerance. With: vertex tolerance expanded.
- **Search anchors**: 'sfe->FixVertexTolerance(TopoDS::Edge(ite.Value()))'

##### `ShapeFix_Wireframe.FixWireGaps.free-wire-post-processing`
- **Line**: ShapeFix_Wireframe.cxx:242  **Axis**: `kernel-pair`
- **Brief**: Post-processing (reorder, self-intersection, tolerance) also applied to free wires.
- **Falsifiable claim**: Without post-processing free wires, they would be left in inconsistent state after gap closure. To test: verify free wire reordered and cleaned up.
- **Minimal reproducer**: Free WIRE with gap. Call FixWireGaps(). Verify wire is reordered and self-intersections fixed.
- **Search anchors**: 'for (TopExp_Explorer expw2(myShape, TopAbs_WIRE, TopAbs_FACE)'

##### `ShapeFix_Wireframe.FixWireGaps.success-return-condition`
- **Line**: ShapeFix_Wireframe.cxx:254  **Axis**: `api-contract`
- **Brief**: Returns true only if gap fixing was attempted and succeeded (status DONE); false otherwise.
- **Falsifiable claim**: Without conditional return, success/failure would be ambiguous. To test: shape with no gaps returns false; shape with fixed gaps returns true.
- **Minimal reproducer**: Create two shapes: one with gaps, one without. Call FixWireGaps() on each. First: true. Second: false.
- **Search anchors**: 'return true;', 'return false;'


#### `ShapeFix_Wireframe.MergeSmallEdges`
 (54 branches; 1 low-confidence; source: `v3-deep-ShapeFix_Wireframe_MergeSmallEdges.json`)

##### `ShapeFix_Wireframe.MergeSmallEdges.empty_set_guard`
- **Line**: ShapeFix_Wireframe.cxx:741  **Axis**: `api-contract`
- **Brief**: Entry guard: method early-exits if input small-edges set is empty.
- **Falsifiable claim**: Without this guard, the algorithm would iterate over empty face-maps and produce redundant Shape context operations. To test: pass a TopoDS_Shape with no small edges; verify no context changes occur.
- **Minimal reproducer**: Construct a valid FACE with all edges >= tolerance (e.g., a 10x10 square). Call MergeSmallEdges(). Verify Context()->Apply() returns the original shape unchanged.
- **Search anchors**: 'theSmallEdges.IsEmpty()', 'early return', 'guard condition'

##### `ShapeFix_Wireframe.MergeSmallEdges.face_binding_check`
- **Line**: ShapeFix_Wireframe.cxx:752  **Axis**: `healer-state`
- **Brief**: Filter faces in the face-to-small-edges map; skip if not bound.
- **Falsifiable claim**: Without this check, unbound face lookups would throw or cause silent failure. To test: verify iteration only processes faces present in theFaceWithSmall map.
- **Minimal reproducer**: Create a COMPOUND with multiple FACEs; mark only one FACE as having small edges in the map. Verify only that face is processed; others are skipped.
- **Search anchors**: 'theFaceWithSmall.IsBound()', 'face iteration', 'map lookup'

##### `ShapeFix_Wireframe.MergeSmallEdges.extent_nonzero_check`
- **Line**: ShapeFix_Wireframe.cxx:754  **Axis**: `healer-state`
- **Brief**: Verify the face actually contains small edges (map value extent > 0).
- **Falsifiable claim**: Without this check, processing empty lists wastes resources and may cause wire data inconsistencies. To test: verify faces with zero small edges in the map are skipped.
- **Minimal reproducer**: Add a FACE to theFaceWithSmall but with an empty edge list. Verify no wire processing occurs for that face.
- **Search anchors**: 'theList.Extent()', 'non-zero check', 'empty list guard'

##### `ShapeFix_Wireframe.MergeSmallEdges.context_face_refresh`
- **Line**: ShapeFix_Wireframe.cxx:757-759  **Axis**: `healer-state`
- **Brief**: Fetch face from context to detect prior transformations; skip if unchanged.
- **Falsifiable claim**: Without this refresh, stale face geometry would cause edge-lookup failures in wires. To test: apply context transformation to a face, then verify the fetched face matches the transformed version.
- **Minimal reproducer**: Create a FACE with small edges. Apply a context replacement (e.g., scale). Call MergeSmallEdges(). Verify edges are found in the refreshed face, not the original.
- **Search anchors**: 'Context()->Apply()', 'face refresh', 'smh#8 comment', 'IsSame()'

##### `ShapeFix_Wireframe.MergeSmallEdges.edge_replacement_cascade`
- **Line**: ShapeFix_Wireframe.cxx:765-780  **Axis**: `healer-state`
- **Brief**: When face is replaced in context, update all small-edge references and edge-to-faces map entries.
- **Falsifiable claim**: Without cascading edge updates, orphaned references to old edges would cause lookup failures later. To test: replace a face in context; verify that small edges from the original face are updated to reference new edges.
- **Minimal reproducer**: Create FACE F with small edge E. Replace F in context with F_new. Verify: (a) E is removed from theSmallEdges and new edge is added; (b) theEdgeToFaces(newEdge) exists.
- **Search anchors**: 'Context()->Status()', 'edge replacement', 'theSmallEdges.Remove/Add', 'theEdgeToFaces map update'

##### `ShapeFix_Wireframe.MergeSmallEdges.wire_shape_filter`
- **Line**: ShapeFix_Wireframe.cxx:788-790  **Axis**: `input-shape`
- **Brief**: Skip sub-shapes in a face that are not WIRE types (e.g., SHELL, VERTEX).
- **Falsifiable claim**: Without filtering, non-wire sub-shapes would cause ShapeFix_Wire to fail or corrupt geometry. To test: create a face with mixed shape types; verify only wires are processed.
- **Minimal reproducer**: Construct FACE with interior shell or vertex sub-shapes. Verify iteration skips them without throwing.
- **Search anchors**: 'TopAbs_WIRE', 'ShapeType()', 'type check', 'continue'

##### `ShapeFix_Wireframe.MergeSmallEdges.face_orientation_normalization`
- **Line**: ShapeFix_Wireframe.cxx:793-795  **Axis**: `conformance-probe`
- **Brief**: Normalize face to FORWARD orientation for consistent wire analysis.
- **Falsifiable claim**: Without normalization, reversed faces would cause angle calculations and vertex orders to be inverted, leading to incorrect merge decisions. To test: process faces with opposite orientations; verify merge decisions are consistent.
- **Minimal reproducer**: Create two identical faces with opposite orientations. Apply MergeSmallEdges to each. Verify the same edges are merged in both cases.
- **Search anchors**: 'Orientation() == TopAbs_REVERSED', 'Oriented(TopAbs_FORWARD)', 'orientation normalization'

##### `ShapeFix_Wireframe.MergeSmallEdges.wire_data_init`
- **Line**: ShapeFix_Wireframe.cxx:797-800  **Axis**: `kernel-pair`
- **Brief**: Initialize wire processing: wrap raw wire in ShapeExtend_WireData and reorder edges.
- **Falsifiable claim**: Without reordering, circular wire traversal would fail if edges are out of sequence. To test: pass a wire with scrambled edge order; verify FixReorder() connects them.
- **Minimal reproducer**: Create WIRE with edges in non-circular order. Verify SFW->FixReorder() produces connected sequence.
- **Search anchors**: 'ShapeExtend_WireData', 'FixReorder()', 'wire initialization'

##### `ShapeFix_Wireframe.MergeSmallEdges.loop_bounds_check`
- **Line**: ShapeFix_Wireframe.cxx:803-806  **Axis**: `api-contract`
- **Brief**: Main loop over wire edges: terminate if wire shrinks to single edge or index out of bounds.
- **Falsifiable claim**: Without bounds checking, array access would cause segfault or process stale edges. To test: verify loop terminates when NbEdges() becomes 1.
- **Minimal reproducer**: Create WIRE with 3 small edges. Call MergeSmallEdges. Verify loop exits when only 1 edge remains.
- **Search anchors**: 'index <= SFW->WireData()->NbEdges()', 'SFW->NbEdges() > 1', 'loop bound'

##### `ShapeFix_Wireframe.MergeSmallEdges.prev_next_wraparound`
- **Line**: ShapeFix_Wireframe.cxx:805-806  **Axis**: `api-contract`
- **Brief**: Circular index arithmetic: wrap prev and next indices at wire boundaries.
- **Falsifiable claim**: Without wraparound, boundary edges (first, last) would not have valid neighbors, breaking loop-closure checks. To test: verify processing of edge at index 1 and index NbEdges().
- **Minimal reproducer**: Create WIRE with small edge at index 1. Verify prev index wraps to NbEdges. Similarly for last edge.
- **Search anchors**: '(index == 1) ? SFW->WireData()->NbEdges() : index - 1', 'wraparound', 'circular'

##### `ShapeFix_Wireframe.MergeSmallEdges.seam_edge_duplicate_guard`
- **Line**: ShapeFix_Wireframe.cxx:812-817  **Axis**: `input-shape`
- **Brief**: Skip processing if middle edge is identical to either neighbor (degenerate triplet).
- **Falsifiable claim**: Without this guard, attempting to merge an edge with itself would corrupt wire topology and create self-referential geometry. To test: inject a duplicate edge into triplet; verify it is skipped.
- **Minimal reproducer**: Create WIRE with pattern [E1, E1, E2]. Verify index++ skips the duplicate E1.
- **Search anchors**: 'edge2.IsSame(edge1)', 'edge2.IsSame(edge3)', 'degenerate triplet'

##### `ShapeFix_Wireframe.MergeSmallEdges.small_edge_selection`
- **Line**: ShapeFix_Wireframe.cxx:822-824  **Axis**: `input-shape`
- **Brief**: Filter loop: process only triplets where middle edge is in the small-edges set.
- **Falsifiable claim**: Without this filter, normal-sized edges would be merged, shrinking the wire unnecessarily. To test: verify only edges in theSmallEdges are candidates for merging.
- **Minimal reproducer**: Create WIRE with mix of small and large edges. Verify only small-edge triplets trigger merge logic.
- **Search anchors**: 'theSmallEdges.Contains(edge2)', 'middle edge filter'

##### `ShapeFix_Wireframe.MergeSmallEdges.self_loop_detection`
- **Line**: ShapeFix_Wireframe.cxx:825  **Axis**: `input-shape`
- **Brief**: Detect if previous and next edges are the same (self-loop or hairpin structure).
- **Falsifiable claim**: Without self-loop detection, merge logic would incorrectly reduce a [E, E_small, E] pattern (hairpin) to [E], losing the hairpin geometry. To test: construct hairpin; verify merge logic is aware of this pattern.
- **Minimal reproducer**: Create hairpin: WIRE [E1, E_small, E1]. Call MergeSmallEdges(). Verify IsAnyJoin flag is set.
- **Search anchors**: 'edge1.IsSame(edge3)', 'IsAnyJoin', 'hairpin'

##### `ShapeFix_Wireframe.MergeSmallEdges.curve3d_extraction`
- **Line**: ShapeFix_Wireframe.cxx:831-833  **Axis**: `encoding`
- **Brief**: Extract 3D parametric curves from edges; skip merge if extraction fails.
- **Falsifiable claim**: Without 3D curves, angle calculations would fail. To test: verify merge is skipped if any of 3 edges lacks a 3D curve.
- **Minimal reproducer**: Create edge with only 2D (surface) geometry. Verify SAE.Curve3d() returns false and merge is skipped.
- **Search anchors**: 'SAE.Curve3d()', '3D curve extraction', 'parameter range'

##### `ShapeFix_Wireframe.MergeSmallEdges.angle_tangent_evaluation`
- **Line**: ShapeFix_Wireframe.cxx:838-874  **Axis**: `conformance-probe`
- **Brief**: Evaluate tangent vectors at edge endpoints; compute turn angles at junctions.
- **Falsifiable claim**: Without tangent evaluation, merge decisions would be blind to geometry discontinuities (e.g., sharp corners), leading to invalid topology. To test: compare merge behavior on sharp vs. smooth junctions.
- **Minimal reproducer**: Create two wires: one with smooth junction (angle ~0), one with 90-degree corner. Verify merge is chosen differently for each.
- **Search anchors**: 'C1->D1()', 'C2->D1()', 'C3->D1()', 'tangent vector', 'Vec1.Angle(Vec2)'

##### `ShapeFix_Wireframe.MergeSmallEdges.degenerate_tangent_handling`
- **Line**: ShapeFix_Wireframe.cxx:849-856  **Axis**: `tolerance`
- **Brief**: Detect degenerate tangent vectors (magnitude < tolerance); assign default angle.
- **Falsifiable claim**: Without degeneracy check, division-by-zero or NaN angles would corrupt merge decisions. To test: create edge with nearly-zero tangent; verify angle = PI/2.
- **Minimal reproducer**: Create edge with tangent vector magnitude < Precision::Confusion(). Verify angle is set to M_PI/2.
- **Search anchors**: 'tol2 = Precision::SquareConfusion()', 'SquareMagnitude() < tol2', 'Ang1 = M_PI / 2'

##### `ShapeFix_Wireframe.MergeSmallEdges.orientation_adjusted_tangent`
- **Line**: ShapeFix_Wireframe.cxx:840-846  **Axis**: `conformance-probe`
- **Brief**: Reverse tangent vectors for REVERSED-oriented edges to get geometric direction.
- **Falsifiable claim**: Without orientation adjustment, reversed edges would have flipped angles, causing incorrect merge-side selection. To test: merge same edge triplet with opposite orientations; verify same side is chosen.
- **Minimal reproducer**: Create WIRE [E1, E_small, E2] with opposite orientations. Compare merge decisions.
- **Search anchors**: 'edge1.Orientation() == TopAbs_REVERSED', 'Vec1.Reverse()', 'geometric direction'

##### `ShapeFix_Wireframe.MergeSmallEdges.multiedge_skip`
- **Line**: ShapeFix_Wireframe.cxx:884-888  **Axis**: `healer-state`
- **Brief**: Skip merge if either edge is in the multi-edge set (shared across many faces).
- **Falsifiable claim**: Without this guard, merging a shared edge would corrupt geometry on all incident faces. To test: create edge shared by 3+ faces; verify it is not merged.
- **Minimal reproducer**: Create SHELL with 3 FACEs sharing a common EDGE. Mark edge as multi-edge. Verify merge is skipped.
- **Search anchors**: 'theMultyEdges.Contains()', 'multi-edge guard'

##### `ShapeFix_Wireframe.MergeSmallEdges.face_adjacency_extent_check`
- **Line**: ShapeFix_Wireframe.cxx:905-910  **Axis**: `kernel-pair`
- **Brief**: Pre-check: both edge pairs must share the same number of incident faces.
- **Falsifiable claim**: Without extent matching, mismatched edge-face relationships would cause invalid merges across disconnected face components. To test: create edges with different face counts; verify merge is skipped.
- **Minimal reproducer**: Create triplet where edge1 touches 1 face, edge2 touches 2 faces. Verify same_set1 = false.
- **Search anchors**: 'theList1.Extent() == theList2.Extent()', 'extent check', 'precondition'

##### `ShapeFix_Wireframe.MergeSmallEdges.seam_consistency_check`
- **Line**: ShapeFix_Wireframe.cxx:905-910  **Axis**: `conformance-probe`
- **Brief**: Seam edges can only be merged with seam neighbors; non-seam only with non-seam.
- **Falsifiable claim**: Without seam consistency, merging a seam edge with non-seam edge would corrupt parametric surface continuity. To test: create FACE with seam; verify merge with non-seam is blocked.
- **Minimal reproducer**: Create FACE of revolution (has seam edge). Attempt to merge seam with non-seam. Verify same_set1 = false.
- **Search anchors**: '(!isSeam && !isSeam1) || (isSeam && isSeam1)', 'seam consistency'

##### `ShapeFix_Wireframe.MergeSmallEdges.face_set_build`
- **Line**: ShapeFix_Wireframe.cxx:911-916  **Axis**: `api-contract`
- **Brief**: Collect all faces incident to middle edge into a set for fast lookup.
- **Falsifiable claim**: Without face-set pre-computation, O(n^2) lookups would make the algorithm quadratic. To test: verify membership queries are O(1).
- **Minimal reproducer**: Create edge incident to 10 faces. Verify theSetOfFaces.Contains() is fast.
- **Search anchors**: 'theSetOfFaces.Add()', 'NCollection_Map', 'face set'

##### `ShapeFix_Wireframe.MergeSmallEdges.face_set_verification_1`
- **Line**: ShapeFix_Wireframe.cxx:917-926  **Axis**: `kernel-pair`
- **Brief**: Verify all faces of edge1 are in the face-set of edge2 (same_set1 = true).
- **Falsifiable claim**: Without this verification, merging would proceed even if edge1 and edge2 don't share faces, creating invalid topology. To test: verify only edges sharing all faces are merged.
- **Minimal reproducer**: Create triplet where edge1 and edge2 share only partial face lists. Verify same_set1 = false after iteration.
- **Search anchors**: 'same_set1 = theSetOfFaces.Contains()', 'face intersection', 'same_set1 && ...'

##### `ShapeFix_Wireframe.MergeSmallEdges.face_set_verification_2`
- **Line**: ShapeFix_Wireframe.cxx:927-936  **Axis**: `kernel-pair`
- **Brief**: Verify all faces of edge3 are in the face-set of edge2 (same_set2 = true).
- **Falsifiable claim**: Without this verification, only one side of the triplet would be validated, allowing asymmetric invalid merges. To test: create edge2 with faces [F1, F2], edge3 with [F3]; verify same_set2 = false.
- **Minimal reproducer**: Create triplet with disjoint edge3 faces. Verify same_set2 = false.
- **Search anchors**: 'same_set2 = theSetOfFaces.Contains()', 'face intersection edge3'

##### `ShapeFix_Wireframe.MergeSmallEdges.both_pair_valid`
- **Line**: ShapeFix_Wireframe.cxx:937-950  **Axis**: `conformance-probe`
- **Brief**: When both edge pairs share faces, choose merge side based on angle difference.
- **Falsifiable claim**: Without angle-based side selection, arbitrary choice would merge the wrong edge, wasting geometry (e.g., merging the longer edge). To test: compare merge side selection for different angle profiles.
- **Minimal reproducer**: Create triplet with Ang1=45deg, Ang2=30deg. Verify take_next = true (merge with edge3).
- **Search anchors**: 'both_sets_valid', 'take_next = (Ang2 < Ang1)', 'angle-driven selection'

##### `ShapeFix_Wireframe.MergeSmallEdges.angle_diff_significance`
- **Line**: ShapeFix_Wireframe.cxx:940-943  **Axis**: `tolerance`
- **Brief**: Compare angle difference against precision threshold; only adjust merge side if significant.
- **Falsifiable claim**: Without significance threshold, numerical noise (e.g., 0.0001 degree difference) would randomly flip merge side, causing non-deterministic output. To test: verify angles differing by less than Precision::Angular() don't change take_next.
- **Minimal reproducer**: Create triplet with Ang1=45.00001deg, Ang2=45.00002deg. Verify take_next unchanged.
- **Search anchors**: 'fabs(Ang2 - Ang1) > Precision::Angular()', 'significance threshold'

##### `ShapeFix_Wireframe.MergeSmallEdges.limit_angle_check_both`
- **Line**: ShapeFix_Wireframe.cxx:949  **Axis**: `tolerance`
- **Brief**: When both pairs share faces, reject merge if both angles exceed the limit angle.
- **Falsifiable claim**: Without angle-limit enforcement, sharp corners would be collapsed, destroying feature boundaries. To test: set aLimitAngle=60deg; verify triplet with Ang1=70, Ang2=80 is skipped.
- **Minimal reproducer**: Create MergeSmallEdges with aLimitAngle=60deg. Triplet with Ang1=70, Ang2=80. Verify index++ (skip).
- **Search anchors**: 'aModLimitAngle && std::min(Ang1, Ang2) > aLimitAngle', 'angle limit enforcement'

##### `ShapeFix_Wireframe.MergeSmallEdges.single_pair_valid`
- **Line**: ShapeFix_Wireframe.cxx:951-963  **Axis**: `kernel-pair`
- **Brief**: Handle cases where only one edge pair (1,2 or 2,3) shares faces.
- **Falsifiable claim**: Without single-pair logic, asymmetric triplets would either fail to merge (wrong condition) or choose the wrong side. To test: create triplet where only (edge1, edge2) share faces; verify that pair is merged.
- **Minimal reproducer**: Create triplet: edge1 and edge2 on FACE F1, edge3 on FACE F2. Verify merge proceeds with edge1+edge2.
- **Search anchors**: 'same_set1 && !same_set2', '!same_set1 && same_set2', 'single pair fallback'

##### `ShapeFix_Wireframe.MergeSmallEdges.limit_angle_single_pair`
- **Line**: ShapeFix_Wireframe.cxx:953, 959  **Axis**: `tolerance`
- **Brief**: For single-pair valid triplets, check angle limit for that pair only.
- **Falsifiable claim**: Without pair-specific angle limit check, a triplet with one angle >limit would still be merged, violating the angle constraint. To test: set limit=60; Ang1=70 (limit exceeded), Ang2=40; verify skip.
- **Minimal reproducer**: aLimitAngle=60. Triplet: only pair1 valid, Ang1=70. Verify isLimAngle=true and merge skipped.
- **Search anchors**: 'Ang1 > aLimitAngle', 'Ang2 > aLimitAngle', 'single pair angle check'

##### `ShapeFix_Wireframe.MergeSmallEdges.same_set_final_gate`
- **Line**: ShapeFix_Wireframe.cxx:964  **Axis**: `api-contract`
- **Brief**: Merge only if a valid face-sharing pair exists AND angle is within limit.
- **Falsifiable claim**: Without this gate, unvalidated triplets (no common faces) or angle-violating pairs would proceed to join, corrupting topology. To test: verify merge is blocked when same_set=false.
- **Minimal reproducer**: Create triplet with disjoint face sets. Verify same_set=false and merge is skipped (index++).
- **Search anchors**: 'if (same_set && !isLimAngle)', 'final gate', 'merge authorization'

##### `ShapeFix_Wireframe.MergeSmallEdges.adjacency_check_other_faces`
- **Line**: ShapeFix_Wireframe.cxx:969-999  **Axis**: `kernel-pair`
- **Brief**: For shared edge pairs, verify edges are geometrically adjacent in all incident faces (not just current).
- **Falsifiable claim**: Without this cross-face validation, merging non-adjacent edges would create topological gaps in shared faces. To test: create shell where edge1-edge2 are adjacent in one face but not another; verify merge is blocked.
- **Minimal reproducer**: Create SHELL with 2 FACEs sharing edge2. In F1: [E1, E2, E3] (adjacent). In F2: [E2, X, Y] (not adjacent). Verify isNeedJoin=false and merge skipped.
- **Search anchors**: 'isNeedJoin', 'adjacency check', 'other faces', 'second face validation'

##### `ShapeFix_Wireframe.MergeSmallEdges.join_operation_call`
- **Line**: ShapeFix_Wireframe.cxx:1011  **Axis**: `kernel-pair`
- **Brief**: Call JoinEdges to merge two edges into one; returns which original edge to keep.
- **Falsifiable claim**: Without JoinEdges, no actual edge fusion would occur and geometry would remain invalid. To test: verify edge3 (result) has combined geometry of edge1 and edge2.
- **Minimal reproducer**: Create two edges with combined length L. Call JoinEdges(). Verify result edge has length ~L.
- **Search anchors**: 'ReplaceFirst = JoinEdges()', 'edge fusion', 'external call'

##### `ShapeFix_Wireframe.MergeSmallEdges.join_failure_handling`
- **Line**: ShapeFix_Wireframe.cxx:1017-1021  **Axis**: `api-contract`
- **Brief**: If JoinEdges returns null, mark failure and skip this triplet.
- **Falsifiable claim**: Without failure handling, null result would cause segfault in subsequent geometry access. To test: force JoinEdges to fail; verify null check prevents crash.
- **Minimal reproducer**: Create edges with incompatible geometry (e.g., disjoint). Verify edge3.IsNull() and FAIL1 status is set.
- **Search anchors**: 'edge3.IsNull()', 'join failure', 'FAIL1 status'

##### `ShapeFix_Wireframe.MergeSmallEdges.vertex_record_first`
- **Line**: ShapeFix_Wireframe.cxx:1025-1031  **Axis**: `healer-state`
- **Brief**: Record merged edge's first endpoint vertex for later context replacement.
- **Falsifiable claim**: Without vertex recording, endpoint replacements would be lost, causing parametric discontinuities. To test: verify recorded vertices match merged edge endpoints.
- **Minimal reproducer**: Merge edges E1, E2 into E3. Verify oldV1 (E3 first endpoint) is recorded in theNewVertices.
- **Search anchors**: 'SAE.FirstVertex(edge3)', 'theNewVertices.Bind()', 'oldV1'

##### `ShapeFix_Wireframe.MergeSmallEdges.vertex_record_last`
- **Line**: ShapeFix_Wireframe.cxx:1032-1040  **Axis**: `healer-state`
- **Brief**: Record merged edge's second endpoint if distinct from first.
- **Falsifiable claim**: Without distinct-vertex check, a degenerate (point) edge would cause duplicate vertex entries. To test: verify second vertex is only recorded if oldV1.IsSame(oldV2) = false.
- **Minimal reproducer**: Merge normal edge (distinct endpoints). Verify both vertices recorded. Merge degenerate edge (same endpoint twice). Verify only one entry.
- **Search anchors**: 'oldV1.IsSame(oldV2)', 'second vertex recording', 'distinct check'

##### `ShapeFix_Wireframe.MergeSmallEdges.internal_external_vertex_transfer` **[low-confidence]**
- **Line**: ShapeFix_Wireframe.cxx:1043-1070  **Axis**: `conformance-probe`
- **Brief**: Transfer INTERNAL/EXTERNAL (non-manifold) vertices from merged edges to result.
- **Falsifiable claim**: Without NM vertex transfer, parametric markers would be lost, causing invalid mesh or attribute associations. To test: create edge with internal vertex; verify it is added to result edge.
- **Minimal reproducer**: Create EDGE with INTERNAL vertex attached. Merge this edge. Verify INTERNAL vertex is copied to result.
- **Search anchors**: 'TopAbs_INTERNAL', 'TopAbs_EXTERNAL', 'ShapeAnalysis_TransferParametersProj::CopyNMVertex()'

##### `ShapeFix_Wireframe.MergeSmallEdges.context_edge_replacement`
- **Line**: ShapeFix_Wireframe.cxx:1077-1088  **Axis**: `healer-state`
- **Brief**: Record edge merges in context: replace one original edge with result, remove the other.
- **Falsifiable claim**: Without context registration, subsequent shape rebuilds would not see the merged geometry. To test: verify Context()->Apply() returns shape with merged edges.
- **Minimal reproducer**: Merge E1, E2 into E3. Verify Context()->Apply(shape) contains E3, not E1 or E2.
- **Search anchors**: 'Context()->Replace()', 'Context()->Remove()', 'merge registration'

##### `ShapeFix_Wireframe.MergeSmallEdges.result_edge_small_check`
- **Line**: ShapeFix_Wireframe.cxx:1072-1098  **Axis**: `input-shape`
- **Brief**: Check if merged edge is itself small; if so, add to small-edges set for re-processing.
- **Falsifiable claim**: Without re-checking, a merged edge that is still small would exit the method unprocessed, leaving small edges in the final shape. To test: merge two edges each 0.4*tol; result might be 0.8*tol but still small.
- **Minimal reproducer**: Create triplet where merged edge length < tolerance. Call MergeSmallEdges. Verify result edge is in theSmallEdges for next pass.
- **Search anchors**: 'CheckSmall()', 'newsmall', 'DONE1 status'

##### `ShapeFix_Wireframe.MergeSmallEdges.merged_edge_position_update`
- **Line**: ShapeFix_Wireframe.cxx:1089-1098  **Axis**: `healer-state`
- **Brief**: Update wire data to place merged edge at correct position (prev or next).
- **Falsifiable claim**: Without position update, merged edge would be left at wrong index, corrupting wire traversal order. To test: verify merged edge is at prev or next index after Set().
- **Minimal reproducer**: Merge at index=2. Verify SFW->WireData()->Set(edge3, prev or next) places result correctly.
- **Search anchors**: 'SFW->WireData()->Set(edge3, prev/next)', 'position update', 'WireData().Remove(index)'

##### `ShapeFix_Wireframe.MergeSmallEdges.edge_face_map_update`
- **Line**: ShapeFix_Wireframe.cxx:1103-1105  **Axis**: `healer-state`
- **Brief**: Update edge-to-faces map: remove old edges, bind result edge to their shared faces.
- **Falsifiable claim**: Without map update, later processing would fail to find incident faces for the result edge. To test: verify theEdgeToFaces(edge3) equals theEdgeToFaces(edge2).
- **Minimal reproducer**: Merge E1, E2 into E3. Verify theEdgeToFaces.IsBound(E3) and extent matches edge2.
- **Search anchors**: 'theEdgeToFaces.UnBind()', 'theEdgeToFaces.Bind(edge3, theList)', 'map update'

##### `ShapeFix_Wireframe.MergeSmallEdges.face_with_small_update`
- **Line**: ShapeFix_Wireframe.cxx:1118-1148  **Axis**: `healer-state`
- **Brief**: Update theFaceWithSmall map: remove old edges, add result if small, clean empty faces.
- **Falsifiable claim**: Without map update, next iteration would process removed edges or miss the result. To test: verify theFaceWithSmall entries are consistent after merge.
- **Minimal reproducer**: Merge small edges. Verify theFaceWithSmall(face) no longer contains E1, E2; contains E3 if still small.
- **Search anchors**: 'theFaceWithSmall(curface)', 'theEdges.Remove()', 'theEdges.Append()', 'UnBind(curface)'

##### `ShapeFix_Wireframe.MergeSmallEdges.drop_mode_entry`
- **Line**: ShapeFix_Wireframe.cxx:1152  **Axis**: `api-contract`
- **Brief**: Alternative path: if drop mode is enabled and merge preconditions fail, remove small edge instead.
- **Falsifiable claim**: Without drop mode, invalid triplets would cause merge failure and small edges would remain. With drop mode enabled, they are removed (at cost of losing material). To test: set myModeDrop=true; verify small edges are removed instead of merged.
- **Minimal reproducer**: Create invalid triplet (disjoint faces). Set MergeSmallEdges(drop_mode=true). Verify small edge is removed.
- **Search anchors**: 'aModeDrop', 'drop mode', 'DONE3 status'

##### `ShapeFix_Wireframe.MergeSmallEdges.drop_mode_validity_check`
- **Line**: ShapeFix_Wireframe.cxx:1170  **Axis**: `api-contract`
- **Brief**: Before drop, verify remaining edges connect (no gap created).
- **Falsifiable claim**: Without connectivity check, drop mode could create disconnected wire segments. To test: verify CheckConnected() fails if edges don't connect after removal.
- **Minimal reproducer**: Create wire [E1, E_small, E2] where removal leaves gap. Verify CheckConnected() fails and drop is rejected.
- **Search anchors**: 'tempSaw.CheckConnected()', 'LastCheckStatus(ShapeExtend_FAIL)', 'connectivity validation'

##### `ShapeFix_Wireframe.MergeSmallEdges.drop_mode_fix_call`
- **Line**: ShapeFix_Wireframe.cxx:1186-1187  **Axis**: `kernel-pair`
- **Brief**: After removing small edge, call FixConnected and FixDegenerated on adjacent edges.
- **Falsifiable claim**: Without fixing adjacent edges, they might remain in invalid state (disconnected or degenerate). To test: verify edges adjacent to removed edge are checked for validity.
- **Minimal reproducer**: Remove small edge from wire. Verify FixConnected() and FixDegenerated() are called on neighbors.
- **Search anchors**: 'SFW->FixConnected()', 'SFW->FixDegenerated()', 'drop mode fixup'

##### `ShapeFix_Wireframe.MergeSmallEdges.drop_mode_map_updates`
- **Line**: ShapeFix_Wireframe.cxx:1198-1252  **Axis**: `healer-state`
- **Brief**: After drop-mode removal, update theEdgeToFaces and theFaceWithSmall for affected edges.
- **Falsifiable claim**: Without map updates, stale references to dropped edge would cause downstream errors. To test: verify maps are consistent after drop.
- **Minimal reproducer**: Drop small edge E_drop. Verify theEdgeToFaces no longer contains E_drop.
- **Search anchors**: 'theEdgeToFaces.UnBind/Bind', 'theFaceWithSmall update', 'drop map updates'

##### `ShapeFix_Wireframe.MergeSmallEdges.circle_protection`
- **Line**: ShapeFix_Wireframe.cxx:1263-1279  **Axis**: `input-shape`
- **Brief**: Detect circular edges (closed curves) and prevent removal.
- **Falsifiable claim**: Without circle detection, a full-circle edge (e.g., radius arc wrapping >180deg) would be treated as normal and removed, destroying the circle. To test: create circular edge; verify it is not removed.
- **Minimal reproducer**: Create EDGE that is a semicircle (180+ degrees). Attempt removal. Verify index++ skips it.
- **Search anchors**: 'p1.Distance(p3) > p1.Distance(p2)', 'circle protection', 'midpoint check'

##### `ShapeFix_Wireframe.MergeSmallEdges.self_loop_removal_next`
- **Line**: ShapeFix_Wireframe.cxx:1280-1299  **Axis**: `input-shape`
- **Brief**: Remove self-loop edge (same start/end vertex) when take_next=true and single incident face.
- **Falsifiable claim**: Without self-loop removal, degenerate loops (point-like edges) would remain, corrupting downstream algorithms. To test: create self-loop edge; verify it is removed.
- **Minimal reproducer**: Create EDGE with V1=V2 (self-loop). Attempt merge. Verify edge is removed.
- **Search anchors**: 'V1.IsSame(V2)', 'self-loop removal', 'DONE2 status'

##### `ShapeFix_Wireframe.MergeSmallEdges.self_loop_removal_prev`
- **Line**: ShapeFix_Wireframe.cxx:1300-1319  **Axis**: `input-shape`
- **Brief**: Remove self-loop edge when take_next=false and single incident face.
- **Falsifiable claim**: Without this variant, some self-loops (e.g., when Ang2<Ang1) would be missed. To test: create self-loop with different angle profile; verify removal.
- **Minimal reproducer**: Create triplet with self-loop on right side (take_next=false). Verify loop is removed.
- **Search anchors**: '!take_next && V1.IsSame(V2)', 'self-loop prev variant'

##### `ShapeFix_Wireframe.MergeSmallEdges.default_skip`
- **Line**: ShapeFix_Wireframe.cxx:1320-1324  **Axis**: `api-contract`
- **Brief**: For non-merge, non-drop, non-loop cases, skip to next triplet.
- **Falsifiable claim**: Without skip, infinite loop would occur. To test: verify index++ is called for unhandled cases.
- **Minimal reproducer**: Create triplet that fails all merge checks. Verify loop progresses (index++ is called).
- **Search anchors**: 'index++', 'default skip', 'fallthrough'

##### `ShapeFix_Wireframe.MergeSmallEdges.final_wire_fixup`
- **Line**: ShapeFix_Wireframe.cxx:1348-1350  **Axis**: `kernel-pair`
- **Brief**: After loop, call FixConnected on remaining wire and replace it in context.
- **Falsifiable claim**: Without final fixup, remaining edges might be disconnected or malformed. To test: verify FixConnected() is called on final wire.
- **Minimal reproducer**: Process wire with remaining edges. Verify FixConnected() is called and wire is registered in context.
- **Search anchors**: 'SFW->FixConnected()', 'Context()->Replace(aWire, SFW->Wire())', 'final fixup'

##### `ShapeFix_Wireframe.MergeSmallEdges.empty_face_removal`
- **Line**: ShapeFix_Wireframe.cxx:1355-1359  **Axis**: `api-contract`
- **Brief**: If a face becomes empty (no wires remain), remove it from the shape.
- **Falsifiable claim**: Without empty-face removal, hollow faces would remain in the shape, causing invalid topology. To test: create face where all edges are removed; verify face is removed.
- **Minimal reproducer**: Create FACE with only small edges. Remove all edges. Verify face is removed from result.
- **Search anchors**: '!aIter.More()', 'Context()->Remove(anewShape)', 'empty face removal'

##### `ShapeFix_Wireframe.MergeSmallEdges.loose_wires_processing`
- **Line**: ShapeFix_Wireframe.cxx:1366-1367  **Axis**: `input-shape`
- **Brief**: Process free wires not on any face (TopExp_Explorer with TopAbs_FACE as exclusion).
- **Falsifiable claim**: Without loose-wire handling, free wires would not be processed and remain malformed. To test: create free wire with small edges; verify they are processed.
- **Minimal reproducer**: Create COMPOUND with free WIRE (not on any FACE). Verify loop processes it.
- **Search anchors**: 'TopExp_Explorer(myShape, TopAbs_WIRE, TopAbs_FACE)', 'loose wires', 'enk block'

##### `ShapeFix_Wireframe.MergeSmallEdges.final_context_apply`
- **Line**: ShapeFix_Wireframe.cxx:1924-1926  **Axis**: `healer-state`
- **Brief**: Apply all accumulated context transformations to the input shape.
- **Falsifiable claim**: Without final context application, shape would not reflect any merges/removals. To test: verify result shape differs from input after successful merge.
- **Minimal reproducer**: Merge small edges. Verify Context()->Apply(myShape) contains merged geometry.
- **Search anchors**: 'Context()->Apply(shape)', 'final rebuild', 'myShape update'

##### `ShapeFix_Wireframe.MergeSmallEdges.same_parameter_fix`
- **Line**: ShapeFix_Wireframe.cxx:1928  **Axis**: `conformance-probe`
- **Brief**: Restore same-parameter flag on all edges (vertices match surface parameters).
- **Falsifiable claim**: Without same-parameter restoration, merged edges would have inconsistent surface parametrization, causing downstream mesh/analysis errors. To test: verify SameParameter() is called.
- **Minimal reproducer**: Merge edges on surface. Verify ShapeFix::SameParameter() is called to restore consistency.
- **Search anchors**: 'ShapeFix::SameParameter(myShape, false)', 'parametric consistency'

##### `ShapeFix_Wireframe.MergeSmallEdges.return_status`
- **Line**: ShapeFix_Wireframe.cxx:1930  **Axis**: `api-contract`
- **Brief**: Return true if any merge/drop operation succeeded (ShapeExtend_DONE bit set).
- **Falsifiable claim**: Without status return, caller cannot determine if any healing was performed. To test: verify return value reflects actual modifications.
- **Minimal reproducer**: Call MergeSmallEdges with no small edges. Verify return false. With small edges merged, verify return true.
- **Search anchors**: 'StatusSmallEdges(ShapeExtend_DONE)', 'return bool', 'status reporting'


### ShapeUpgrade_ClosedFaceDivide_SplitSurface

#### `ShapeUpgrade_ClosedFaceDivide_SplitSurface`
 (20 branches; source: `v3-deep-ShapeUpgrade_ClosedFaceDivide_SplitSurface.json`)

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.null-splitter`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:65-68  **Axis**: `healer-state`
- **Brief**: SplitSurface tool acquisition fails, blocking all seam-handling logic.
- **Falsifiable claim**: Without this branch guard, null-pointer dereference would occur on SplitSurf->Init() at line 250. To test: Trigger context where GetSplitSurfaceTool() returns null handle.
- **Minimal reproducer**: Create closed face; invoke ShapeUpgrade_ClosedFaceDivide.Perform() with mocked GetSplitSurfaceTool() returning null. Without guard: segfault at line 250. With guard: returns false gracefully.
- **Search anchors**: 'SplitSurf.IsNull()', 'GetSplitSurfaceTool', 'null handle guard'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.face-shape-type`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:70-74  **Axis**: `api-contract`
- **Brief**: Non-face shape type in myResult triggers early exit with FAIL3 status.
- **Falsifiable claim**: Without this validation, TopAbs_FACE type assumption would be violated at TopoDS::Face() cast. To test: Pass edge or wire as myResult; should set FAIL3 status and return false.
- **Minimal reproducer**: Set myResult to an edge instead of face via context manipulation. Invoke SplitSurface(). Without guard: undefined behavior at cast. With guard: FAIL3 status set, false returned.
- **Search anchors**: 'myResult.ShapeType() != TopAbs_FACE', 'ShapeExtend_FAIL3', 'type enforcement'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.infinite-bounds`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:77-84  **Axis**: `tolerance`
- **Brief**: Infinite UV bounds (e.g., from unbounded surfaces) prevent safe parametric splitting.
- **Falsifiable claim**: Without bounds check, step calculation at lines 160, 170, 202, 229 divides by infinite range yielding NaN. To test: Load face with infinite U or V bounds (e.g., half-plane), invoke SplitSurface().
- **Minimal reproducer**: Construct face from HalfPlane (infinite in one direction). ShapeAnalysis::GetFaceUVBounds() returns inf. Without check: NaN splits propagate to step calc. With check: returns false immediately.
- **Search anchors**: 'IsInfinite(Uf)', 'IsInfinite(Ul)', 'unbounded surface', 'infinite bounds'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.seam-wire-iteration`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:94-99  **Axis**: `api-contract`
- **Brief**: Non-wire shape children are skipped; only wires checked for seams.
- **Falsifiable claim**: Without ShapeType check, calling ShapeExtend_WireData on non-wire (shell, edge) would cause API contract violation. To test: Add non-wire to face's child iterator; seams would be missed or crash.
- **Minimal reproducer**: Construct face with malformed topology (child that is neither wire nor void). Iterate face children. Without type filter: API error from ShapeExtend_WireData constructor. With filter: gracefully skips.
- **Search anchors**: 'iter.Value().ShapeType() != TopAbs_WIRE', 'continue skip', 'wire-only processing'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.seam-detection`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:104-106  **Axis**: `input-shape`
- **Brief**: Seam edges detected and marked for splitting; first seam found sets doSplit=true.
- **Falsifiable claim**: Without seam detection, cylindrical/toroidal periodic surfaces would not be split. To test: Cylinder with seam edge; without logic, seam remains unsplit causing invalid topology.
- **Minimal reproducer**: Construct cylinder (radius 5, height 10, placed at origin). Seam edge at u=0. Without logic: face retains seam. With logic: face split into two half-cylinders.
- **Search anchors**: 'sewd->IsSeam(i)', 'doSplit = true', 'periodic seam'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.pcurve-extraction-first`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:111-114  **Axis**: `encoding`
- **Brief**: First edge parametric curve extraction fails, skipping to next edge.
- **Falsifiable claim**: Without continue, degenerate curves or non-existing pcurves would cause invalid splits. To test: Add seam edge without proper pcurve definition.
- **Minimal reproducer**: Topologically mark edge as seam but omit pcurve definition in face's BRep. sae.PCurve() returns false. Without skip: c1 is null/invalid, causing NullPointerException at FillBndBox. With skip: gracefully continues to next seam.
- **Search anchors**: 'sae.PCurve(edge, face, c1', 'if (!sae.PCurve...continue', 'missing pcurve'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.reversed-edge-pcurve`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:116-120  **Axis**: `encoding`
- **Brief**: Reversed edge pcurve must differ from forward pcurve; if identical, skip seam.
- **Falsifiable claim**: Without distinct forward/reversed pcurves, split-point calculation would be meaningless. To test: Malformed seam where both orientations share identical curve.
- **Minimal reproducer**: Torus: seam edge at u=0. Both forward and reversed orientations must map to different parametric positions (one at 0, one at 2π). If BRep incorrectly stores same curve for both: without check, xf==xl and yf==yl, step=0, no split generated.
- **Search anchors**: 'edge.Reversed()', 'sae.PCurve(TopoDS::Edge(tmpE)', 'if (c2 == c1) continue'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.seam-bounding-box-gap`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:126-154  **Axis**: `conformance-probe`
- **Brief**: Bounding box gap between seam and reversed-seam pcurves determines split axis and location.
- **Falsifiable claim**: Without gap detection, split would be placed at boundary instead of mid-gap, preserving periodicity. To test: Cylinder u=[0,2π]; seam pcurves at u≈0 and u≈2π, gap≈2π.
- **Minimal reproducer**: Sphere (radius 5) with seam at v=0 and v=π. FillBndBox(c1) spans v∈[0,π-ε], FillBndBox(c2) spans v∈[π+ε,π]. Gap dV≈2ε. Split at v=π eliminates seam discontinuity. Without gap logic: split placed at boundary, preserving artifact.
- **Search anchors**: 'FillBndBox', 'x1min,x1max,x2min,x2max', 'xf,xl,yf,yl gap detection'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.u-split-dominance`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:156-177  **Axis**: `healer-state`
- **Brief**: Larger gap (dU vs dV) selects U-splitting; smaller gap selects V-splitting.
- **Falsifiable claim**: Without axis selection, arbitrary choice could split along wrong parametric direction, degrading mesh quality or preserving seam. To test: Seam with dU>>dV; should split U.
- **Minimal reproducer**: Ellipsoid (a=10, b=5, c=3) with seam at u=0. Gap dU=10π>>dV≈1. Without logic: split V (wrong), seam remains at u=0. With logic: split U at u=5π, seam removed.
- **Search anchors**: 'dU = xl - xf', 'dV = yl - yf', 'if (dU > dV)', 'isUSplit'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.split-value-generation`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:160-177  **Axis**: `healer-state`
- **Brief**: Split values generated at uniform intervals myNbSplit+1 times within detected gap.
- **Falsifiable claim**: Without interval generation, split would be at gap boundary (preserving seam). To test: myNbSplit=1, dU=10, xf=0, xl=10; should generate [5].
- **Minimal reproducer**: Cylinder with seam at u=0, parametric bounds [0,2π]. After FillBndBox: xf≈0, xl≈2π, dU≈2π. myNbSplit=1: step=2π/2=π, val=π. Split appends [π]. Without generation: split=[]. Surface not split, seam persists.
- **Search anchors**: 'step = dU / (myNbSplit + 1)', 'val = xf + step', 'for (int j = 1; j <= myNbSplit', 'split->Append(val)'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.geometric-uclosed-detection`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:185-215  **Axis**: `input-shape`
- **Brief**: For surfaces with no explicit seam edges, geometric U-closure is checked; thin faces are split if closure is marginal.
- **Falsifiable claim**: Without geometric check, implicitly-closed surfaces (e.g., torus without explicit seam markup) would not be split. To test: Torus where BRep omits seam edge; surface is geometrically closed.
- **Minimal reproducer**: Torus (major=10, minor=2) where seam edge is missing from wire. sas->IsUClosed() returns true. GAS.UResolution() is ~10^-6. (U2-U1)-(Ul-Uf)=10^-7 < toler. Create half-torus via RectangularTrimmedSurface, test if half-closed. If not half-closed: split generated. Without logic: face remains with hidden seam.
- **Search anchors**: 'sas->IsUClosed(Precision())', '(U2 - U1) - (Ul - Uf) < toler', 'geometric closure'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.thin-uclosed-face`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:194-214  **Axis**: `tolerance`
- **Brief**: Thin U-closed faces (full surface bounds near trim bounds) are split at mid-parameter.
- **Falsifiable claim**: Without thin-face logic, marginally-closed surfaces would create degenerate mesh. To test: Face trimmed to [0, 2π-1e-7] of full [0, 2π] cylinder.
- **Minimal reproducer**: Cylinder: full bounds [0, 2π], trim bounds [0, 2π-1e-8]. Difference <tolerance. Create RTS from [0, π]. IsUClosed() test on RTS returns false. Without logic: face kept at edge of period, mesh degenerates. With logic: split at π, creates two clean sub-faces.
- **Search anchors**: 'GAS.UResolution(Precision())', 'Geom_RectangularTrimmedSurface', 'thin face'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.geometric-vclosed-detection`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:216-242  **Axis**: `input-shape`
- **Brief**: For surfaces with no U-split, geometric V-closure is checked as fallback.
- **Falsifiable claim**: Without V-closure fallback, cylindrical surfaces closed in V only (no U seam) would not be split. To test: Surface closed in V, open in U.
- **Minimal reproducer**: Cone (apex + circular base) where V is geometrically closed at apex. No U seam. vclosed=true, doSplit=false. RTS from [Vmin, (Vmin+Vmax)/2]. If half-RTS is not V-closed: split generated at Vmin+(Vl-Vf)/2. Without fallback: cone not split, apex remains problematic.
- **Search anchors**: 'sas->IsVClosed(Precision())', 'vclosed && !doSplit', 'V fallback'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.thin-vclosed-face`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:221-241  **Axis**: `tolerance`
- **Brief**: Thin V-closed faces are split at mid-V after U-closure check fails.
- **Falsifiable claim**: Without thin V-split, cone with nearly-full V coverage would degenerate. To test: Cone bounds V=[0, π-1e-8] of full [0, π].
- **Minimal reproducer**: Cone: full V=[0, π], trim [0, π-1e-9]. (V2-V1)-(Vl-Vf)<toler. Create RTS(V1, (V1+V2)/2). IsVClosed() on half is false. Without logic: kept at boundary. With logic: split at Vf+ε, creates two clean cones.
- **Search anchors**: 'GAS.VResolution(Precision())', 'Geom_RectangularTrimmedSurface false', 'thin V-split'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.no-split-fallback`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:245-248  **Axis**: `api-contract`
- **Brief**: If no seams and surface not geometrically closed, return false without splitting.
- **Falsifiable claim**: Without this check, SplitSurf->Init() would be called with empty split sequence, creating invalid grid. To test: Open surface (non-periodic, non-closed).
- **Minimal reproducer**: Load non-closed surface (e.g., spherical cap, 90°, u=[0,π/2], v=[0,π]). No seams. uclosed=false, vclosed=false. doSplit remains false. Without fallback: SplitSurf->SetUSplitValues(empty) then Perform(), creating degenerate grid. With check: returns false.
- **Search anchors**: 'if (!doSplit) return false', 'early exit', 'no split needed'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.splitter-initialization`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:250-258  **Axis**: `healer-state`
- **Brief**: Split surface tool initialized with bounds and split values; axis selected via isUSplit.
- **Falsifiable claim**: Without proper initialization, Perform() would operate on wrong bounds or axis. To test: Pass inverted Uf>Ul or empty split sequence.
- **Minimal reproducer**: Cylinder [0,2π]×[0,10]. Seam detected, split=[π] generated, isUSplit=true. Init(surf, 0, 2π, 0, 10); SetUSplitValues([π]). Perform splits U at π. Without init: Perform() uses default bounds, misses split.
- **Search anchors**: 'SplitSurf->Init(surf, Uf, Ul, Vf, Vl)', 'SetUSplitValues', 'SetVSplitValues'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.perform-status-check`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:260-264  **Axis**: `healer-state`
- **Brief**: Perform() execution status checked; DONE flag required for valid grid.
- **Falsifiable claim**: Without status check, invalid grid would propagate to CompShell, causing topology errors. To test: Malformed split sequence causing Perform() to fail.
- **Minimal reproducer**: Cylinder. Split=[π, 1e20] (second value far outside bounds [0,2π]). Perform() fails, DONE not set. Without check: Grid used anyway, CompShell fails silently. With check: early return false.
- **Search anchors**: 'SplitSurf->Perform(mySegmentMode)', 'Status(ShapeExtend_DONE)', 'status validation'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.composite-shell-build`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:265-275  **Axis**: `kernel-pair`
- **Brief**: Composite grid converted to shell; FAIL status set if composition fails.
- **Falsifiable claim**: Without composition, split surface grid remains as abstract grid, not valid topology. To test: Grid with boundary misalignment.
- **Minimal reproducer**: After Perform(), grid is abstract 2D array of surfaces. CompShell.Init(Grid, L, face, Precision()) converts to valid topological shell. Without CompShell: grid not usable. With CompShell: produces Face or Shell with valid edges/wires.
- **Search anchors**: 'ShapeFix_ComposeShell CompShell', 'CompShell.Init(Grid, L, face', 'Status(ShapeExtend_FAIL)'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.recursive-split`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:279-289  **Axis**: `kernel-pair`
- **Brief**: Each resulting face from composite shell is recursively split if it has its own seams.
- **Falsifiable claim**: Without recursion, nested seams in split faces would not be handled. To test: Toroidal surface requiring multiple splits across periodic directions.
- **Minimal reproducer**: Torus: both U and V closed. First SplitSurface() splits U at u=π, creating two sub-faces. Each sub-face may inherit V-closure. Recursive SplitSurface() call on sub-face detects V-closure, splits V. Without recursion: V-seams persist in sub-faces.
- **Search anchors**: 'for (TopExp_Explorer exp(res, TopAbs_FACE)', 'if (SplitSurface())', 'Context()->Replace(f, myResult)', 'recursive call'

##### `ShapeUpgrade_ClosedFaceDivide.SplitSurface.context-apply-final`
- **Line**: ShapeUpgrade_ClosedFaceDivide.cxx:290-291  **Axis**: `kernel-pair`
- **Brief**: Final result applied through context; recursively-modified faces reflected in output.
- **Falsifiable claim**: Without Context()->Apply(), recursive replacements would be lost. To test: Recursive split followed by context read-back.
- **Minimal reproducer**: After recursive SplitSurface() loop, myResult points to last sub-face. Context()->Replace() records all replacements. myResult = Context()->Apply(res) merges all replacements into final shell. Without Apply: only last sub-face returned.
- **Search anchors**: 'Context()->Apply(res)', 'final result', 'context propagation'


### ShapeUpgrade_ConvertCurve2dToBezier

#### `ShapeUpgrade_ConvertCurve2dToBezier.Compute`
 (10 branches; 4 low-confidence; source: `v3-deep-ShapeUpgrade_ConvertCurve2dToBezier_Compute.json`)

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.BSpline_or_Bezier_line_approximation_deviation_threshold`
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:60-82  **Axis**: `kernel-pair`
- **Brief**: First condition checks if BSpline/Bezier approximates a line within deviation threshold, but the tmpF/tmpL output parameters are not used when mySplitValues differs from First/Last.
- **Falsifiable claim**: Without this branch, a nearly-linear BSpline would be converted to the full curve instead of a simplified 2-point Bezier. To test: feed a 3-knot BSpline that is geometrically linear within 1e-7; expected outcome is a line Bezier using tmpF/tmpL bounds; actual outcome without this branch is full curve retained.
- **Minimal reproducer**: Construct BSpline2d with 3 control points collinear within PConfusion(). Set mySplitValues=[0.3, 0.7]. Call Compute(). If branch present: 2-point Bezier appended with mySplitParams=[0.3,0.7]. If missing: either full BSpline or empty segments.
- **Search anchors**: 'ConvertToLine2d', 'aDeviation', 'Precision::Approximation()', 'tmpF', 'tmpL'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.trimmed_curve_recursion_mySplitValues_coupling`
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:84-103  **Axis**: `healer-state`
- **Brief**: Trimmed curve handling recursively invokes Compute() on basis curve, then unconditionally replaces mySplitValues by copying converter results, risking silent loss of original split boundaries if basis curve spans exceed trimmed domain.
- **Falsifiable claim**: Without proper coupling between caller's mySplitValues and recursive converter's result, a periodic seam trimmed to [0.1, 0.9] on [0, 2π) basis could lose the distinction between caller's boundaries and recursive split points. To test: feed TrimmedCurve(PeriodicBSpline, 0.5*π, 1.5*π) with mySplitValues containing intermediate knots; observe whether result respects original split or uses recursive split.
- **Minimal reproducer**: Construct TrimmedCurve from periodic B-spline (period 2π) trimmed to [π/2, 3π/2]. Set mySplitValues=[π/2, π, 3π/2] (3 elements = 2 segments). Call Compute(). Expected: mySegments has 2 curves, mySplitParams bounded by π/2, 3π/2, respecting original intervals. Without fix: mySplitValues replaced by recursive values, original segment count lost.
- **Search anchors**: 'mySplitValues->ChangeSequence()', 'converter.Compute()', 'BasisCurve()', 'Geom2d_TrimmedCurve'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.bezier_segment_precision_boundary_off_by_one` **[low-confidence]**
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:104-120  **Axis**: `tolerance`
- **Brief**: Bezier curve case uses numeric comparison (First < precision && Last > 1 - precision) to determine if curve spans full domain [0,1], but periodic surfaces seams may have First=0, Last=2π, causing false negatives.
- **Falsifiable claim**: Without checking the actual curve domain bounds, a Bezier spanning [0, 2π) on a periodic surface seam would bypass Segment() call and reuse entire curve instead of trimming. To test: create Bezier on periodic seam with mySplitValues=[0, 2π]; if logic treats [0, 2π] as 'full', it skips Segment(); a subsequent edge using [π, 2π] would receive wrong parameterization.
- **Minimal reproducer**: Construct Bezier2d with natural domain [0,1], but use it on periodic seam via mySplitValues=[0, 2π] (manually scaled). Call Compute(). Expected: Segment() invoked, curve trimmed. Without: condition 'Last > 1-precision' fails for Last=2π, Segment() skipped, wrong Bezier appended.
- **Search anchors**: 'First < precision', 'Last > 1 - precision', 'Segment()', 'bezier->Copy()'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.line_makebezier2d_endpoint_sampling` **[low-confidence]**
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:122-131  **Axis**: `kernel-pair`
- **Brief**: MakeBezier2d() helper creates 2-point Bezier from curve endpoints, discarding curvature; lines are safe, but polymorphic curve types passed here may have non-linear behavior between endpoints.
- **Falsifiable claim**: Without validating that the converted curve is actually linear, a conic arc (ellipse, hyperbola) approximated as line via ConvertToLine2d could produce a degenerate or topologically wrong 2-point Bezier. To test: feed circular arc with aDeviation=0 (spurious approx); MakeBezier2d(arc, 0, π/2) produces straight line instead of arc.
- **Minimal reproducer**: Construct Geom2d_Circle, call ConvertToLine2d with high tolerance allowing circular arc to pass deviation check. MakeBezier2d(circle, 0, π/2) creates line from (r,0) to (0,r) instead of arc. Validate by evaluating Bezier at π/4: should be (r/√2, r/√2), but gets (r/2, r/2).
- **Search anchors**: 'MakeBezier2d', 'poles(1)', 'poles(2)', 'Geom2d_BezierCurve(poles)'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.conic_approximation_shift_accumulation`
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:145-163  **Axis**: `healer-state`
- **Brief**: Conic curves are approximated to BSpline, introducing a parametric Shift = First - aBSpline2d->FirstParameter(). This shift is applied to knot values but may accumulate incorrectly across recursive TrimmedCurve chains.
- **Falsifiable claim**: Without proper shift tracking through nested conversions, a TrimmedConic at [0.2, 0.8] converted to BSpline with FirstParameter()=0.15 would compute Shift=0.05, which is later added to knot positions; if a parent TrimmedCurve layer exists, shifts compound and mySplitParams become disconnected from mySplitValues domain.
- **Minimal reproducer**: Construct TrimmedCurve(Geom2d_Ellipse, 0.2, 0.8), where ellipse maps [0, 2π) to ellipse domain. After approx to BSpline with FirstParameter()=0.15, Shift=0.05. Then apply another trim layer. Call Compute(). Check mySplitParams: should relate to [0.2, 0.8]; with accumulation bug, values drift toward ellipse native domain.
- **Search anchors**: 'Shift = First - aBSpline2d->FirstParameter()', 'knots(j + 1) + Shift', 'newLast = nextKnot + Shift'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.knot_interval_precision_guard_missed_split`
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:196-210  **Axis**: `tolerance`
- **Brief**: Interval check 'nextKnot - mySplitParams->Value(...) > precision' may skip knot insertion if delta equals precision, causing missed splits on boundaries of segments with tight tolerance bands.
- **Falsifiable claim**: Without strict > comparison, a knot distance exactly equal to PConfusion() (1e-7) would be discarded, merging two segments. For periodic seams where knots cluster at seam (e.g., u=0, u=2π), this causes topology loss. To test: insert knots at spacing = PConfusion(); observe segment count.
- **Minimal reproducer**: BSpline2d with knots [0, eps, 2*eps, ...] where eps=Precision::PConfusion()~1e-7. Call Compute(). Expected: each eps-separated knot creates segment. Without >: knots skipped, fewer segments than knots.
- **Search anchors**: 'nextKnot - mySplitParams->Value', '> precision', 'NbArcs'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.bezier_arc_line_check_parameter_scope_mismatch`
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:211-227  **Axis**: `kernel-pair`
- **Brief**: Bezier arc line-detection test uses aCrv2d (the arc from BSpline) but subsequent MakeBezier2d() call uses aBSpline2d (parent) with newFirst/newLast bounds, creating scope mismatch where evaluated points come from different curves.
- **Falsifiable claim**: Without using consistent curve reference, line approximation test operates on arc but created Bezier samples parent BSpline, producing geometrically invalid curves. To test: feed BSpline with one Bezier arc forming local circle; line approx passes for arc, but MakeBezier2d(aBSpline2d, ...) creates line between parent curve points, not arc points.
- **Minimal reproducer**: B-spline with circular arc piece (Bezier knot span). Arc approximates to line (e.g., small angle). ConvertToLine2d(aCrv2d, newFirst, newLast) returns valid line. But MakeBezier2d(aBSpline2d, newFirst, newLast) samples aBSpline2d at same bounds, which may not be collinear if aBSpline2d has different shape. Result: Bezier represents parent, not arc.
- **Search anchors**: 'aCrv2d = tool.Arc(j)', 'MakeBezier2d(aBSpline2d, newFirst, newLast)', 'ConvertToLine2d(aCrv2d, ...)'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.split_values_insertion_index_off_by_one`
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:234-250  **Axis**: `healer-state`
- **Brief**: Loop inserting knots into mySplitValues iterates j++ inside insertion loop, but incremented j is then used as loop bound, causing skipped or duplicated insertions when knot count exceeds pre-insertion expectation.
- **Falsifiable claim**: Without careful index management, inserting knots into mySplitValues during iteration causes subsequent j references to miss or duplicate inserted values. To test: mySplitValues with 2 elements, 10 knots to insert; loop should insert all, but with j++ inside, some knots skipped or list corrupted.
- **Minimal reproducer**: mySplitValues=[0, 1] (2 elements, 1 segment). Knot array with 10 internal knots. Loop at line 236-248: j=2 initially. For each j, insert multiple knots before incrementing j. Expected: 11 split values (1+10). With bug: fewer values, gaps in knot coverage, segments missing.
- **Search anchors**: 'for (j = 2; j <= mySplitValues->Length(); j++)', 'mySplitValues->InsertBefore(j++, valknot)', 'First = Last'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.conic_bspline_conversion_fallback_no_error_handling` **[low-confidence]**
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:168-183  **Axis**: `kernel-pair`
- **Brief**: Conic-to-BSpline conversion via approx.Curve() or fallback CurveToBSplineCurve() succeeds silently even if approximation quality is poor, and no validation checks the resulting BSpline's fidelity before proceeding.
- **Falsifiable claim**: Without validating BSpline approximation error, a parabolic conic with high-degree approximation could produce a numerically unstable or ill-conditioned spline. To test: feed parabola with extreme parameters; resulting BSpline should be validated for condition number or re-approximated if error threshold exceeded.
- **Minimal reproducer**: Construct Geom2d_Parabola with parameter range [0, 1e6]. Call Compute(). ApproxCurve with 100 degree, 6 max segments may produce BSpline with very large/small control point magnitudes. Validate: check max pole coordinate magnitude; if > 1e8, approximation quality degraded.
- **Search anchors**: 'Geom2d_Conic', 'Geom2dConvert_ApproxCurve', 'HasResult()', 'CurveToBSplineCurve'

##### `ShapeUpgrade_ConvertCurve2dToBezier.Compute.parameter_clamping_doesnt_update_split_params` **[low-confidence]**
- **Line**: ShapeUpgrade_ConvertCurve2dToBezier.cxx:176-191  **Axis**: `healer-state`
- **Brief**: When First/Last are clamped to BSpline bounds due to domain mismatch, mySplitValues is updated but mySplitParams remains uninitialized (only appended to later), creating potential inconsistency in parametric alignment.
- **Falsifiable claim**: Without synchronizing mySplitParams with clamped First/Last, subsequent code appending to mySplitParams may use wrong base values, causing misalignment with segments. To test: edge with mySplitValues=[−0.1, 1.1] on BSpline [0,1]; after clamping mySplitValues=[0,1], mySplitParams starts at 0 but First cached value may cause offset.
- **Minimal reproducer**: BSpline with domain [0, 1]. Set mySplitValues=[-0.1, 1.1]. Call Compute(). Clamping updates mySplitValues to [0, 1], but mySplitParams->Append(First) at line 216 uses already-clamped First=0. Check: mySplitParams should be [0, ...], and it is, but intermediate state is fragile if exception occurs between clamping and append.
- **Search anchors**: 'First < bf', 'Last > bl', 'mySplitValues->SetValue', 'mySplitParams->Append(First + Shift)'


### ShapeUpgrade_UnifySameDomain

#### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces`
 (75 branches; 2 low-confidence; source: `v3-deep-ShapeUpgrade_UnifySameDomain_IntUnifyFaces.json`)

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.processed_face_skip`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3207  **Axis**: `healer-state`
- **Brief**: Skip already-processed faces to avoid duplicate unification attempts.
- **Falsifiable claim**: Without this branch, the kernel would process same face twice in one IntUnifyFaces call, leading to incorrect results or assertions. To test: call IntUnifyFaces on shape where same face appears in iteration twice.
- **Minimal reproducer**: Create a wire-based shape where face appears in two disconnected positions; marshal with ShapeUpgrade_UnifySameDomain. Without check: face unifies twice, corrupting myFaceNewFace map. With: processed face is skipped.
- **Search anchors**: 'aProcessed.Contains', 'continue after Contains check'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.null_surface_defense`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3213  **Axis**: `input-shape`
- **Brief**: Guard against faces with null underlying surface (e.g., degenerate or corrupted input).
- **Falsifiable claim**: Without this check, ClearRts or surface operations downstream would crash on null Geom_Surface. To test: pass STEP with invalid FACE definition.
- **Minimal reproducer**: Construct STEP with FACE having null underlying surface definition. Call IntUnifyFaces. Without guard: crash in ClearRts or BRep_Tool. With: face skipped gracefully.
- **Search anchors**: 'aBaseSurface.IsNull()', 'Bug 33894'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.degenerate_edge_skip`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3218  **Axis**: `input-shape`
- **Brief**: Skip degenerate edges during adjacency search.
- **Falsifiable claim**: Without this skip, degenerate edges (zero-length in 3D) would be treated as valid connectors between faces, causing topology errors. To test: merge coplanar faces with degenerate shared edge.
- **Minimal reproducer**: Create two coplanar faces meeting at a degenerate edge (e.g., cone apex). IntUnifyFaces should unify faces but not treat degeneracy as valid seam. Without: may attempt seam logic on degenerate. With: skipped.
- **Search anchors**: 'BRep_Tool::Degenerated'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.non_manifold_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3225  **Axis**: `api-contract`
- **Brief**: Filter non-manifold edges unless myAllowInternal permits them.
- **Falsifiable claim**: Without this check, non-manifold topology (edge shared by >2 faces, or free boundary) would be unified, breaking solid validity. To test: call with myAllowInternal=false on edge touching 3+ faces.
- **Minimal reproducer**: Create shell with edge touching 3 faces; myAllowInternal=false. Call IntUnifyFaces. Without guard: edge treated as unifiable seam. With: skipped unless myAllowInternal.
- **Search anchors**: 'myAllowInternal', 'aGList.Extent() != 2', 'theFreeBoundMap.Contains'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.local_edge_limit_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3232  **Axis**: `healer-state`
- **Brief**: Require edge to have exactly 2 faces in the current input shape.
- **Falsifiable claim**: Without this check, edges internal to one shell but shared by >1 face elsewhere would be incorrectly handled. To test: merge multiple disjoint shells with shared edge references.
- **Minimal reproducer**: Build input shape with two shells sharing an edge; in shell-1 edge is interior (2 faces), in shell-2 edge touches 1 face. Without: may skip edge. With: correctly identifies local connectivity.
- **Search anchors**: 'aList.Extent() < 2'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.planar_pcurve_optimization`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3239  **Axis**: `healer-state`
- **Brief**: Pre-build pcurves for planar faces in non-safe mode for speed.
- **Falsifiable claim**: Without this branch, planar-face pcurve evaluation would be slower. To test: profile IntUnifyFaces on coplanar face set with mySafeInputMode=false.
- **Minimal reproducer**: Create 10 coplanar faces; IntUnifyFaces with mySafeInputMode=false. Performance should improve with BuildPCurveForEdgeOnPlane. Measure time to unify.
- **Search anchors**: 'mySafeInputMode', 'BRepLib::BuildPCurveForEdgeOnPlane'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.normal_check_shortcut`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3251  **Axis**: `tolerance`
- **Brief**: Compute face normal for early rejection of non-coplanar/non-cospherical adjacencies.
- **Falsifiable claim**: Without bCheckNormals, faces at steep angles would still attempt IsSameDomain check, wasting cycles. To test: measure branch coverage on faces meeting at 45-degree angle.
- **Minimal reproducer**: Create two faces meeting at 45 degrees; myAngTol=0.1 rad. If bCheckNormals=true, angle check should early-skip. If false: proceeds to IsSameDomain.
- **Search anchors**: 'bCheckNormals = GetNormalToSurface', 'aDN1.Angle(aDN2)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.same_face_self_skip`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3260  **Axis**: `healer-state`
- **Brief**: Skip comparison of face with itself in adjacency iteration.
- **Falsifiable claim**: Without this check, face would be added to unification set twice (once as base, once in iteration), causing double-merge in myContext. To test: construct edge with same face on both sides.
- **Minimal reproducer**: Create non-manifold edge (same face on both sides, e.g., internal loop). Iterate face adjacency. Without: face added to 'faces' twice. With: self-comparison skipped.
- **Search anchors**: 'aCheckedFace.IsSame(aFace)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.same_shell_containment_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3266  **Axis**: `conformance-probe`
- **Brief**: Only unify faces that belong to the same shell(s).
- **Falsifiable claim**: Without this check, faces from disjoint shells would be unified, breaking multi-shell topology. To test: create solid with internal cavity (two shells); try to unify coplanar faces across shells.
- **Minimal reproducer**: Build solid with shell-outer and shell-inner (cavity). Define coplanar faces F_outer and F_inner. Without: IntUnifyFaces might merge them, breaking topology. With: isSameSets check prevents merge.
- **Search anchors**: 'theGMapFaceShells.Seek', 'isSameSets(pFShells1, pFShells2)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.angle_tolerance_filter`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3284  **Axis**: `tolerance`
- **Brief**: Reject adjacent faces with angle between normals exceeding myAngTol.
- **Falsifiable claim**: Without angle check, slightly non-coplanar faces would be treated as same domain, producing incorrect merged geometry. To test: call on two faces at angle myAngTol + epsilon.
- **Minimal reproducer**: Create two cylindrical faces on same axis, offset by angle > myAngTol (e.g., 0.2 rad if myAngTol=0.1). IntUnifyFaces should reject merge. Without: may unify. With: angle prevents.
- **Search anchors**: 'if (anAngle > myAngTol)', 'continue'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.same_domain_geometry_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3295  **Axis**: `kernel-pair`
- **Brief**: Verify that adjacent faces lie on the same geometric surface (plane, cylinder, etc.).
- **Falsifiable claim**: Without IsSameDomain call, faces touching different surfaces (plane + cylinder) would be merged, causing geometric inconsistency. To test: call on edge between plane and cylinder.
- **Minimal reproducer**: Create planar face F1, cylindrical face F2 sharing an edge. IntUnifyFaces should reject merge. Without IsSameDomain: may attempt merge. With: checked.
- **Search anchors**: 'if (IsSameDomain(aFace, aCheckedFace, ...))'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.already_processed_face_skip_inner`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3266  **Axis**: `healer-state`
- **Brief**: Skip checked face if already unified with another face in this iteration.
- **Falsifiable claim**: Without this check, already-unified face would be added twice to 'faces' sequence, causing duplicate operations. To test: three coplanar faces F1-F2-F3; iterate edges after F2 unified.
- **Minimal reproducer**: Create three coplanar faces sharing edges. After F2 added to 'faces' and aProcessed, next iteration should skip F2. Without: F2 may be re-added. With: aProcessed.Contains prevents.
- **Search anchors**: 'aProcessed.Contains(aCheckedFace)', 'continue after Contains'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.multi_face_unification_guard`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3311  **Axis**: `healer-state`
- **Brief**: Only proceed with unification logic if >1 face collected.
- **Falsifiable claim**: Without this guard, single-face shapes would enter expensive wire-building logic unnecessarily. To test: call IntUnifyFaces on isolated coplanar face pair with no shared edge.
- **Minimal reproducer**: Create single face with no adjacent same-domain faces. Without guard: enters full unification pipeline. With guard: skips to next face.
- **Search anchors**: 'if (faces.Length() > 1)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.plane_map_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3313  **Axis**: `healer-state`
- **Brief**: Update RefFace with plane from myFacePlaneMap if available.
- **Falsifiable claim**: Without this check, RefFace might retain non-planar surface even when faces are planar, causing incorrect pcurve computation. To test: call on faces with cached plane in myFacePlaneMap.
- **Minimal reproducer**: Pre-populate myFacePlaneMap with planar surface for face F1. IntUnifyFaces should detect and use it. Without: may use non-planar surface. With: updated.
- **Search anchors**: 'myFacePlaneMap.IsBound(faces(1))', 'BB.UpdateFace(RefFace, aPlane, ...)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.add_pcurves_to_faces`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3322  **Axis**: `healer-state`
- **Brief**: Ensure all edges have correct parametric curves on merged reference surface.
- **Falsifiable claim**: Without AddPCurves, edges from non-reference faces would lack correct pcurves on RefFace, breaking downstream face building. To test: call IntUnifyFaces with multi-face set; check pcurves.
- **Minimal reproducer**: Merge two coplanar faces with edge E. After merge, all edges must have pcurves on RefFace. Without AddPCurves: edge from F2 lacks pcurve. With: added.
- **Search anchors**: 'AddPCurves(faces, F_RefFace, MapEdgesWithTemporaryPCurves)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.edge_face_map_construction`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3325  **Axis**: `healer-state`
- **Brief**: Build connectivity map for edges in merged face set.
- **Falsifiable claim**: Without this map, downstream logic for identifying multi-connected edges would fail. To test: verify aMapEF is populated after this loop.
- **Minimal reproducer**: Merge N faces; aMapEF must contain all edges and their face adjacencies. Without map: aKeepEdges identification breaks. With: correct.
- **Search anchors**: 'TopExp::MapShapesAndAncestors', 'aMapEF'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.multi_connected_edge_detection`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3333  **Axis**: `conformance-probe`
- **Brief**: Identify edges with exactly 2 faces in merged set but >2 in global shape.
- **Falsifiable claim**: Without this detection, multi-connected edges (internal to merge set but touching external faces) would be treated as boundary edges, breaking topology. To test: merge faces with internal edge touching external face.
- **Minimal reproducer**: Create face-set where edge E is interior (2 faces in set) but touches face F_external. Without: E treated as boundary. With: E added to aKeepEdges for special handling.
- **Search anchors**: 'aGLF.Extent() > 2', 'aKeepEdges.Append'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.keep_edges_non_internal_handling`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3350  **Axis**: `api-contract`
- **Brief**: When myAllowInternal=false, remove faces from merge if they only connect via multi-connected edges.
- **Falsifiable claim**: Without this logic, merging faces with multi-connected edges would break external topology. To test: call with myAllowInternal=false on faces meeting at non-manifold edge.
- **Minimal reproducer**: Create face-pair meeting at edge touching 3+ faces globally; myAllowInternal=false. Without: faces merged, breaking topology. With: faces removed from merge set.
- **Search anchors**: 'if (!myAllowInternal)', 'anAvoidFaces.Add', 'hasConnectAnotherFaces'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.find_external_connections`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3370  **Axis**: `conformance-probe`
- **Brief**: Check if face has edges connecting to faces outside merge set.
- **Falsifiable claim**: Without this check, isolated internal faces would be kept in merge even if they only touch multi-connected edges. To test: remove this check and verify topology breaks.
- **Minimal reproducer**: Face F_iso touches only multi-connected edges; without check, F_iso stays in merge despite isolation. With: hasConnectAnotherFaces identifies external connections.
- **Search anchors**: 'TopExp_Explorer ex(faces(i), TopAbs_EDGE)', 'hasConnectAnotherFaces = true'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.face_removal_from_set`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3387  **Axis**: `healer-state`
- **Brief**: Remove face from unification if it only touches multi-connected edges.
- **Falsifiable claim**: Without removal, face would remain in merged set even if unification breaks external connections. To test: verify face count in 'faces' sequence before/after this branch.
- **Minimal reproducer**: Face with no external edge connections should be removed. Without: remains in set. With: AddOrdinaryEdges called and face removed.
- **Search anchors**: 'faces.Remove(i)', 'i--'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.keep_edges_already_unified`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3398  **Axis**: `healer-state`
- **Brief**: Check if keep edges already belong to unified faces in reduced set.
- **Falsifiable claim**: Without this check, faces touching keep edges would be kept unnecessarily, bloating merge set. To test: verify second removal pass catches faces missed in first pass.
- **Minimal reproducer**: After first removal pass, some faces with keep edges may remain isolated. Second pass should remove them. Without: remain. With: removed.
- **Search anchors**: 'aMapFaces.Contains(aLF.First())', 'aMapFaces.Contains(aLF.Last())'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.internal_edges_allowed_branch`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3427  **Axis**: `api-contract`
- **Brief**: When myAllowInternal=true, add multi-connected edges as internal to unified face.
- **Falsifiable claim**: Without this branch, multi-connected edges would be lost or cause topology errors when myAllowInternal=true. To test: call with myAllowInternal=true and verify internal edges preserved.
- **Minimal reproducer**: Set myAllowInternal=true; merge faces touching multi-connected edge E. E should be added with INTERNAL orientation. Without: E lost. With: preserved as INTERNAL.
- **Search anchors**: 'else { // internal edges are allowed', 'edges.Append(aE.Oriented(TopAbs_INTERNAL))'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.orientation_preservation`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3484  **Axis**: `healer-state`
- **Brief**: Correct edge orientations for internal edges in merged face.
- **Falsifiable claim**: Without this correction, internal edges would have incorrect orientation, breaking face winding. To test: verify internal edge orientation after merge.
- **Minimal reproducer**: Add internal edge to unified face; its orientation must match merged face. Without: orientation incorrect. With: corrected.
- **Search anchors**: 'if (myAllowInternal && myKeepShapes.Contains(anEdge) && aLF.Extent() == 2)', 'edges(ii).Orientation(TopAbs_INTERNAL)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.preserve_edge_orientation`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3460  **Axis**: `healer-state`
- **Brief**: Restore original edge orientation if not internal.
- **Falsifiable claim**: Without this restoration, edge orientation from aMapEF would be overwritten, breaking wire building. To test: verify edge orientation matches aMapEF for non-internal edges.
- **Minimal reproducer**: Non-internal edge E from aMapEF should preserve its orientation. Without: overwritten. With: restored.
- **Search anchors**: 'if (anEdge.Orientation() != TopAbs_INTERNAL)', 'edges(ii) = aMapEF.FindKey(indE)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.internal_edge_extraction`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3467  **Axis**: `healer-state`
- **Brief**: Separate internal edges from boundary edges before wire building.
- **Falsifiable claim**: Without this separation, internal edges would be treated as wire boundaries, causing invalid topology. To test: verify InternalEdges contains all INTERNAL-oriented edges.
- **Minimal reproducer**: Merge faces with internal edges. Before wire building, INTERNAL edges must be extracted. Without: may become boundary wires. With: separated correctly.
- **Search anchors**: 'InternalEdges.Add(anEdge)', 'edges.Remove(ind_e)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.reversed_face_orientation_handling`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3484  **Axis**: `healer-state`
- **Brief**: Reverse edges if unified face has REVERSED orientation.
- **Falsifiable claim**: Without this reversal, edges would have incorrect orientation relative to reversed face, breaking winding. To test: call IntUnifyFaces on reversed face; check edge orientations.
- **Minimal reproducer**: Create face with RefFaceOrientation=REVERSED. Edges must be reversed to maintain winding. Without: winding incorrect. With: reversed.
- **Search anchors**: 'if (RefFaceOrientation == TopAbs_REVERSED)', 'edges(ii).Reverse()'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.seam_edge_detection_reallyclosed`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3469  **Axis**: `kernel-pair`
- **Brief**: Identify seam edges on periodic surfaces.
- **Falsifiable claim**: Without seam detection, periodic faces would be treated as non-periodic, causing incorrect pcurve reconstruction. To test: call on coplanar periodic faces; check SeamFound flag.
- **Minimal reproducer**: Create two coplanar periodic faces (cylindrical surface). SeamFound should be true. Without detection: false, breaking seam logic. With: correctly identified.
- **Search anchors**: 'BRep_Tool::IsClosed(anEdge, face_ii)', 'BRepTools::IsReallyClosed(anEdge, face_ii)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.u_seam_detection`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3478  **Axis**: `kernel-pair`
- **Brief**: Distinguish U-direction seams from V-direction seams.
- **Falsifiable claim**: Without this distinction, seam reconstruction logic would apply wrong direction transformations. To test: call on periodic surface with U-seam; verify UseamFound=true, VseamFound=false.
- **Minimal reproducer**: Periodic cylinder with U-seam. IsUiso check should set UseamFound. Without: both flags may be set. With: correctly distinguished.
- **Search anchors**: 'if (IsUiso(anEdge, face_ii))', 'UseamFound = true', 'VseamFound = true'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.edge_with_two_pcurves_detection`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3487  **Axis**: `healer-state`
- **Brief**: Find non-seam edges that have 2 pcurves on surface (indicates near-seam condition).
- **Falsifiable claim**: Without this detection, BSpline periodicity reconstruction would be skipped. To test: call with myConcatBSplines=true on faces with edge having 2 pcurves.
- **Minimal reproducer**: Create edge E with 2 pcurves (seam-like but not really seam). EdgeWith2pcurves should be set. Without detection: skipped. With: used for seam reconstruction.
- **Search anchors**: 'else { EdgeWith2pcurves = anEdge; }'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.concat_bsplines_continuity_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3544  **Axis**: `tolerance`
- **Brief**: Verify smooth transition (G1+) across edge before attempting periodicity reconstruction.
- **Falsifiable claim**: Without continuity check, low-quality faces would have periodicity forced, creating artifacts. To test: call with edge having C0 continuity; verify aIsEdgeWith2pcurvesSmooth=false.
- **Minimal reproducer**: Create edge E between two faces with only C0 continuity. Without check: periodicity might be forced. With: check prevents (aIsEdgeWith2pcurvesSmooth=false).
- **Search anchors**: 'BRepLib::ContinuityOfFaces', 'aIsEdgeWith2pcurvesSmooth = (anOrderOfCont >= GeomAbs_G1)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.smooth_edge_pcurve_extraction`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3555  **Axis**: `healer-state`
- **Brief**: Extract parametric curves from both sides of smooth edge with 2 pcurves.
- **Falsifiable claim**: Without extraction, periodicity direction determination would fail. To test: verify aPC1 and aPC2 are populated after CurveOnSurface calls.
- **Minimal reproducer**: Edge E with 2 pcurves on RefFace. aPC1 and aPC2 must be extracted. Without: curves null. With: populated.
- **Search anchors**: 'aPC1 = BRep_Tool::CurveOnSurface(EdgeWith2pcurves, F_RefFace, ...)', 'aPC2 = BRep_Tool::CurveOnSurface(EdgeWith2pcurves.Reverse(), ...)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.periodicity_direction_determination`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3565  **Axis**: `tolerance`
- **Brief**: Determine whether seam-like edge spans U or V parametric direction.
- **Falsifiable claim**: Without direction determination, periodicity would be set on wrong axis. To test: verify anIsUclosed matches expected direction (X vs Y difference in 2D).
- **Minimal reproducer**: Edge with 2 pcurves; aPnt1.X() >> aPnt1.Y() means U-closed. Without: direction guessed wrong. With: correctly determined.
- **Search anchors**: 'bool anIsUclosed = (std::abs(aPnt1.X() - aPnt2.X()) > std::abs(aPnt1.Y() - aPnt2.Y()))'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.u_periodicity_flag_set`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3568  **Axis**: `healer-state`
- **Brief**: Mark for U-periodicity if seam-like edge spans U and surface not already U-periodic.
- **Falsifiable claim**: Without this flag, U-periodicity would not be reconstructed. To test: call on surface with seam-like edge in U, Uperiod=0; verify aToMakeUPeriodic=true.
- **Minimal reproducer**: Seam-like edge spans U direction, Uperiod=0. aToMakeUPeriodic should be set. Without: false. With: true.
- **Search anchors**: 'if (anIsUclosed && Uperiod == 0.)', 'aToMakeUPeriodic = true'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.v_periodicity_flag_set`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3571  **Axis**: `healer-state`
- **Brief**: Mark for V-periodicity if seam-like edge spans V and surface not already V-periodic.
- **Falsifiable claim**: Without this flag, V-periodicity would not be reconstructed. To test: call on surface with seam-like edge in V, Vperiod=0; verify aToMakeVPeriodic=true.
- **Minimal reproducer**: Seam-like edge spans V direction, Vperiod=0. aToMakeVPeriodic should be set. Without: false. With: true.
- **Search anchors**: 'if (!anIsUclosed && Vperiod == 0.)', 'aToMakeVPeriodic = true'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.periodicity_reconstruction_attempt`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3576  **Axis**: `kernel-pair`
- **Brief**: Attempt to make non-periodic surface periodic via BSpline periodicity setting.
- **Falsifiable claim**: Without this attempt, surfaces with seam-like edges would remain non-periodic, breaking face merge. To test: verify SetUPeriodic() or SetVPeriodic() called when flags set.
- **Minimal reproducer**: Non-periodic surface with seam-like edge; aToMakeUPeriodic=true. SetUPeriodic() must be called. Without: skipped. With: called.
- **Search anchors**: 'if (aToMakeUPeriodic || aToMakeVPeriodic)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.bspline_surface_cast_attempt`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3580  **Axis**: `kernel-pair`
- **Brief**: Try to cast base surface to BSplineSurface for periodicity modification.
- **Falsifiable claim**: Without this cast, periodicity would not be set. To test: verify aBSplineSurface non-null if base surface is BSpline.
- **Minimal reproducer**: BSpline surface with seam-like edge. aBSplineSurface should be non-null after cast. Without: null. With: cast succeeds.
- **Search anchors**: 'aBSplineSurface = occ::down_cast<Geom_BSplineSurface>(aBaseSurface)', 'if (aBSplineSurface.IsNull())'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.non_bspline_surface_approximation`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3580  **Axis**: `kernel-pair`
- **Brief**: Approximate non-BSpline surface to BSpline for periodicity reconstruction.
- **Falsifiable claim**: Without approximation, non-BSpline surfaces (e.g., plane, cylinder) cannot be made periodic. To test: call on planar seam-like merge; verify approximation executed.
- **Minimal reproducer**: Planar surface with seam-like edge. If cast fails, approximate to BSpline. Without: periodicity impossible. With: approximation enables it.
- **Search anchors**: 'GeomConvert_ApproxSurface Approximator(...)', 'aBSplineSurface = Approximator.Surface()'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.set_u_periodic_bspline`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3593  **Axis**: `kernel-pair`
- **Brief**: Mark BSpline surface as U-periodic.
- **Falsifiable claim**: Without SetUPeriodic, surface remains non-periodic despite reconstruction. To test: verify Uperiod updated after SetUPeriodic() call.
- **Minimal reproducer**: BSpline with aToMakeUPeriodic=true. SetUPeriodic() must be called. Without: Uperiod unchanged. With: set.
- **Search anchors**: 'if (aToMakeUPeriodic)', 'aBSplineSurface->SetUPeriodic()'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.set_v_periodic_bspline`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3598  **Axis**: `kernel-pair`
- **Brief**: Mark BSpline surface as V-periodic.
- **Falsifiable claim**: Without SetVPeriodic, surface remains non-periodic despite reconstruction. To test: verify Vperiod updated after SetVPeriodic() call.
- **Minimal reproducer**: BSpline with aToMakeVPeriodic=true. SetVPeriodic() must be called. Without: Vperiod unchanged. With: set.
- **Search anchors**: 'if (aToMakeVPeriodic)', 'aBSplineSurface->SetVPeriodic()'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.ref_face_update_after_periodicity`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3604  **Axis**: `healer-state`
- **Brief**: Replace RefFace with new BSpline surface after periodicity modification.
- **Falsifiable claim**: Without update, RefFace would retain old non-periodic surface, breaking downstream pcurve logic. To test: verify RefFace uses new aBSplineSurface after update.
- **Minimal reproducer**: Surface made periodic (aBSplineSurface != aBaseSurface). RefFace must be rebuilt with new surface. Without: uses old. With: updated.
- **Search anchors**: 'if (aBSplineSurface != aBaseSurface)', 'RefFace.Nullify()', 'BB.MakeFace(RefFace, aBSplineSurface, ...)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.edge_pcurve_migration_to_new_surface`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3610  **Axis**: `healer-state`
- **Brief**: Transfer edge pcurves from old surface to new periodic surface.
- **Falsifiable claim**: Without pcurve transfer, edges would lack curves on new surface, breaking wire building. To test: verify all edges have pcurves on RefFace after loop.
- **Minimal reproducer**: RefFace updated with new periodic surface. All edges must have pcurves transferred. Without: pcurves null. With: transferred.
- **Search anchors**: 'occ::handle<Geom2d_Curve> aPCurve = BRep_Tool::CurveOnSurface(anEdge, OldRefFace, ...)', 'BB.UpdateEdge(anEdge, aPCurve, RefFace, ...)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.temporary_pcurve_cleanup`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3616  **Axis**: `healer-state`
- **Brief**: Remove temporary pcurves from edges before updating with real ones.
- **Falsifiable claim**: Without cleanup, temporary pcurves would interfere with new surface pcurves. To test: verify MapEdgesWithTemporaryPCurves cleared for updated edges.
- **Minimal reproducer**: Edges with temporary pcurves must have them cleared before new ones added. Without: pcurve conflicts. With: cleaned.
- **Search anchors**: 'if (MapEdgesWithTemporaryPCurves.Contains(anEdge))', 'BB.UpdateEdge(anEdge, NullPCurve, OldRefFace, 0.)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.closed_non_periodic_period_inference`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3768  **Axis**: `kernel-pair`
- **Brief**: For closed non-periodic surfaces, infer period from surface bounds.
- **Falsifiable claim**: Without inference, Uperiod/Vperiod would remain 0 for closed non-periodic surfaces, breaking seam reconstruction. To test: call on sphere (U/V-closed, non-periodic); verify Uperiod/Vperiod set.
- **Minimal reproducer**: Sphere is U-closed and V-closed but non-periodic. Bounds give period range. Without: period=0. With: inferred.
- **Search anchors**: 'if (Uperiod == 0 && aSurf->IsUClosed())', 'Uperiod = Ulast - Ufirst'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.find_seam_u_bounds`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3736  **Axis**: `healer-state`
- **Brief**: Locate U-coordinate extrema of face set in parametric space.
- **Falsifiable claim**: Without bounds, seam-origin relocation would fail. To test: verify FaceUmin/FaceVmin updated after edge iteration.
- **Minimal reproducer**: Edge set has U range [0.5, 1.5]. FaceUmin should be 0.5. Without: FaceUmin=RealLast. With: 0.5.
- **Search anchors**: 'if (aFirstPoint.X() < FaceUmin)', 'FaceUmin = aFirstPoint.X()'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.find_seam_v_bounds`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3814  **Axis**: `healer-state`
- **Brief**: Locate V-coordinate extrema of face set in parametric space.
- **Falsifiable claim**: Without bounds, seam-origin relocation would fail for V-direction. To test: verify FaceVmin updated after edge iteration.
- **Minimal reproducer**: Edge set has V range [2.0, 3.0]. FaceVmin should be 2.0. Without: FaceVmin=RealLast. With: 2.0.
- **Search anchors**: 'if (aFirstPoint.Y() < FaceVmin)', 'FaceVmin = aFirstPoint.Y()'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.wire_building_from_edges`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3827  **Axis**: `healer-state`
- **Brief**: Construct wires from boundary edges of merged faces.
- **Falsifiable claim**: Without wire building, faces would have no boundaries, causing invalid topology. To test: verify NewWires non-empty after while loop.
- **Minimal reproducer**: Merged face with boundary edges. Wires must be built. Without: no wires. With: wires built.
- **Search anchors**: 'while (!edges.IsEmpty())', 'TopoDS_Wire aNewWire', 'BB.MakeWire(aNewWire)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.find_non_degenerate_start_edge`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3829  **Axis**: `input-shape`
- **Brief**: Select non-degenerate edge as wire starting point.
- **Falsifiable claim**: Without non-degenerate start, wire would collapse. To test: verify StartEdge is non-degenerate after while loop.
- **Minimal reproducer**: Edge list with degenerate edges at start. Loop must skip to non-degenerate. Without: StartEdge=degenerate. With: non-degenerate.
- **Search anchors**: 'while (BRep_Tool::Degenerated(StartEdge) && istart < edges.Length())', 'istart++'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.skip_null_pcurve_edge`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3847  **Axis**: `input-shape`
- **Brief**: Skip edges lacking parametric curves on reference surface.
- **Falsifiable claim**: Without skip, null pcurve would cause crash in downstream D1 evaluation. To test: call on edge with null StartPCurve; verify skip executed.
- **Minimal reproducer**: Edge E lacks pcurve on F_RefFace. StartPCurve.IsNull()=true. Without: crash. With: skipped.
- **Search anchors**: 'if (StartPCurve.IsNull())', 'edges.Remove(istart)', 'continue'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.wire_loop_start_vertex_extraction`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3852  **Axis**: `healer-state`
- **Brief**: Extract start and end vertices of initial edge for wire building.
- **Falsifiable claim**: Without vertices, wire chain cannot be built. To test: verify StartVertex and CurVertex populated after TopExp::Vertices call.
- **Minimal reproducer**: StartEdge defines wire start. StartVertex must match FirstVertex. Without: vertex null. With: extracted.
- **Search anchors**: 'TopExp::Vertices(StartEdge, StartVertex, CurVertex, true)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.edge_orientation_to_parameters`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3853  **Axis**: `healer-state`
- **Brief**: Map edge orientation (FORWARD/REVERSED) to parametric curve parameter direction.
- **Falsifiable claim**: Without mapping, pcurve traversal would go backward, causing wire closing to fail. To test: verify StartParam and CurParam match orientation.
- **Minimal reproducer**: FORWARD edge: StartParam=fpar, CurParam=lpar. REVERSED: reversed. Without: parameters swapped. With: correct.
- **Search anchors**: 'if (StartEdge.Orientation() == TopAbs_FORWARD)', 'StartParam = fpar', 'CurParam = lpar'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.pcurve_end_point_evaluation`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3862  **Axis**: `healer-state`
- **Brief**: Evaluate parametric curve at start and end to get 2D coordinates.
- **Falsifiable claim**: Without evaluation, wire closing logic would fail (no 2D point comparison). To test: verify StartPoint and CurPoint non-null after evaluation.
- **Minimal reproducer**: Edge with pcurve. StartPoint = StartPCurve->Value(StartParam). Without: point null. With: evaluated.
- **Search anchors**: 'gp_Pnt2d StartPoint = StartPCurve->Value(StartParam)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.empty_vertex_edge_list_seam_reconstruction` **[low-confidence]**
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3879  **Axis**: `kernel-pair`
- **Brief**: When vertex has no connected edges, check if it's the wire closure point on periodic surface.
- **Falsifiable claim**: Without this check, periodic-surface wires would not close correctly. To test: verify ReconstructMissedSeam called when Elist empty and CurVertex~=StartVertex.
- **Minimal reproducer**: Wire on periodic surface; at closure, CurVertex~=StartVertex but 2D points differ by period. Without: wire open. With: seam reconstructed.
- **Search anchors**: 'if (CurVertex.IsSame(StartVertex))', 'if ((Uperiod != 0. && std::abs(StartPoint.X() - CurPoint.X()) > Uperiod / 2) || ...'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.singularity_vertex_detection`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3911  **Axis**: `kernel-pair`
- **Brief**: Detect if current vertex lies on surface singularity (e.g., pole of sphere).
- **Falsifiable claim**: Without detection, singularity vertices would cause invalid wire splitting. To test: call on vertex at sphere pole; verify anIsOnSingularity=true.
- **Minimal reproducer**: Vertex V at sphere north pole. IsOnSingularity(Elist) should be true. Without: false, breaking splitting. With: true.
- **Search anchors**: 'bool anIsOnSingularity = IsOnSingularity(Elist)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.multi_edge_vertex_splitting_marker`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3912  **Axis**: `healer-state`
- **Brief**: Mark vertices with multiple non-singularity edges for wire splitting.
- **Falsifiable claim**: Without marking, multi-connected vertices would be treated as simple vertices, breaking wire topology. To test: verify SplittingVertices contains vertices with Elist.Extent() > 1.
- **Minimal reproducer**: Vertex V with 3 connected edges, not on singularity. SplittingVertices.Add(V). Without: not added. With: marked for splitting.
- **Search anchors**: 'if (!anIsOnSingularity && Elist.Extent() > 1)', 'SplittingVertices.Add(CurVertex)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.candidate_edge_orientation_filter`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3919  **Axis**: `healer-state`
- **Brief**: Filter edges to those starting from current vertex and not yet used.
- **Falsifiable claim**: Without filtering, TrueElist would contain wrong edges, breaking wire continuity. To test: verify all edges in TrueElist start from CurVertex.
- **Minimal reproducer**: CurVertex has 3 connected edges; only 2 start from it. TmpElist should have length 2. Without: wrong count. With: filtered.
- **Search anchors**: 'TopExp::FirstVertex(anEdge, true)', 'if (!aFirstVertex.IsSame(CurVertex))', 'continue'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.direction_based_edge_selection_periodic`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3932  **Axis**: `healer-state`
- **Brief**: On non-periodic surfaces, select edge with max angle to continue wire smoothly.
- **Falsifiable claim**: Without angle-based selection, wire might fork at multi-connected vertices. To test: call on multi-edge vertex with Uperiod=0, Vperiod=0.
- **Minimal reproducer**: Vertex V with 3 edges on non-periodic surface. MaxAngle selection picks edge with largest turn angle. Without: random selection. With: smooth continuation.
- **Search anchors**: 'if (TmpElist.Extent() <= 1 || (Uperiod != 0. || Vperiod != 0))', 'else { // max angle selection }'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.current_edge_direction_extraction`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3943  **Axis**: `healer-state`
- **Brief**: Extract tangent vector of current edge at exit vertex.
- **Falsifiable claim**: Without tangent, direction comparison would fail, breaking edge selection. To test: verify CurDir non-zero after D1 evaluation.
- **Minimal reproducer**: CurEdge at exit vertex. D1 must give non-zero tangent. Without: CurDir zero. With: extracted.
- **Search anchors**: 'CurPCurve->D1(CurParam, CurPoint, CurDir)', 'CurDir.Normalize()'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.candidate_edge_direction_comparison`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3951  **Axis**: `healer-state`
- **Brief**: Evaluate tangent at candidate edge start and compare angle with current exit direction.
- **Falsifiable claim**: Without comparison, edge with max angle would not be identified. To test: verify anAngle computed for each candidate.
- **Minimal reproducer**: Candidate edge has direction aDir. Angle between CurDir and aDir computed. Without: angle not used. With: used for selection.
- **Search anchors**: 'double anAngle = CurDir.Angle(aDir)', 'if (anAngle > MaxAngle)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.max_angle_edge_selection`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3968  **Axis**: `healer-state`
- **Brief**: Select edge with maximum turn angle for smooth wire continuation.
- **Falsifiable claim**: Without max-angle selection, wire would fork incorrectly at multi-edges. To test: verify TrueEdge is edge with largest anAngle.
- **Minimal reproducer**: 3 candidate edges with angles 0.5, 1.2, 0.8 rad. TrueEdge should be edge with 1.2 rad. Without: random. With: 1.2.
- **Search anchors**: 'MaxAngle = anAngle', 'TrueEdge = anEdge'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.true_edge_candidate_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3976  **Axis**: `tolerance`
- **Brief**: Check if selected true edge connects to current vertex within tolerance.
- **Falsifiable claim**: Without tolerance-based check, degenerate vertices would cause edge mismatch. To test: verify edge start point within CoordTol of CurPoint.
- **Minimal reproducer**: Edge start point differs from CurPoint by < CoordTol. Continue check should pass. Without: tolerance not checked. With: checked.
- **Search anchors**: 'double DiffU = std::abs(aPoint.X() - CurPoint.X())', 'if (Uperiod != 0. && DiffU > CoordTol && std::abs(DiffU - Uperiod) > CoordTol)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.periodic_boundary_crossing_seam_reconstruction` **[low-confidence]**
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3998  **Axis**: `kernel-pair`
- **Brief**: When edge endpoint is far from start (> period/2), reconstruct missing seam to connect them.
- **Falsifiable claim**: Without seam reconstruction, periodic-surface wires would break at period boundary. To test: call on periodic surface with edges spanning boundary.
- **Minimal reproducer**: Two edges on periodic surface at U=0.1 and U=3.0 (period=2π). Seam reconstruction connects them. Without: break. With: seam built.
- **Search anchors**: 'if ((Uperiod != 0. && DiffU > Uperiod / 2) || (Vperiod != 0. && DiffV > Vperiod / 2))', 'ReconstructMissedSeam'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.end_of_wire_on_seam_detection`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3013  **Axis**: `healer-state`
- **Brief**: Detect if reconstructed seam closes the wire at start vertex.
- **Falsifiable claim**: Without detection, wire would continue past closure. To test: verify EndOfWire=true when seam leads back to StartVertex.
- **Minimal reproducer**: Seam reconstruction ends at StartVertex. EndOfWire should be true. Without: false, wire continues. With: true.
- **Search anchors**: 'if (LastVertexOfSeam.IsSame(StartVertex) && ...)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.null_next_edge_periodic_fallback`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4040  **Axis**: `healer-state`
- **Brief**: On periodic surface with null NextEdge, attempt seam reconstruction or exit wire loop.
- **Falsifiable claim**: Without fallback, null NextEdge would cause infinite loop or crash. To test: call on periodic surface with incomplete edge chain.
- **Minimal reproducer**: Periodic surface with incomplete boundary edges. At end, NextEdge=null. Without: infinite loop. With: ReconstructMissedSeam or return.
- **Search anchors**: 'if (NextEdge.IsNull())', 'if (Uperiod != 0. || Vperiod != 0.)', 'ReconstructMissedSeam'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.null_next_edge_non_periodic_exit`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4064  **Axis**: `healer-state`
- **Brief**: Exit wire building immediately if NextEdge null on non-periodic surface.
- **Falsifiable claim**: Without exit, incomplete wire would cause assertion or invalid face. To test: call on non-periodic surface with broken edge chain.
- **Minimal reproducer**: Non-periodic surface with missing edge at end of chain. NextEdge=null, no fallback. Without: infinite loop. With: return.
- **Search anchors**: 'else { return; }'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.degenerate_edge_skip_in_wire_building`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:3830  **Axis**: `input-shape`
- **Brief**: Skip degenerate edges during wire construction from boundary edges.
- **Falsifiable claim**: Without skip, degenerate edges would be added to wire, breaking geometry. To test: verify degenerate edges not in NewWires.
- **Minimal reproducer**: Boundary edge list with degenerate edges. Wire building should skip them. Without: added to wire. With: skipped.
- **Search anchors**: 'while (BRep_Tool::Degenerated(StartEdge) && istart < edges.Length())'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.edge_on_surface_boundary_detection`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4094  **Axis**: `conformance-probe`
- **Brief**: Detect if wire contains edge on surface boundary (e.g., seam or closed edge).
- **Falsifiable claim**: Without detection, boundary-edge wires would be treated as holes, breaking face topology. To test: call on face with seam-wire; verify EdgeOnBoundOfSurfFound=true.
- **Minimal reproducer**: Wire contains closed edge on RefFace. EdgeOnBoundOfSurfFound should be true. Without: false, treated as hole. With: true.
- **Search anchors**: 'if (BRep_Tool::IsClosed(anEdge, RefFace))', 'EdgeOnBoundOfSurfFound = true'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.boundary_wire_face_creation`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4104  **Axis**: `conformance-probe`
- **Brief**: Create separate face for wire touching surface boundary.
- **Falsifiable claim**: Without separate face, boundary-touching wire would be treated as hole, breaking multi-shell logic. To test: verify NewFaces contains face for boundary wire.
- **Minimal reproducer**: Wire touches surface boundary. NewFaces should contain new face for it. Without: treated as hole. With: face created.
- **Search anchors**: 'if (EdgeOnBoundOfSurfFound)', 'BB.MakeFace(aResult, aSurf, aLoc, 0)', 'NewFaces.Append(aResult)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.hole_wire_splitting`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4117  **Axis**: `healer-state`
- **Brief**: Split hole-wires at multi-connected vertices if needed.
- **Falsifiable claim**: Without splitting, hole-wires with multiple components would be invalid. To test: verify SplitWire called when SplittingVertices non-empty.
- **Minimal reproducer**: Hole-wire with multi-connected vertex. SplitWire should split it. Without: unsplit. With: split.
- **Search anchors**: 'if (!SplittingVertices.IsEmpty())', 'SplitWire(aNewWire, F_RefFace, SplittingVertices, NewWires)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.internal_edge_wire_construction`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4139  **Axis**: `healer-state`
- **Brief**: Build wires from internal edges of merged faces.
- **Falsifiable claim**: Without internal wire building, internal edges would not be preserved in output faces. To test: verify InternalWires non-empty after loop if InternalEdges present.
- **Minimal reproducer**: InternalEdges present. Internal wires must be built. Without: InternalWires empty. With: built.
- **Search anchors**: 'while (!InternalEdges.IsEmpty())', 'TopoDS_Wire anInternalWire', 'BB.MakeWire(anInternalWire)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.internal_wire_closure_check`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4152  **Axis**: `healer-state`
- **Brief**: Detect if internal wire is closed (both vertices of first edge same).
- **Falsifiable claim**: Without closure check, open internal wires would be treated as closed. To test: verify loop exits when VV[0]==VV[1].
- **Minimal reproducer**: First internal edge has same start/end vertex (closed). VV[0].IsSame(VV[1]) should be true. Without: continues loop. With: breaks.
- **Search anchors**: 'if (VV[0].IsSame(VV[1]))', 'break'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.internal_edge_chain_extension`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4160  **Axis**: `healer-state`
- **Brief**: Extend internal wire by finding next connected edge at either vertex.
- **Falsifiable claim**: Without chaining, internal edges would not form complete wires. To test: verify internal wire extended until closure or dead-end.
- **Minimal reproducer**: Internal edges form chain E1-E2-E3 (closed). Without: only E1 in wire. With: all three.
- **Search anchors**: 'for (int ii = 0; ii < 2; ii++)', 'if (anEdge.IsSame(EndEdges[ii]))', 'continue'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.single_result_face_no_seam`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4188  **Axis**: `healer-state`
- **Brief**: When no outer wires present, create single result face with all holes.
- **Falsifiable claim**: Without this branch, face with only holes and no outer wire would be invalid. To test: call on merged faces with only internal boundaries.
- **Minimal reproducer**: Merge produces outer=null but NewWires non-empty. Single face created. Without: invalid. With: face created.
- **Search anchors**: 'if (NewFaces.IsEmpty())', 'BB.MakeFace(aResult, aSurf, aLoc, 0.)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.single_outer_wire_face_result`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4209  **Axis**: `healer-state`
- **Brief**: When one outer wire present, create single result face with holes.
- **Falsifiable claim**: Without this branch, NewFaces.Length()==1 case would fall through to complex multi-face logic. To test: verify single face result when NewFaces.Length()==1.
- **Minimal reproducer**: One outer wire, multiple holes. Single face should be created. Without: multi-face logic. With: single face.
- **Search anchors**: 'else if (NewFaces.Length() == 1)', 'BB.Add(aNewFace, NewWires(ii))'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.multi_face_wire_insertion`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4232  **Axis**: `healer-state`
- **Brief**: Insert boundary and internal wires into correct outer faces.
- **Falsifiable claim**: Without insertion logic, wires would not be associated with correct faces. To test: verify all wires inserted into NewFaces.
- **Minimal reproducer**: Multiple outer faces, multiple holes. InsertWiresIntoFaces assigns wires to correct faces. Without: wrong assignment. With: correct.
- **Search anchors**: 'InsertWiresIntoFaces(NewWires, NewFaces, RefFace)', 'InsertWiresIntoFaces(InternalWires, NewFaces, RefFace)'

##### `ShapeUpgrade_UnifySameDomain.IntUnifyFaces.original_faces_to_result_mapping`
- **Line**: ShapeUpgrade_UnifySameDomain.cxx:4235  **Axis**: `healer-state`
- **Brief**: Map original merged faces to new result faces for context merge.
- **Falsifiable claim**: Without mapping, context merge would not know which old faces correspond to new faces. To test: verify edge in NewFaces appears in at least one original face.
- **Minimal reproducer**: Original faces F1, F2 merged to NewFace NF. For each edge in NF, find F1 or F2 containing it. Without: mapping fails. With: works.
- **Search anchors**: 'TopExp::MapShapes(faces(ii), aEmap)', 'Emaps.Append(aEmap)'

