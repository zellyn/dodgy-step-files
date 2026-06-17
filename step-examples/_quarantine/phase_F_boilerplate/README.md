## Phase F regens — quarantined for boilerplate geometry

These 66 fixtures were originally truncated mid-construction (caught by
Part-21 validator's E_NO_CLOSE / E_NO_DATA / E_UNRESOLVED_REFS error
codes during the 2026-06-17 corpus audit).

Three haiku regen batches "fixed" them syntactically (Part-21
validator now reports `accept`), but a follow-up adversarial verify
of 15 sampled regens found **15 of 15 were generic unit-square
boilerplate** that doesn't demonstrate the catalog-claimed defect.

Examples:
* Tsh036 claims revolution but contains no SURFACE_OF_REVOLUTION
* Tsh021 claims bowtie / non-manifold vertex but has a normal vertex
  1-ring
* Tfa098 claims null-line edges but all edges reference valid entities
* Tsh027 claims two touching manifolds but contains a single shell
* Tfa145 claims two-splitter conflict but contains no inner wires

The pattern: haiku regen agents, when asked to "regenerate Tsh036 per
its catalog claim", produced a default unit cube + PRODUCT chain
instead of geometry matching the specific defect.

## Why quarantine instead of keep-and-fix-later

Generic boilerplate that *passes structural validation* is worse than
known-broken truncation: it gives a false sense of corpus coverage.
Keeping them out of `step-examples/<section>/` until proper regens
are produced.

## Regen plan

For each ID:
1. Read the catalog entry's Description and Expected kernel behavior
2. Construct geometry that *specifically* exhibits the defect mechanism
   (e.g. for "two touching manifolds": two MANIFOLD_SOLID_BREP entities
   sharing a planar face)
3. Use a stronger model than haiku, or constrain haiku with very
   explicit per-fixture geometric requirements

## Catalog impact

These IDs still have catalog entries (the entries were NOT modified
during this work). The catalog will count them as "claimed defect
classes" but the orphan-fixture check will flag them as missing from
disk. Acceptable until proper regen.
