# Confirmed-invalid fixtures: regen / quarantine queue

Generated 2026-06-18 from Sonnet verification of 33 Haiku-INVALID flags.
Only 4 survived the careful re-check; the other 29 were Haiku over-flags
(promoted back to VALID).

Per audit_pattern memory: never act on Haiku sweep verdicts alone — always
structural-grep-verify with a higher-tier model before regen/quarantine.

## CONFIRMED_INVALID (regen or quarantine)

| ID | Section | Defect class | Failure mode | Suggested fix |
|----|---------|--------------|--------------|---------------|
| Tsh028 | 12-3a-shells | Sliver-face styling | DATA has zero STYLED_ITEM; the entire defect (styling-on-sliver) is missing | Bespoke regen: add STYLED_ITEM + PRESENTATION_STYLE chain on the sliver face |
| Gp053 | 12-2a-pcurves | Asymmetric vertex tolerance | No per-vertex tolerance entities encoded; only filename string | Either reword catalog claim (tolerance lives in description) or add UNCERTAINTY/POSITIONAL_TOLERANCE per-vertex |
| Gs140 | 12-2c-surfaces | False-periodicity grid | Claim: first/last V-columns coincide spatially. Reality: X coords are 0 vs 4 | Bespoke regen: fix control-grid so V-edge endpoints actually coincide |
| Gs143 | 12-2c-surfaces | MakeBSpline false-periodic point grid | File encodes pre-built B_SPLINE_SURFACE_WITH_KNOTS; defective MakeBSpline path is never exercised | Quarantine OR rebuild via point-grid synthesis pipeline (not directly emittable in current builder) |

## Notes for follow-up

- Tsh028 + Gs140 can be regenerated with current builder (Python `step_builder.py`)
- Gp053 likely just needs a catalog claim reword
- Gs143 may need quarantine — the defect requires triggering OCCT's internal
  point→B-spline fitting path, which isn't representable as a static STEP file.
  Demote to a kernel-test-pair entry instead.
