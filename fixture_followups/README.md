# Fixture follow-ups — small one-investigation-per-file backlog

When a fixture-synthesis attempt gets refuted by adversarial review (or
lands WEAK_VALID with a clear path to a stronger version), we drop a
note here. Goal: chew on these later, one at a time, without losing the
breadcrumbs.

## File-per-investigation convention

One Markdown file per defect-class-we-couldn't-cleanly-demonstrate.
Filename: `<fixture-id>.md`, where `<fixture-id>` is the catalog ID we
were aiming at (e.g. `Twi102.md`, `Tfa071.md`). If multiple attempts
target the same ID, the file gets a new `## Attempt N (YYYY-MM-DD)`
section appended; we don't create a second file.

If the defect class doesn't yet have a catalog ID (e.g. the deep-pass
record exists but no fixture has been attempted), pick the next free
prefix slot and use that as the placeholder filename — same as if we
were about to add it to the catalog.

## Frontmatter schema

```yaml
---
fixture_id: <prefix><nnn>      # e.g. Twi102
defect_class: <OCCT method.suffix from OCCT_HEAL_COVERAGE_V3.md>
v3_record:  OCCT_HEAL_COVERAGE_V3.md:<line>     # line in our coverage doc
occt_source: src/.../<file>.cxx                  # OCCT source path
occt_lines: <start>-<end>                        # OCCT source line range
occt_ref:   master@<commit-hash>                 # OCCT git hash we sampled
status:     weak-valid | refuted | runtime-api-pair | open
attempts:   <N>
last_touch: 2026-MM-DD
---
```

`occt_ref` should pin to a specific commit; if we only have a branch
name (`master`) we should backfill the hash when we revisit. The point
is to be able to look at the *same* OCCT source we looked at last time,
even after upstream changes.

## Body structure

**License-cleanliness rule (same as the rest of the repo):** OCCT is
LGPL. Never paste verbatim source code into these notes. Use line-number
pointers + git hash so a future reader can fetch the same code
themselves, and describe the relevant branch in prose-laundered form.
If a quoted name (variable, function, condition) is essential, that's
fine — just don't reproduce the body.

1. **OCCT source pointer + prose** — line range, file path, git hash, then
   a prose-laundered narrative of what the branch does. No verbatim code.
2. **Attempts** — chronological log of each fixture-synthesis pass
   we ran, what we tried, and what the adversarial reviewer found
   wrong. One subsection per attempt.
3. **Why it's hard** — narrative summary of the structural challenge
   (e.g. "the defect lives at runtime API call, not file state").
4. **Next directions** — bullet list of concrete next things to try.
   Sized so each bullet is one "chew" worth.

## Sample entries

- [`Twi102.md`](Twi102.md) — `ShapeFix_Wire.FixDegenerated` modulo-index
  wraparound (WEAK_VALID — degenerate at index 3 with n=4 doesn't
  cross the boundary the bug needs)
- [`Tfa071.md`](Tfa071.md) — `ShapeFix_Face.FixPeriodicDegenerated`
  apex-curve direction (WEAK_VALID — fixture wraps the cone but the
  apex pole edge isn't constructed in the file)
- [`Tfa073.md`](Tfa073.md) — `ShapeFix_FixSmallFace.ComputeSharedEdgeForStripFace`
  asymmetry (WEAK_VALID — endpoint mismatch correct, but single-edge
  wires bypass the shared-edge construction code path)
- [`Tfa075.md`](Tfa075.md) — `ShapeFix_ComposeShell.MakeFacesOnPatch`
  non-WIRE fallback (WEAK_VALID — valid WIRE provided, but the bug
  needs a non-WIRE loop type)

## When to close a follow-up out

When a future attempt makes the fixture strong-VALID (adversarial
reviewer can't find a hole). Move the file to `fixture_followups/closed/`
with a final note on what fixed it. Don't delete — the historical
"why this took N attempts" record is the point.
