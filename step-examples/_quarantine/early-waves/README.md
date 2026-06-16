## Early-wave quarantine

Files here were synthesized in early waves before the fixture-template
mandates had stabilized. They were surfaced by an adversarial sample
sweep (2026-06-16) and confirmed via structural grep across the whole
prefix.

They are NOT deleted because:
1. Their catalog entries describe **real OCCT defects** that still need a
   fixture demonstration.
2. The file-level bugs are mechanical (template mistakes), not
   conceptual — they can be regenerated against the current canonical
   template without rethinking the defect.
3. Keeping them as quarantined evidence preserves the "why this took N
   attempts" record that motivates the `fixture_followups/` convention.

## Quarantined sets

### N055–N075 (20 files) — pre-fix LINE template

Two distinct bugs:

- **N055–N060 (6 files)** use `LINE('name', (#pt, #vtx))` — args
  wrapped in a list instead of comma-separated, second argument is a
  VERTEX_POINT where Part-21 LINE requires a VECTOR.
- **N062–N075 (14 files)** use `LINE('name', #pt, #(VECTOR(...)))` — the
  `#(...)` inline-instance syntax is invalid Part-21. Vectors must be
  declared as their own top-level entity and referenced by ID.

Correct form (see N076+ as exemplars):

```
#100=DIRECTION('',(1.0,0.0,0.0));
#101=VECTOR('',#100,1.0);
#102=LINE('',#10,#101);
```

### Tsh001–Tsh068 (55 files) — pre-PRODUCT-chain mandate

Missing `SHAPE_DEFINITION_REPRESENTATION` and the entire
PRODUCT/PRODUCT_DEFINITION/MANIFOLD_SURFACE_SHAPE_REPRESENTATION
chain (#9000–#9023 in the canonical template). Without that chain,
OCCT's `TransferRoots` cannot reach any of the topology — the file
loads but produces an empty result, so no healing pass is ever
exercised.

Tsh069+ have the chain and pass the sweep.

## Regen plan

When picked up:

1. Read the catalog entry (`### Tsh###` or `### N###`) for each ID in
   `STEP_PROBLEM_CATALOG.md` — the defect description there is
   authoritative.
2. Use the canonical fixture template (mandatory PRODUCT chain
   #9000–#9023; correct LINE/VECTOR/DIRECTION construction; closed
   EDGE_LOOPs; no forward refs).
3. Re-run an adversarial validator before promoting back to the
   active corpus.

See `fixture_followups/_early-waves-quarantine.md` for the collective
follow-up note that tracks this work.
