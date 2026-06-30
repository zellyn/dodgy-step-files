# Overnight session — 2026-06-29 / 2026-06-30

User went to sleep after directing: kick off B4 wave-5 mining, then continue
with whatever's next-best for the catalog. Auto mode active.

## What shipped overnight

| Commit | Title |
|---|---|
| `8cfb6cd9` | B4.5 batch B — 3 NURBS/tangency fixtures (Gn174, Gn175, Gs184) |
| `7377fadf` | B4.5 batch C — 3 surfaces/adversarial fixtures (Ad128, Gs185, Gs186) |
| `c8bdf966` | B4.5 batch A — 3 PMI fixtures (Pmi137, Pmi138, Pmi139) |
| `ea54c4a9` | B2.5c: extend tier-3 introspection to quadric surfaces |
| `c720e3ad` | B2.5c assertion pass: 392 quadric assertions across 173 fixtures |

## Cumulative wave-4→6 results

| Wave | Type | Outcome |
|---|---|---|
| B4 wave-4 | Mining | 35 defects, 34.3% novelty (vs wave-3 saturation of 9.3%) |
| B4.5 | Synthesis | 9 new fixtures from wave-4 deferred list |
| B2.5c | Introspection extension | cylinder/cone/sphere/torus radius/angle/axis exposed |
| B2.5c | Assertion sweep | 392 new tier-3 assertions, 173 catalog entries |
| B4 wave-5 | Mining | **In flight** — will complete autonomously |

## Cumulative B2.5b/c since 2026-06-27

- pilot: 25 assertions (11 NURBS fixtures)
- scale-up: 108 assertions (58 NURBS fixtures)
- edge-orient: 16 assertions (8 fixtures)
- mismatch fixes: 9 assertions (4 fixtures)
- Gn090 description fix: 2 assertions
- **quadric extension: 392 assertions (173 fixtures)**

**Total: 552 new tier-3 assertions across ~245 entries.**
Catalog tier-3 assertion total: 3,300 → ~3,850 (+550, +17%).

## Wave-5 status

Background sub-agent mining commercial+academic sources NOT covered in
wave-4: Siemens NX, PTC Creo per-version, SolidWorks forum, CATIA
migration, MicroStation, FARO, NIST STEPcode, older arXiv papers,
3MF Consortium. Expected output:
`/Users/zellyn/gh/dodgy-step-files/audit/b4_mining_wave_5_2026-06-30.md`

When wave-5 completes, natural next move = dispatch 3 parallel B4.5b
synthesis sub-agents (same pattern as B4.5: ~3 fixtures each).

## DEF-C verification (TORUS over-segmentation)

Audit's wave-4 deferred list flagged DEF-C as "needs oracle verify first".
Verified via existing fixture Tfa216 (TOROIDAL_SURFACE with R=2.0, r=0.5):
local OCCT loads as **1 face**, not 4 (cf. autodesk forum report of
importer splitting into 4 quadrants). DEF-C is not reproducible on
OCCT — it's a different-importer-specific defect. Recommend skipping
DEF-C from B4.5b synthesis unless target receiver is non-OCCT.

## DEF-G verification (NURBS face domain shrinkage)

Audit's wave-4 flagged DEF-G as "HOOPS Exchange-specific". Not
yet locally verified; safe to keep in deferred list as "valid input"
that an OCC-tier kernel should accept without shrinking.

## CI status

`validate-full` green twice in succession (04:06:39Z, 04:11:15Z UTC).
`validate-fast` pending for the c720e3ad push.

## What's next (when you wake up)

1. Wave-5 audit will be at `audit/b4_mining_wave_5_2026-06-30.md`
2. If novelty rate is still high (>15%), dispatch B4.5b synthesis
3. If wave-5 saturates (<10%), pivot strategy:
   - **Q5 silent-empty subset strengthening** (long-deferred, lots
     of fixtures where defects are oracle-invisible)
   - **B2.5d: edge analytic curves** (circle radius, ellipse focal,
     line direction) — symmetric to today's quadric surface work
   - **B3.6 v2 refresh** with the 9 B4.5 fixtures + Gn090 description
     fix folded in

## Files / artifacts

- All commits pushed to main
- Browse/ regenerated (3112 pages)
- No uncommitted work in tree
