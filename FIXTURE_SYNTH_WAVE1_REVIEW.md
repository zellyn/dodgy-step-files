# Fixture synthesis wave 1 — adversarial review

First experiment with the user's stated 3-stage pipeline:
1. ✅ describe every defect class (OCCT v3 deep-pass complete, 327 methods / 2058 branches)
2. ⏳ synthesize STEP fixtures matching the catalog descriptions  ← **WAVE 1**
3. ⏳ adversarial sub-agents prove the fixtures demonstrate the claimed defect

Wave 1 dispatched 3 parallel Haiku synthesis agents to produce 15 fixtures (N051-N055 tolerance / Twi102-Twi106 wires / Tfa071-Tfa075 faces). Each fixture was then adversarially attacked by an independent agent.

## Outcome

| ID | Verdict | Primary failure |
|---|---|---|
| N051 | INVALID | No PRODUCT chain → OCCT TransferRoots returns empty → buggy InTolerance branch never reached |
| N052 | INVALID | No SHELL/multi-face → BRepBuilderAPI_Sewing never invoked |
| N053 | INVALID | EDGE_CURVE referencing VERTEX_POINT (type mismatch) + no PRODUCT chain |
| N054 | INVALID | No EDGE binding vertex to surfaces — bare geometry doesn't trigger FixVertexTolerance |
| N055 | INVALID | LimitTolerance is healer-state — STEP file alone cannot encode tmin == tmax bounds |
| Twi102 | INVALID | Wire not closed: P0→P1→P2→P2 ends at P2, missing P2→P0 |
| **Twi103** | **VALID** | Self-intersection pattern correctly forces 30-iteration convergence path |
| Twi104 | INVALID | Wire completely open — CheckTail precondition rejects before reaching buggy branch |
| Twi105 | INVALID | Wire open + broken edge connectivity (E3 starts at wrong vertex) |
| **Twi106** | **VALID** | 5-vertex zigzag with cascading intersections — demonstrates accumulation cascade |
| Tfa071 | INVALID | Wire uses LINE curves instead of curves on the cone — apex direction logic unreachable |
| Tfa072 | INVALID | Edges don't geometrically connect the spot vertices |
| Tfa073 | WEAK_VALID | Endpoint asymmetry correct, but single-edge wires bypass shared-edge construction |
| Tfa074 | INVALID | Single loop with two ORIENTED_EDGEs of the same edge — not the "two wires" pattern |
| Tfa075 | WEAK_VALID | Valid WIRE loop, but defect requires non-WIRE loop type |

**2 VALID / 2 WEAK_VALID / 11 INVALID = ~13% solid-pass rate.**

## What we learned

1. **The 3-stage pipeline works.** The adversarial pass caught real issues that a careful human reviewer would also catch — and caught some that a casual review might miss (e.g., the EDGE_CURVE vs VERTEX_POINT type mismatch).

2. **First-pass synthesis from prose alone is insufficient.** The Haiku synthesis agents had the v3 prose plus existing fixture examples, but produced byte-malformed and topologically-incomplete fixtures.

3. **Required minimum scaffolding** for any fixture targeting a *healer-pass* defect:
   - Full PRODUCT chain (APPLICATION_CONTEXT → PRODUCT → PRODUCT_DEFINITION → ... → SHAPE_DEFINITION_REPRESENTATION) so OCCT TransferRoots reaches the geometry.
   - Closed-wire topology for any wire-defect class.
   - Surface-bound curves (pcurves) for any face-defect class that reads PCurveOf().
   - Specific tolerance escalation paths that the healer must traverse — bare value mismatches aren't enough.

4. **Runtime-only defects** (e.g., LimitTolerance API contract, SetMaxTolerance cap bypass) cannot be reproduced by a STEP file in isolation. They require driving the healer with specific input parameters. These defect classes belong in a *kernel test* rather than a corpus fixture, OR the fixture needs to be paired with documentation of the exact API call sequence.

5. **Synthesis budget.** Each agent produced 5 fixtures in ~3 minutes — total wall-clock under 10 minutes for 15. Fast iteration is possible; the binding constraint is fixture quality, not throughput.

## Next steps

Two paths:

A. **Targeted rebuild**: For each INVALID fixture, dispatch a second-round synthesis agent armed with the adversarial feedback ("you previously failed because X — produce a corrected version that addresses X"). Risk: same Haiku model may make different mistakes. Mitigation: include a complete reference fixture (e.g., `Twi050.stp`) and demand structural parity with it.

B. **Adjust scope**: Accept that some defect classes (especially runtime-API-contract ones) need a different artifact than a STEP file. Categorize defects into: (a) producible-as-fixture, (b) requires-kernel-test-pair, (c) describable-only. Build fixtures for (a), document (b) for the kernel's test suite, and keep (c) as catalog entries without fixtures.

Decision pending user direction.

## Full adversarial reports

- `/tmp/adversarial-A.md` (N051-N055)
- `/tmp/adversarial-B.md` (Twi102-Twi106)
- `/tmp/adversarial-C.md` (Tfa071-Tfa075)
