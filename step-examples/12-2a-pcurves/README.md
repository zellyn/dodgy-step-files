# §12.2a — P-curve / 2D parameter-space defects (Gp-prefix)

Pcurve definitional issues: missing pcurves on parametric surfaces, wrong UV domain, pcurve/edge-3D mismatch, periodic-shift defects, degenerate pcurves, missing `representation_item` wiring, and parametric-vs-3D inconsistencies.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.2a) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Gp001](Gp001.stp) | Missing pcurve on edge — only the 3D curve representation is present |
| [Gp002](Gp002.stp) | Pcurve endpoints disagree with edge vertex 3D positions |
| [Gp005](Gp005.stp) | Pcurve with single-pole apex on sphere/cone (singularity) |
| [Gp007](Gp007.stp) | Edge parameter range outside the pcurve's natural domain |
| [Gp008](Gp008.stp) | Pcurve oscillations producing wire-intersector corruption |
| [Gp010](Gp010.stp) | Surface_curve.associated_geometry contains a 3D curve in lieu of pcurve |
| [Gp011](Gp011.stp) | Seam curve with same pcurve referenced twice |
| [Gp012](Gp012.stp) | `SURFACE_CURVE` / seam-curve `associated_geometry` list contains a null `$` entry |
| [Gp013](Gp013.stp) | CATIA "like-seam": two pcurves on same near-closed `B_SPLINE_SURFACE_WITH_KNOTS` |
| [Gp014](Gp014.stp) | Shared pcurve across multiple edges (SYRKO) |
| [Gp015](Gp015.stp) | Pcurve/3D-curve trimming failure ("Trimming of 2D curve failed") |
| [Gp016](Gp016.stp) | Pcurve in shifted/transformed UV frame relative to host surface |
| [Gp018](Gp018.stp) | Pcurve gaps / nearly-duplicate pcurves near periodic boundary after `B_SPLINE_SURFACE` conversion |
| [Gp019](Gp019.stp) | Edge on a composite-surface face is missing per-patch pcurve |
| [Gp020](Gp020.stp) | 2D gap between adjacent edges in wire — pcurves disagree in UV |
| [Gp021](Gp021.stp) | 3D curve and pcurve on same edge disagree about edge location (skewed/off-unit pcurve `LINE`) |
| [Gp022](Gp022.stp) | `EDGE_CURVE` `SameParameter=.T.` asserted but 3D curve and pcurve use different parameterisations (degenerate B-spline pcurve) |
| [Gp023](Gp023.stp) | Point-projection onto trimmed periodic `CYLINDRICAL_SURFACE` returns UV outside trimmed band (pcurve start parameter shifted by period) |
| [Gp024](Gp024.stp) | Pcurve refit after non-uniform scale produces large errors |
| [Gp026](Gp026.stp) | `EDGE_LOOP` contour not closed in UV (Jordan-curve violation across periodic-surface seam) |
| [Gp027](Gp027.stp) | Closed-face splitter leaves new pcurves out of sync with 3D curves on `CYLINDRICAL_SURFACE` |
| [Gp028](Gp028.stp) | Wire crosses periodic-surface seam without an explicit seam edge (pcurve trim range vs vertex angular position mismatch) |
| [Gp029](Gp029.stp) | Period-shift fix on revolved face leaves wire in inconsistent UV band, blocks meshing |
| [Gp030](Gp030.stp) | Bent / polyline-form `B_SPLINE` pcurve from PRO/E IGES requires protective handling |
| [Gp031](Gp031.stp) | Cylinder represented twice as duplicate `CYLINDRICAL_SURFACE` instances loses analytic identity |
| [Gp033](Gp033.stp) | B-spline curve has C0 internal break that downstream tools cannot ingest |
| [Gp034](Gp034.stp) | Composite curve segments do not meet within connectivity tolerance |
| [Gp035](Gp035.stp) | Edge has 3D curve but no pcurve, requiring projection onto host surface |
| [Gp036](Gp036.stp) | Pcurve shifting on non-periodic surface produces wrong result |
| [Gp037](Gp037.stp) | Pcurve projection produces infinite line instead of bounded |
| [Gp038](Gp038.stp) | Vertex 3D point and pcurve do not match within tolerance |
| [Gp039](Gp039.stp) | Pcurve projection unstable on closed B-spline curve |
| [Gp040](Gp040.stp) | Pcurves emitted by default duplicate / contradict the surface 3D curve |
| [Gp041](Gp041.stp) | Sample-point divergence between 3D curve and PCURVE exceeds tolerance. |
| [Gp042](Gp042.stp) | Edge on planar face missing PCURVE despite 3D curve geometry. |
| [Gp043](Gp043.stp) | B-spline PCURVE reversal corrupts knot-vector structure without re-evaluation. |
| [Gp044](Gp044.stp) | Endpoint-bias projection picks wrong candidate when multiple equidistant points exist. |
| [Gp045](Gp045.stp) | Edge copy during SameParameter recomputation inherits stale parameter range when curve is BSpline. |
| [Gp046](Gp046.stp) | ShapeFix_Edge.FixVertexTolerance face-context null underestimates multi-surface tolerance |
| [Gp047](Gp047.stp) | ShapeAnalysis_Edge.CheckPCurveRange parameter-domain mismatch |
| [Gp048](Gp048.stp) | ShapeFix_Edge.FixAddPCurve degenerate-curve at cone apex |
| [Gp049](Gp049.stp) | ShapeAnalysis_Edge.CheckOverlapping arc-length vs parameter-space |
| [Gp050](Gp050.stp) | ShapeFix_Edge.FixSameParameter recursive SameRange |
| [Gp051](Gp051.stp) | ShapeAnalysis_Edge.GetEndTangent2d B-spline endpoint tangent divergence |
| [Gp052](Gp052.stp) | ShapeFix_Edge.FixSameParameter copyedge stale range |
| [Gp053](Gp053.stp) | ShapeAnalysis_Edge.CheckVerticesWithPCurve start vs end asymmetry |
| [Gp054](Gp054.stp) | ShapeFix_Edge.FixReversed2d non-B-spline pcurve |
| [Gp055](Gp055.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve uniformly sampled miss |
| [Gp056](Gp056.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve LOCATION transformation |
| [Gp057](Gp057.stp) | ShapeFix_Edge.FixAddCurve3d trim-aware extension |
| [Gp058](Gp058.stp) | ShapeAnalysis_Edge.CheckPCurveRange degenerate-vertex parameters |
| [Gp059](Gp059.stp) | ShapeFix_Edge.FixSameParameter zero-length edge |
| [Gp060](Gp060.stp) | ShapeAnalysis_Edge.GetEndTangent2d PCURVE-on-closed-surface seam |
| [Gp061](Gp061.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve sample-count threshold |
| [Gp062](Gp062.stp) | ShapeFix_Edge.FixAddPCurve trimmed-surface boundary |
| [Gp063](Gp063.stp) | ShapeAnalysis_Edge.CheckOverlapping bounded-curve trim |
| [Gp064](Gp064.stp) | ShapeFix_Edge.FixRemovePCurve degenerate-on-cone |
| [Gp065](Gp065.stp) | ShapeAnalysis_Edge.GetEndTangent2d POLYLINE variant |
| [Gp066](Gp066.stp) | ShapeFix_Edge.FixSameParameter selection-bias tolerance comparison |
| [Gp067](Gp067.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve trimmed-bspline misclassification |
| [Gp068](Gp068.stp) | ShapeFix_Edge.FixReversed2d circular-curve range |
| [Gp069](Gp069.stp) | ShapeAnalysis_Edge.CheckOverlapping common-sub-pattern miss |
| [Gp070](Gp070.stp) | ShapeFix_Edge.FixVertexTolerance double-update |
| [Gp071](Gp071.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve scaled-host-surface |
| [Gp072](Gp072.stp) | ShapeFix_Edge.FixAddPCurve B-spline projection failure |
| [Gp073](Gp073.stp) | ShapeAnalysis_Edge.CheckSameParameter periodic-domain |
| [Gp074](Gp074.stp) | ShapeFix_Edge.FixSameParameter precision-cliff |
| [Gp075](Gp075.stp) | ShapeAnalysis_Edge.CheckOverlapping with surfaces |
| [Gp076](Gp076.stp) | ShapeFix_Edge.FixAddPCurve periodic-surface-seam |
| [Gp077](Gp077.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve sampling-period-mismatch |
| [Gp078](Gp078.stp) | ShapeFix_Edge.FixSameParameter near-degenerate |
| [Gp079](Gp079.stp) | ShapeAnalysis_Edge.CheckOverlapping degenerate-pcurve |
| [Gp080](Gp080.stp) | ShapeFix_Edge.FixReversed2d offset-curve handling |
| [Gp081](Gp081.stp) | CheckSameParameter periodic-shift normalization |
| [Gp082](Gp082.stp) | FixAddCurve3d trim-domain extension |
| [Gp083](Gp083.stp) | CheckOverlapping period-shifted edges |
| [Gp084](Gp084.stp) | FixSameParameter cone-apex singularity tolerance |
| [Gp085](Gp085.stp) | GetEndTangent2d ellipse derivative asymmetry |
| [Gp086](Gp086.stp) | CheckPCurveRange domain-larger-than-3D |
| [Gp087](Gp087.stp) | FixAddPCurve high-curvature near-tangent |
| [Gp088](Gp088.stp) | CheckSameParameter B-spline parameter shift |
| [Gp089](Gp089.stp) | FixReversed2d trimmed-circle |
| [Gp090](Gp090.stp) | CheckOverlapping spline-vs-line |
| [Gp091](Gp091.stp) | ShapeFix_Edge.FixSameParameter pcurve absent |
| [Gp092](Gp092.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve degenerate-pcurve |
| [Gp093](Gp093.stp) | ShapeFix_Edge.FixAddPCurve construct-on-conical-surface near-apex |
| [Gp094](Gp094.stp) | ShapeAnalysis_Edge.CheckOverlapping curves-tangent-at-endpoint |
| [Gp095](Gp095.stp) | ShapeFix_Edge.FixVertexTolerance face-vertex-conflict |
| [Gp096](Gp096.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve direction-reversed-but-coincident |
| [Gp097](Gp097.stp) | ShapeFix_Edge.FixAddPCurve composite-curve-on-surface |
| [Gp098](Gp098.stp) | ShapeAnalysis_Edge.CheckOverlapping arc-tangent-to-line |
| [Gp099](Gp099.stp) | ShapeFix_Edge.FixSameParameter very-long-edge |
| [Gp100](Gp100.stp) | ShapeAnalysis_Edge.GetEndTangent2d POLYLINE first-point |
| [Gp101](Gp101.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve sample-skip near-endpoint |
| [Gp102](Gp102.stp) | ShapeFix_Edge.FixAddPCurve toroidal projection |
| [Gp103](Gp103.stp) | ShapeAnalysis_Edge.CheckPCurveRange CIRCLE-vs-trim-mismatch |
| [Gp104](Gp104.stp) | ShapeFix_Edge.FixSameParameter offset-curve-3d |
| [Gp105](Gp105.stp) | ShapeAnalysis_Edge.CheckOverlapping zero-tolerance-overlap |
| [Gp106](Gp106.stp) | CheckSameParameter spline-vs-spline-shifted |
| [Gp107](Gp107.stp) | FixSameParameter degenerate-on-spline |
| [Gp108](Gp108.stp) | CheckPCurveRange B-spline-out-of-knot |
| [Gp109](Gp109.stp) | FixReversed2d composite-pcurve |
| [Gp110](Gp110.stp) | GetEndTangent2d zero-derivative |
| [Gp111](Gp111.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve different-trim-ranges |
| [Gp112](Gp112.stp) | ShapeFix_Edge.FixAddPCurve scaled-surface |
| [Gp113](Gp113.stp) | ShapeAnalysis_Edge.CheckOverlapping different-curves-same-geometry |
| [Gp114](Gp114.stp) | ShapeFix_Edge.FixSameParameter periodic-curve-with-non-periodic-pcurve |
| [Gp115](Gp115.stp) | ShapeAnalysis_Edge.GetEndTangent2d tangent-mid-knot |
| [Gp116](Gp116.stp) | Sphere pole singularity in pcurve |
| [Gp117](Gp117.stp) | Closed pcurve, open 3D curve mismatch |
| [Gp118](Gp118.stp) | Very-many-samples high-curvature edge |
| [Gp119](Gp119.stp) | Cylinder seam-edge pcurve ambiguity |
| [Gp120](Gp120.stp) | Composite pcurve tangent discontinuity |
| [Gp121](Gp121.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve OFFSET_CURVE |
| [Gp122](Gp122.stp) | ShapeFix_Edge.FixAddPCurve B-spline-on-trimmed-surface |
| [Gp123](Gp123.stp) | ShapeAnalysis_Edge.CheckPCurveRange CIRCLE with-large-radius |
| [Gp124](Gp124.stp) | ShapeFix_Edge.FixReversed2d HYPERBOLA |
| [Gp125](Gp125.stp) | ShapeAnalysis_Edge.GetEndTangent2d at-trim-boundary |
| [Gp126](Gp126.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve plane-projection mismatch |
| [Gp127](Gp127.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve missing P-curve (FAIL1) |
| [Gp128](Gp128.stp) | ShapeFix_Edge.FixAddPCurve transform surface down_cast failure |
| [Gp129](Gp129.stp) | ShapeAnalysis_Curve.Project degenerate-curve NaN |
| [Gp130](Gp130.stp) | ShapeFix_Edge.FixSameParameter B-spline parameter range mismatch |
| [Gp131](Gp131.stp) | Confusion tolerance fallback downgrades precision |
| [Gp132](Gp132.stp) | PCurve projection tolerance escalation unchecked |
| [Gp133](Gp133.stp) | FixSameParameter scope ambiguity on non-SameRange edges |
| [Gp134](Gp134.stp) | BoundedCurve endpoint distance early return bias |
| [Gp135](Gp135.stp) | FixSameParameter copyedge range divergence |
| [Gp136](Gp136.stp) | ShapeFix_Edge.FixRemovePCurve.orphan_pcurves |
| [Gp137](Gp137.stp) | ShapeFix_Face.FixMissingSeam.pcurve-translation-period-sync |
| [Gp138](Gp138.stp) | ShapeFix_IntersectionTool.SplitEdge2.pcurve-endpoint-detection |
| [Gp139](Gp139.stp) | BRepBuilderAPI_Sewing.SameParameterEdge.seam-dual-pcurve-extraction |
| [Gp140](Gp140.stp) | ShapeFix_ComposeShell.SplitByLine.pcurve-missing-skip |
| [Gp141](Gp141.stp) | Missing PCurve Extraction Failure |
| [Gp142](Gp142.stp) | Negligible Parameter Delta Precision Loss |
| [Gp143](Gp143.stp) | Endpoint Tangent from Interior Point Fallback |
| [Gp144](Gp144.stp) | Asymmetric Start Tangent Forward Difference |
| [Gp145](Gp145.stp) | Zero Magnitude Tangent from Flat Section |
| [Gp146](Gp146.stp) | D1 derivative zero; falls back to D2 second derivative |
| [Gp147](Gp147.stp) | D2 second derivative zero; falls back to D3 third derivative |
| [Gp148](Gp148.stp) | D3 third derivative zero; falls back to line endpoints |
| [Gp149](Gp149.stp) | Straight-line tangent magnitude zero; complete tangent degeneracy |
| [Gp150](Gp150.stp) | Edge orientation reversal negates computed tangent post-computation |
| [Gp151](Gp151.stp) | ShapeAnalysis_Edge.CheckPCurveRange periodic_range_semantics |
| [Gp152](Gp152.stp) | ShapeAnalysis_Edge.CheckVerticesWithPCurve location_transformation_semantics |
| [Gp153](Gp153.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve planar_surface_bypass |
| [Gp154](Gp154.stp) | ShapeAnalysis_Edge.CheckVerticesWithPCurve selective_vertex_checking |
| [Gp155](Gp155.stp) | ShapeAnalysis_Edge.CheckCurve3dWithPCurve pcurve_extraction_failure |
| [Gp156](Gp156.stp) | ShapeAnalysis_Edge.GetEndTangent2d `parameter_degeneracy_precision` |
| [Gp157](Gp157.stp) | ShapeAnalysis_Surface.ProjectDegenerated `lazy-singularity-init` |
| [Gp158](Gp158.stp) | ShapeAnalysis_Surface.ProjectDegenerated `whole-edge-degenerate` |
| [Gp159](Gp159.stp) | ShapeAnalysis_Surface.ProjectDegenerated `partial-edge-collapse` |
| [Gp160](Gp160.stp) | ShapeAnalysis_Surface.ProjectDegenerated `singularity-tolerance-threshold` |
| [Gp161](Gp161.stp) | seam_detection_1843 |
| [Gp162](Gp162.stp) | line_circle_reparametrization_2106 |
| [Gp163](Gp163.stp) | circle_parameter_1930 |
| [Gp164](Gp164.stp) | range_mismatch_2055 |
| [Gp165](Gp165.stp) | vertex_tolerance_mismatch_1971 |
| [Gp166](Gp166.stp) | `ProjectDegenerated.whole-edge-degenerate` |
| [Gp167](Gp167.stp) | `ProjectDegenerated.partial-edge-collapse` |
| [Gp168](Gp168.stp) | `ProjectDegenerated.lazy-compute` |
| [Gp169](Gp169.stp) | `ProjectDegenerated.dual-distance-logic` |
| [Gp170](Gp170.stp) | `ProjectDegenerated.iso-flag-unvalidated` |
| [Gp171](Gp171.stp) | Full-circle `CIRCLE` `EDGE_CURVE` with two near-coincident but distinct `VERTEX_POINT`s |
| [Gp172](Gp172.stp) | `PCURVE.basis_surface` referencing the wrong (adjacent) `ADVANCED_FACE` surface |
| [Gp173](Gp173.stp) | General (non-analytic) `B_SPLINE_CURVE_WITH_KNOTS` 3D edge on a `SPHERICAL_SURFACE` forcing the sampled pcurve-projection fallback |
| [Gp175](Gp175.stp) | Missing pcurve on one edge of an otherwise-healthy closed 4-edge wire (crash-free isolation of Gp001/Gp042) |
| [Gp176](Gp176.stp) | `COMPOSITE_CURVE` segment list out of connected geometric order (segment 2 before segment 1) |
| [Gp177](Gp177.stp) | Edge's interior 3D curve passes directly over a sphere pole, strictly between its endpoints |
| [Gp178](Gp178.stp) | Contour wrapping both a degenerated pole and the periodic seam, missing half its seam pcurve pair |
| [Gp179](Gp179.stp) | 3D-curve endpoint disagrees with vertex position beyond tolerance; pcurve is trustworthy (`FixRemoveCurve3d` mirror of Gp064) |
| [Gp180](Gp180.stp) | 2D pcurve knot vector with a near-zero-length span after Bezier decomposition (2D-curve sibling of Gn042) |
| [Gp181](Gp181.stp) | CATIA-style near-closed non-periodic B-spline seam-like edge, mirrored onto the V direction (Gp013 is the U-direction original) |
| [Gp182](Gp182.stp) | CATIA-style seam-like edge (two pcurves on one surface) on a non-B-spline (`CYLINDRICAL_SURFACE`) base |
| [Gp183](Gp183.stp) | Edge `same_range` flag claims parametric agreement that does not hold, face-hosted (`bc-invalid-same-range-flag`, PARTIAL) |
| [Gp184](Gp184.stp) | 3D B-spline curve with a genuine C0 interior knot, reachable in a live face (`seq-split-continuity`, PARTIAL, missing 1 of 3: curve subvariant) |
| [Gp185](Gp185.stp) | Pcurve winds multiple full periods of a closed surface (`seq-xsalgo-pcurve-consistency`, PARTIAL, missing 1 of 3: multi-period subvariant) |
| [Gp186](Gp186.stp) | Two pcurve-bearing edges actually merged by sewing, reversed contributor with a 4x parameter-domain mismatch (`sew-pcurve-domain-reconciliation`, PARTIAL) |
| [Gp187](Gp187.stp) | Ill-conditioned (highly non-uniform) pcurve knot spacing (`sew-pcurve-parameter-desync-repair`, PARTIAL, subvariant: arc-length reparametrization trigger) |
| [Gp188](Gp188.stp) | Second independent COMPOSITE_CURVE with a genuine closure-seam connectivity gap (`stp-compcurve-disconnected`, PARTIAL, single-fixture-thin) |
| [Gp189](Gp189.stp) | EDGE_CURVE's associated_geometry lists a PCURVE that itself fails to translate, not a null slot (`stp-missing-pcurve-projection`, PARTIAL, missing 1 of 2) |
| [Gp190](Gp190.stp) | CATIA-style pseudo-seam split ACROSS TWO DIFFERENT FACES (IsLikeSeam's cross-wire domain) |
| [Gp191](Gp191.stp) | Pcurve whose 2D trim parameters literally collapse to a point (w1==w2) on a real, non-degenerate 3D edge |
| [Gp192](Gp192.stp) | Pcurve range straddles a U-periodic surface's seam in the wrong order (w1>w2) |
