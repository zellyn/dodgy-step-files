# OCCT tests/ mining log

**Status:** B1 from `BACKLOG.md`, in progress.

Pattern-mine OCCT's own `tests/` tree for STEP-parsing wisdom not yet
captured in our catalog. Per the user's audit-pattern memory, the
methodology is:

1. **Sample**: random-stratified pick from `tests/de/step/`, `tests/bug/`,
   `tests/parser/`, etc.
2. **Extract**: the OCCT-test recipe (what defect it exercises), the
   entity types involved, the unique structural signature.
3. **Match**: search our existing catalog for the defect class. Record
   match-or-novelty.
4. **Synthesize**: for non-matches, write a Python builder source that
   pattern-matches the *defect*, never copies OCCT's bytes (LGPL-clean).
5. **Verify**: run the adversarial-verify loop on the new fixture.

## Provenance

Source repo: https://github.com/Open-Cascade-SAS/OCCT (LGPL 2.1).
Cloned shallow to `/tmp/occt-mining/occt` for read-only inspection.
Never copied verbatim into our corpus.

## Waves

### Wave 1 — initial inventory + 30-fixture sample

Status: inventory + BM25 search done. Synthesis pending.

- [x] Enumerate `tests/de/step_*` and `tests/bugs/step/` directories.
      Total: 1041 test recipes (830 in `de/step_*`, 212 in `bugs/step`,
      18 in `de_mesh/step_*`).
- [x] Extract recipe metadata: 449 have prose description; 159
      reference a `.stp` filename; 312 carry TODO/known-bug markers.
- [x] BM25-search each prose description against our 2307-entry catalog.
      With a relevance threshold of 20: **192 lexical hits, 257 misses**
      (57% nominal-novelty rate before noise filtering).
- [x] Filter generic noise (TODO test syntax, "faulty_N" variables, IGES
      tests, separator banners). Remaining signal: **47 candidate
      novel-defect descriptions** in `/tmp/occt_mining_misses_filtered.json`.
- [ ] Manual review of the 47 candidates. Classify each:
      "true novelty (synthesize)" vs "matches an existing entry our BM25
      missed (annotate)" vs "noise (drop)".
- [ ] Synthesize the true-novelty subset as new Wave-1 fixtures via the
      Python builder.

### Wave 1 candidate themes (sampled from filtered misses)

A few recurring themes in the 47-candidate set worth synthesizing:

- **AP238 / STEP-NC entity import** (`bug29415`, `bug28414`, `bug33261`,
  `bug33053`, `bug33331`): "Step reader cannot read the surfaces of the
  main body of the shape", "STEP entity not correctly read",
  "Empty shape after reading process", "Compound with vertex is ignored",
  "Unsupported Representation Items". Likely covered partially by our
  `M*` section but new specific entities may be novel.
- **Export-side defects** (`bug32817_1` "writing untrimmed Curve",
  `bug32556` "toroidal part corrupted while writing"). Our `Wr*` section
  has 52 entries; targeted writer-defect coverage may be incomplete.
- **Import crashes** (`bug348_2/3/4` "Crash on importing STEP file").
  We have signal-segfault fixtures (Ad015, Ad077, Gp001, Gs026) but
  three more numbered import-crash variants suggest a class we may
  cover incompletely.
- **Annotation/PMI mismatch** (`bug28449` "wrong Annotation plane").
- **Scaling-transform regression** (`bug_ocp1949` "Apply a scaling
  transformation to STEP; Error: wrong position of the i...").

### Future waves

Follow the same recipe. Track per-wave novelty rate to detect
convergence (low single-digit % novelty = approaching the bound).

## Provenance: source data

- `tests/bugs/step/` — 212 OCCT bug-fix tests (named by Mantis IDs)
- `tests/de/step_{1..5}/` — 830 STEP data-exchange tests (named by
  letter+number, e.g. A1, B12, C42)
- `tests/de_mesh/step_{read,write}/` — 18 STEP mesh data-exchange tests

Inventory cached in `/tmp/occt-test-inventory.json` (1041 records).
Filtered misses in `/tmp/occt_mining_misses_filtered.json` (47 entries).
Hits in `/tmp/occt_mining_hits.json` (192 entries).
