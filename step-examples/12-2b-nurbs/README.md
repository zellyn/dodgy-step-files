# §12.2b — NURBS / B-spline defects (Gn-prefix)

B-spline curve and surface defects: knot-vector irregularities, multiplicity mismatches, control-point/weight count errors, degree mismatches, non-rational vs rational issues, periodic/closed flags inconsistencies, and degenerate parameterizations.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.2b) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Gn001](Gn001.stp) | `B_SPLINE_SURFACE_WITH_KNOTS` knot/multiplicity inconsistency: descending or duplicated-without-multiplicity knot vector |
| [Gn002](Gn002.stp) | RATIONAL_BSPLINE_CURVE / SURFACE with `NbWeights ≠ NbControlPoints` |
| [Gn003](Gn003.stp) | BSpline curve with single unique knot or zero control points |
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
