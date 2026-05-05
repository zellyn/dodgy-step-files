# §12.1b Header & Instance-Numbering Validation Report

Adversarial validation of every `Lh*.stp` file in `step-examples/12-1b-header/`
against catalog §12.1b. For each file we ran
`uv run python -m step_corpus.validate <file> --json` and inspected the source
when the validator's signal was inconclusive. The verdict tries to **disprove**
the claimed defect; CONFIRMED means the defect is genuinely embedded in the
file as the catalog describes.

Note on `byte_signature.starts_with_iso_token=False`: every Lh fixture begins
with a `/* ... */` Part-21 comment block, so the literal first bytes are not
`ISO-10303-21;`. This is not a header defect — every file does carry the
opening token after the comment. We disregard this column when grading.

## Per-file Verdicts

- Lh002 — CONFIRMED (missing `END-ISO-10303-21;`; `ends_with_close_token=false`; OCCT/gmsh/ifcopenshell all reject).
- Lh003 — CONFIRMED (no `ENDSEC;` between HEADER and DATA; OCCT/gmsh reject; ifcopenshell rejects).
- Lh004 — CONFIRMED (FILE_SCHEMA absent; `byte_signature.file_schema=null`; ifcopenshell strict rejects "Unable to parse IFC SPF header"; OCCT/gmsh tolerantly accept — divergence as predicted).
- Lh005 — CONFIRMED (FILE_NAME has 8 args, expected 7; ifcopenshell rejects; OCCT/gmsh accept silently).
- Lh006 — CONFIRMED (`FILE_SCHEMA('AUTOMOTIVE_DESIGN')` single-paren; ifcopenshell "No schema loaded"; OCCT/gmsh accept).
- Lh007 — CONFIRMED (two schema names in one list); ifcopenshell rejects; OCCT/gmsh accept (last/first-wins).
- Lh008 — CONFIRMED (two separate FILE_SCHEMA records); validator picks last (`AP203_CONFIG_CONTROL_DESIGN`) — see notes.
- Lh009 — CONFIRMED (`AUTOMOTIVE_DESIGN_MIM` non-canonical long form, missing `_LF`).
- Lh010 — CONFIRMED (`implementation_level='Simulia 2018'` not in canonical set).
- Lh011 — CONFIRMED (timestamp `'27/12/2003 11:57'` — locale-formatted, not ISO-8601).
- Lh012 — CONFIRMED (unquoted timestamp `2026-04-26T00:00:00`).
- Lh013 — AMBIGUOUS (single-file fixture; defect is producer-side timestamp drift between exports and cannot be observed from one file. Header carries a sub-second clock-derived timestamp `2026-04-26T13:42:07.918473` consistent with the catalog's wild-corpus signature; treat as illustrative only).
- Lh015 — CONFIRMED (`VENDOR_INFO('SolidWorks 2024',...)` user-defined header entity without `!` prefix).
- Lh016 — CONFIRMED (Edition-3 `FILE_POPULATION` / `SECTION_LANGUAGE` / `FILE_INFO` present; `implementation_level='3;1'`).
- Lh017 — CONFIRMED (`#50=!MYCURVE(...)` — `!`-prefixed user-defined entity inside DATA section).
- Lh018 — CONFIRMED (`#10=cartesian_point(...)`, `Direction(...)`, `Axis2_Placement_3d(...)` — lower- and mixed-case keywords).
- Lh019 — CONFIRMED (header claims `IFC4` but DATA carries `IFC2X3_PROJECT`; ifcopenshell *accepts* — silent mis-binding, exactly the catalog-predicted failure mode).
- Lh022 — CONFIRMED (`#4=PRODUCT('part-a',...);` immediately followed by `#4=PRODUCT('part-b',...);`); OCCT/gmsh accept (last-wins overwrite).
- Lh023 — CONFIRMED (`# 12 = DIRECTION(...)`, `# /* note */ 13 = ...`, and a tab-split `#1<TAB>4`).
- Lh024 — CONFIRMED (two `DATA;...ENDSEC;` sections with reused `#10`, `#11`, `#12` IDs across sections; `DATA('extra',(...))` opens the second section).
- Lh025 — CONFIRMED (`@1=POSITIVE_LENGTH_MEASURE(2.5)` value-namespace alongside `#NNN` entity-namespace).
- Lh026 — CONFIRMED (Edition-3 `ANCHOR;`, `REFERENCE;`, `SIGNATURE;` sections; OCCT/gmsh reject with `IFSelect_RetFail`, ifcopenshell rejects — Edition-2 readers can't parse).
- Lh027 — CONFIRMED (`<part_anchor>=#42@x;` — non-numeric token after `#`).
- Lh028 — CONFIRMED (`<part_anchor>=#100;` but `#100` never defined in any DATA section).
- Lh029 — CONFIRMED (`FILE_SCHEMA(('CONFIG_CONTROL_DESIGN' /* legacy */, 'AUTOMOTIVE_DESIGN'))` — embedded Part-21 comment inside the schema-name list).
- Lh030 — CONFIRMED (`GEOMETRIC_TOLERANCE_RELATIONSHIP('Composite',...)` — Title-case where RP keyword `'composite'` is canonical).
- Lh031 — CONFIRMED (FILE_NAME originating-system field `'I-DEAS Master Series 8'`; no `NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION` in DATA; the substring-detection false-positive scenario).
- Lh032 — CONFIRMED (`#11=DIRECTION('mis-uses-#PI-as-constant',(#PI,0.0,0.0))` — `#PI` constant reference where REAL is required).

## Summary Block

- **Total fixtures**: 28 (Lh001/Lh014/Lh020/Lh021 are merged-into-other-IDs and not present, as expected).
- **CONFIRMED**: 27.
- **AMBIGUOUS**: 1 (Lh013, by construction — a single-file fixture cannot prove timestamp non-determinism).
- **FAIL**: 0.
- **Validator-rejection footprint**:
  - All five tiers reject Lh002, Lh003, Lh026 (missing END marker / missing ENDSEC / Ed.3 sections — structural defects that prevent the byte stream from being parsed at all).
  - ifcopenshell strict rejects every other Lh fixture (it does not load schemas in the AUTOMOTIVE_DESIGN / AP203 / CONFIG_CONTROL_DESIGN families used here, which is a property of the validator's IFC bias rather than of the fixtures).
  - OCCT (heal_on/off) and gmsh (autofix_on/off) tolerantly accept Lh004–Lh025, Lh027–Lh032. This **matches** the catalog-predicted divergence: many §12.1b defects (missing FILE_SCHEMA, arity mismatches, bare-string FILE_SCHEMA, multi-schema lists, duplicate FILE_SCHEMA, non-canonical implementation_level, unquoted timestamp, lower-case keywords, duplicate `#N`, `!`-prefixed entities, ANCHOR forward refs, `#PI` undefined constants) are accepted silently by mainstream tolerant readers — exactly the silent-corruption surface the catalog warns about.
- **Notable false-negatives observed in the wild tools** (this is *correct* corpus behaviour, not a fixture bug; documents the tolerance gap):
  - OCCT and gmsh accept Lh022 (duplicate `#4`), confirming the use-after-free / silent-overwrite class.
  - ifcopenshell *accepts* Lh019 (IFC4 header + IFC2X3 entities) — silent schema mis-binding, the catalog's predicted "Lh019 in the wild" outcome.

## Recommendations for FAILs

None. No fixture failed validation. The single AMBIGUOUS case (Lh013) is
inherent to its defect class:

- **Lh013**: To exercise build-time timestamp pollution, the corpus would need
  *two* otherwise-identical exports of the same input with different
  `FILE_NAME` timestamps (e.g. `Lh013_a.stp` and `Lh013_b.stp` with synthetic
  drift between them). Consider adding a paired sibling fixture, or annotating
  the catalog entry that single-file detection is impossible and the wild-corpus
  signature is *delta*-based (hash diff confined to the timestamp slot).

## Per-tier Sanity Cross-checks

- `byte_signature.ends_with_close_token`: false **only** for Lh002 (the file
  catalogued as missing the close marker). All other 27 files end with
  `END-ISO-10303-21;`. Matches expectation.
- `byte_signature.file_schema`: null **only** for Lh004 (the file catalogued
  as omitting FILE_SCHEMA). Every other fixture exposes a header schema name.
  Matches expectation.
- ifcopenshell `Unable to parse IFC SPF header` distinguishes structural header
  failures (Lh004) from supported-schema failures (`Unsupported schema: ...`)
  and from FILE_SCHEMA-shape failures (`No schema loaded` for Lh006, Lh007,
  Lh029 — the malformed/multi-schema cases). The discrimination is consistent
  with the predicted reject-class for each defect.
- OCCT loud-stderr warning `unexpected end of file, expecting ENDSTEP` fires
  for Lh002 only — matches the missing-end-marker fixture.

## Methodology Notes

- All validator runs used `uv run python -m step_corpus.validate <file> --json`
  from `/Users/zellyn/gh/cad/research/validation/`, captured to
  `/tmp/lh-validation/<name>.json`.
- Adversarial inspection used direct file reads to confirm each defect was
  textually present (FILE_SCHEMA arity, ANCHOR contents, duplicate `#N`,
  `!`-prefixed keywords, etc.).
- Verdicts side with the catalog **only** when both (a) the validator output
  is consistent with the predicted reject/accept profile, and (b) the source
  text contains the literal defect.
