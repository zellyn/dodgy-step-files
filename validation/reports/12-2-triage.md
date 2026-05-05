# §12.2 CONCERN Triage

Triage of 16 CONCERN entries across §12.2a (pcurves), §12.2b (NURBS), §12.2c (surfaces).

Triage rule: defect = kernel's failure to handle input correctly. Catalog-claims-rejection + validator-silently-accepts (empty) = CONFIRMED. Catalog-claims-crash + segfault = CONFIRMED. Catalog-claims-crash + empty = CONFIRMED-WEAK. Validator segfault when catalog doesn't claim crash = CONFIRMED (stronger than documented).

## Summary

| Verdict        | Count |
|----------------|-------|
| CONFIRMED      | 14    |
| CONFIRMED-WEAK | 2     |
| FAIL           | 0     |

## §12.2a pcurves (6)

| ID    | Validator               | Catalog expected           | Verdict   | Rationale                                                                 |
|-------|-------------------------|----------------------------|-----------|---------------------------------------------------------------------------|
| Gp007 | occt=empty gmsh=empty   | heal/reject pcurve range   | CONFIRMED | Silent acceptance: bad pcurve range produces no shape and no diagnostic.  |
| Gp008 | occt=empty gmsh=empty   | heal (refit) / reject      | CONFIRMED | Oscillating pcurve silently dropped without warning.                      |
| Gp015 | occt=empty gmsh=empty   | heal (wrap) / reject       | CONFIRMED | Trim-failure case yields empty shape; no diagnostic surfaced.             |
| Gp019 | occt=signal(11) gmsh=signal(11) | heal/reject       | CONFIRMED | Segfault on missing per-patch pcurve — stronger than catalog's "reject".   |
| Gp020 | occt=empty gmsh=empty   | heal (FixGap2d) / reject   | CONFIRMED | 2D wire gap silently produces empty result instead of healing.            |
| Gp026 | occt=empty gmsh=empty   | heal (FixConnected) / reject | CONFIRMED | UV-domain unclosed contour silently dropped.                              |

## §12.2b NURBS (3)

| ID    | Validator               | Catalog expected         | Verdict        | Rationale                                                                       |
|-------|-------------------------|--------------------------|----------------|---------------------------------------------------------------------------------|
| Gn001 | occt=empty gmsh=empty   | warn (identical) / reject (descending) | CONFIRMED | Knot-vector violation silently produces empty shape — neither warn nor diagnostic reject. |
| Gn002 | occt=empty gmsh=empty   | heal (pad weights), do not crash | CONFIRMED-WEAK | Catalog hints crash history; current behavior is silent empty rather than heal. |
| Gn010 | occt=empty gmsh=empty   | reject the surface       | CONFIRMED      | Out-of-range / NaN control points silently dropped without diagnostic.          |

## §12.2c surfaces (7)

| ID    | Validator               | Catalog expected            | Verdict        | Rationale                                                                  |
|-------|-------------------------|-----------------------------|----------------|----------------------------------------------------------------------------|
| Gs001 | occt=empty gmsh=empty   | heal (flip orient) / reject | CONFIRMED      | Negative-radius torus silently produces no shape rather than flipping.     |
| Gs024 | occt=empty gmsh=empty   | heal by analytic recovery   | CONFIRMED      | Plane-as-degree-1-NURBS not canonicalized; result is empty.                |
| Gs026 | occt=signal(11) gmsh=signal(11) | heal (emit LINE)    | CONFIRMED      | Segfault on helix-on-cylinder — catalog didn't claim crash; defect stronger. |
| Gs031 | occt=empty gmsh=empty   | heal (dedupe) / reject      | CONFIRMED      | Duplicated outer contour silently dropped.                                 |
| Gs032 | occt=empty gmsh=empty   | reject + warn               | CONFIRMED      | Degenerate extrusion silently rejected with no warning.                    |
| Gs036 | occt=empty gmsh=empty   | reject; never crash         | CONFIRMED      | Zero-magnitude direction silently dropped without diagnostic.              |
| Gs037 | occt=empty gmsh=empty   | heal (descend wrappers)     | CONFIRMED-WEAK | Catalog reports exception during UIso eval; validator shows empty-only.    |

## Notes

- All 16 CONCERN entries are confirmed defects. Two are CONFIRMED-WEAK because the catalog explicitly references a crash/exception path and the validator only shows silent empty (kernel may have papered over the throw rather than truly fixing it).
- §12.2 defects are largely entity-level (single bad pcurve / surface / NURBS) so empty top-level shape is the correct manifestation; no per-file STP inspection altered any verdict.
- Two segfaults (Gp019, Gs026) reveal kernel pathology stronger than catalog documented.
