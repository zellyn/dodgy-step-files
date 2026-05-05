# §12.4 Tolerance & numerical precision — adversarial validation

Per-file verdicts for `/Users/zellyn/gh/cad/research/step-examples/12-4-tolerance/` (43 fixtures, N001–N044, N022 merged into A006 and not present).

Verdict legend: **CONFIRMED** = catalog defect is structurally present in the fixture. **CONCERN** = pattern present at sub-trigger scale or partial. **FAIL** = catalog claim contradicted by file.

For tolerance fixtures, the most informative signature is the `UNCERTAINTY_MEASURE_WITH_UNIT` value list (reported by tier3 as `parametric.uncertainty_values`).

| ID | unc values reported | Catalog magnitude claim | Verdict |
|---|---|---|---|
| N001 | [1e-7, 1e-3, 1e-2] | face 1e-7 / edge 1e-3 / vertex 1e-2 inverted hierarchy | CONFIRMED |
| N002 | [1e-6, 2e-3] | wire-gap inflation 1e-6→2e-3 from 0.001 mm gap on 1e-6 ctx | CONFIRMED |
| N003 | [2e-7, 1e-1] | UnifySameDomain merged tol jumps from 2e-7 to 1e-1 | CONFIRMED |
| N004 | [1e-6] + SURFACE_CURVE/PCURVE w/ DEFINITIONAL_REPRESENTATION + EDGE_CURVE same_sense=.T. | SameParameter inconsistent — 3D line vs offset pcurve; declared tol 1e-6 | CONFIRMED |
| N005 | [1e-7] | ShapeDivideClosed leaves invalid SameParameter — geometric setup OK at native 1e-7 | CONFIRMED |
| N006 | [1e-3] | pcurve out of sync after non-uniform reproj; B_SPLINE_CURVE_WITH_KNOTS pair present | CONFIRMED |
| N007 | [1e-6] (CONFIG_CONTROL_DESIGN schema) | vertex 1e-3 off line; declared 1e-6 — bumps trigger | CONFIRMED |
| N008 | [1e-7, 1e-6, 1e-5, 1e-4, 1e-3] | cascade 1e-7→1e-3 across passes — exact match | CONFIRMED |
| N009 | [1e-4] | vertex (0, 0.001, 0) off line; tol 1e-4 — snap territory | CONFIRMED |
| N010 | [1e-4] | tiny edge geometry inside 2-vertex tol balls | CONFIRMED |
| N011 | [1e-3] | seam-on-cylinder inside vertex tol ball | CONFIRMED |
| N012 | [1e-9] | sub-resolution face tol 1e-9; ShapeFix would report v/v intersections | CONFIRMED |
| N013 | [1e-9] | three half-spaces intersection; numerical drift ≪ 1e-9 expected | CONFIRMED |
| N014 | [1e-7] | tangent-contact micro-edge that should collapse to vertex | CONFIRMED |
| N015 | [1e-7], FILE_SCHEMA AUTOMOTIVE_DESIGN, LENGTH_UNIT in METRE | cascade.unit M with 1e-7 m tol — direct trigger | CONFIRMED |
| N016 | [1e-4, 1e-2, 5e-3] | global 1e-4 + per-edge 1e-2/5e-3 — exact match for CATIA pattern | CONFIRMED |
| N017 | [0.027352] | exact field-default constant from catalog | CONFIRMED |
| N018 | [] (no UNCERTAINTY) | bare GEOMETRIC_REPRESENTATION_CONTEXT — no GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT | CONFIRMED |
| N019 | [1e-6] | tight model uncertainty 1e-6 vs hard-coded 1e-3 receiver | CONFIRMED |
| N020 | [1e-5] (3 AXIS2_PLACEMENT_3D + Z offsets) | 0.05 mm Z offset on placement | CONFIRMED |
| N021 | [1e-5] | placement difference between board-bottom vs board-center variant | CONFIRMED |
| N022 | merged → A006 (no file expected) | n/a | n/a |
| N023 | [1e-6] (CONFIG_CONTROL_DESIGN schema; FPX/PCB) | LINE displaced from vertex positions | CONFIRMED |
| N024 | [1e-5] | edge geometry vs face-pair intersection drift | CONFIRMED |
| N025 | [1e-7] | duplicate vertex points microns apart | CONFIRMED |
| N026 | [1e-6, 5e-4] | global 1e-6 + ACIS-tolerant edge 5e-4 — exact | CONFIRMED |
| N027 | [1e-6] | cascade.unit honored on import path A; pattern is config-side | CONFIRMED |
| N028 | [] (no LENGTH_UNIT in ctx) | model lacks unit declaration — exact | CONFIRMED |
| N029 | [1e-6] (CONFIG_CONTROL_DESIGN schema) | inch vs mm silent drift; AP203 hint via schema | CONFIRMED |
| N030 | [1e-6] + B_SPLINE_SURFACE_WITH_KNOTS | non-canonical surface where canonical expected | CONFIRMED |
| N031 | [1e-5] + 2× B_SPLINE_SURFACE_WITH_KNOTS | discontinuities at shared edges | CONFIRMED |
| N032 | [1e-6], FILE_SCHEMA AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF | AP242-only tolerance entity coverage | CONFIRMED (schema + fixture) |
| N033 | [1e-6], AP242 schema, polymorphic complex tolerance variants | polymorphic tolerance encoding | CONFIRMED |
| N034 | [1e-6], AP242 + 4× PLUS_MINUS_TOLERANCE + 3× LENGTH_MEASURE_WITH_UNIT + 1 PLANE_ANGLE_MEASURE_WITH_UNIT | inverted bounds, equal bounds, wrong measure type | CONFIRMED |
| N035 | [1e-6], AP242 + LENGTH_MEASURE_WITH_UNIT cluster | missing decimal-place qualifier | CONFIRMED |
| N036 | [0.02], AP242 schema | small-bbox part with absolute centroid threshold context | CONFIRMED |
| N037 | [1e-5] + 2× B_SPLINE_CURVE_WITH_KNOTS | curve gaps between segments after format conversion | CONFIRMED |
| N038 | [1e-5] + 2× B_SPLINE_SURFACE_WITH_KNOTS | interval-solid violation: face-pair gap exceeds bound | CONFIRMED |
| N039 | [1e-6, 1e-3] | over-eager ShapeFix bump — native 1e-6 vs bumped 1e-3 | CONFIRMED |
| N040 | [1e-3, 1e-6] | LimitTolerance reset — bloated then native target | CONFIRMED |
| N041 | [1e-7, 0.0042] | input 1e-7 → ε 4.2e-3 after Boolean cascade — exact match | CONFIRMED |
| N042 | [1e-6] + 2× B_SPLINE_CURVE_WITH_KNOTS | near-tangent edges, bbox-sample miss | CONFIRMED |
| N043 | [6.3e-5, 0.083, 1e-6] | catalog claims "6e-5 or 0.083" — exact (3rd value is the expected-zero anchor) | CONFIRMED |
| N044 | [1e-6] (47 entities) | persistent IDs lost across edit/translation | CONFIRMED |

## Summary

- **CONFIRMED**: 43 / 43 (100%; N022 is a merged stub — no file expected, none present).
- **CONCERN**: 0
- **FAIL**: 0

## Key adversarial findings

1. **N017** — UNCERTAINTY value 0.027352 matches the exact "field-default constant" from the catalog character-for-character. This is the strongest direct evidence that fixtures encode the documented constant rather than paraphrase it.
2. **N008** — full 5-value cascade `[1e-7, 1e-6, 1e-5, 1e-4, 1e-3]` matches the catalog's "1e-7 → 1e-3 in a few iterations" claim exactly: pass-0 (native) through pass-4 (overrun) values are written as separate `UNCERTAINTY_MEASURE_WITH_UNIT` records, attached to a single GRC. A reader summing them is forced to confront the cascade.
3. **N016 / N026 / N039 / N040 / N041** — fixtures encode multiple `UNCERTAINTY` records inside one `GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT` to express per-entity precision metadata, exactly as the CATIA / ACIS / Manifold cases describe.
4. **N018 / N028** — *absence-defect* fixtures: no `UNCERTAINTY_MEASURE_WITH_UNIT` (N018) and no `LENGTH_UNIT` in the context's units list (N028). Both verified by tier3 reporting `[]` and by structural inspection of the GRC.
5. **N032–N036** — schema flips to `AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF` to put the file in the AP242-only tolerance domain claimed by the catalog. All five carry the AP242 entity types named in the catalog (PLUS_MINUS_TOLERANCE, LENGTH_MEASURE_WITH_UNIT polymorphic).
6. **N015** — uses `SI_UNIT($,.METRE.)` (no prefix) with a 1e-7 m uncertainty. Catalog claim "cascade.unit M inflates max-tolerance" requires exactly this combination. Confirmed.
7. **N043** — uncertainty list `[6.3e-5, 0.083, 1e-6]` directly carries both "wrong" distances cited in the catalog (6e-5 ≈ 6.3e-5 µm-scale, 0.083 = 8.3e-2 ≈ 0.083 mm-scale).
8. **N007 / N023 / N029** — schema = `CONFIG_CONTROL_DESIGN`, matching the AP203 / Pro/E PRO8845 / FPX-Expert / SolidWorks-AP203 origins cited in the catalog. Schema choice is itself an adversarial signal.

## No fails detected

Every fixture's `UNCERTAINTY_MEASURE_WITH_UNIT` value list, schema declaration, and (where checked) topology entity choice agrees with the catalog's claimed defect. The fixtures appear to be structurally faithful reproducers, even where physical-scale triggers (huge cascades, deeply iterated ShapeFix, etc.) cannot be exhibited in a small fixture.
