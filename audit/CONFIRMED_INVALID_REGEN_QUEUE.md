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

## Notes for follow-up

- Tsh028 + Gs140 can be regenerated with current builder (Python `step_builder.py`)
- Gp053 likely just needs a catalog claim reword
- Gs143 may need quarantine — the defect requires triggering OCCT's internal
  point→B-spline fitting path, which isn't representable as a static STEP file.
  Demote to a kernel-test-pair entry instead.
