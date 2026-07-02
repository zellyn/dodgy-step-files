# Q5 Quarantine Candidates — 2026-07-01

## Method

Mutation test (`_mutation_test.py --mutations 3 --workers 6`) run against 4 metadata-heavy sections after baseline cache repopulation. A fixture is a "quarantine candidate" when 3 independent mutations of a target byte all leave the validate2 summary unchanged from baseline (`status=undetected`) — meaning the defect is not observable by any wired oracle at the BRep-load layer. These fixtures document a defect that lives in bytes/context that OCC does not parse into shape topology.

## Section-Level Results

| Section          | Total | Detected | Undetected | No-baseline | No-target-byte | Oracle-invisible % |
|------------------|-------|----------|------------|-------------|----------------|--------------------|
| 12-1a-encoding   | 54    | 23       | 29         | 0           | 2              | **53.7%**          |
| 12-1b-header     | 46    | 35       | 7          | 0           | 4              | 15.2%              |
| 12-5-units       | 37    | 26       | 11         | 0           | 0              | 29.7%              |
| 12-7-pmi         | 100   | 97       | 0          | 3           | 0              | 0.0%               |

Key finding: §12-7-pmi is 100% oracle-active — PMI mutations flip the summary. §12-1a-encoding is majority oracle-invisible.

## Quarantine Candidates (47 fixtures)

### §12-1a-encoding — 29 fixtures
Le004, Le007, Le008, Le009, Le012, Le013, Le014, Le016, Le023, Le026, Le027, Le029, Le032, Le036, Le037, Le038, Le040, Le041, Le042, Le043, Le044, Le046, Le048, Le049, Le051, Le052, Le053, Le054, Le058

### §12-1b-header — 7 fixtures
Lh007, Lh009, Lh010, Lh015, Lh016, Lh018, Lh030

### §12-5-units — 11 fixtures
U002, U004, U005, U006, U014, U018, U022, U026, U033, U034, U035

## Recommended Next Step (design decision — awaiting direction)

Three options for tagging these fixtures:

1. **Notes-only `Provenance tier:` annotation** — follows the pattern already implicit in `_category_lint.EXEMPT_ASSEMBLY_PRESENCE` (which references "Provenance tier: annotations in the catalog Notes"). No schema change; text-only edit to each entry's Notes field.
2. **New `provenance_tier` catalog field** — adds a first-class field via `_build_catalog_json.py` (writer-time metadata). Requires parser + renderer + JSON schema updates. Higher blast radius but cleaner query surface.
3. **New `oracle_active: false` boolean** — narrower than provenance tier; specifically marks fixtures where no wired oracle can flip on mutation. Similar infrastructure cost to option 2.

Option 1 is the lowest-risk, matches existing `_category_lint` foreshadowing, and requires no code changes — just 47 catalog Notes edits.

## Raw JSON

Per-section JSON at `/tmp/qmut_12-{5-units,1a-encoding,1b-header,7-pmi}.json`. Each entry has `id`, `status`, `baseline`, and the mutation results.

## Source Files

- Mutation test: `validation/src/step_corpus/_mutation_test.py`
- Baseline cache: `/tmp/cad-v2-out/` (2517 fixtures, freshly repopulated 2026-07-01 via `_run_corpus --workers 4`)
- Tier-3 cache: `/tmp/cad-v2-out-tier3/` (2680 files, retained from earlier run)
