# §12.2b — NURBS / B-spline defects (Gn-prefix)

B-spline curve and surface defects: knot-vector irregularities, multiplicity mismatches, control-point/weight count errors, degree mismatches, non-rational vs rational issues, periodic/closed flags inconsistencies, and degenerate parameterizations.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.2b) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Gn001](Gn001.stp) | `B_SPLINE_SURFACE_WITH_KNOTS` U knots duplicated without justifying multiplicity |
| [Gn002](Gn002.stp) | RATIONAL_BSPLINE_CURVE / SURFACE with `NbWeights ≠ NbControlPoints` |
| [Gn003](Gn003.stp) | BSpline curve with empty `control_points_list` |
| [Gn004](Gn004.stp) | Complex BSpline surface entity with empty knots/multiplicities |
| [Gn007](Gn007.stp) | Under-sampled `B_SPLINE_CURVE_WITH_KNOTS` for long helical thread (Creo relative-accuracy tessellation) |
| [Gn008](Gn008.stp) | High-curvature curves: knot multiplicity at full degree producing near-cusps |
| [Gn009](Gn009.stp) | High-degree NURBS surface bloat (degree >5, redundant knots) |
| [Gn010](Gn010.stp) | Out-of-range / NaN NURBS control points |
| [Gn011](Gn011.stp) | Excess-degree `B_SPLINE_CURVE_WITH_KNOTS` / `B_SPLINE_SURFACE_WITH_KNOTS` requiring degree restriction |
| [Gn012](Gn012.stp) | C0 BSpline curves should be split into C1+ pieces |
| [Gn013](Gn013.stp) | Convert elementary to BSpline (or back): producer/consumer requires specific form |
| [Gn014](Gn014.stp) | `B_SPLINE_SURFACE_WITH_KNOTS` that fits a `PLANE` / `CYLINDRICAL_SURFACE` / `CONICAL_SURFACE` / `SPHERICAL_SURFACE` / `TOROIDAL_SURFACE` (canonical recognition) |
| [Gn015](Gn015.stp) | Rational `B_SPLINE_SURFACE_WITH_KNOTS` that is actually a `SURFACE_OF_REVOLUTION` (sqrt(2)/2 weights, 360° sweep) |
| [Gn016](Gn016.stp) | `SURFACE_OF_REVOLUTION` on `ELLIPSE`: basis curve becomes `TRIMMED_CURVE` over rational B-spline plus non-unit axis `DIRECTION` after round-trip |
| [Gn017](Gn017.stp) | `B_SPLINE_SURFACE_WITH_KNOTS` requiring split-at-interior-knots Bezier conversion for legacy export |
| [Gn018](Gn018.stp) | Bezier surface and rational Bezier surface unimplemented (BRL-CAD step-g) |
| [Gn019](Gn019.stp) | Degenerate zero-length `B_SPLINE` pcurve (coincident control points / sample count <2) |
| [Gn020](Gn020.stp) | Spline approximation of analytic primitive (sender philosophy) |
| [Gn021](Gn021.stp) | `OFFSET_SURFACE` of complex BSpline base fails parsing only when wrapped |
| [Gn023](Gn023.stp) | STEP→BREP silently injects new `B_SPLINE_CURVE_WITH_KNOTS` (analytic `CIRCLE` cylinder cap edges replaced) |
| [Gn024](Gn024.stp) | Self-intersecting `B_SPLINE_CURVE_WITH_KNOTS` edge (figure-eight or fold; coincident first/last control points) |
| [Gn025](Gn025.stp) | Folded/non-injective BSpline surface (Jacobian flip) |
| [Gn026](Gn026.stp) | High-degree clamped `B_SPLINE_CURVE_WITH_KNOTS` requiring degree-restriction with continuity guarantee |
| [Gn030](Gn030.stp) | Flat 3D curve as p-curve (instead of 2D PCURVE) |
| [Gn031](Gn031.stp) | `EDGE_CURVE` periodic-to-non-periodic conversion on small-edge export (swapped start/end vertices on tiny-radius rational B-spline arc) |
| [Gn032](Gn032.stp) | Pro/E non-uniform parameter scaling on 2D Geom2dAPI_Interpolate curves |
| [Gn033](Gn033.stp) | Pcurve / 3D-curve large jumps on closed-but-not-periodic `B_SPLINE_SURFACE_WITH_KNOTS` (undeclared `closed_u` seam) |
| [Gn034](Gn034.stp) | B-spline knots packed below parametric resolution |
| [Gn035](Gn035.stp) | Circle translated to NURBS form with rational weights but missing weight metadata |
| [Gn036](Gn036.stp) | `B_SPLINE_SURFACE_WITH_KNOTS` V knot vector strictly descending |
| [Gn037](Gn037.stp) | BSpline curve whose knot vector collapses to a single unique value |
| [Gn038](Gn038.stp) | `BOUNDED_PCURVE` LoadONBrep stub (BRL-CAD step-g) |
| [Gn039](Gn039.stp) | ShapeAnalysis_Curve.IsClosed B-spline near-closure rejection |
| [Gn040](Gn040.stp) | ShapeAnalysis_Curve.FillBndBox S-curve extremum undersample |
| [Gn041](Gn041.stp) | ShapeAnalysis_Surface.NextValueOfUV C0-knot Newton convergence |
| [Gn042](Gn042.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis double-knot thin patch |
| [Gn043](Gn043.stp) | ShapeAnalysis_Curve.GetSamplePoints rational curve 4x amplification |
| [Gn044](Gn044.stp) | ShapeUpgrade_ConvertCurve2dToBezier degree-elevation skip on degree=1 |
| [Gn045](Gn045.stp) | ShapeUpgrade_SplitSurface.Init split-parameters validation out-of-domain |
| [Gn046](Gn046.stp) | ShapeAnalysis_Curve.IsPlanar near-coplanar at tolerance boundary |
| [Gn047](Gn047.stp) | ShapeAnalysis_Curve.GetSamplePoints 2D rational weight-ratio dominance |
| [Gn048](Gn048.stp) | ShapeFix_Edge.FixSameParameter B-spline endpoint knot-multiplicity |
| [Gn049](Gn049.stp) | ShapeAnalysis_Curve.IsClosed parameter-infinite B-spline curve with knot sentinel |
| [Gn050](Gn050.stp) | ShapeUpgrade_SplitSurface.SetUSplitValues empty parameter list |
| [Gn051](Gn051.stp) | ShapeAnalysis_Curve.GetSamplePoints offset/trimmed recursion depth |
| [Gn052](Gn052.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis knot-multiplicity C0 boundary |
| [Gn053](Gn053.stp) | ShapeAnalysis_Curve.IsPlanar weighted BSpline poles threshold false positive |
| [Gn054](Gn054.stp) | ShapeAnalysis_Curve.IsPlanar BSpline dispatch false-negative |
| [Gn055](Gn055.stp) | ShapeUpgrade_SplitSurface knot-spec mismatch on QUASI_UNIFORM |
| [Gn056](Gn056.stp) | ShapeAnalysis_Curve.FillBndBox exact-mode knot-boundary clamping |
| [Gn057](Gn057.stp) | ShapeAnalysis_Curve.GetSamplePoints high-radius full-circle 360K cap |
| [Gn058](Gn058.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis symmetric-knot asymmetric extraction |
| [Gn059](Gn059.stp) | ShapeAnalysis_Curve.FillBndBox SearchForExtremum drift |
| [Gn060](Gn060.stp) | ShapeUpgrade_ConvertCurve2dToBezier loop-variable persistence |
| [Gn061](Gn061.stp) | ShapeAnalysis_Curve.GetSamplePoints (3D 2pt LINE shortcut) |
| [Gn062](Gn062.stp) | ShapeUpgrade_SplitSurface.SetVSplitValues out-of-order |
| [Gn063](Gn063.stp) | ShapeAnalysis_Curve.GetSamplePoints rational pole density |
| [Gn064](Gn064.stp) | ShapeAnalysis_Curve.IsClosed periodic vs closed semantic |
| [Gn065](Gn065.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis BSpline-of-BSpline |
| [Gn066](Gn066.stp) | ShapeAnalysis_Curve.IsPlanar OffsetCurve detection failure |
| [Gn067](Gn067.stp) | ShapeUpgrade_SplitSurface degree mismatch |
| [Gn068](Gn068.stp) | ShapeAnalysis_Curve.FillBndBox elliptic-arc midpoint sampling |
| [Gn069](Gn069.stp) | ShapeAnalysis_Curve.GetSamplePoints BSpline knot-aware sampling |
| [Gn070](Gn070.stp) | ShapeUpgrade_ConvertCurve2dToBezier weight-based delegation |
| [Gn071](Gn071.stp) | ShapeAnalysis_Curve.IsClosed BezierCurve check |
| [Gn072](Gn072.stp) | ShapeUpgrade_SplitSurface explicit-knot-spec mismatch |
| [Gn073](Gn073.stp) | ShapeAnalysis_Curve.FillBndBox composite-curve segment switch |
| [Gn074](Gn074.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis degree truncation |
| [Gn075](Gn075.stp) | ShapeAnalysis_Curve.FillBndBox approximation-mode underestimate |
| [Gn076](Gn076.stp) | ShapeUpgrade_SplitSurface u-multiplicity loss |
| [Gn077](Gn077.stp) | ShapeAnalysis_Curve.IsClosed with self-intersecting direction reversal |
| [Gn078](Gn078.stp) | ShapeUpgrade_ConvertCurve2dToBezier double-degree-elevation knot error |
| [Gn079](Gn079.stp) | ShapeAnalysis_Curve.IsPlanar BSpline interior bow |
| [Gn080](Gn080.stp) | ShapeUpgrade_SplitSurface.SetUSplitValues duplicate dedup |
| [Gn081](Gn081.stp) | ShapeAnalysis_Curve.GetSamplePoints CIRCLE scale-insensitive cap |
| [Gn082](Gn082.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis multi-patch seam drift |
| [Gn083](Gn083.stp) | ShapeAnalysis_Curve.FillBndBox endpoint-bias extremum miss |
| [Gn084](Gn084.stp) | ShapeAnalysis_Curve.IsPlanar tolerance-zero |
| [Gn085](Gn085.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis cylinder-conversion |
| [Gn086](Gn086.stp) | ShapeAnalysis_Curve.GetSamplePoints helix-sampling |
| [Gn087](Gn087.stp) | ShapeUpgrade_SplitSurface.SetUSplitValues neg-zero |
| [Gn088](Gn088.stp) | ShapeAnalysis_Curve.IsClosed B-spline open-via-knots |
| [Gn089](Gn089.stp) | ShapeUpgrade_SplitSurface non-rectangular-region |
| [Gn090](Gn090.stp) | B-spline with 1E100 overflow control point (NaN-proxy) |
| [Gn091](Gn091.stp) | ShapeUpgrade_ConvertCurve2dToBezier endpoint-pole-multiplicity |
| [Gn092](Gn092.stp) | ShapeAnalysis_Curve.GetSamplePoints offset-curve sample-density |
| [Gn093](Gn093.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis u-and-v-knot-asymmetry |
| [Gn094](Gn094.stp) | ShapeAnalysis_Curve.IsClosed degree-0-curve |
| [Gn095](Gn095.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis 1x1-control-grid |
| [Gn096](Gn096.stp) | ShapeAnalysis_Curve.FillBndBox infinite-bbox |
| [Gn097](Gn097.stp) | ShapeUpgrade_SplitSurface.Init duplicate-split-values |
| [Gn098](Gn098.stp) | ShapeAnalysis_Curve.IsPlanar exactly-2-points |
| [Gn099](Gn099.stp) | ShapeAnalysis_Curve.GetSamplePoints conic-arc rational-weight cap |
| [Gn100](Gn100.stp) | ShapeUpgrade_SplitSurface high-multiplicity-clamp |
| [Gn101](Gn101.stp) | ShapeAnalysis_Curve.IsClosed COMPOSITE_CURVE with-discontinuity |
| [Gn102](Gn102.stp) | ShapeUpgrade_ConvertCurve2dToBezier degree-elevation-skip |
| [Gn103](Gn103.stp) | ShapeAnalysis_Curve.FillBndBox bspline-bezier-mixed |
| [Gn104](Gn104.stp) | trimmed-recursion on B-spline |
| [Gn105](Gn105.stp) | rational-with-coincident-poles IsClosed |
| [Gn106](Gn106.stp) | B-spline-of-Bezier conversion bloat |
| [Gn107](Gn107.stp) | approximate-mode B-spline high-frequency |
| [Gn108](Gn108.stp) | Init u_min > u_max inverted bounds |
| [Gn109](Gn109.stp) | ShapeAnalysis_Curve.IsPlanar non-rational-bspline-3D |
| [Gn110](Gn110.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis bezier-with-trim |
| [Gn111](Gn111.stp) | ShapeAnalysis_Curve.GetSamplePoints cubic-with-flat-region |
| [Gn112](Gn112.stp) | ShapeUpgrade_SplitSurface.Init split-at-knot |
| [Gn113](Gn113.stp) | ShapeAnalysis_Curve.IsClosed periodic-with-knot-asymmetry |
| [Gn114](Gn114.stp) | ShapeAnalysis_Curve.IsClosed knot-vector-not-symmetric |
| [Gn115](Gn115.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis non-uniform-degree |
| [Gn116](Gn116.stp) | ShapeAnalysis_Curve.GetSamplePoints near-collinear-poles |
| [Gn117](Gn117.stp) | ShapeUpgrade_SplitSurface with-rational-and-non-rational-mixed |
| [Gn118](Gn118.stp) | ShapeAnalysis_Curve.IsPlanar two-points-and-one-offset |
| [Gn119](Gn119.stp) | ShapeAnalysis_Curve.GetSamplePoints with-clustered-knots |
| [Gn120](Gn120.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis with-clamped-knots-degenerate |
| [Gn121](Gn121.stp) | ShapeAnalysis_Curve.IsPlanar B-spline-of-degree-1 |
| [Gn122](Gn122.stp) | ShapeUpgrade_SplitSurface.Init with-control-net-collapsed |
| [Gn123](Gn123.stp) | ShapeAnalysis_Curve.IsClosed COMPOSITE_CURVE with-direction-reversal |
| [Gn124](Gn124.stp) | ShapeAnalysis_Curve.FillBndBox with-degenerate-segments |
| [Gn125](Gn125.stp) | ShapeUpgrade_SplitSurface.SetVSplitValues partial-domain |
| [Gn126](Gn126.stp) | ShapeAnalysis_Curve.GetSamplePoints CIRCLE with-trim-near-2π |
| [Gn127](Gn127.stp) | ShapeUpgrade_ConvertCurve2dToBezier with-already-bezier |
| [Gn128](Gn128.stp) | ShapeAnalysis_Curve.IsClosed B-spline with-identical-knots-different-poles |
| [Gn129](Gn129.stp) | Geom_BSplineSurface periodic-U-closure weight-extraction |
| [Gn130](Gn130.stp) | ShapeUpgrade_ConvertCurveToBezier non-uniform-knots tail-degenerate |
| [Gn131](Gn131.stp) | ShapeFix_ComposeShell.SplitOnEdges B-spline pcurve tangent-mismatch |
| [Gn132](Gn132.stp) | Geom_BSplineCurve.IncreaseDegree weight-redistribution asymmetry |
| [Gn133](Gn133.stp) | ShapeAnalysis_Curve.CheckOffsetCurve knot-ratio-overflow degenerate-segment |
| [Gn134](Gn134.stp) | NURBS weight array uniform propagation |
| [Gn135](Gn135.stp) | B-spline curve non-uniform interior knots |
| [Gn136](Gn136.stp) | NURBS iterator loop boundary fault in split |
| [Gn137](Gn137.stp) | B-spline curve precision asymmetry in split |
| [Gn138](Gn138.stp) | NURBS trimmed surface Bezier basis delegation |
| [Gn139](Gn139.stp) | TrimmedCurve Wrapping Periodic B-spline |
| [Gn140](Gn140.stp) | U-Periodic Surface with V-Bounds Check Mismatch |
| [Gn141](Gn141.stp) | High V-Multiplicity Continuity Gap |
| [Gn142](Gn142.stp) | Large Pole-Count Surface Sampling Threshold |
| [Gn143](Gn143.stp) | RectangularTrimmedSurface Basis Unwrap Null-Check |
| [Gn144](Gn144.stp) | Periodic knot-vector closure mismatch |
| [Gn145](Gn145.stp) | Interior knot multiplicity C(-1) discontinuity |
| [Gn146](Gn146.stp) | Rational NURBS singular weight |
| [Gn147](Gn147.stp) | Stripe singularity (collapsed pole row) |
| [Gn148](Gn148.stp) | Ill-conditioned knot distribution |
| [Gn149](Gn149.stp) | Rational weight singularity detection |
| [Gn150](Gn150.stp) | Trimmed periodic basis unwrap |
| [Gn151](Gn151.stp) | B-spline C0 interior knot discontinuity |
| [Gn152](Gn152.stp) | Knot ratio anomaly post-C0→C1 upgrade |
| [Gn153](Gn153.stp) | Periodic B-spline origin re-anchor post-upgrade |
| [Gn154](Gn154.stp) | Rational B-spline with zero-weight pole singularity |
| [Gn155](Gn155.stp) | Interior B-spline knot multiplicity equals degree (C1 discontinuity) |
| [Gn156](Gn156.stp) | Periodic B-spline with non-closing control polygon, origin-shift risk |
| [Gn157](Gn157.stp) | Rational B-spline with extreme weight ratio (1e4), numerical conditioning |
| [Gn158](Gn158.stp) | B-spline curve with clustered interior knots, condition-number escalation |
| [Gn159](Gn159.stp) | B-spline surface with collapsed U-boundary pole (pin-face singularity) |
| [Gn160](Gn160.stp) | Periodic B-spline curve with parameter wrapping |
| [Gn161](Gn161.stp) | B-spline surface with asymmetric pole clustering |
| [Gn162](Gn162.stp) | B-spline curve with interior knot over-multiplicity |
| [Gn163](Gn163.stp) | B-spline surface with degenerate patch from split |
| [Gn164](Gn164.stp) | Rational BSpline Closure Detection Bypass |
| [Gn165](Gn165.stp) | Ill-Conditioned Knot Spacing (44:1 Ratio) |
| [Gn166](Gn166.stp) | Boundary Pole Singularity (First Row) |
| [Gn167](Gn167.stp) | Non-Planar Degree-4 BSpline |
| [Gn168](Gn168.stp) | Interior C0 Discontinuity (Tangent Jump) |
| [Gn169](Gn169.stp) | Rational B-spline with weight singularity near origin |
| [Gn170](Gn170.stp) | B-spline surface with extreme knot ratio and clustering |
| [Gn171](Gn171.stp) | Periodic B-spline curve with non-closing control polygon |
| [Gn172](Gn172.stp) | B-spline with interior knot multiplicity equals degree (C0 discontinuity) |
| [Gn173](Gn173.stp) | Rational B-spline surface with extreme pole clustering and weight ratio |
| [Gn174](Gn174.stp) | B-spline surface with extreme aspect-ratio control net (1000:1) causing empty BRepMesh output |
| [Gn175](Gn175.stp) | Gordon surface ill-conditioned guide-curve network (nearly parallel rails, V-extent 0.01 mm) |
| [Gn176](Gn176.stp) | SolidWorks `RECTANGULAR_TRIMMED_SURFACE` with negative NURBS pole weight |
| [Gn177](Gn177.stp) | Genuinely rational `B_SPLINE_SURFACE_WITH_KNOTS` (exact quarter-circle profile) requiring polynomial re-approximation |
| [Gn178](Gn178.stp) | Analytic `CONICAL_SURFACE` requiring `SURFACE_OF_REVOLUTION` representation |
| [Gn179](Gn179.stp) | `SURFACE_OF_REVOLUTION` sweeping a straight generatrix `LINE` recognized as an elementary `CYLINDRICAL_SURFACE` |
