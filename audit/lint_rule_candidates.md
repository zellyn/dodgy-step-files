# Lint-rule candidates from burn-down audits

Findings collected from `/tmp/burndown-*.md` reports during the
autonomous burn-down. Each rule corresponds to a recurring failure
mode the current `_construction_lint.py` does NOT catch.

These are **proposals**, not implementations. Implementing any of
them is out of scope for the autonomous run (per the scope-discipline
memory). Listed here for separate review.

## Rule 1: undefined-#-reference (catches truncation)

When any `#N` reference appears in a body but `#N=Type(...)` is never
declared in the same DATA section, the file is structurally broken —
typically because it was truncated mid-construction.

**Surfaced by**: Tsh043, N012 (burn-down 1 + 6)
**Approximate prevalence**: ~1-2% of older fixtures

Implementation: regex-scan all `#\d+` references, regex-scan all
`#\d+=` declarations, set-diff. False-positive risk: low — undefined
refs are unambiguously broken.

## Rule 2: fixture-file vs catalog-entry consistency (catches orphans)

Every `step-examples/<dir>/<ID>.stp` should have a matching
`### <ID> —` entry in `STEP_PROBLEM_CATALOG.md`, and every
`### <ID> —` entry should reference an existing file.

**Surfaced by**: Gs094-Gs138 orphans (Gs100, Gs112, Gs113, Gs132 etc),
plus possibly mirror orphan catalog-entries (not yet surveyed).

Implementation: set-compare filesystem against catalog JSON. False-
positive risk: low.

## Rule 3: forward-reference detection

A `#N` reference where N > the entity being defined, in cases where
Part-21 ordering matters (some readers tolerate, others reject).

**Surfaced by**: Twi246 (FILE_DESCRIPTION region + various)
**Approximate prevalence**: ~3-5% of older fixtures

Implementation: walk entity definitions in order, flag any reference
to a numerically greater ID. Exception list needed (some entity types
genuinely allow forward refs).

## Rule 4: FILE_DESCRIPTION arity (catches header-template bugs)

`FILE_DESCRIPTION` per ISO 10303-21 takes exactly 2 args:
`(LIST OF STRING, STRING)`. Templates that pack timestamps, version
numbers, or extra strings into FILE_DESCRIPTION are invalid.

**Surfaced by**: Twi246 (catalog FILE_DESCRIPTION has 7 fields
including timestamp + version#)

Implementation: regex-match `FILE_DESCRIPTION\((.*?)\);` and verify
the parsed argument list has exactly 2 items at the top level.

## Rule 5: non-ASCII arithmetic characters in numeric vectors

Unicode minus (U+2212, "−") instead of ASCII hyphen-minus (U+002D, "-")
in numeric tuples like `DIRECTION('',(−1.0,0.0,0.0))`. Part-21 lexer
only accepts ASCII numerics.

**Surfaced by**: burn-down 6 pattern note
**Approximate prevalence**: rare; usually copy-paste from markdown

Implementation: scan numeric-context bytes for any non-ASCII.

## Rule 6: empty-EDGE_LOOP detection (CEILING regression)

`EDGE_LOOP('',())` with empty tuple — claims to be a loop but has no
edges. Already partially caught by `_tier3_lint` per the placeholder
geometry memory; verify coverage.

**Surfaced by**: Tsh140, Tfa170 (broader audit 1)

## Rule 7: B-spline knot multiplicity sum check

`sum(knot_multiplicities) MUST equal n_control_points + degree + 1`
for each parametric direction in B_SPLINE_CURVE/SURFACE_WITH_KNOTS.

**Surfaced by**: Gn064, Gn091, Gs143 (wave 55), Gs153 (wave 58 intentional)
**Approximate prevalence**: ~5% of B-spline fixtures

Implementation: parse the B_SPLINE entity, sum multiplicity vector,
compare against (n_poles + degree + 1).

## Rule 8: parameter range alignment 3D vs pcurve

When an EDGE_CURVE has both a 3D curve and a pcurve, their parameter
ranges should match. Mismatches indicate either a healing target or
a synthesis bug.

**Surfaced by**: Gp117 (followup), wave 56 pattern
**Implementation difficulty**: medium — need to parse curve params.
**Should only flag** when no catalog claim explicitly addresses this
mismatch.

## Rule 9: Exemplar-quality gate

**Surfaced by**: burn-down 7 spot-check of Tfa150 (the current exemplar
for face synthesis). Tfa150 has 7× U+2212 minus signs AND 7-arg
FILE_DESCRIPTION instead of 2-arg. Tsh100 (shells exemplar) has the
familiar `((...),'2;1');` arity-imbalance pattern. These broken
exemplars propagate to every synthesis wave that uses them as
templates.

Implementation: a meta-lint that flags any fixture used as
`/Users/zellyn/gh/dodgy-step-files/step-examples/...` exemplar but
itself fails the other lint rules. Should also be part of new-exemplar
selection: don't pick a fixture as exemplar without lint-clean status.

Action: regenerate Tfa150, Tsh100, Twi200, N100, Gp100, Gn100, Gs100
as canonical-clean exemplars, then re-point synthesis prompts at the
new versions.

## Prevalence summary (very rough, from ~210 audited)

| Rule | Estimated rate |
|---|---|
| Rule 2 (orphans) | 30+ catalog gaps confirmed in Gs094-138 |
| Rule 1 (truncation) | ~1-2% |
| Rule 3 (forward refs) | ~3-5% |
| Rule 7 (knot sum) | ~5% |
| Others | <1% |

Rules 1, 2, 4 are the highest-impact / lowest-risk to implement.
