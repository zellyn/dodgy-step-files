# B2.5b NURBS catalog claim/reality mismatches — 2026-06-27

While scaling up tier-3 assertion harvest across 64 bspline-load-ok
fixtures (commit pair to follow), 3 Sonnet sub-agents surfaced
**7 catalog claim/reality mismatches** — places where the prose
description doesn't match what OCCT actually loaded.

These are tracked as a deferred work item: each mismatch represents
either (a) a catalog prose error worth correcting, (b) an OCCT
conversion behavior worth documenting (e.g. BEZIER → BSpline
silently), or (c) a fixture whose builder doesn't actually produce
the entity the prose describes.

## Full mismatches (no tier-3 assertion added)

| ID | Prose claim | Introspection reality | Likely cause |
|---|---|---|---|
| Gs066 | "SPHERICAL_SURFACE" | surface_type=bspline, degree (1,1) | Builder emits bilinear B-spline proxy instead of true sphere |
| Gs090 | "Bezier surface" | surface_type=bspline | OCCT silently converts BEZIER_SURFACE → BSpline on load |
| Gs091 | "Rational B-spline surface with asymmetric weights" | is_rational=False | Weights actually uniform; builder bug or prose error |
| Gs102 | "BEZIER_SURFACE passthrough" | surface_type=bspline | Same OCCT Bezier→BSpline conversion as Gs090 |

## Partial mismatches (some assertions added, contested claim withheld)

| ID | Contested claim | Reality | Confirmed claims | Note |
|---|---|---|---|---|
| Tfa082 | "NURBS" (rational) | is_rational=False | surface_type=bspline | Prose's "NURBS" probably loose terminology for B-spline |
| Tfa222 | "2 rational B-spline edges" | edge.bspline.is_rational=False | surface_type, both periodicity flags | Edge rationality contradicted, surface claims confirmed |
| N031 | "RATIONAL_B_SPLINE_SURFACE" | is_rational=False on both faces | surface_type=bspline (both faces) | Strong prose claim, no rationality witness |

## Recommended follow-up

1. **OCCT-conversion-class** (Gs090, Gs102): Add a catalog "OCC behavior" note
   that BEZIER_SURFACE entities round-trip as B-spline post-load. Possibly
   add a separate `loaded_surface_type` vs `declared_surface_type`
   distinction in the catalog schema.

2. **Builder-output-class** (Gs066, Gs091, N031): Verify the fixture
   source actually emits what the prose claims. If the builder is wrong,
   regenerate the fixture; if the prose is wrong, update the prose. These
   are 3 candidates for the next Sonnet-regen pass.

3. **Loose-terminology-class** (Tfa082, Tfa222): "NURBS" / "rational
   B-spline" used as generic terms for "B-spline surface in general".
   Sharpen the catalog prose: reserve "rational" for fixtures where
   is_rational=True actually fires.

These are quality-improvement leads, not regressions. The 108 tier-3
assertions added in the same pass all pass against live OCCT — these
7 just couldn't be turned into assertions because of the mismatch.
