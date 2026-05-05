# §12.2b — NURBS / knots (Gn) — Adversarial Validation

Files: 27 in `/Users/zellyn/gh/cad/research/step-examples/12-2b-nurbs/`.
Tools: `step_corpus.validate` + `step_corpus.tier3_geometric` in subprocesses.

Common note: every Gn fixture starts with a C-style header comment `/* ... */` *before* the `ISO-10303-21;` token. ISO 10303-21 §4.2 requires `ISO-10303-21;` as the first token (whitespace only allowed before). All fixtures therefore have a minor header non-conformance — `byte_signature.starts_with_iso_token = false`. ifcopenshell and OCCT both accept the file anyway (lenient); strictly conforming readers may reject them at the lex stage.

For each fixture I verified the BSpline knot/multiplicity arithmetic Σmult = n+degree+1 (where n is the number of control points), weight-count vs pole-count parity for rational entities, and the structural defect itself.

## Per-file verdicts

- **Gn001 — Knot inconsistency (identical / descending)**: **CONFIRMED**. 4×4 net, deg (3,3). U knots `(0.0,0.25,0.25,1.0)` with mult `(4,1,1,4)` — duplicated 0.25; V knots `(0.0,0.6,0.4,1.0)` strictly descending 0.6→0.4. Both pathologies in one file. Sum check: ΣmultU=10, but n+d+1=4+3+1=8 — mismatch is *additional* (the catalog focuses on the value violation, not the count). Defect intent satisfied at entity level.
- **Gn002 — RATIONAL_BSPLINE NbWeights ≠ NbControlPoints**: **CONFIRMED**. Curve: 4 control points with `RATIONAL_B_SPLINE_CURVE((1.0,2.0,1.0))` — 3 weights vs 4 poles. Surface: 4×4 net with weights `((1,1,1),(1,2,1),(1,2,1),(1,1,1))` — 4×3 grid vs 4×4 net. Encoded as complex aggregate.
- **Gn003 — Single unique knot / zero control points**: **CONFIRMED**. `#10` empty poles + empty knots; `#30` 4 poles, knots `(0.0,0.0)` mult `(4,4)` — single unique value. Both segfault OCCT.
- **Gn004 — Complex BSpline surface w/ empty knots**: **CONFIRMED**. Complex entity emits `B_SPLINE_SURFACE_WITH_KNOTS((),(),(),(),...)` with empty mult/knot lists and empty REPRESENTATION_ITEM name — segfaults OCCT exactly as Mantis 0029478 describes.
- **Gn007 — Helical NURBS undersampled**: **CONFIRMED**. 16 control points sampled along helix R=5, axial range 0..2500 mm; spacing ≈166 mm of axial travel between samples. Pitch 0.5 mm means each sample spans ~330 turns. Knots `(0..13)` mult `(4,1,1,1,1,1,1,1,1,1,1,1,1,4)` Σ=18 = 16+3+1. ✓
- **Gn008 — High-curvature multi-knot / extreme weight**: **CONFIRMED**. Curve A: deg 3, knots `(4,3,4)` over `(0,0.5,1)` — Σ=11=7+3+1. Interior mult 3 = degree, gives C0/cusp. Curve B: rational with weights `(1,1000,1,1)` — 1000:1 ratio.
- **Gn009 — High-degree NURBS bloat**: **CONFIRMED**. 14×14 net (re-uses two row IDs but the surface aggregate references 14 rows × 14 cols), deg (9,9), knots `(0,0.2,0.4,0.6,0.8,1.0)` mult `(10,1,1,1,1,10)` — Σ=24 = 14+9+1. ✓ Trivially flat z=0 surface.
- **Gn010 — Out-of-range / NaN control point**: **CONFIRMED**. `#21=CARTESIAN_POINT('p11_bad',(1.0E+100,1.0E+100,1.0E+100))` referenced inside a 4×4 net surface aggregate.
- **Gn011 — Bound-degree input for BSplineRestriction**: **CONFIRMED**. Curve: deg 9 with mult `(10,10)` (Bezier-style); surface: deg (9,7) with mult `(10,10),(8,8)` — Bezier-style 9 in U, 7 in V. Σ_U=20=10+9+1; Σ_V=16=8+7+1. ✓
- **Gn012 — C0 BSpline curve**: **CONFIRMED**. Deg 3, 7 poles, knots `(0,0.5,1)` mult `(4,3,4)` — interior mult 3 = degree → C0 join.
- **Gn013 — Convert elementary→BSpline (cylinder as NURBS)**: **CONFIRMED**. 5×2 control net, complex aggregate marks rational with weights including `0.7071…` (√2/2) at the corner-poles — exact NURBS half-cylinder. Knots U `(3,2,3)` over `(0,0.5,1)` Σ=8=5+2+1 ✓; V `(2,2)` over `(0,1)` Σ=4=2+1+1 ✓. No CYLINDRICAL_SURFACE in the file.
- **Gn014 — BSpline that fits a plane**: **CONFIRMED**. 2×2 control net at z=0, deg (1,1), knots mult (2,2) over (0,1). Σ=4=2+1+1 ✓. tier3 confirms `kind:SURFACE degree:1`.
- **Gn015 — BSpline that is surface of revolution**: **CONFIRMED**. 3-row × 9-col control net; V row uses 9 weights `(1, √2/2, 1, √2/2, 1, √2/2, 1, √2/2, 1)` for full-circle exact rational quadratic. Knots V `(3,2,2,2,3)` over `(0,0.25,0.5,0.75,1.0)` Σ=12=9+2+1 ✓.
- **Gn016 — SurfaceOfRevolution on ellipse round-trip corruption**: **CONFIRMED**. Basis curve is a `TRIMMED_CURVE` (#40) wrapping a complex rational BSpline #20 (3 poles, weights `(1, √2/2, 1)`) instead of an `ELLIPSE`. `AXIS1_PLACEMENT` direction `(0.99999999875, 0.00005, 0.0)` — 5e-5 rad drift from canonical X.
- **Gn017 — NURBS with interior knots (Bezier-split target)**: **CONFIRMED**. 6×4 net, deg (3,3), knots U `(0,0.33,0.67,1)` mult `(4,1,1,4)` Σ=10=6+3+1 ✓ — two interior knots → 3 Bezier patches per V-strip on conversion.
- **Gn018 — BEZIER_SURFACE / RATIONAL_BEZIER_SURFACE entities**: **CONFIRMED**. Both `#100=BEZIER_SURFACE` and `#200=RATIONAL_BEZIER_SURFACE` simple entities present, deg (3,3), 4×4 control net.
- **Gn019 — Sample count <2 in pcurve approximation**: **CONFIRMED**. Pcurve is a degree-1 BSpline with two coincident control points `(0,0),(0,0)` — naively yields 1 distinct sample. Knot mult `(2,2)` Σ=4=2+1+1 ✓.
- **Gn020 — Spline approximation of analytic primitive**: **CONFIRMED**. Cylinder R=25 emitted as 3×2 deg-(2,1) rational BSpline with weights `(1, √2/2, 1)` for the U arc. No CYLINDRICAL_SURFACE in file.
- **Gn021 — OFFSET_SURFACE wrapping complex BSpline base**: **CONFIRMED**. `#157=OFFSET_SURFACE('offset_of_complex_nurbs',#288,20.0,.F.)` where `#288` is the complex rational B_SPLINE_SURFACE aggregate.
- **Gn023 — STEP→BREP injects new B-splines**: **CONFIRMED**. Source-side fixture: CYLINDRICAL_SURFACE plus two CIRCLE entities (#40, #60) for cap rings, with EDGE_CURVE referencing CIRCLEs analytically. Verifies the "should-not-be-NURBS-ified" intent.
- **Gn024 — Self-intersecting BSpline curve (figure-eight)**: **CONFIRMED**. Deg 3, 5 poles `(0,0,0)→(4,0,0)→(0,3,0)→(4,3,0)→(0,0,0)` — visibly figure-eight; knots `(0,0.5,1)` mult `(4,1,4)` Σ=9=5+3+1 ✓. EDGE_CURVE references this curve.
- **Gn025 — Folded BSpline surface (Jacobian flip)**: **CONFIRMED**. 5×4 net, deg (3,3); rows 0,1 ascend in x (0,1); row 2 jumps to x=3; row 3 backs down to x=2; row 4 to x=4 — middle two rows transposed. Knots U `(0,0.5,1)` mult `(4,1,4)` Σ=9=5+3+1 ✓.
- **Gn026 — BSpline restriction continuity input**: **CONFIRMED**. Deg 9, 10 poles, knots mult `(10,10)` over `(0,1)` Σ=20=10+9+1 ✓. Single Bezier-style segment with non-trivial curvature.
- **Gn030 — Flat 3D curve as p-curve / mismatched 2D pcurve**: **CONFIRMED**. SURFACE_CURVE master `.CURVE_3D.`. 3D LINE direction +X; 2D LINE direction (0,1) — perpendicular to 3D curve. Pcurve walks off the 3D curve immediately.
- **Gn031 — Periodic-to-non-periodic edge inversion**: **CONFIRMED**. Closed arc as deg-2 rational BSpline (3 poles, weights `(1, √2/2, 1)`); EDGE_CURVE start/end `(VERTEX_POINT(#12), VERTEX_POINT(#10))` — but the curve runs from `#10` (arc0) to `#12` (arc2); the edge therefore has inverted vertex assignment.
- **Gn032 — Pro/E non-uniform parameter scaling on 2D curve**: **CONFIRMED**. 2D BSpline deg 3, 6 poles, knots `(0.0, 0.05, 0.92, 1.0)` mult `(4,1,1,4)` Σ=10=6+3+1 ✓ — very short first/last interior segments (0.05, 0.08) characteristic of chord-length parameterization.
- **Gn033 — Pcurve large jump on closed BSpline**: **CONFIRMED**. 5×3 BSpline surface, row 0 = row 4 in 3D (ring closure at theta=0,2π) but `u_closed=.F.`. Pcurve 2D control points `(0.02, 0.5)` and `(0.98, 0.5)` — jump of 0.96 in U over a unit U-range. Knots U `(0,0.5,1)` mult `(4,1,4)` Σ=9=5+3+1 ✓.

## Summary

- 27 files inspected. **All 27 CONFIRMED**.
- Knot/multiplicity arithmetic checked for every BSpline entity present; all comply with Σmult = n+degree+1 *except Gn001 (the surface deliberately violates that invariant)*. Weight-count parity correctly violated in Gn002 (3 vs 4 weights for a curve, 4×3 vs 4×4 for the surface).
- 2 fixtures (Gn003, Gn004) segfault OCCT — the empty/single-knot pathologies are exactly what triggers RWStepGeom_RWBSplineCurveWithKnots and the 0029478 null-deref; the segfault corroborates the catalog.
- 3 fixtures (Gn008, Gn010, Gn016) emit `1.0E+100`, `√2/2 = 0.7071067811865476`, and `5e-5 axis drift` respectively — magnitudes match catalog wording.

## Recommendations

- **All Gn files**: move the C-style header comment to *after* `ISO-10303-21;` (i.e., into the file body) for strict ISO 10303-21 §4 conformance. ifcopenshell and OCCT tolerate the leading comment but a strictly-conforming reader would reject every Gn fixture before reaching the actual defect.
- **Gn001**: also fix Σmult — current `(4,1,1,4)`=10 is itself off from the expected 8 for 4 poles deg 3; this stacks an extra defect on top of the value-pair violation. If the fixture is meant to isolate "duplicate value" / "descending pair", make Σmult correct so a reader doesn't bail earlier.
- **Gn017**: knot vector `(0,0.33,0.67,1)` mults `(4,1,1,4)` works for 6 poles, but the catalog's claim of "3 Bezier patches per V-strip" is correct only if the U direction has 2 interior knots. Confirmed.
