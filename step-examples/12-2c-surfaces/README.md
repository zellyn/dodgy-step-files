# §12.2c — Surface & curve degeneracy defects (Gs-prefix)

Surface/curve geometric degeneracies: zero-radius cylinders/cones/spheres, self-intersecting surfaces, degenerate elementary curves, sweep/extrusion direction issues, axis-placement defects, and other low-level geometric pathologies.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.2c) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Gb001](Gb001.stp) | Curve approximation cannot meet the requested tolerance |
| [Gb002](Gb002.stp) | Surface tangent / normal undefined at a parameter (LProp_Status.Undefined) |
| [Gb003](Gb003.stp) | Closed B-spline curve has reversed end-tangent |
| [Gb004](Gb004.stp) | Pcurve and 3D curve disagree by a measurable distance (CheckCurveOnSurface) |
| [Gs001](Gs001.stp) | TOROIDAL_SURFACE with negative MajorRadius (SolidWorks/Pro-E orientation marker) |
| [Gs002](Gs002.stp) | Degenerate (lemon/apple) torus where minor_radius >= major_radius |
| [Gs005](Gs005.stp) | Surface periodicity not declared but actually closed |
| [Gs006](Gs006.stp) | Surface singularities (degenerate poles) not in declared form |
| [Gs007](Gs007.stp) | Pcurve U coordinate outside canonical [0, 2π) seam range on `CYLINDRICAL_SURFACE` (whole wire off by period) |
| [Gs009](Gs009.stp) | Self-intersecting / figure-eight `EDGE_LOOP` wire on planar face (non-simple polygon) |
| [Gs010](Gs010.stp) | Self-intersecting / folded `B_SPLINE_SURFACE_WITH_KNOTS` (Jacobian sign change, transposed interior rows) |
| [Gs011](Gs011.stp) | Crossed-trim `EDGE_LOOP` with non-shared diagonals (mesh-derived BRep, STL→STEP) |
| [Gs012](Gs012.stp) | Non-simple `EDGE_LOOP` (face boundary self-crosses in UV: bow-tie quadrilateral) |
| [Gs014](Gs014.stp) | Zero-area / sliver / degenerate `ADVANCED_FACE` (sliver, spot, strip, pin; tiny aspect-ratio rectangle) |
| [Gs015](Gs015.stp) | Sliver face (high aspect ratio, two long edges within tolerance) |
| [Gs018](Gs018.stp) | Mismatched orientation of 3D curve and pcurve |
| [Gs019](Gs019.stp) | Pcurves shifted by integer period on closed surface |
| [Gs021](Gs021.stp) | Line displaced from true position (FPX Expert PCB) |
| [Gs024](Gs024.stp) | Round-trip planar face becomes trimmed B-spline (degree-1 NURBS) |
| [Gs025](Gs025.stp) | `B_SPLINE_CURVE_WITH_KNOTS` C0 cusp / kink at interior knot of full multiplicity (C1 expected) |
| [Gs026](Gs026.stp) | Helix on `CYLINDRICAL_SURFACE` mis-projected: pcurve missing or BSpline-approximated (analytic line lost) |
| [Gs028](Gs028.stp) | Pseudo-seam edge: `SURFACE_CURVE` claims `PCURVE_S1_AND_S2` but lists same pcurve twice |
| [Gs029](Gs029.stp) | Curve with last < first parameter range |
| [Gs030](Gs030.stp) | Edge geometry inconsistent with adjacent faces' actual intersection |
| [Gs031](Gs031.stp) | `ADVANCED_FACE` with two `FACE_OUTER_BOUND` entries (duplicated outer contour, overlapping pcurves) |
| [Gs032](Gs032.stp) | Surface-of-linear-extrusion whose direction is parallel to its basis line |
| [Gs033](Gs033.stp) | Trim curves on `TOROIDAL_SURFACE` / NURBS produce jagged tessellation borders (`TRIMMED_CURVE` on `ELLIPSE` pcurve) |
| [Gs034](Gs034.stp) | Twisted / pinched / vertex-split face: `EDGE_LOOP` revisits a shared vertex (Möbius-cell pathology) |
| [Gs035](Gs035.stp) | Composite curve segment with null `parent_curve` |
| [Gs036](Gs036.stp) | Negative-radius / zero-magnitude direction or vector |
| [Gs037](Gs037.stp) | Offset of a surface-of-linear-extrusion fails iso-curve evaluation |
| [Gs038](Gs038.stp) | Pcurve U/V parameter has large jump near periodic boundary on BSpline |
| [Gs039](Gs039.stp) | Helical sweep / variable-radius blend silently emitted as incomplete shell (cap-only face on `SPHERICAL_SURFACE` with `VERTEX_LOOP` bound) |
| [Gs040](Gs040.stp) | High-curvature curve / cusp from NURBS knot insertion |
| [Gs041](Gs041.stp) | `RECTANGULAR_COMPOSITE_SURFACE` with non-uniform patch grid |
| [Gs042](Gs042.stp) | `CURVE_BOUNDED_SURFACE` with self-intersecting (bowtie) boundary |
| [Gs043](Gs043.stp) | `OFFSET_CURVE_3D` with `ref_distance` equal to the basis curve's radius of curvature (collapse) |
| [Gs044](Gs044.stp) | `INTERSECTION_CURVE` between two surfaces with multiple disjoint intersection branches, only one represented |
| [Gs045](Gs045.stp) | `SURFACE_OF_REVOLUTION` whose revolution axis crosses the basis curve at an interior point |
| [Gs046](Gs046.stp) | `SURFACE_OF_LINEAR_EXTRUSION` with zero-magnitude extrusion vector |
| [Gs047](Gs047.stp) | `BLENDED_EDGE_SURFACE` with mismatched fillet radii at a shared vertex |
| [Gs048](Gs048.stp) | `OFFSET_CURVE_2D` with sign of `ref_distance` flipping mid composite-curve chain |
| [Gs049](Gs049.stp) | B-spline surface has C0 isoparametric line that triggers split-on-import |
| [Gs050](Gs050.stp) | Toroidal surface stored incorrectly: major / minor swapped |
| [Gs051](Gs051.stp) | Sphere/cylinder cut produces wrong pcurves on second seam |
| [Gs052](Gs052.stp) | Surface of revolution with offset basis curve breaks on export |
| [Gs053](Gs053.stp) | Scaled sphere as B-spline approximation broken on export |
| [Gs054](Gs054.stp) | Composite curve segment self-cyclic to its containing composite |
| [Gs055](Gs055.stp) | Composite curve segment with infinite trim parameters |
| [Gs056](Gs056.stp) | `SURFACE_OF_REVOLUTION` of an ellipse around its own centre produces a degenerate surface |
| [Gs057](Gs057.stp) | `RECTANGULAR_COMPOSITE_SURFACE` LoadONBrep stub (BRL-CAD step-g) |
| [Gs058](Gs058.stp) | `SURFACE_PATCH` `transition_code` / `u_sense` / `v_sense` parsed but ignored (BRL-CAD step-g) |
| [Gs059](Gs059.stp) | B-spline knot-multiplicity closure sanity |
| [Gs060](Gs060.stp) | Spherical surface pole singularity detection |
| [Gs061](Gs061.stp) | B-spline surface normal degeneracy at cusp |
| [Gs062](Gs062.stp) | Trimmed cylinder ValueOfUV dispatch |
| [Gs063](Gs063.stp) | Trimmed offset surface Bezier delegation |
| [Gs064](Gs064.stp) | ShapeAnalysis_Surface.IsVClosed midpoint sampling on torus |
| [Gs065](Gs065.stp) | ShapeAnalysis_Surface.ValueOfUV near-tangent surface |
| [Gs066](Gs066.stp) | ShapeAnalysis_Surface.SortSingularities cone vs cylinder differing singularities |
| [Gs067](Gs067.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis offset surface with negative distance |
| [Gs068](Gs068.stp) | ShapeAnalysis_Surface.UVFromIso boundary U-iso failure |
| [Gs069](Gs069.stp) | ShapeAnalysis_Surface.IsDegenerated zero-length axis |
| [Gs070](Gs070.stp) | ShapeUpgrade_SplitSurfaceContinuity.Compute trimmed-fallback |
| [Gs071](Gs071.stp) | ShapeAnalysis_Surface.ProjectDegenerated even-redistribution |
| [Gs072](Gs072.stp) | ShapeAnalysis_Surface.ValueOfUV bounded surface Newton overflow |
| [Gs073](Gs073.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis plane-approximation thin patch |
| [Gs074](Gs074.stp) | Plane Singularity Misclassification |
| [Gs075](Gs075.stp) | Cylindrical Surface Seam-Aware Split |
| [Gs076](Gs076.stp) | Newton Fallback Comparison Bias |
| [Gs077](Gs077.stp) | Newton Discriminant Near-Zero Abort |
| [Gs078](Gs078.stp) | Offset-of-Offset Sign Error |
| [Gs079](Gs079.stp) | ShapeAnalysis_Surface.UVFromIso periodic reset |
| [Gs080](Gs080.stp) | ShapeUpgrade_FaceDivide.SplitSurface boundary-merge |
| [Gs081](Gs081.stp) | ShapeAnalysis_Surface.IsUClosed extrusion-base form |
| [Gs082](Gs082.stp) | ShapeAnalysis_Surface.NextValueOfUV curvature step-size |
| [Gs083](Gs083.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis quasi-uniform vs non-uniform mismatch |
| [Gs084](Gs084.stp) | ShapeAnalysis_Surface.IsDegenerated bounded-surface zero-area |
| [Gs085](Gs085.stp) | ShapeUpgrade_SplitSurfaceContinuity.Compute criterion-elevation offset |
| [Gs086](Gs086.stp) | ShapeAnalysis_Surface.Singularity boundary singularity |
| [Gs087](Gs087.stp) | ShapeAnalysis_Surface.ComputeBoundIsos cache-stale |
| [Gs088](Gs088.stp) | ShapeUpgrade_FaceDivide.SplitSurface periodic |
| [Gs089](Gs089.stp) | ShapeAnalysis_Surface.UVFromIso B-spline midspan failure |
| [Gs090](Gs090.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis thin-patch elimination threshold |
| [Gs091](Gs091.stp) | ShapeAnalysis_Surface.IsUClosed B-spline rational weights |
| [Gs092](Gs092.stp) | ShapeAnalysis_Surface.ComputeBoundIsos extrusion-direction reset |
| [Gs093](Gs093.stp) | ShapeUpgrade_SplitSurface BSpline irregular knots |
| [Gs094](Gs094.stp) | ShapeAnalysis_Surface.UVFromIso parameter-clamp underflow |
| [Gs095](Gs095.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis sphere |
| [Gs096](Gs096.stp) | ShapeAnalysis_Surface.ComputeSingularities torus pinch |
| [Gs097](Gs097.stp) | ShapeUpgrade_FaceDivideArea.Perform threshold reset |
| [Gs098](Gs098.stp) | ShapeAnalysis_Surface.IsDegenerated revolution-axis-on-curve |
| [Gs099](Gs099.stp) | Sphere pole singularity: iso-curve sampling misses pole |
| [Gs100](Gs100.stp) | SplitSurface trim-aware split: splits base not trimmed wrapper |
| [Gs101](Gs101.stp) | ShapeAnalysis_Surface.ValueOfUV: antipodal sphere convergence failure |
| [Gs102](Gs102.stp) | ConvertSurfaceToBezierBasis: Bezier passthrough produces re-extracted copy |
| [Gs103](Gs103.stp) | IsUClosed: periodic-vs-closed semantic mismatch |
| [Gs104](Gs104.stp) | SURFACE_OF_REVOLUTION with profile-on-axis |
| [Gs105](Gs105.stp) | FaceDivide crossing-curves defect |
| [Gs106](Gs106.stp) | Concentrated-poles surface with Newton underflow |
| [Gs107](Gs107.stp) | Closed-surface preservation in Bezier conversion |
| [Gs108](Gs108.stp) | Singularity boundary classification error |
| [Gs109](Gs109.stp) | ShapeAnalysis_Surface.UVFromIso v-iso-at-pole |
| [Gs110](Gs110.stp) | ShapeUpgrade_SplitSurface.SetUSplitValues count-mismatch |
| [Gs111](Gs111.stp) | ShapeAnalysis_Surface.IsDegenerated SURFACE_OF_LINEAR_EXTRUSION zero-extrusion |
| [Gs112](Gs112.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis cone-with-trim |
| [Gs113](Gs113.stp) | ShapeAnalysis_Surface.ComputeBoundIsos negative-trim |
| [Gs114](Gs114.stp) | B-spline surface |
| [Gs115](Gs115.stp) | B-spline surface |
| [Gs116](Gs116.stp) | B-spline surface |
| [Gs117](Gs117.stp) | B-spline surface |
| [Gs118](Gs118.stp) | B-spline surface |
| [Gs119](Gs119.stp) | CONICAL_SURFACE with zero radius (degenerate point) |
| [Gs120](Gs120.stp) | FaceDivide splitter curve tangent to boundary (zero-area sub-face) |
| [Gs121](Gs121.stp) | SurfaceNewton trapped in local minimum of distance function |
| [Gs122](Gs122.stp) | Rational B-spline surface with zero weight (degenerate interior) |
| [Gs123](Gs123.stp) | TOROIDAL_SURFACE with major_radius < minor_radius (self-intersecting) |
| [Gs124](Gs124.stp) | B-SPLINE_SURFACE with u_periodic flag but non-coincident poles |
| [Gs125](Gs125.stp) | B-SPLINE_SURFACE with very wide U domain |
| [Gs126](Gs126.stp) | B-SPLINE_SURFACE with high-curvature Newton singularity |
| [Gs127](Gs127.stp) | B-SPLINE_SURFACE with degenerate edge after split |
| [Gs128](Gs128.stp) | TOROIDAL_SURFACE with v-closed property and u-iso wraparound |
| [Gs129](Gs129.stp) | CYLINDRICAL_SURFACE with non-unit radius underflowing tolerance check |
| [Gs130](Gs130.stp) | FACE with trim coincident to existing split edge |
| [Gs131](Gs131.stp) | TOROIDAL_SURFACE with Newton iteration near convergence |
| [Gs132](Gs132.stp) | TOROIDAL_SURFACE wrongly elevated to non-analytic Bezier |
| [Gs133](Gs133.stp) | CYLINDRICAL_SURFACE degenerate edge with sub-optimal projection |
| [Gs134](Gs134.stp) | ShapeAnalysis_Surface.UVFromIso intermediate-bounce |
| [Gs135](Gs135.stp) | ShapeUpgrade_ConvertSurfaceToBezierBasis with-self-intersecting |
| [Gs136](Gs136.stp) | ShapeAnalysis_Surface.Singularity TOROIDAL_SURFACE non-standard-axis |
| [Gs137](Gs137.stp) | ShapeUpgrade_SplitSurface non-axis-aligned-split |
| [Gs138](Gs138.stp) | ShapeAnalysis_Surface.IsDegenerated bounded-surface-with-only-corner-points |
| [Gs139](Gs139.stp) | IsUClosed pole-singularity false positive |
| [Gs140](Gs140.stp) | IsVClosed Bezier pole-coincidence shortcut |
| [Gs141](Gs141.stp) | FixMissingSeam RectangularTrimmedSurface bound mismatch |
| [Gs142](Gs142.stp) | Segment rational-weight singularity |
| [Gs143](Gs143.stp) | MakeBSpline grid-sampling false periodicity |
| [Gs144](Gs144.stp) | ComputeBoxes null-ISO silent skip |
| [Gs145](Gs145.stp) | ProjectDegenerated lazy singularity init |
| [Gs146](Gs146.stp) | SurfaceNewton zero-normal break |
| [Gs147](Gs147.stp) | ValueOfUV projection beyond bound |
| [Gs148](Gs148.stp) | DegeneratedValues singularity gap classification |
| [Gs149](Gs149.stp) | ShapeAnalysis_Surface.IsUVBounded |
| [Gs150](Gs150.stp) | ShapeConstruct_Surface.AdjustByTransformation |
| [Gs151](Gs151.stp) | ShapeFix_Face.FixWireTool |
| [Gs152](Gs152.stp) | ShapeUpgrade_Surface.SplitSurface |
| [Gs153](Gs153.stp) | ShapeAnalysis_Surface.CalcMaxDegree |
| [Gs154](Gs154.stp) | CheckSmall weak tolerance comparison |
| [Gs155](Gs155.stp) | CopyTrimmedSurface uv-param loss |
| [Gs156](Gs156.stp) | EditVertex ordering corruption |
| [Gs157](Gs157.stp) | GetSurfaceType misidentification via precision |
| [Gs158](Gs158.stp) | AddFace null geometry propagation |
| [Gs159](Gs159.stp) | RectangularTrimmedSurface null-basis unwrap |
| [Gs160](Gs160.stp) | GeomAdaptor_Surface offset-surface misclassification |
| [Gs161](Gs161.stp) | Face with null geometric surface |
| [Gs162](Gs162.stp) | Surface C0 in single direction undetected |
| [Gs163](Gs163.stp) | ShapeUpgrade large-pole B-spline threshold |
| [Gs164](Gs164.stp) | BezierSurface pole extraction dispatch |
| [Gs165](Gs165.stp) | OffsetSurface detection and collection mode |
| [Gs166](Gs166.stp) | SurfaceOfRevolution V-closed seam edge gap |
| [Gs167](Gs167.stp) | RectangularTrimmedSurface null basis detection |
| [Gs168](Gs168.stp) | B-spline C0 continuity asymmetric detection |
| [Gs169](Gs169.stp) | ShapeAnalysis_Surface: rational surface knot-unaware sampling gap |
| [Gs170](Gs170.stp) | ShapeAnalysis_Surface: trimmed surface closure validation skip |
| [Gs171](Gs171.stp) | ShapeAnalysis_Surface: surface domain mismatch on projection result |
| [Gs172](Gs172.stp) | ShapeAnalysis_Surface: degenerate surface derivative guard omission |
| [Gs173](Gs173.stp) | ShapeUpgrade_ShapeCopy: offset surface mode coverage validation omission |
| [Gs174](Gs174.stp) | SphericalSurface Pole Singularities |
| [Gs175](Gs175.stp) | ToroidalSurface Dual-Pinch Singularities |
| [Gs176](Gs176.stp) | RectangularTrimmedSurface Null Basis |
| [Gs177](Gs177.stp) | ConicalSurface Apex Singularity |
| [Gs178](Gs178.stp) | OffsetSurface Edge Degeneracy |
| [Gs179](Gs179.stp) | ShapeAnalysis_Surface.BSplineBoundaries rational-knot-sum validation omission |
| [Gs180](Gs180.stp) | ShapeAnalysis_Surface.ComputeBoxes null-knot-vector tolerance handling |
| [Gs181](Gs181.stp) | ShapeConstruct_Surface.ConvertCurveToSurface invalid-basis bypass |
| [Gs182](Gs182.stp) | ShapeUpgrade_Surface.SplitContinuity periodic-knot discontinuity mask |
| [Gs183](Gs183.stp) | ShapeAnalysis_Surface.ComputeSingularities edge-proximity cache-invalidation |
| [Gs184](Gs184.stp) | Two adjacent B-spline surfaces at G1-tangency boundary with tessellation polyline crossing |
| [Gs185](Gs185.stp) | CONICAL_SURFACE EDGE_LOOP incorrectly trimmed — lateral face degenerate |
| [Gs186](Gs186.stp) | SPHERICAL_SURFACE PCURVE V-range [0, π] instead of ISO-10303-42 §4.4.32 standard [-π/2, +π/2] |
| [Gs187](Gs187.stp) | `CONICAL_SURFACE` tessellation null in OCCT 7.8+ (truncated cone frustum, R_bottom=15, R_top=5, height=20) |
| [Gs188](Gs188.stp) | Onshape `SURFACE_OF_REVOLUTION` micro-geometry (radius ≈ 2 μm) faulty self-import topology |
| [Gs189](Gs189.stp) | `SPHERICAL_SURFACE` hemispherical cap with zero-radius `CIRCLE` `EDGE` at pole |
| [Gs190](Gs190.stp) | `TOROIDAL_SURFACE` with `minor_radius` and `major_radius` attribute values swapped |
| [Gs191](Gs191.stp) | Slicer chord-deflection defect on small-radius `B_SPLINE_SURFACE_WITH_KNOTS` |
| [Gs192](Gs192.stp) | OCCT STEP export duplicates `B_SPLINE_SURFACE_WITH_KNOTS` entity instances |
| [Gs193](Gs193.stp) | Fusion 360 → PTC Creo circular chamfer: single 360° `CONICAL_SURFACE` face with internal seam edge |
| [Gs194](Gs194.stp) | `TOROIDAL_SURFACE` face closed in both U and V requires a recursive re-split to fully separate |
| [Gs195](Gs195.stp) | `SURFACE_OF_REVOLUTION` wedge on a closed profile curve exercises the V-only geometric-closure fallback split |
| [Gs196](Gs196.stp) | `CYLINDRICAL_SURFACE` trimmed to within tolerance of a full period forces a half-surface closure probe before splitting |
| [Gs197](Gs197.stp) | `SURFACE_OF_REVOLUTION` whose C0 basis CURVE (not the surface itself) forces a continuity-driven split |
| [Gs198](Gs198.stp) | Geometrically-smooth over-multiplied B-spline surface knot repaired by `RemoveUKnot` instead of split |
| [Gs199](Gs199.stp) | `VERTEX_LOOP` sole bound on a `TOROIDAL_SURFACE` silently discarded (no warning, unlike sphere/plane) |
| [Gs200](Gs200.stp) | V-periodic (tube-direction) seam-pair on a `TOROIDAL_SURFACE` requires sewing-stage merge validation |
| [Gs201](Gs201.stp) | `EDGE_CURVE` vertex parameters fall outside a bounded curve's own definition range, forcing `UpdateParam3d`'s clamp |
| [Gs202](Gs202.stp) | `EDGE_CURVE` vertices swapped relative to an ordinary B-spline curve's own parametrization, forcing `UpdateParam3d`'s curve-reversal fix |
| [Gs203](Gs203.stp) | B-spline curve closed only within 3D tolerance (not formally `.Closed`) forces `UpdateParam3d`'s near-loop wrong-end reinterpretation |
