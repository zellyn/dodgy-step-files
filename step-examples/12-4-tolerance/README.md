# §12.4 — Tolerance & numerical-precision defects (N-prefix)

Numerical-precision and tolerance defects: precision/tolerance mismatch, `uncertainty_measure_with_unit` errors, geometric-set tolerance issues, snap-to-grid artefacts, near-zero magnitudes, and other floating-point-precision corner cases.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.4) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [N001](N001.stp) | Vertex `UNCERTAINTY_MEASURE_WITH_UNIT` larger than edge / face value (tolerance hierarchy violation) |
| [N002](N002.stp) | Wireframe gap-fix inflates tolerance instead of bridging the gap |
| [N003](N003.stp) | Same-domain face merge inflates shared-vertex tolerance to worst input |
| [N004](N004.stp) | Edge same-parameter flag asserted but 3D curve and pcurve disagree at sampled parameters (`SameParameter=.T.` lie) |
| [N005](N005.stp) | Splitting a closed periodic face leaves new edges with reversed pcurve vs 3D curve parameterisation |
| [N006](N006.stp) | Pcurve drifts out of sync with 3D-curve parameterisation (geometric flavour) |
| [N007](N007.stp) | Vertex tolerance bump factor hard-coded `1.000001 *` on disagreement |
| [N008](N008.stp) | Vertex tolerance inflation by repeated self-intersection healing cascades |
| [N009](N009.stp) | Vertex 3D point lies far from incident-edge curve endpoints (dispersion exceeds tolerance) |
| [N010](N010.stp) | `EDGE_CURVE` shorter than vertex tolerance (tiny edge covered by vertices, `distance_accuracy` exceeds edge length) |
| [N011](N011.stp) | Seam edge inserted inside an existing vertex tolerance ball produces zero-length edge |
| [N012](N012.stp) | Setting face tolerance to a tiny value then ShapeFix produces vertex/vertex intersections |
| [N013](N013.stp) | Boolean cascade vertex deviation (independently computed pairwise intersections) |
| [N014](N014.stp) | Spurious tiny `EDGE_CURVE` that should have collapsed: vertex separation below declared tolerance |
| [N015](N015.stp) | `xstep.cascade.unit M` meters setting inflates tolerance and corrupts geometry |
| [N016](N016.stp) | Edge tolerance 2-3 orders of magnitude > file tolerance (CATIA per-edge precision) |
| [N017](N017.stp) | `UNCERTAINTY_MEASURE_WITH_UNIT` populated with a fixed field-default value (untrustworthy) |
| [N018](N018.stp) | `GEOMETRIC_REPRESENTATION_CONTEXT` missing `GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT` leaf → fall back to read.precision |
| [N019](N019.stp) | `OFFSET_SURFACE` with sub-tolerance offset (fixed-tolerance importer hard-codes 1e-3) |
| [N020](N020.stp) | Coordinate-system origin offset: hard-coded BOARD_OFFSET 0.05mm in PCB→MCAD pipeline |
| [N021](N021.stp) | VRML/STEP origin convention mismatch within same producer |
| [N023](N023.stp) | `EDGE_CURVE` based on `LINE` displaced from true vertex position |
| [N024](N024.stp) | `EDGE_CURVE` 3D `LINE` stale relative to translated host `PLANE` (rebuild-edge case) |
| [N025](N025.stp) | Coincident-but-not-shared vertices/edges (cross-translator round-off) |
| [N026](N026.stp) | Cross-kernel topology rejection: source-valid, target-invalid by tolerance bookkeeping |
| [N027](N027.stp) | Small-mm `CYLINDRICAL_SURFACE` with target-unit mismatch (gmsh `OCCTargetUnit` silently ignored on `importShapesNativePointer` path) |
| [N028](N028.stp) | `GEOMETRIC_REPRESENTATION_CONTEXT` missing `LENGTH_UNIT` (only angle units present) → user-configured cascade.unit ignored |
| [N029](N029.stp) | Inch-units silent treatment as mm (25.4× scale error) |
| [N030](N030.stp) | Quarter `CYLINDRICAL_SURFACE` stored as `B_SPLINE_SURFACE_WITH_KNOTS` (canonical recognition tolerance budget) |
| [N031](N031.stp) | Surface discontinuities introduced by translation (G0/G1/G2 break at shared edges) |
| [N032](N032.stp) | Tolerance type entity coverage: AP242 tolerance entities dropped on import |
| [N033](N033.stp) | Tolerance value polymorphic encoding (`MeasureRepresentationItem` vs plain measure) |
| [N034](N034.stp) | `+/-` tolerance bounds inverted, equal, or wrong measure type |
| [N035](N035.stp) | Default tolerance precision: missing decimal-place qualifier |
| [N036](N036.stp) | Centroid validation breaks down when relative threshold goes below modeling tolerance |
| [N037](N037.stp) | Curve gaps between adjacent segments after format conversion (LOTAR exchange defect) |
| [N038](N038.stp) | Patrikalakis interval-solid violation: face-pair gap exceeds bound |
| [N039](N039.stp) | Healing pass over-eagerly inflates tolerances 1000× on sub-shapes that needed no fix (post-fix `UNCERTAINTY_MEASURE_WITH_UNIT` bloat) |
| [N040](N040.stp) | `Limit Tolerance` clamp re-exposes gaps that bloated tolerances were hiding (Salome) |
| [N041](N041.stp) | Manifold ε-validity contract: cumulative transform error inflates ε beyond input scale |
| [N042](N042.stp) | Self-intersecting wire from coarse-discretization bbox check (sample-count too small) |
| [N043](N043.stp) | Shape-to-shape distance reports nonzero gap for clearly intersecting parts |
| [N044](N044.stp) | Persistent IDs lost across editing/translation breaks PMI tolerance attachment |
| [N045](N045.stp) | Vertex tolerance under-checked: edge-internal intersection ignored |
| [N046](N046.stp) | Default tolerance projection wrong on non-default tolerance shapes (free CARTESIAN_POINT off PLANE within declared tolerance but beyond hard-coded internal tolerance) |
| [N047](N047.stp) | Linear and angular tolerance for same-surface face merging not user-specifiable |
| [N048](N048.stp) | Walk-line initial step unrelated to tolerance during surface intersection |
| [N049](N049.stp) | Reading a structurally valid STEP file produces an invalid `TopoDS_Shape` |
| [N050](N050.stp) | File-supplied `UNCERTAINTY_MEASURE_WITH_UNIT` parsed but never consumed (BRL-CAD step-g) |
| [N051](N051.stp) | ShapeAnalysis_ShapeTolerance.InTolerance vertex polarity inversion |
| [N052](N052.stp) | BRepBuilderAPI_Sewing.SameParameterEdge SetMaxTolerance bypass |
| [N053](N053.stp) | ShapeAnalysis_ShapeTolerance.AddTolerance polarity asymmetry |
| [N054](N054.stp) | ShapeFix_Edge.FixVertexTolerance multi-surface underestimation |
| [N055](N055.stp) | ShapeFix_ShapeTolerance.LimitTolerance boundary ambiguity |
| [N056](N056.stp) | ShapeFix_ShapeTolerance.SetTolerance bulk-rewrite |
| [N057](N057.stp) | ShapeAnalysis_ShapeTolerance.GlobalTolerance weight dispatch inversion |
| [N058](N058.stp) | BRepLib.SameRange null-pcurve null-check dereference |
| [N059](N059.stp) | BRepLib.UpdateEdgeTol sampling-grid undersample |
| [N060](N060.stp) | ShapeFix_Edge.FixSameParameter SameParameterEdge upper-bound |
| [N061](N061.stp) | BRepLib.BoundingVertex bounding-sphere under-estimate |
| [N062](N062.stp) | ShapeAnalysis_ShapeTolerance.GlobalTolerance min/max dispatch |
| [N063](N063.stp) | ShapeFix_Edge.FixVertexTolerance escalation cascade |
| [N064](N064.stp) | ShapeAnalysis_Edge.CheckPoints precision asymmetry |
| [N065](N065.stp) | ShapeFix_ShapeTolerance.LimitTolerance partial-tree application |
| [N066](N066.stp) | ShapeAnalysis_ShapeTolerance.OverTolerance >= vs > comparison |
| [N067](N067.stp) | ShapeFix_ShapeTolerance.SetTolerance compound cascade incomplete |
| [N068](N068.stp) | BRepLib.UpdateInnerTolerances minimal 2-point sampling |
| [N069](N069.stp) | ShapeAnalysis_Edge.CheckOverlapping parameter vs arc-length scale |
| [N070](N070.stp) | ShapeFix_ShapeTolerance.LimitTolerance zero lower-bound as no-op marker |
| [N071](N071.stp) | BRepLib.UpdateEdgeTol surface-mesh consistency unchecked |
| [N072](N072.stp) | ShapeFix_Edge.FixSameParameter precision-loss via TempSameRange |
| [N073](N073.stp) | BRepLib.UpdateDeflection null-triangulation skip |
| [N074](N074.stp) | ShapeAnalysis_Edge.CheckPoints colinear-points shortcut |
| [N075](N075.stp) | ShapeFix_ShapeTolerance.SetTolerance vertex-not-in-shape |
| [N076](N076.stp) | ShapeAnalysis_ShapeTolerance.AddTolerance cumulative-mode |
| [N077](N077.stp) | BRepLib.BuildCurves3d batch-batch failure |
| [N078](N078.stp) | ShapeFix_Edge.FixSameParameter precision-floor |
| [N079](N079.stp) | ShapeAnalysis_Edge.CheckPointsAreOnEdges sphere-pole |
| [N080](N080.stp) | ShapeFix_ShapeTolerance.LimitTolerance recursive-only-vertex |
| [N081](N081.stp) | BRepLib.UpdateEdgeTol dual-path divergence |
| [N082](N082.stp) | ShapeAnalysis_ShapeTolerance.AddTolerance shape-type membership |
| [N083](N083.stp) | ShapeFix_ShapeTolerance.SetTolerance compound + nested |
| [N084](N084.stp) | BRepLib.UpdateInnerTolerances degenerate-edge postcondition |
| [N085](N085.stp) | ShapeAnalysis_Edge.CheckPoints precision-asymmetry |
| [N086](N086.stp) | Closed BSpline SameParameter wrapping |
| [N087](N087.stp) | CheckOverlapping parameterization mismatch |
| [N088](N088.stp) | Vertex at cone apex zero tolerance |
| [N089](N089.stp) | LimitTolerance recursion stops at WIRE |
| [N090](N090.stp) | GlobalTolerance weighted mode edge direction bug |
| [N091](N091.stp) | ShapeFix_Edge.FixSameParameter wrong-floor-clamp |
| [N092](N092.stp) | ShapeAnalysis_ShapeTolerance.AddTolerance type-mismatch |
| [N093](N093.stp) | BRepLib.UpdateInnerTolerances on-degenerate-curve |
| [N094](N094.stp) | ShapeFix_Edge.FixVertexTolerance precision-floor |
| [N095](N095.stp) | ShapeAnalysis_Edge.CheckPoints tolerance-aware-distance |
| [N096](N096.stp) | BRepLib.UpdateInnerTolerances cone-apex-singularity |
| [N097](N097.stp) | ShapeFix_ShapeTolerance.LimitTolerance same-min-and-max |
| [N098](N098.stp) | ShapeAnalysis_ShapeTolerance.GlobalTolerance empty-shape |
| [N099](N099.stp) | BRepLib.UpdateEdgeTol multi-face-edge buffer overflow |
| [N100](N100.stp) | ShapeAnalysis_Edge.CheckPoints precision-asymmetry-extreme |
| [N101](N101.stp) | ShapeFix_Edge.FixVertexTolerance reset-on-fix |
| [N102](N102.stp) | ShapeAnalysis_Edge.CheckOverlapping multi-curve three-way overlap |
| [N103](N103.stp) | BRepLib.UpdateEdgeTol negative-coverage sparse sampling |
| [N104](N104.stp) | ShapeFix_ShapeTolerance.SetTolerance applied-to-frozen-shape |
| [N105](N105.stp) | ShapeAnalysis_Edge.CheckOverlapping coincident-but-different-direction |
| [N106](N106.stp) | ShapeFix_Edge.FixVertexTolerance vertex-on-singular-surface |
| [N107](N107.stp) | ShapeAnalysis_ShapeTolerance.AddTolerance with-history |
| [N108](N108.stp) | BRepLib.SameRange clamped-range |
| [N109](N109.stp) | ShapeFix_ShapeTolerance.SetTolerance with-cyclic-reference |
| [N110](N110.stp) | ShapeAnalysis_Edge.CheckPoints precision-vs-projection-distance |
| [N111](N111.stp) | FixVertexTolerance vertex-tolerance-from-tessellation |
| [N112](N112.stp) | CheckOverlapping with-tolerance-zero |
| [N113](N113.stp) | UpdateEdgeTol with-coincident-vertices |
| [N114](N114.stp) | FixSameParameter with-NaN-input |
| [N115](N115.stp) | OverTolerance threshold-equality |
| [N116](N116.stp) | ShapeFix_Edge.FixVertexTolerance shared-by-many-edges |
| [N117](N117.stp) | ShapeAnalysis_Edge.CheckOverlapping mixed-curve-orientation |
| [N118](N118.stp) | BRepLib.UpdateEdgeTol with-pcurve-discontinuity |
| [N119](N119.stp) | ShapeFix_ShapeTolerance.LimitTolerance with-very-large-shape |
| [N120](N120.stp) | ShapeAnalysis_ShapeTolerance.GlobalTolerance averaging-over-empty |
| [N121](N121.stp) | ShapeFix_Edge.FixVertexTolerance with-tessellation-only-context |
| [N122](N122.stp) | ShapeAnalysis_Edge.CheckPoints with-NaN-precision-input |
| [N123](N123.stp) | BRepLib.UpdateEdgeTol with-edge-on-degenerate-surface |
| [N124](N124.stp) | ShapeFix_ShapeTolerance.SetTolerance recursion-stack-overflow |
| [N125](N125.stp) | ShapeAnalysis_ShapeTolerance.AddTolerance concurrent-modification |
| [N126](N126.stp) | ShapeAnalysis_ShapeTolerance.InTolerance vertex-filtering-inverted |
| [N127](N127.stp) | ShapeFix_ShapeTolerance.SetTolerance no-validation-negative-precision |
| [N128](N128.stp) | ShapeFix_ShapeTolerance.LimitTolerance boundary-equality-nondeterminism |
| [N129](N129.stp) | BRep_Tool::Tolerance vertex-null-dereference-risk |
| [N130](N130.stp) | ShapeFix_ShapeTolerance.SetTolerance recursive-double-mutation-shared-vertex |
| [N131](N131.stp) | ShapeAnalysis_ShapeTolerance vertex range inversion |
| [N132](N132.stp) | ShapeFix_ShapeTolerance ambiguous equality bound |
| [N133](N133.stp) | ShapeFix_ShapeTolerance negative precision acceptance |
| [N134](N134.stp) | ShapeFix_ShapeTolerance shared vertex double mutation |
| [N135](N135.stp) | ShapeAnalysis_ShapeTolerance missing face validity check |
| [N136](N136.stp) | ShapeAnalysis_ShapeTolerance.MaxTolerance.unbounded_edge_iteration |
| [N137](N137.stp) | BRepBuilderAPI_Sewing.AnalysisNearestEdges.distance_tolerance_filter_bypass |
| [N138](N138.stp) | ShapeAnalysis_Edge.CheckPoints.tolerance_conservatism_fail |
| [N139](N139.stp) | ShapeAnalysis_ShapeTolerance.OuterWire.tolerance_layer_recursion |
| [N140](N140.stp) | ShapeAnalysis_Surface.Continuity.tolerance_interval_mismatch |
| [N141](N141.stp) | ShapeFix_IntersectionTool.FixIntEdges tolerance_selection |
| [N142](N142.stp) | ShapeUpgrade_ConvertCurve2dToBezier precision-semantics,asymmetric-tolerance |
| [N143](N143.stp) | ShapeUpgrade_RemoveLocations.MakeNewShape null-reference-tolerance |
| [N144](N144.stp) | ShapeUpgrade_UnifySameDomain.UnionPCurves vertex_tolerance_mismatch |
| [N145](N145.stp) | BRepBuilderAPI_Sewing.SameParameterEdge setMaxTolerance-bypass-raw-write |
| [N146](N146.stp) | EvaluateDistances.zero_angle_count_guard |
| [N147](N147.stp) | FindCandidates.acceptance_criteria_composite_filter |
| [N148](N148.stp) | EvaluateDistances.projection_direction_selection |
| [N149](N149.stp) | FindCandidates.equidistant_precision_test |
| [N150](N150.stp) | IsMergedClosed.v_overlap_negativity_test |
| [N151](N151.stp) | `BRepBuilderAPI_Sewing.SameParameterEdge.recursive-tolerance-comparison` |
| [N152](N152.stp) | `BRepBuilderAPI_Sewing.SameParameterEdge.location-transform-in-tolerance-eval` |
| [N153](N153.stp) | `BRepBuilderAPI_Sewing.SameParameterEdge.final-tolerance-validation` |
| [N154](N154.stp) | `ShapeUpgrade_UnifySameDomain.MergeSubSeq.circle_spatial_closure_tolerance` |
| [N155](N155.stp) | `ShapeAnalysis_CheckSmallFace.CheckPin.tolerance-fallback` |
| [N156](N156.stp) | tolerance_asymmetry conflation |
| [N157](N157.stp) | distance_tolerance_filter_second_pass bypass |
| [N158](N158.stp) | location_transform_in_tolerance_eval bypass |
| [N159](N159.stp) | direct_BRep_TEdge_tolerance_write bypass |
| [N160](N160.stp) | ComputeTol overflow_error tolerance corruption |
| [N161](N161.stp) | `tolerance_escalation` — unbounded multiplier |
| [N162](N162.stp) | `tolerance_selection` — coarse fallback unvalidated |
| [N163](N163.stp) | `precision_tolerance` — mixed-unit-scale mismatch |
| [N164](N164.stp) | `tolerance_closure` — EDGE_LOOP gap exceeds threshold |
| [N165](N165.stp) | `tolerance_conservatism` — no safety margin |
| [N166](N166.stp) | InTolerance VERTEX inverted-comparison bug \| ShapeAnalysis_ShapeTolerance \| tolerance \| ShapeAnalysis_ShapeTolerance.InTolerance.vertex_tolerance_filtering_BUGGY \| vertex range filter uses >= instead of <= \| tolerance-regression \| reproducible \| true |
| [N167](N167.stp) | LimitTolerance iamax boundary-condition flip \| ShapeFix_ShapeTolerance \| tolerance \| ShapeFix_ShapeTolerance.LimitTolerance.iamax_logic_flip \| equality check (tmax >= tmin) semantically requires (tmax > tmin), edge case unchecked \| boundary-condition-ambiguity \| reproducible \| true |
| [N168](N168.stp) | LimitTolerance recursive WIRE double-mutation \| ShapeFix_ShapeTolerance \| double-mutation \| ShapeFix_ShapeTolerance.LimitTolerance.recursive_wire_vertices \| shared vertices in wire mutated twice on single call \| double-mutation \| reproducible \| true |
| [N169](N169.stp) | GetTolerance mixed-precision accumulation \| BRep_Tool \| tolerance \| BRep_Tool::GetTolerance \| accumulates vertex/edge tolerances without precision normalization \| precision-tolerance-mismatch \| reproducible \| true |
| [N170](N170.stp) | Sewing unevaluated distance filter bypass \| BRepBuilderAPI_Sewing \| tolerance \| BRepBuilderAPI_Sewing.AnalysisNearestEdges.unevaluated_distance_filter_first_pass \| first-pass distance check bypassed, over-tolerance edges enter candidate pool \| kernel-pair \| reproducible \| true |
| [N171](N171.stp) | Shared CIRCLE basis between EDGE_CURVEs at different scales (radius derivation defect) |
| [N172](N172.stp) | `seq-set-tolerance` "outside acceptable band" clamp, on a live face |
| [N173](N173.stp) | Per-entity vertex-tolerance bumps ACCUMULATE across several edges of one shell (multi-edge tolerance-ceiling clamp) |
| [N174](N174.stp) | `stp-vertex-tol-gap`, displaced-line-with-correct-direction subvariant (PCB/FPX export quirk) |
| [Tb001](Tb001.stp) | Sub-tolerance vertex gap that closes at 1e-3 but yawns open at 1e-7 |
| [Tb002](Tb002.stp) | Sub-tolerance vertex gap that closes at 1e-7 but inflates at 1e-3 |
| [Tb003](Tb003.stp) | Vertex-edge-face tolerance hierarchy holds in mm but inverts in m |
| [Tb004](Tb004.stp) | Vertex-edge-face hierarchy holds in mm but inverts when scaled to inches |
| [Tb005](Tb005.stp) | Face area sub-tolerance squared (`tol*tol` threshold defect) |
| [Tb006](Tb006.stp) | Edge length sub-tolerance squared in 2D pcurve length |
| [Tb007](Tb007.stp) | NURBS knot-difference quantum below tolerance: knot collapses or doesn't |
| [Tb008](Tb008.stp) | NURBS knot-difference quantum scaled by parametric range |
| [Tb009](Tb009.stp) | Self-intersection visible at full precision but rounded out at receiver tolerance |
| [Tb010](Tb010.stp) | Self-intersection that vanishes when round-tripped through float32 |
| [Tb011](Tb011.stp) | Periodic-surface seam matching requires period-relative tolerance |
| [Tb012](Tb012.stp) | Sphere seam matching across pole singularity |
| [Tb013](Tb013.stp) | Coordinate at 1e-300 tests as "near zero" only under denormalized math |
| [Tb014](Tb014.stp) | Sliver triangle whose smallest internal angle is at the hardcoded trigger |
| [Tb015](Tb015.stp) | Sliver edge length at sqrt(tol) — under squared comparison or linear? |
| [Tb016](Tb016.stp) | Tolerance budget exhausted by accumulation across long edge chain |
| [Tb017](Tb017.stp) | Two coincident faces at distance equal to declared tolerance |
| [Tb018](Tb018.stp) | UNCERTAINTY value of exactly zero — no fuzzy compare |
| [Tb019](Tb019.stp) | UNCERTAINTY value of `1.0E-30` — below any sane working precision |
| [Tb020](Tb020.stp) | UNCERTAINTY value of `1.0E+30` — astronomically loose |
| [Tb021](Tb021.stp) | Multiple UNCERTAINTY entries with conflicting values, no labels |
| [Tb022](Tb022.stp) | Tolerance declared in different units than coordinates |
| [Tb023](Tb023.stp) | Coordinates near 1e15 where float64 ULP exceeds declared tolerance |
| [Tb024](Tb024.stp) | STEP labels with IfcShapeAspect have wrong location reference |
