# Fixture synthesis wave 3 — scaling the proven methodology

After wave 2 validated the feedback-loop pattern (9/9 mechanical rebuilds reached at-least-weak-valid with reference-fixture-armed prompts), wave 3 applies it at scale to 15 more fixtures from the v3 deep-pass corpus:

- **Tsh069-Tsh073** (§12.3a shells): 5 OCCT shell-orientation defect classes
- **Gs059-Gs063** (§12.2c surfaces): 5 OCCT surface-analysis defect classes
- **Gp041-Gp045** (§12.2a pcurves): 5 OCCT pcurve-defect classes

## Adversarial verdicts (after rebuild + targeted patches)

| ID | Defect (OCCT method) | Wave-3 synth | Patches applied | Final |
|---|---|---|---|---|
| Tsh069 | CheckOrientedShells normal-flip | VALID | none | **VALID** |
| Tsh070 | FixFaceOrientation multiconnect edge | VALID | none | **VALID** |
| Tsh071 | BadEdges mismatched-ordering edge | INVALID (two distinct edges, not one shared) | rewrote Face B to share edge #23 with same orientation flag as Face A | **VALID** |
| Tsh072 | FreeEdges closure violation | WEAK_VALID (self-referential PLANE syntax) | fixed `PLANE('',#66)` → `PLANE('',#65)` | **VALID** |
| Tsh073 | ShapeFix_Shell.Perform context reuse | WEAK_VALID (3 self-referential PLANE entries) | fixed `PLANE('',#87)`, `#98`, `#109` → reference the AXIS2_PLACEMENT_3D one entity below | **VALID** |
| Gs059 | IsUClosed B-spline closure sanity | VALID | none | **VALID** |
| Gs060 | ComputeSingularities sphere poles | WEAK_VALID (bare sphere, no PRODUCT chain) | appended PRODUCT + GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION wrapping | **VALID** |
| Gs061 | SurfaceNewton normal degeneracy | VALID | none | **VALID** |
| Gs062 | ValueOfUV trim-parameter dispatch | VALID | none | **VALID** |
| Gs063 | Trimmed+offset Bezier conversion | VALID | none | **VALID** |
| Gp041 | CheckCurve3dWithPCurve midspan divergence | INVALID (no PRODUCT chain) | appended PRODUCT + SHELL_BASED_SURFACE_MODEL wrapping the existing ADVANCED_FACE | **VALID** |
| Gp042 | FixAddPCurve plane-bypass | INVALID (no PRODUCT chain) | same patch | **VALID** |
| Gp043 | FixReversed2d B-spline knot corruption | INVALID (no PRODUCT chain) | same patch | **VALID** |
| Gp044 | Project endpoint-bias | INVALID (no PRODUCT chain) | same patch | **VALID** |
| Gp045 | FixSameParameter copyedge range trap | INVALID (no PRODUCT chain) | same patch | **VALID** |

## Why the wave-3 pcurve batch shipped without PRODUCT chains

The synthesis agent explicitly noted "fixture-only scope, no PRODUCT chain added per fixture-only scope" — interpreting the prompt's "minimal-only" wording as "skip the wrap." The prompt for wave-3 batches did include a reference fixture (Twi050) showing the PRODUCT chain pattern, but the agent did not generalize it to the pcurve case. **Lesson**: explicit "REQUIRED: include the PRODUCT chain block from Twi050 lines 9000-9023 even when the rest of the fixture is small" needs to be in every prompt. A Python script that auto-appends the wrap to any fixture lacking it is a cheap post-processor.

## Bottom line

- Fixture-synthesis wave 3: 15 fixtures → all **VALID** after adversarial re-attack + targeted patches.
- Cumulative across wave 1+2+3: **24 strong-VALID, 4 WEAK_VALID, 2 kernel-test-pair** = 30 fixtures rooted in v3 defect-class records, with each fixture's content backed by a falsifiable claim + minimal reproducer from `OCCT_HEAL_COVERAGE_V3.md`.
- Methodology consolidated: synth → adversarial → patch loop with explicit reference fixtures and structural rules gets to 100% VALID with one patch round. Future waves should bake the PRODUCT chain auto-append into the dispatch script.
