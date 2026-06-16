---
fixture_id: _early-waves-quarantine
defect_class: meta — pre-mandate template bugs across N055-N075 + Tsh001-Tsh068
v3_record: n/a (collective follow-up, not a single defect class)
occt_source: n/a
occt_lines: n/a
occt_ref: n/a
status: quarantined
attempts: 1
last_touch: 2026-06-16
---

## Why this exists

Adversarial sample sweep on 2026-06-16 surfaced systematic file-level
breakage in two early-wave file sets. Confirmed via structural grep
across the full prefix (not just the sample). Files are quarantined in
`step-examples/_quarantine/early-waves/`, not deleted, because the
catalog entries describe real defect classes.

This is one collective follow-up file rather than 75 individual ones —
the work is mechanical regeneration against the current template, not
75 separate defect-class investigations.

## What's quarantined

### N055–N075 (20 files)

Two distinct LINE-constructor bugs:

- **N055–N060**: `LINE('name', (#pt, #vtx))` — list-wrapped args, plus
  passing a VERTEX_POINT in the slot Part-21 LINE expects a VECTOR.
- **N062–N075**: `LINE('name', #pt, #(VECTOR(...)))` — the `#(...)`
  inline-instance form is not valid Part-21. VECTOR entities must be
  top-level instances referenced by `#N`.

The bug pattern is contained to this contiguous ID range. N076+ use
the correct three-arg form with separately-declared VECTOR.

### Tsh001–Tsh068 (55 files, with gaps)

Missing the entire PRODUCT chain (#9000–#9023 in the canonical
template), so OCCT's `TransferRoots` returns nothing and no healing
pass ever runs against the topology. Tsh069+ all have the chain.

Specific missing entries: see `step-examples/_quarantine/early-waves/`
directory listing.

## Why it's not just "delete"

- Each ID has a catalog entry describing a real OCCT-healing defect.
- The defect is correctly identified; the mistake is at the fixture
  layer.
- A future regen against the canonical template should produce a
  strong-VALID fixture for most of these IDs without any
  defect-class re-investigation.

## Next directions

- **Batch regen, low priority**: 75 mechanical regens is real work
  but not blocking. The 600+ active fixtures (Twi/Tfa/Gs/Gn/Gp + late N
  + late Tsh) are the actual deliverable; this is debt to clear when
  there's a calm wave.
- **Before regen, audit the canonical template**: confirm the current
  mandatory-PRODUCT-chain template in synthesis prompts produces files
  that match the structural checks `_tier3_lint` cares about.
  Re-running 75 fixtures against a still-buggy template wastes the
  effort.
- **Check whether any IDs are duplicates** of better fixtures already
  in the live corpus before regenerating — sometimes a later wave
  picked up the same defect class under a different ID.
- **Re-run adversarial validator on each regen** before promoting back
  to the active prefix.
