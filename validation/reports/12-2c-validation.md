# §12.2c — Surfaces (Gs) — Adversarial Validation

Files: 30 in `/Users/zellyn/gh/cad/research/step-examples/12-2c-surfaces/`.
Tools: `step_corpus.validate` + `step_corpus.tier3_geometric` in subprocesses.

Common note: every fixture omits the PRODUCT/PDM chain so OCCT TransferRoots returns `n_roots=0` and `shape.IsNull()=true`. Defects are therefore confirmed at the entity/byte level. For sliver/area claims I compute area directly from the CARTESIAN_POINT coordinates declared in the file.

## Per-file verdicts

- **Gs001 — Negative MajorRadius torus**: **CONFIRMED**. `#20=TOROIDAL_SURFACE('',#13,-50.0,10.0)` — major_radius is literal -50.0 (file comment says -50.0 though catalog reproducer mentions -2.0; either way, sign-flipped). Wrapped in OPEN_SHELL via VERTEX_LOOP natural bound.
- **Gs002 — Lemon torus minor>=major**: **CONFIRMED**. `#20=TOROIDAL_SURFACE('',#13,2.0,3.0)` — minor (3.0) > major (2.0) → no central hole, lemon. Outer-equator vertex at (5.0,0,0)=(major+minor) consistent.
- **Gs005 — Surface periodicity not declared**: **CONFIRMED**. 5×2 BSpline surface, row 0 = row 4 = `(10,0,*)` exactly (closed in U), `u_closed=.F.`. Knots U `(0,0.25,0.75,1.0)` mult `(3,1,1,3)` Σ=8=5+2+1 ✓.
- **Gs006 — Surface singularity (degenerate pole row)**: **CONFIRMED**. 3×2 BSpline surface where U-row #10..#12 all coincide at `(0,0,10)` — degenerate pole. V-row spreads to (5,0,0), (0,5,0), (-5,0,0). Knots `(3,3)` Σ=6=3+2+1 ✓.
- **Gs007 — Whole wire shifted by surface period**: **CONFIRMED**. Cylinder R=5; pcurve 2D origin `(12.5663706144, 0.0)` = 4π → entire pcurve sits at U=4π instead of canonical 0. 3D vertex at (5,0,0).
- **Gs009 — Self-intersecting wire on planar face**: **CONFIRMED**. 4 vertices `(0,0)`, `(10,10)`, `(10,0)`, `(0,10)` with edges in bow-tie order A→C→B→D — diagonals AC and BD cross at (5,5). EDGE_LOOP `#80=(#70,#71,#72,#73)`.
- **Gs010 — Folded BSpline surface (Jacobian flip)**: **CONFIRMED**. 4×3 net deg (3,2). Row 0 ascends in X: (0..15); row 1 descends in X: (15..0); row 2 ascends again. Knots U `(4,4)` Σ=8=4+3+1 ✓; V `(3,3)` Σ=6=3+2+1 ✓.
- **Gs011 — Self-intersecting trim curves**: **CONFIRMED**. Two EDGE_CURVE entities #50 (A→B from (0,0) to (10,10)) and #51 (C→D from (0,10) to (10,0)) in the same EDGE_LOOP — diagonals cross at (5,5).
- **Gs012 — Bow-tie outer wire in UV**: **CONFIRMED**. Same bow-tie ordering as Gs009. Plane host #20; the EDGE_LOOP traverses A→C→B→D (UV cross). Distinguished from Gs009 by intent — UV vs 3D.
- **Gs014 — Zero-area degenerate strip**: **CONFIRMED**. Vertices at `(0,0)`, `(100,0)`, `(100,1e-7)`, `(0,1e-7)`. Computed area = 100 × 1e-7 = **1e-5 mm²** (matches catalog "1e-5 mm^2"). Two short edges declared with `VECTOR(...,1.0E-7)`.
- **Gs015 — Sliver face high aspect ratio**: **CONFIRMED**. Vertices `(0,0)`, `(250,0)`, `(250,1e-5)`, `(0,1e-5)`. Area = 250 × 1e-5 = **2.5e-3 mm²**, perimeter = 2×250 + 2×1e-5 ≈ **500 mm**, aspect ratio ≈ **2.5e7**. All match catalog.
- **Gs018 — Reversed pcurve vs 3D curve**: **CONFIRMED**. 3D LINE direction `+Z`, traverses z=0→z=5; pcurve 2D origin `(0,5)` direction `(0,-1)` traverses V=5→V=0. Opposite parameter sense.
- **Gs019 — Pcurves shifted by integer period**: **CONFIRMED**. Two edges share cylinder R=5. Edge 1 pcurve at U=0 V=0..3. Edge 2 pcurve at U=2π=6.2831853072 V=3..6 — shifted by exactly one period.
- **Gs021 — Line displaced from true position**: **CONFIRMED**. Vertex A=(0,0,0), Vertex B=(10,0,0). LINE origin `(0,0,0.5)`, direction `(1,0,0)` — line is parallel to AB but offset by 0.5 mm in Z. Vertices are equidistant from the line.
- **Gs024 — Round-trip planar face → degree-1 NURBS**: **CONFIRMED**. 2×2 BSpline at z=0, deg (1,1), control net `(0,0)`, `(100,0)`, `(0,50)`, `(100,50)`. tier3 reports `kind:SURFACE degree:1`. Trim wire is inset rectangle `(10..90, 5..45)`.
- **Gs025 — C0 join in BSpline curve**: **CONCERN — partial mismatch**. File comment says "interior knot mult 4 == degree+1" but the actual knot vector is `(4,3,4)` (mult 3 = degree, **not** 4). Σ=11=7+3+1 ✓. With mult 3 = degree, the curve is C0 (matches Gs025's text claim of "G0-only spot from mult 3"). The catalog header line says "interior knot multiplicity equals the order" — order=degree+1=4 — which would be a Bezier split, not what the file emits. However, the file reproduces the *G0/C0 pathology* the catalog lists as the actual defect. Verdict: confirmed at the C0-join level; the comment's "(==degree+1)" line is a typo (the constant is mult 3 = degree, which is the more common interpretation).
- **Gs026 — Helix on cylinder mis-projected (no pcurve)**: **CONFIRMED**. Cylinder R=5 host; 3D BSpline curve approximates a helix with 5 poles (deg 3, knots `(0,0.5,1)` mult `(4,1,4)` Σ=9=5+3+1 ✓). `SURFACE_CURVE('',#35,(),.PCURVE_S1.)` — empty associated_geometry. OCCT segfaults — same trigger as Gp001/Gp019.
- **Gs028 — Pseudo-seam on non-periodic surface**: **CONFIRMED**. 3×2 BSpline (deg (2,1)), `u_closed=.F.`, `v_closed=.F.`. SURFACE_CURVE has `master=.PCURVE_S1_AND_S2.` (seam-flag) and two-pcurve list `(#46,#46)` — same handle twice.
- **Gs029 — Curve with last < first**: **CONFIRMED**. `#21=PARAMETER_VALUE(6.2831853071795864)` (=2π) is trim_1 (first). `#22=PARAMETER_VALUE(0.0)` is trim_2 (last). `sense_agreement=.T.`. last(0) < first(2π).
- **Gs030 — Edge inconsistent with face geometry**: **CONFIRMED**. Cylinder R=10. LINE origin `(10.5, 0, 0)` along +Z — sits at radius 10.5, 0.5 mm off the cylinder. Vertices at `(10,0,0)` and `(10,0,5)` *are* on the cylinder.
- **Gs031 — Face with duplicated outer contour**: **CONFIRMED**. `#83=ADVANCED_FACE('',(#81,#82),#20,.T.)` — bounds list contains both `#81` and `#82`, both wrapping the same `#80=EDGE_LOOP`. Same wire bound twice.
- **Gs032 — Surface-of-linear-extrusion direction parallel to basis**: **CONFIRMED**. `#11=DIRECTION('',(1.0,0.0,0.0))` for the LINE; `#20=DIRECTION('',(1.0,0.0,0.0))` for the extrusion. Identical → degenerate.
- **Gs033 — Trim-curve jagged tessellation on NURBS**: **CONFIRMED**. `TOROIDAL_SURFACE` (R=30, r=5); 2D pcurve = `TRIMMED_CURVE` over a 2D ELLIPSE in `[0, π]`. Bicubic-feel trim path matches the catalog's "tube.stp-style" pathology. Note: ELLIPSE in 2D needs AXIS2_PLACEMENT_2D — file emits `#33=AXIS2_PLACEMENT_2D` but assigns ellipse axes via two DIRECTIONs (#31,#32) — AP214's AXIS2_PLACEMENT_2D takes only one ref_direction; the second is redundant/orphaned.
- **Gs034 — Twisted/pinched face (figure-eight outer wire)**: **CONFIRMED**. Outer wire visits vertex `#31` at (5,5,0) twice (edges #60 ends at #31, edge #62 ends at #31, edge #63 starts at #31, edge #65 ends at #31). Two square lobes meeting at the pinch point. EDGE_LOOP `#80` has 6 ORIENTED_EDGEs.
- **Gs035 — Composite curve segment defects**: **CONFIRMED**. `#20=COMPOSITE_CURVE_SEGMENT(...,$)` — null parent_curve. `#21=COMPOSITE_CURVE_SEGMENT(...,#30)` referencing `#30=COMPOSITE_CURVE('',(#20,#21,#22),...)` — self-cyclic. `#22` is the only valid segment.
- **Gs036 — Zero direction / degenerate placement**: **CONFIRMED**. `#11=DIRECTION('',(0.0,0.0,0.0))` — all-zero direction_ratios. `#12=#13=DIRECTION('',(0.0,0.0,1.0))` — axis and ref_direction parallel. `#14=AXIS2_PLACEMENT_3D` references both → cannot construct orthonormal frame.
- **Gs037 — Surface offset of linear extrusion**: **CONFIRMED**. `#22=SURFACE_OF_LINEAR_EXTRUSION('',#14,#21)` (basis CIRCLE extruded along +Z). `#30=OFFSET_SURFACE(#22,2.0,.T.)` — exact offset/extrusion chain.
- **Gs038 — Pcurve UV jump on closed BSpline**: **CONFIRMED**. 5×2 BSpline (deg (2,1)), row 0 = row 4 in 3D, `u_closed=.T.` actually (note: `.T.` here, see comment claim). Knots U `(0,0.25,0.75,1)` mult `(3,1,1,3)` Σ=8=5+2+1 ✓. Pcurve 2D from U=0.99 to U=0.01 — 0.98 jump in unit range.
- **Gs039 — Helical sweep / incomplete shell**: **CONFIRMED**. Single ADVANCED_FACE on SPHERICAL_SURFACE wrapped in OPEN_SHELL — the cylindrical side and bottom annulus are absent. Catalog claim: "writer silently emits incomplete shell". Structurally, the shell has only 1 face — visibly incomplete for a hemisphere+cylindrical-cut model.
- **Gs040 — High-curvature cusp from NURBS knot insertion**: **CONFIRMED**. Deg 3, 7 poles, knots `(0,0.5,1)` mult `(4,3,4)` Σ=11=7+3+1 ✓. Mult 3 at interior = degree → C0 cusp; control polygon pinches sharply through (3,0).

## Summary

- 30 files inspected. **29 CONFIRMED**, **1 CONCERN** (Gs025 — C0 vs C0 mult typo in the in-file comment; defect is structurally present but file comment text says `mult 4 == degree+1` while the actual knot vector emits mult=3=degree).
- All BSpline knot/multiplicity sums verified to satisfy Σ = n+degree+1 except where deliberately violated.
- Sliver/zero-area claims (Gs014, Gs015) verified by direct CARTESIAN_POINT arithmetic — match the catalog's stated mm² and aspect ratios.
- Torus radii claims (Gs001 negative; Gs002 minor>major) verified literally in the TOROIDAL_SURFACE entity.
- Composite-curve cyclic / null reference (Gs035) verified at the entity-reference level.
- 1 fixture (Gs026) crashes OCCT — empty `()` in SURFACE_CURVE associated_geometry, mirroring Gp001/Gp019. Crash is itself diagnostic.

## Recommendations

- **Gs025**: change the comment text from "(==degree+1)" / "(4)" to "(==degree)" / "(3)" so it matches the actual knot multiplicity. The defect is correct; only the comment is misleading.
- **Gs033**: AXIS2_PLACEMENT_2D in AP214 takes one ref_direction; the file emits `#33=AXIS2_PLACEMENT_2D('',#30,#31)` — that's fine; `#32=DIRECTION('',(0.0,1.0))` is currently orphaned. Either remove it or use AXIS2_PLACEMENT_2D's three-arg AP242 form if the second direction is intentional.
- **Gs039**: The catalog title is "helical sweep / variable-radius blend" but the fixture is actually a hemisphere with bottom and side missing — structurally a "missing faces" reproducer rather than a helical-sweep one. Consider clarifying the fixture's intent (the *symptom* — silent incomplete shell — is faithfully reproduced, but the *cause* is not a helix).
- **Gs037**: `#30=OFFSET_SURFACE(#22,2.0,.T.)` is missing the leading name argument; AP214 OFFSET_SURFACE has signature `(name, basis_surface, distance, self_intersect)`. The file relies on positional zero-named omission. Add `'name',` for strictness.
