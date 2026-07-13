# §12.3c — Face / sewing / free-bound defects (Tfa-prefix)

Face-level topology defects: missing/wrong face bounds, free-bound usage errors, face-surface mismatches, sewing tolerance failures, advanced-face/oriented-face wrapper issues, and inconsistent face_outer_bound vs face_bound usage.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.3c) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Hea001](Hea001.stp) | Top-level shape-healing pipeline must converge over multi-defect GEOMETRIC_SET (mixed defective ADVANCED_FACE, OPEN_SHELL, free EDGE_LOOP wire) |
| [Hea002](Hea002.stp) | Solid-level healing on MANIFOLD_SOLID_BREP wrapping an OPEN_SHELL (instead of CLOSED_SHELL): iterate shell fixes and re-evaluate closure |
| [Hea003](Hea003.stp) | Free-bound properties pipeline computes area/perimeter/notches together |
| [Hea004](Hea004.stp) | Free-bound contour analysis filters EDGE_LOOPs with sub-precision wiggle vertices (many short sub-segments, deviations below tolerance) |
| [Hea005](Hea005.stp) | Triangular notch detour detected on a free-bound EDGE_LOOP contour (sub-mm vertices break a straight side into 3+ segments) |
| [Hea006](Hea006.stp) | Shape-contents inventory: subshape histogram (e.g., GEOMETRIC_SET counting one ADVANCED_FACE plus one free EDGE_LOOP wire) |
| [Hea007](Hea007.stp) | Transferring parameter values between 3D curve and pcurve when EDGE_CURVE has B_SPLINE_CURVE_WITH_KNOTS in 3D and a LINE pcurve with non-affine reparam |
| [Hea008](Hea008.stp) | Transfer parameters using projection (not affine remapping) |
| [Hea009](Hea009.stp) | Convert curves and surfaces of a shape (e.g., FACE_OUTER_BOUND on a degree-2 B_SPLINE_CURVE_WITH_KNOTS) to Bezier representation |
| [Hea010](Hea010.stp) | Shape-divide pipeline propagates B_SPLINE_SURFACE C0 knot-line splits (e.g., U-knot multiplicity = degree) to topology |
| [Hea011](Hea011.stp) | Shape-healing driver runs a runtime-configured operator sequence over a GEOMETRIC_SET with sub-tolerance EDGE_CURVE, OPEN_SHELL, and same-parameter violation |
| [Hea012](Hea012.stp) | Shape-process operator contract: pluggable healing step over face with scrambled inner FACE_BOUND triangle (near-coincident vertices, edges out of order) |
| [Hea013](Hea013.stp) | User-defined shape-process operator (UOperator) on face with scrambled inner FACE_BOUND triangle (near-coincident vertices, edges out of order) |
| [Hea014](Hea014.stp) | Compound rebuild misses location chain when child SHAPE_REPRESENTATION via REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION at non-identity placement |
| [Hea015](Hea015.stp) | Shape healing regression: shared EDGE_CURVE between two ADVANCED_FACEs on same PLANE has duplicate PCURVE_S1_AND_S2 entries (identical UV start and direction) |
| [Hea016](Hea016.stp) | Empty solid output from STEP export of complex body, despite STL succeeding |
| [Hea017](Hea017.stp) | Extrude of 2D Offset of Sketch fails STEP export as non-manifold (offset trace not closed) |
| [Tfa001](Tfa001.stp) | FACE_SURFACE.face_geometry is null |
| [Tfa002](Tfa002.stp) | Unbound ADVANCED_FACE (no FACE_OUTER_BOUND, no FACE_BOUND) |
| [Tfa003](Tfa003.stp) | FaceOuterBound translation failed (face incomplete without outer wire) |
| [Tfa004](Tfa004.stp) | Missing natural bound on sphere / torus face |
| [Tfa005](Tfa005.stp) | Periodic face given by single belt wire (degenerate pole case) |
| [Tfa006](Tfa006.stp) | Spot face: face collapsed to a point |
| [Tfa007](Tfa007.stp) | Strip face: face one-dimensional within tolerance |
| [Tfa008](Tfa008.stp) | Pin / sliver face |
| [Tfa010](Tfa010.stp) | Splitting vertex within face (vertex of one wire on edge of another) |
| [Tfa011](Tfa011.stp) | `ADVANCED_FACE` with multiple `FACE_OUTER_BOUND` entries (face needs split) |
| [Tfa012](Tfa012.stp) | Face area zero / negative after fixshape |
| [Tfa013](Tfa013.stp) | Face area exceeds limit (needs split) |
| [Tfa014](Tfa014.stp) | Small `ADVANCED_FACE` below area threshold (FixFaceSize) |
| [Tfa015](Tfa015.stp) | DropSmallSolids / debris solids from booleans |
| [Tfa016](Tfa016.stp) | Adjacent faces share same supporting surface (redundant internal edge) |
| [Tfa017](Tfa017.stp) | Same-domain face merge inflates vertex tolerance on the result |
| [Tfa018](Tfa018.stp) | Same-domain face merge across periodic seam: shared `EDGE_CURVE` reused with `.T.`/`.F.` on both halves (missed-seam reconstruction) |
| [Tfa019](Tfa019.stp) | Adjacent `ADVANCED_FACE`s with distinct `VERTEX_POINT`/`EDGE_CURVE` for the same shared boundary (FaceConnect: vertices not shared) |
| [Tfa020](Tfa020.stp) | Sewing — free bounds on closed shell |
| [Tfa022](Tfa022.stp) | Almost-closed `EDGE_LOOP` with sub-tolerance gap and wrong Closed flag (ConnectEdgesToWires) |
| [Tfa023](Tfa023.stp) | STEP file delivers disjoint faces with no shell wrapping (sewing required) |
| [Tfa024](Tfa024.stp) | Glue Faces (coincident faces) |
| [Tfa025](Tfa025.stp) | Glue Edges: duplicate `EDGE_CURVE` instances over duplicated `LINE` / `VERTEX_POINT` entities (coincident edges) |
| [Tfa026](Tfa026.stp) | OFFSET_SURFACE used (out of AP214 scope) |
| [Tfa028](Tfa028.stp) | Full-revolution `CYLINDRICAL_SURFACE` `ADVANCED_FACE` with single seam `EDGE_CURVE` used twice (split_angle: angular span exceeds cap) |
| [Tfa030](Tfa030.stp) | `ADVANCED_FACE` `PLANE` `AXIS2_PLACEMENT_3D` ignored relative to raw-global `CARTESIAN_POINT` bounds (subshape replacement helper drops local placement) |
| [Tfa031](Tfa031.stp) | Locations attached to sub-shapes — instance flattening |
| [Tfa032](Tfa032.stp) | Same-domain face merge introduces overlap / self-intersection on boolean result |
| [Tfa034](Tfa034.stp) | Face orientation flag inconsistent with shell normal (FixFaceOrientation) |
| [Tfa036](Tfa036.stp) | Face on composite surface with boundary crossing patch seams |
| [Tfa037](Tfa037.stp) | Face-level healing pipeline must orchestrate wire/orientation/seam/area sub-fixes (e.g., ADVANCED_FACE with outer rectangle plus a defective inner FACE_INNER_BOUND triangle) |
| [Tfa038](Tfa038.stp) | Face on closed surface lacks outer boundary |
| [Tfa039](Tfa039.stp) | Face has multiple wires that intersect in UV |
| [Tfa040](Tfa040.stp) | Small-face dispatcher orchestrates spot/strip/pin classification (e.g., sub-tolerance ADVANCED_FACE outer loop ~0.001x0.001 mm) |
| [Tfa041](Tfa041.stp) | Spot face: face collapsed to a near-point |
| [Tfa042](Tfa042.stp) | Strip face: face whose width is below tolerance |
| [Tfa043](Tfa043.stp) | Single-face dispatcher: classify-and-heal small face |
| [Tfa044](Tfa044.stp) | Pin face: long thin protrusion at a vertex |
| [Tfa045](Tfa045.stp) | Multiple inner FACE_BOUND wires of an ADVANCED_FACE touch tangentially at a single point (kissing wires sharing a VERTEX_POINT) |
| [Tfa046](Tfa046.stp) | Spot-face diagnostic emits Pnt-located warning before healing (sub-tolerance ADVANCED_FACE outer EDGE_LOOP ~0.001x0.001 mm) |
| [Tfa047](Tfa047.stp) | Single-strip ADVANCED_FACE detection with U/V direction classification (long thin face, e.g., 100 x 0.001 mm rectangle outer EDGE_LOOP) |
| [Tfa048](Tfa048.stp) | Strip face flagged using caller-supplied tolerance |
| [Tfa049](Tfa049.stp) | Pin diagnostic: classify smooth vs sharp vs stretched pin (long thin triangular ADVANCED_FACE outer EDGE_LOOP, e.g., 10mm long with sub-mm width tip) |
| [Tfa050](Tfa050.stp) | Pin face (long thin triangular ADVANCED_FACE) produces edge-correspondence map for healing |
| [Tfa051](Tfa051.stp) | Face needs splitting (knot insertion / sub-faces) for downstream tools |
| [Tfa052](Tfa052.stp) | ADVANCED_FACE split because surface area exceeds threshold (e.g., a 100x100 mm square face must be divided into bounded-area sub-faces) |
| [Tfa053](Tfa053.stp) | Composite-surface patches do not connect on shared boundary |
| [Tfa054](Tfa054.stp) | Face has no underlying surface |
| [Tfa055](Tfa055.stp) | Two distinct wires of one face cross each other in UV |
| [Tfa056](Tfa056.stp) | Face has a redundant wire (wire fully inside another wire of same face) |
| [Tfa057](Tfa057.stp) | Face wire's orientation contradicts the outer/inner role |
| [Tfa058](Tfa058.stp) | Plane-typed face whose vertices are non-coplanar |
| [Tfa059](Tfa059.stp) | Pcurve projection failed: 3D edge curve cannot be lifted onto the host surface |
| [Tfa060](Tfa060.stp) | Shell parametric coverage exceeds host surface bounds |
| [Tfa061](Tfa061.stp) | Sewing of thin faces takes excessive time during seam-edge creation |
| [Tfa062](Tfa062.stp) | Face crash during fix on invalid face — null inner wire |
| [Tfa063](Tfa063.stp) | Stack overflow on `RemoveSmallFaces` due to unbounded recursion |
| [Tfa064](Tfa064.stp) | Missing-seam reconstruction fails on ADVANCED_FACE on CYLINDRICAL_SURFACE whose wire contains a partial seam line plus horizontal CIRCLE arcs |
| [Tfa065](Tfa065.stp) | Healed face uses inflated tolerance instead of original (small gap between adjacent EDGE_LOOP vertices, e.g., 1e-3 mm between V3 and next-edge start) |
| [Tfa066](Tfa066.stp) | Pipe-like face with seam edge wrongly removed as "small" |
| [Tfa067](Tfa067.stp) | Top face dropped after STEP import (CLOSED_SHELL cube whose top FACE_OUTER_BOUND edge has 3D LINE vs B_SPLINE_CURVE_WITH_KNOTS pcurve mismatch) |
| [Tfa068](Tfa068.stp) | STEP export duplicates surfaces, leading to non-conformal geometry between adjacent faces |
| [Tfa069](Tfa069.stp) | Lettering bottoms not closed in exported STEP (text-on-surface non-solid result) |
| [Tfa070](Tfa070.stp) | `CURVE_BOUNDED_SURFACE.implicit_outer = .U.` (unset BOOLEAN) leaves boundary semantics ambiguous (BRL-CAD step-g) |
| [Tfa071](Tfa071.stp) | ShapeFix_Face.FixPeriodicDegenerated apex-curve direction |
| [Tfa072](Tfa072.stp) | ShapeFix_FixSmallFace.ReplaceVerticesInCaseOfSpot coherence |
| [Tfa073](Tfa073.stp) | ShapeFix_FixSmallFace.ComputeSharedEdgeForStripFace asymmetry |
| [Tfa074](Tfa074.stp) | ShapeFix_Face.FixWiresTwoCoincEdges orientation detection |
| [Tfa075](Tfa075.stp) | ShapeFix_ComposeShell.MakeFacesOnPatch fallback resolution |
| [Tfa076](Tfa076.stp) | FixAddNaturalBound seam-edge skip |
| [Tfa077](Tfa077.stp) | FixSmallAreaWire small-area early-exit |
| [Tfa078](Tfa078.stp) | FixLoopWire intersecting-loops merge |
| [Tfa079](Tfa079.stp) | CheckSplittingVertices vertex-on-edge midspan |
| [Tfa080](Tfa080.stp) | CheckTwisted normal-inversion |
| [Tfa081](Tfa081.stp) | ShapeFix_Face.FixOrientation reversed-normal heal |
| [Tfa082](Tfa082.stp) | ShapeAnalysis_CheckSmallFace.CheckPin pin-direction classification |
| [Tfa083](Tfa083.stp) | ShapeFix_Face.FixNotchedEdges near-tangent notch detection |
| [Tfa084](Tfa084.stp) | ShapeAnalysis_FreeBoundsProperties.CheckNotches gap-after-fix |
| [Tfa085](Tfa085.stp) | ShapeFix_Face.FixSplitFace split-result multiplicity |
| [Tfa086](Tfa086.stp) | ShapeFix_Face.FixWiresTwoCoincEdges: 3-edge coincidence |
| [Tfa087](Tfa087.stp) | ShapeAnalysis_CheckSmallFace.CheckStripEdges: aspect-ratio threshold |
| [Tfa088](Tfa088.stp) | ShapeFix_Face.FixAddNaturalBound: sphere natural boundary |
| [Tfa089](Tfa089.stp) | ShapeAnalysis_CheckSmallFace.CheckSpotFace: tolerance scaling |
| [Tfa090](Tfa090.stp) | ShapeFix_Face.Perform: mode-flag ordering |
| [Tfa091](Tfa091.stp) | ShapeFix_Face.FixLoopWire intersecting-loop touch |
| [Tfa092](Tfa092.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted concave-saddle |
| [Tfa093](Tfa093.stp) | ShapeFix_Face.FixSmallAreaWire interior-wire skip |
| [Tfa094](Tfa094.stp) | ShapeAnalysis_CheckSmallFace.CheckSplittingVertices boundary T-vertex |
| [Tfa095](Tfa095.stp) | ShapeFix_Face.FixPeriodicDegenerated SURFACE_OF_REVOLUTION apex |
| [Tfa096](Tfa096.stp) | ShapeFix_Face.FixOrientation degenerate-wire bypass |
| [Tfa097](Tfa097.stp) | ShapeAnalysis_CheckSmallFace.CheckPinFace blunt-pin classification |
| [Tfa098](Tfa098.stp) | ShapeFix_Face.FixSplitFace null-line |
| [Tfa099](Tfa099.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted concave-cone |
| [Tfa100](Tfa100.stp) | ShapeFix_Face.FixWiresTwoCoincEdges with seam |
| [Tfa101](Tfa101.stp) | ShapeFix_Face.FixAddNaturalBound torus complete-surface |
| [Tfa102](Tfa102.stp) | ShapeAnalysis_CheckSmallFace.CheckSmallArea aspect-ratio infinite |
| [Tfa103](Tfa103.stp) | ShapeFix_Face.FixPeriodicDegenerated apex-at-V-min |
| [Tfa104](Tfa104.stp) | ShapeAnalysis_CheckSmallFace.CheckSplittingVertices NM-vertex |
| [Tfa105](Tfa105.stp) | ShapeFix_Face.FixSmallAreaWire seam-aware |
| [Tfa106](Tfa106.stp) | Concentric inner wires (FixLoopWire topology loss) |
| [Tfa107](Tfa107.stp) | High-curvature surface spot detection |
| [Tfa108](Tfa108.stp) | Natural boundary on trimmed surface |
| [Tfa109](Tfa109.stp) | Obtuse-angle pin misclassification |
| [Tfa110](Tfa110.stp) | Single-edge circular wire orientation ambiguity |
| [Tfa111](Tfa111.stp) | ShapeFix_Face.FixSmallAreaWire mixed-context |
| [Tfa112](Tfa112.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted bspline-saddle |
| [Tfa113](Tfa113.stp) | ShapeFix_Face.FixOrientation 8-face polyhedron |
| [Tfa114](Tfa114.stp) | ShapeAnalysis_CheckSmallFace.CheckSpotFace zero-radius |
| [Tfa115](Tfa115.stp) | ShapeFix_Face.FixPeriodicDegenerated revolution-axis edge |
| [Tfa116](Tfa116.stp) | ShapeFix_Face.FixLoopWire concentric circles |
| [Tfa117](Tfa117.stp) | ShapeAnalysis_CheckSmallFace.CheckSplittingVertices vertex-on-degenerate-edge |
| [Tfa118](Tfa118.stp) | ShapeFix_Face.FixSplitFace line-tangent-to-wire |
| [Tfa119](Tfa119.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted opposite-winding-inner-wire |
| [Tfa120](Tfa120.stp) | ShapeFix_Face.FixAddNaturalBound trimmed-conical |
| [Tfa121](Tfa121.stp) | ShapeFix_Face.FixWiresTwoCoincEdges different-host-surfaces |
| [Tfa122](Tfa122.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted self-touching wire |
| [Tfa123](Tfa123.stp) | ShapeFix_Face.FixSmallAreaWire near-collinear edges |
| [Tfa124](Tfa124.stp) | ShapeAnalysis_CheckSmallFace.CheckSpotFace asymmetric |
| [Tfa125](Tfa125.stp) | ShapeFix_Face.FixPeriodicDegenerated u-axis-degenerate |
| [Tfa126](Tfa126.stp) | FixLoopWire: crossing-wires defect |
| [Tfa127](Tfa127.stp) | CheckPin: oversized-pin |
| [Tfa128](Tfa128.stp) | FixOrientation: already-correct |
| [Tfa129](Tfa129.stp) | CheckSplittingVertices: T-vertex at B-spline midpoint |
| [Tfa130](Tfa130.stp) | FixSmallAreaWire: mixed-size-wires |
| [Tfa131](Tfa131.stp) | FixWiresTwoCoincEdges crossing-wires-coincident-segment |
| [Tfa132](Tfa132.stp) | CheckTwisted spline-tangent-discontinuity |
| [Tfa133](Tfa133.stp) | FixOrientation outer-bound-but-inner-correct |
| [Tfa134](Tfa134.stp) | CheckStripFace strip-with-pin |
| [Tfa135](Tfa135.stp) | FixSmallAreaWire chained-removal |
| [Tfa136](Tfa136.stp) | ShapeFix_Face.FixSplitFace splitter-out-of-range |
| [Tfa137](Tfa137.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted face-with-hole |
| [Tfa138](Tfa138.stp) | ShapeFix_Face.FixAddNaturalBound surface-not-closed-but-flagged |
| [Tfa139](Tfa139.stp) | ShapeAnalysis_CheckSmallFace.CheckSpotFace spot-with-internal-pin |
| [Tfa140](Tfa140.stp) | ShapeFix_Face.FixLoopWire wire-with-self-intersection |
| [Tfa141](Tfa141.stp) | ShapeFix_Face.FixWiresTwoCoincEdges B-spline-vs-LINE |
| [Tfa142](Tfa142.stp) | ShapeAnalysis_CheckSmallFace.CheckSmallArea torus-patch |
| [Tfa143](Tfa143.stp) | ShapeFix_Face.FixAddNaturalBound cone-with-apex-in-domain |
| [Tfa144](Tfa144.stp) | ShapeAnalysis_CheckSmallFace.CheckPinFace 3D-vs-parametric-pin |
| [Tfa145](Tfa145.stp) | ShapeFix_Face.FixSplitFace two-splitters |
| [Tfa146](Tfa146.stp) | ShapeFix_Face.FixOrientation parametric-vs-3D-winding |
| [Tfa147](Tfa147.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted face-on-plane |
| [Tfa148](Tfa148.stp) | ShapeFix_Face.FixSmallAreaWire min-area-threshold-collision |
| [Tfa149](Tfa149.stp) | ShapeAnalysis_CheckSmallFace.CheckSplittingVertices wire-not-closed |
| [Tfa150](Tfa150.stp) | ShapeFix_Face.FixPeriodicDegenerated B-spline-revolution |
| [Tfa151](Tfa151.stp) | ShapeFix_Face.FixLoopWire one-inner-touches-outer |
| [Tfa152](Tfa152.stp) | ShapeAnalysis_CheckSmallFace.CheckSpotFace exactly-zero-area |
| [Tfa153](Tfa153.stp) | ShapeFix_Face.FixSmallAreaWire computational-overflow |
| [Tfa154](Tfa154.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted disconnected-wire-region |
| [Tfa155](Tfa155.stp) | ShapeFix_Face.FixOrientation seam-vertex-shared |
| [Tfa156](Tfa156.stp) | ShapeFix_Face.FixSmallAreaWire wire-with-tangent-edges |
| [Tfa157](Tfa157.stp) | ShapeAnalysis_CheckSmallFace.CheckPin extreme-axis-pin |
| [Tfa158](Tfa158.stp) | ShapeFix_Face.FixOrientation closed-shell-context-loss |
| [Tfa159](Tfa159.stp) | ShapeAnalysis_CheckSmallFace.CheckStripFace cylindrical-strip |
| [Tfa160](Tfa160.stp) | ShapeFix_Face.FixWiresTwoCoincEdges loop-inside-loop |
| [Tfa161](Tfa161.stp) | ShapeFix_Face.FixOrientation single-loop-face |
| [Tfa162](Tfa162.stp) | ShapeAnalysis_CheckSmallFace.CheckSpotFace negative-area-detection |
| [Tfa163](Tfa163.stp) | ShapeFix_Face.FixSplitFace splitter-along-edge |
| [Tfa164](Tfa164.stp) | ShapeAnalysis_CheckSmallFace.CheckPin two-pins-on-one-face |
| [Tfa165](Tfa165.stp) | ShapeFix_Face.FixAddNaturalBound subsurface |
| [Tfa166](Tfa166.stp) | ShapeFix_Face.FixSmallAreaWire negative-area-from-orientation |
| [Tfa167](Tfa167.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted mobius-strip-face |
| [Tfa168](Tfa168.stp) | ShapeFix_Face.FixOrientation degenerate-edge-only |
| [Tfa169](Tfa169.stp) | ShapeAnalysis_CheckSmallFace.CheckSplittingVertices vertex-shared-by-many |
| [Tfa170](Tfa170.stp) | ShapeFix_Face.FixWiresTwoCoincEdges asymmetric-tolerance-merge |
| [Tfa171](Tfa171.stp) | ShapeFix_Face.FixLoopWire complex-self-intersection |
| [Tfa172](Tfa172.stp) | ShapeAnalysis_CheckSmallArea non-planar-face |
| [Tfa173](Tfa173.stp) | ShapeFix_Face.FixSplitFace splitter-tangent-at-vertex |
| [Tfa174](Tfa174.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted near-flat-saddle |
| [Tfa175](Tfa175.stp) | ShapeFix_Face.FixAddNaturalBound boundary-curve-doesnt-close |
| [Tfa176](Tfa176.stp) | ShapeFix_Face.FixOrientation face-with-100-edges |
| [Tfa177](Tfa177.stp) | ShapeAnalysis_CheckSmallFace.CheckPin near-zero-tip-angle |
| [Tfa178](Tfa178.stp) | ShapeFix_Face.FixSmallAreaWire wire-touching-outer-corner |
| [Tfa179](Tfa179.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted with-degenerate-edge |
| [Tfa180](Tfa180.stp) | ShapeFix_Face.FixWiresTwoCoincEdges with-curved-edges |
| [Tfa181](Tfa181.stp) | ShapeFix_Face.FixLoopWire wire-with-tail-segment |
| [Tfa182](Tfa182.stp) | ShapeAnalysis_CheckSmallFace.CheckSmallArea polygon-vs-curve |
| [Tfa183](Tfa183.stp) | ShapeFix_Face.FixSplitFace splitter-extends-beyond-face |
| [Tfa184](Tfa184.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted face-on-cone-apex |
| [Tfa185](Tfa185.stp) | ShapeFix_Face.FixAddNaturalBound surface-with-discontinuity |
| [Tfa186](Tfa186.stp) | ShapeFix_Face.FixOrientation with-inner-wires-only |
| [Tfa187](Tfa187.stp) | ShapeAnalysis_CheckSmallFace.CheckPin pin-with-fillet |
| [Tfa188](Tfa188.stp) | ShapeFix_Face.FixSmallAreaWire wire-bigger-than-face |
| [Tfa189](Tfa189.stp) | ShapeAnalysis_CheckSmallFace.CheckTwisted face-on-sphere-with-pole |
| [Tfa190](Tfa190.stp) | ShapeFix_Face.FixWiresTwoCoincEdges with-coincident-vertex-only |
| [Tfa191](Tfa191.stp) | ShapeFix_Face.FixLoopWire with-multiple-inner-loops-touching |
| [Tfa192](Tfa192.stp) | ShapeAnalysis_CheckSmallFace.CheckPin three-way-pin-asymmetric |
| [Tfa193](Tfa193.stp) | ShapeFix_Face.FixSmallAreaWire wire-equal-to-face-area |
| [Tfa194](Tfa194.stp) | ShapeAnalysis_CheckSmallFace.CheckSpotFace face-with-bbox-much-larger |
| [Tfa195](Tfa195.stp) | ShapeFix_Face.FixOrientation face-on-curved-vs-planar |
| [Tfa196](Tfa196.stp) | ShapeAnalysis_Surface.ComputeSingularities toroidal-pinch |
| [Tfa197](Tfa197.stp) | ShapeAnalysis_Surface.IsUClosed bspline-periodic-u |
| [Tfa198](Tfa198.stp) | ShapeAnalysis_FreeBoundsProperties.CheckNotches gap-after-fix |
| [Tfa199](Tfa199.stp) | ShapeFix_Face.FixMissingSeam seam-detection |
| [Tfa200](Tfa200.stp) | ShapeAnalysis_Surface.DegeneratedValues cone-apex-degeneracy |
| [Tfa201](Tfa201.stp) | CheckSpotFace parametric interior singularity |
| [Tfa202](Tfa202.stp) | CheckTwisted normal inversion on elementary |
| [Tfa203](Tfa203.stp) | FixMissingSeam null surface guard |
| [Tfa204](Tfa204.stp) | FixLoopWire closed topology reordering |
| [Tfa205](Tfa205.stp) | FixAddNaturalBound cone apex degenerate |
| [Tfa206](Tfa206.stp) | FixOrientation TinyWireFiltering single-edge degenerate |
| [Tfa207](Tfa207.stp) | FixOrientation PeriodicBoundingBoxShift torus seam wrapping |
| [Tfa208](Tfa208.stp) | FixSmallAreaWire undersized perimeter degenerate loop |
| [Tfa209](Tfa209.stp) | FixWiresTwoCoincEdges duplicate coincident edges |
| [Tfa210](Tfa210.stp) | FixSplitFace multi-loop split on disconnected wires |
| [Tfa211](Tfa211.stp) | ShapeFix_Face.FixMissingSeam.null-surface-guard |
| [Tfa212](Tfa212.stp) | ShapeFix_Face.FixMissingSeam.bspline-non-periodic-rejection |
| [Tfa213](Tfa213.stp) | ShapeFix_Face.FixMissingSeam.infinite-bounds-fallback |
| [Tfa214](Tfa214.stp) | ShapeFix_Face.FixMissingSeam.degenerate-wire-consolidation |
| [Tfa215](Tfa215.stp) | ShapeFix_Face.FixMissingSeam.orientation-correction-partial-closure |
| [Tfa216](Tfa216.stp) | seam_detection_orientation_loss |
| [Tfa217](Tfa217.stp) | curve_copy_trimming |
| [Tfa218](Tfa218.stp) | circle_parameter |
| [Tfa219](Tfa219.stp) | vertex_tolerance_mismatch |
| [Tfa220](Tfa220.stp) | concat_result_truncation |
| [Tfa221](Tfa221.stp) | FixMissingSeam.null-surface-guard |
| [Tfa222](Tfa222.stp) | FixMissingSeam.no-closure-early-exit |
| [Tfa223](Tfa223.stp) | FixMissingSeam.infinite-bounds-fallback |
| [Tfa224](Tfa224.stp) | FixMissingSeam.degenerate-wire-consolidation |
| [Tfa225](Tfa225.stp) | FixMissingSeam.seam-boundary-clamping |
| [Tfa226](Tfa226.stp) | ShapeFix_Face.Add.null-wire-guard |
| [Tfa227](Tfa227.stp) | ShapeFix_Face.ClearModes.init-all-modes |
| [Tfa228](Tfa228.stp) | ShapeFix_Face.FixAddNaturalBound.null-surface-guard |
| [Tfa229](Tfa229.stp) | ShapeFix_Face.FixLoopWire.orientation-handling |
| [Tfa230](Tfa230.stp) | ShapeFix_Face.FixLoopWire.wire-topology |
| [Tfa231](Tfa231.stp) | FixSmallAreaWire shape-type filter |
| [Tfa232](Tfa232.stp) | FixWiresTwoCoincEdges FORWARD orientation dispatch |
| [Tfa233](Tfa233.stp) | FixPeriodicDegenerated context transformation |
| [Tfa234](Tfa234.stp) | FixAddNaturalBound seam-edge exclusion |
| [Tfa235](Tfa235.stp) | FixMissingSeam P-curve absence on torus |
| [Tfa236](Tfa236.stp) | ShapeFix_Face.FixOrientation |
| [Tfa237](Tfa237.stp) | ShapeFix_Face.SplitEdge (line-2653) |
| [Tfa238](Tfa238.stp) | ShapeFix_Face.SplitEdge (line-2741) |
| [Tfa239](Tfa239.stp) | ShapeFix_Face.FixSplitFace (line-2908) |
| [Tfa240](Tfa240.stp) | ShapeFix_Face.Perform (line-346) |
| [Tfa241](Tfa241.stp) | `ShapeFix_Face.FixOrientation.WireBoundingBoxComputation` |
| [Tfa242](Tfa242.stp) | `ShapeFix_Face.FixOrientation.PeriodicBoundingBoxShift` |
| [Tfa243](Tfa243.stp) | `ShapeFix_Face.FixOrientation.ToroidalDiagonalShift` |
| [Tfa244](Tfa244.stp) | `ShapeFix_Face.FixLoopWire.FLW-007` |
| [Tfa245](Tfa245.stp) | `ShapeFix_Face.FixMissingSeam.sphere-apex-edge-synthesis` |
| [Tfa246](Tfa246.stp) | STEP import missing edges: FACE_OUTER_BOUND wraps empty EDGE_LOOP |
| [Tfa247](Tfa247.stp) | Exported STEP produces empty objects (SHAPE_REPRESENTATION with no items) |
| [Tfa248](Tfa248.stp) | Draft OrthoArray missing objects on STEP export (MAPPED_ITEM dropped) |
| [Tfa249](Tfa249.stp) | Splitting vertex genuinely unattached: independent vertex sits on another edge's interior (T-junction not expressed as shared topology) |
| [Tfa252](Tfa252.stp) | EDGE_CURVE null edge_geometry ($) wired into a live, reachable face |
| [Tfa253](Tfa253.stp) | Outer/inner wire share a >50% collinear overlap segment |
| [Tfa254](Tfa254.stp) | Outer/inner wire touch at a clean endpoint-endpoint contact |
| [Tfa255](Tfa255.stp) | Sphere hole wire touches the pole via a degenerated edge: merges into the natural whole-surface boundary |
| [Tfa256](Tfa256.stp) | Face with two coincident-edge wires, multi-wire gate satisfied |
| [Tfa257](Tfa257.stp) | Two independent full-circle boundaries at the same location, closed-edge vertex reconciliation |
