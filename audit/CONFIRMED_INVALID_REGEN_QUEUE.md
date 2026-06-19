# Confirmed-invalid fixtures: regen / quarantine queue

Generated 2026-06-18 from Sonnet verification of 33 Haiku-INVALID flags.
Only 4 survived the careful re-check; the other 29 were Haiku over-flags
(promoted back to VALID).

Per audit_pattern memory: never act on Haiku sweep verdicts alone — always
structural-grep-verify with a higher-tier model before regen/quarantine.

## CONFIRMED_INVALID (regen or quarantine) — ALL RESOLVED 2026-06-18

| ID | Section | Defect class | Failure mode | Resolution |
|----|---------|--------------|--------------|------------|
| Tsh028 | 12-3a-shells | Sliver-face styling | DATA had zero STYLED_ITEM | RESOLVED: added STYLED_ITEM/PRESENTATION_STYLE_ASSIGNMENT chain referencing sliver face #62 via Tsh028.py |
| Gp053 | 12-2a-pcurves | Asymmetric vertex tolerance | No per-vertex tolerance entities encoded | RESOLVED: catalog reword — asymmetry is runtime kernel state, not STEP-encodable. Fixture provides the geometric setup |
| Gs140 | 12-2c-surfaces | False-periodicity grid | First/last V-columns didn't coincide; also malformed flat control list + self-ref LINE | RESOLVED: rebuilt via Gs140.py with proper 4×4 Bezier grid; V=0 and V=3 rows now spatially identical |
| Gs143 | 12-2c-surfaces | MakeBSpline false-periodic point grid | Defect lives in OCCT runtime; not Part-21-representable | RESOLVED: catalog reword — documented as kernel-test-pair shape carrier (scaffold) |

## Round 2: weak-verify pass (2026-06-18)

Sonnet re-verified the 64 weak_valid candidates. 35 promoted to ACTUALLY_VALID
(Haiku over-flag); 23 remain genuinely weak; 6 new CONFIRMED_INVALID surfaced:

| ID | Section | Failure mode | Suggested fix |
|----|---------|--------------|---------------|
| Gs097 | 12-2c-surfaces | "area threshold 0.0" is a runtime API param, not STEP-encodable; file is a plain planar face | Catalog reword (runtime-only defect, like Gp053/Gs143) |
| N152 | 12-4-tolerance | SHELL_BASED_SURFACE_MODEL references LENGTH_UNIT (#100); broken differently than claimed | Bespoke regen via builder |
| Tfa132 | 12-3c-faces | Claims B-spline surface with C0 discontinuity; file contains only a PLANE (comment in file admits the substitution) | Bespoke regen with real B-spline carrier + C0 |
| Twi248 | 12-3b-wires | Claims edge with only 2D pcurve (null 3D); all 4 edges have full 3D LINE geometry | Bespoke regen to remove 3D geometry from target edge |
| Twi268 | 12-3b-wires | Claims seam edge on periodic surface; file is flat planar square with no periodic surface | Bespoke regen with real periodic surface (CYLINDRICAL/TOROIDAL) |
| Twi270 | 12-3b-wires | Claims disconnected edge chains near tolerance; file is a perfectly connected planar square | Bespoke regen with actual disconnection |

## Notes for follow-up

- Tsh028 + Gs140 can be regenerated with current builder (Python `step_builder.py`)
- Gp053 likely just needs a catalog claim reword
- Gs143 may need quarantine — the defect requires triggering OCCT's internal
  point→B-spline fitting path, which isn't representable as a static STEP file.
  Demote to a kernel-test-pair entry instead.
