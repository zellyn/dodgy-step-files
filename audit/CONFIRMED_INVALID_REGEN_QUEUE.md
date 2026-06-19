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

## Round 2: weak-verify pass (2026-06-18) — ALL RESOLVED

Sonnet re-verified the 64 weak_valid candidates. 35 promoted to ACTUALLY_VALID
(Haiku over-flag); 23 remain genuinely weak; 6 new CONFIRMED_INVALID surfaced:

| ID | Section | Failure mode | Resolution |
|----|---------|--------------|---------------|
| Gs097 | 12-2c-surfaces | runtime API threshold, not STEP-encodable | RESOLVED: catalog reword as runtime-only |
| N152 | 12-4-tolerance | structurally broken SBSM | RESOLVED: rebuilt scaffold via builder + reworded as kernel-test-pair |
| Tfa132 | 12-3c-faces | claim says B-spline w/ C0 break; file was just a PLANE | RESOLVED: rebuilt with real degree-3 B-spline + interior knot mult=3 at u=0.5 |
| Twi248 | 12-3b-wires | claim says null 3D; all edges had 3D LINE | RESOLVED: rebuilt with SURFACE_CURVE($, pcurve) for one edge |
| Twi268 | 12-3b-wires | claim says periodic seam; file was flat plane | RESOLVED: rebuilt on CYLINDRICAL_SURFACE with edge along u=0 seam |
| Twi270 | 12-3b-wires | claim says within-tolerance disconnect; file was connected | RESOLVED: rebuilt with 5e-8mm gap at vertex shared by edge0/edge1 |

## Notes for follow-up

- Tsh028 + Gs140 can be regenerated with current builder (Python `step_builder.py`)
- Gp053 likely just needs a catalog claim reword
- Gs143 may need quarantine — the defect requires triggering OCCT's internal
  point→B-spline fitting path, which isn't representable as a static STEP file.
  Demote to a kernel-test-pair entry instead.
