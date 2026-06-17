# Autonomous session summary — 2026-06-17

## Bookends

- **Started**: user said "I'm going to sleep, so after that, please do
  what you think is best next. And then again." (after wave 52 audit
  + initial regen work was committed earlier in the day)
- **Ended**: 20 waves of synthesis (53-72) + 7 broader burn-down
  audits, with this summary as the final commit.

## Numbers

| Metric | Pre-session | Post-session |
|---|---:|---:|
| Active v3-prefix fixtures | ~1280 | ~1450 |
| Total catalog entries (canonical) | 1972 | 2242 |
| Adversarially verified VALID | ~95 | 412 |
| Known weak/invalid | 11 | 61 |
| `fixture_followups/` entries | 9 | 15 |
| Local commits (this session) | 0 | 36+ |
| Lint-rule candidates documented | 0 | 9 |

All commits pushed to origin/main. Nothing tagged (per "push but not
tag if any known problems" policy).

## Cadence

5 parallel agents per cycle, ~5-8 minutes wall-clock per cycle:
1. Wave NA — 5 synth fixtures, prefix X
2. Wave NB — 5 synth fixtures, prefix Y
3. Wave NC — 5 synth fixtures, prefix Z
4. Verify wave N-1 — 7 of 15 sampled
5. Burn-down chunk — 30 random older-corpus fixtures

After each cycle: merge catalog fragments, refresh audit tracking,
commit, push. ~36 commits total.

## What the burn-down found (and why it matters)

The per-wave verify samples (7 fixtures from each fresh wave) were
catching same-day synthesis bugs effectively. The broader burn-down
revealed a **second class of issues** in older waves the per-wave
verify never sampled:

1. **Truncated fixtures** (Tsh043, Tsh028, N012, Tfa175) — files that
   open the DATA section but never close it, leaving entity
   references unresolved. Caused by haiku-batch truncation during
   prior synthesis recoveries.

2. **FILE_DESCRIPTION arity bugs** (Twi246, Twi262, and the systemic
   ~103-file pattern noted earlier) — header templates that pack
   timestamp+version+strings into FILE_DESCRIPTION instead of the
   spec's `(LIST OF STRING, STRING)` 2-arg form.

3. **Unicode minus signs (U+2212)** in numeric tuples like
   `DIRECTION('',(−1.0,0.0,0.0))` — Part-21 lexer wants ASCII `-`.

4. **B-spline knot multiplicity violations** (Gn064, Gn091, Gp052,
   Gs089) — `sum(knot_mults) != n_poles + degree + 1`.

5. **Forward references** in older imports (Gp053) — `#N` referenced
   before its declaration.

6. **Orphan fixtures vs catalog gaps** (Gs094-Gs138 range) — ~45
   fixture files exist without matching `### ID —` catalog entries.

7. **Exemplar contamination** (Tfa150, Tsh100) — the templates
   downstream synthesis waves reference are themselves malformed,
   propagating their bugs into newly-synthesized fixtures.

## Lint-rule candidates (full list in `audit/lint_rule_candidates.md`)

1. undefined-#-reference (catches truncation)
2. fixture-file vs catalog-entry consistency (catches orphans)
3. forward-reference detection
4. FILE_DESCRIPTION arity check
5. non-ASCII arithmetic in numeric vectors
6. empty-EDGE_LOOP (CEILING; partial coverage today)
7. B-spline knot multiplicity sum
8. parameter range alignment 3D vs pcurve
9. exemplar-quality gate (new today)

Rules 1, 2, 4 highest-impact / lowest-risk.

## Recommended next actions

These are proposals; nothing started without user authorization.

### Immediate (low-risk)

1. **Implement lint rules 1, 2, 4** — undefined-ref, orphan check,
   FILE_DESCRIPTION arity. Each is regex-based, ~30 lines.
2. **Regenerate the 7 exemplars** (Tfa150, Tsh100, Twi200, N100,
   Gp100, Gn100, Gs100) with strict lint-clean templates. Re-point
   synthesis prompts at the new versions.
3. **Backfill Gs094-Gs138 catalog entries** — orphan fixtures with
   real defect claims that just need their `### ID —` entries added.

### Medium-term

4. **Implement lint rules 3, 5, 7** — forward-ref, non-ASCII,
   knot-sum. More involved but high-value.
5. **Continue burn-down** — 976 fixtures still unverified at session
   end. Rate was ~30/cycle; ~33 more cycles to complete.
6. **Pause new-wave synthesis** until exemplars are fixed. Otherwise
   each new wave inherits propagated bugs.

### Larger work

7. **Audit + regenerate** the ~60 weak/invalid fixtures identified
   today. Each has a follow-up note in `fixture_followups/`.
8. **Consider switching synthesis model** — haiku produces ~75% strong-
   VALID on first pass; sonnet (the few times it didn't 529) was
   higher. Cost vs reliability tradeoff.

## What's stable / what's risky

**Stable**:
- The per-wave synth+verify pipeline (3 synth + 1 verify per cycle)
- The merge+normalize catalog flow with em-dash normalization
- The audit tracking files in `audit/`
- All 9 documented lint-rule candidates

**Risky** (proceed with care):
- Bulk corpus modifications (any cross-prefix script touching
  hundreds of files) — see what happened with the cookie-position
  normalization earlier today
- Regenerating exemplars without confirming they'll still match
  catalog claims for those exemplar IDs
- Trusting the burn-down agents to count file existence — one
  agent in chunk 4 hallucinated 19 missing files

## Files of interest

- `audit/audit_remaining.txt` — 976 unverified IDs
- `audit/verified_valid.txt` — 412 confirmed VALID
- `audit/weak_or_invalid.txt` — 61 flagged
- `audit/lint_rule_candidates.md` — 9 proposed rules
- `fixture_followups/` — 15 individual follow-up notes
- `/tmp/burndown-*.md` — 7 burn-down reports (ephemeral; would
  benefit from being moved to `audit/burndown-reports/` in a future
  commit)
