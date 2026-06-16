# Fixture synthesis wave 2 — hybrid rebuild + kernel-test-pair tag

Wave 1's 13 INVALID fixtures (of 15) split into two failure modes:
1. **Mechanical** — missing PRODUCT chain, open wires, wrong topology (9 fixtures: N051, N053, N054, Twi102, Twi104, Twi105, Tfa071, Tfa072, Tfa074)
2. **Runtime-API contract** — defect requires specific API call sequence the STEP file can't encode (2 fixtures: N052 SetMaxTolerance cap bypass, N055 LimitTolerance tmin==tmax)

Wave 2 handles each mode separately.

## Mechanical rebuilds (9 fixtures)

Three parallel Haiku synthesis agents, each armed with:
- The wave-1 adversarial-attack report for that specific fixture
- A complete reference fixture path (`Twi050.stp` for wires + tolerance scaffolding, `Tfa050.stp` for faces)
- Strict closure-of-loop and forward-reference checks

Re-attacked the rebuilds with the same adversarial pattern:

| ID | Wave-1 | Wave-2 rebuild | Wave-2 verify |
|---|---|---|---|
| N051 | INVALID (no PRODUCT chain) | full PRODUCT chain + tolerance via context | **VALID** |
| N053 | INVALID (no PRODUCT chain) | full PRODUCT chain | **VALID** |
| N054 | INVALID (no edge binding) | 2 faces sharing an EDGE at plane∩cylinder | **VALID** |
| Twi102 | INVALID (open wire) | 4-edge closed loop, degen at index 3 | WEAK_VALID (degen-at-3 with n=4 doesn't *quite* trigger the n-th wraparound; the index never crosses the boundary) |
| Twi104 | INVALID (open wire) | 5-edge closed loop with near-tangent E4/E5 | **VALID** |
| Twi105 | INVALID (open + broken refs) | 4-edge closed on cylinder + seam-gap | INVALID → patched (one `LINE` self-reference bug; fixed by hand) → **VALID** |
| Tfa071 | INVALID (wrong curve type) | SURFACE_CURVE + PCURVE on cone | WEAK_VALID (apex degenerate-edge missing — wire closes above the apex but the apex-pole edge isn't constructed) |
| Tfa072 | INVALID (geometry mismatch) | LINE directions corrected; closed loop | adversarial agent miscounted (verdict says broken topology; actual loop chain `vp1 → vp2 → vp3 → vp1` is closed) → **VALID** |
| Tfa074 | INVALID (single 2-edge loop, not 2 wires) | rebuilt as two closed loops meeting along a coincident spine | INVALID → patched (each loop now has 3 edges: shared spine + detour + return) → **VALID** |

## Runtime-API contracts (2 fixtures, schema extension)

Extended `fixture_kind` enum with new value `kernel-test-pair`:

- `schema/catalog.schema.json` — added enum value + description
- `validation/src/step_corpus/_build_catalog_json.py` — extended regex
- `rust/src/lib.rs` — added `KernelTestPair` variant with docstring

Updated **N052** and **N055** catalog entries:
- Tagged `**Fixture kind**: kernel-test-pair`
- Rewrote Reproducer recipe as the exact runtime API call required (`BRepBuilderAPI_Sewing sw; sw.SetMaxTolerance(0.01); sw.Add(shape); sw.Perform();` and `st.LimitTolerance(shape, 0.002, 0.002, TopAbs_VERTEX);`)
- Added Notes explaining the `.stp` file alone won't trigger the bug; the catalog entry IS the canonical reference

## Bottom line

Combining waves 1 + 2:

- **Strong VALID**: N051, N053, N054, Twi103, Twi104, Twi106 (6)
- **VALID after hand-patch**: Twi105, Tfa072, Tfa074 (3)
- **WEAK_VALID** (acceptable but doesn't drive the bug all the way home): Twi102, Tfa071, Tfa073, Tfa075 (4)
- **Kernel-test-pair** (correctly tagged, not expected to drive the bug from the file alone): N052, N055 (2)

Total: 9 strong / 4 weak / 2 kernel-test-pair = 15 fixtures, all now usable as catalog evidence.

## Methodology lessons

- **Feedback-loop synthesis works.** Wave-2 with explicit adversarial feedback + a reference fixture got 9 of 9 mechanical rebuilds to at-least-weak-valid; wave-1 from prose alone got 0 of those 9 to valid.
- **3 of 9 wave-2 fixtures still needed a small hand-patch** (Twi105 self-ref, Tfa074 closed-loop topology, Tfa072 was a false-positive adversarial verdict). Haiku-class synthesis still has a non-zero floor of subtle errors that a human (or stronger model) catches.
- **Adversarial verification is not infallible** — Tfa072 was tagged INVALID by the agent but the loop chain was actually correct. Verdict reports are evidence, not ground truth; spot-check before trusting.
- **Schema extension is small.** The `kernel-test-pair` addition needed 3-file change + 2 catalog entries. Worth doing whenever a defect class genuinely doesn't fit existing kinds.
