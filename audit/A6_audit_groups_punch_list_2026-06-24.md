# A6 Audit Groups — punch list, scanned 2026-06-24

Source: Q3 BACKLOG item. Original spec in PLAN_OF_ATTACK.md "Phase 7": 75
fixtures across 4 defect categories. Scan target: 2343 non-quarantine
.stp fixtures.

## Status overview

Groups 1 and 3 are already substantively complete per DONE.md
(June 2026 Q3 work, commits 4ca129f / e581fba / 8a06221 / d07b694
for Group 1; 3a8fd88 through c7bfa37 for Group 3). The BACKLOG Q3
item is partially stale.

| Group | Spec count | Remaining in bytes | Action needed |
|-------|-----------:|-------------------:|---------------|
| 1. no-bounds ADVANCED_FACE | 24 | 0 done; 3 KEEPs | Optional Tsh229 audit |
| 2. EDGE_LOOP doesn't chain | 23 | **26** | Per-fixture verify (likely all KEEPs) |
| 3. Empty EDGE_LOOP | 11 | 0 done; 9 KEEPs | None |
| 4. EDGE_CURVE twice same orient | 17 → 10 | **4** | Per-fixture verify (likely all KEEPs) |

## Group 1 — no-bounds ADVANCED_FACE (KEEPs)

These three currently have `ADVANCED_FACE('...',(),...)` in bytes; all
are intentional:

- **Tfa002** — "Unbound ADVANCED_FACE (no FACE_OUTER_BOUND, no FACE_BOUND)" — empty bounds IS the defect.
- **Ad015** — adversarial multi-empty-aggregate fixture.
- **Tsh229** — ghost face uses `ADVANCED_FACE('ghost_face',(),#9999,.T.)` where `#9999` is a dangling reference; empty bounds is part of the ghost mechanism. **Recommended audit:** verify the catalog claim is fully demonstrated by the bytes.

## Group 2 — EDGE_LOOP doesn't chain (26 fixtures)

Structural scan (full vertex-ID walk: end of edge[i] ≠ start of edge[i+1])
confirms the chain break in bytes for 26 fixtures. Every one of these
has a catalog title describing wire ordering, scrambled edge lists,
disconnected endpoints, or FixReorder/FixConnected behavior — the
chain break is the **intended** defect, not a side effect.

Representative — **Twi003**: `#42=EDGE_LOOP('',(#38,#39,#40,#41))` —
OE#38 ends at vertex #15, OE#39 starts at vertex #16 (distinct IDs)
across all four junctions.

**Full list:**

Ad101, Pf024, Ps010, Tfa022, Twi003, Twi007, Twi008, Twi028, Twi038,
Twi051, Twi053, Twi065, Twi078, Twi087, Twi107, Twi116, Twi136, Twi156,
Twi159, Twi164, Twi200, Twi202, Twi238, Twi242, Twi262, Twi264

## Group 3 — empty EDGE_LOOP (KEEPs)

These nine currently have `EDGE_LOOP('...',())` in bytes; all are
legitimate per Q3 phase-7 disposition:

Ad015, Ad050, Tfa246, Tsh023, Tsh053, Tsh167, Twi001, Twi252, Xp008

## Group 4 — EDGE_CURVE used twice same orientation (4 fixtures)

| Fixture | Catalog title (abbrev.) | Duplicate pattern |
|---------|------------------------|-------------------|
| **Bo006** | One edge shared by ≥3 faces in 2-manifold shell | EC#25.F.×2 across two EDGE_LOOPs |
| **Tfa028** | Full-revolution CYLINDRICAL_SURFACE with single seam | EC#20.T. in 4-edge outer wire + 1-edge seam loop |
| **Wr055** | Writer regression flips half of ORIENTED_EDGE directions | EC#17.T.×2 and EC#25.T.×2 across two loops |
| **Xp012** | Reversed face normal × non-watertight × duplicate edge | EC#22,26,30.T.×2 — four EDGE_CURVEs each appear .T. twice |

Of the 17 spec entries, 13 have been fixed during other Q3 work (vs.
the spec's "7 already fixed"). 6 additional were repaired incidentally
without being explicitly tracked against this group.

The remaining 4 (above) have catalog claims that explicitly require
the duplicate-orientation pattern as the defect mechanism — likely
all KEEPs.

## Recommended disposition

The 30 nominally-remaining fixtures (26 in Group 2 + 4 in Group 4)
appear to be correctly built — the structural pattern detected by the
scan IS the intended defect per the catalog claim. The original
75-fixture spec was a "fix the build errors" punch list; in the
intervening months, all real build errors have been fixed.

Two paths:
1. **Accept and close Q3.** The corpus is in good shape on these
   defect categories. Mark task #116 complete.
2. **Per-fixture deep audit** for Groups 2 & 4 (30 fixtures): for each,
   verify the bytes-level defect matches the catalog mechanism claim,
   not just the structural pattern. This is ~30 Sonnet sub-agent
   minutes if dispatched in batches of 10.

Recommendation: accept and close, with the Tsh229 audit as a single
follow-up task.
