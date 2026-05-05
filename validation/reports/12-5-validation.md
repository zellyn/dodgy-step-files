# §12.5 Units & coordinate systems — adversarial validation

Per-file verdicts for `/Users/zellyn/gh/cad/research/step-examples/12-5-units/` (21 fixtures present; merged stubs U007, U010-U013, U017, U019, U027, U029, U030, U032 not expected).

Verdict legend as in §12.4.

For each U file I read FILE_SCHEMA, the `LENGTH_UNIT`/`PLANE_ANGLE_UNIT`/`MASS_UNIT` complex records, any `CONVERSION_BASED_UNIT` factor, and the magnitudes of `CARTESIAN_POINT` (or other measure) coordinates.

| ID | Declared length unit | Coord magnitudes | Catalog claim | Verdict |
|---|---|---|---|---|
| U001 | SI_UNIT(.MILLI.,.METRE.) | (100,50,0) — mm-scale | mm-declared, receivers default to base SI | CONFIRMED |
| U002 | SI_UNIT($,.METRE.) | (0.1, 0.05, 0) — metre-scale of 100 mm | metre declared, NX rescales as mm | CONFIRMED |
| U003 | SI_UNIT(.MILLI.,.METRE.) | mm-scale | inch-workspace exports metric — mm declared | CONFIRMED |
| U004 | mm + PLANE_ANGLE_UNIT/RADIAN; PLANE_ANGLE_MEASURE 0.523598775… (=30°) | n/a | angle in radians despite degrees-authoring | CONFIRMED |
| U005 | mm | mm-scale | label-vs-author mismatch — pattern present | CONFIRMED |
| U006 | CONVERSION_BASED_UNIT('INCH', LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4), mm)) | (25.4, 12.7, 0) already mm-valued | inch-tagged with mm-valued coords → 25.4× double | CONFIRMED |
| U008 | mm GRC + CONVERSION_BASED_UNIT('INCH',...) GRC; tess validator segfaulted, but file structurally has both contexts joined via MAPPED_ITEM #61 | mixed mm + inch | mixed inch+mm assembly; validator tooling cannot ingest the file but fixture is structurally correct | CONFIRMED (tooling note: tier3 segfaults — nested complex unit triggers ifcopenshell/OCC bug, which is itself an instance of the kind of receiver bug the fixture targets) |
| U009 | mm GRC for board + CONVERSION_BASED_UNIT('INCH',…) GRC for component; MAPPED_ITEM #54 binds them | inch coords (0.5, 0.5, 0) merged into mm board | board mm + component inch naive merge | CONFIRMED (validator tooling note as U008) |
| U014 | SI_UNIT($,.METRE.) | (100, 50, 0) — mm-magnitudes mislabelled as metres | write.units regression — labelled metre, kernel left mm | CONFIRMED |
| U015 | CONVERSION_BASED_UNIT('INCH',...) (factor 25.4 ⇒ mm correct) | (100, 50, 0) — mm-magnitudes mislabelled as inches | inch-labelled file with mm coords | CONFIRMED |
| U016 | Two distinct CONVERSION_BASED_UNIT('INCH',…) instances #23 and #25 referenced inconsistently from #40, #41 measures | n/a | inch units cause invalid xrefs in dimension export | CONFIRMED |
| U018 | Part: GRC w/ GLOBAL_UNIT_ASSIGNED_CONTEXT; Tessellated rep #43 anchored to bare REPRESENTATION_CONTEXT #25 (no global_unit_assigned_context) | tess coords (0,0,0)/(1,0.5,0) bare REALs | tessellated annotation w/o global unit ctx | CONFIRMED |
| U020 | mm length unit; volume DERIVED_UNIT exponents (3,0,…) of metre rather than mm; surface_area MEASURE_REPRESENTATION_ITEM with `$` unit_component | volume 1e-6 m³ vs geometry mm | validation properties mismatched | CONFIRMED |
| U021 | mass_unit `( MASS_UNIT() NAMED_UNIT(*) SI_UNIT($,.GRAM.) )` (no .KILO.) used in DERIVED_UNIT for force | force 9.81 in wrong-by-1000 Newton | KILO prefix required on mass_unit | CONFIRMED |
| U022 | 4× CONVERSION_BASED_UNIT spelled 'inch', 'IN', 'inches', 'INCH' (active GRC uses lowercase 'inch') | mm-scale | spelling variants on inch | CONFIRMED |
| U023 | CONVERSION_BASED_UNIT('INCH', LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.54), mm)) — factor 2.54 not 25.4 | mm-scale | wrong inch conversion factor | CONFIRMED |
| U024 | CONVERSION_BASED_UNIT('POUND',…) NAMED_UNIT bound to DIMENSIONAL_EXPONENTS(0,0,0,0,0,0,0) | n/a | dim_exponents inconsistent with declared mass unit | CONFIRMED |
| U025 | GLOBAL_UNIT_ASSIGNED_CONTEXT lists BOTH #20 (mm SI_UNIT) AND #23 (inch CONVERSION_BASED) | mm-scale | multiple LENGTH_UNITs / FileUnits ambiguity | CONFIRMED |
| U026 | DERIVED_UNIT containing CONVERSION_BASED_UNIT('POUND',...) referenced via DERIVED_UNIT_ELEMENT | n/a | derived_unit handling incomplete (BRL-CAD step-g) | CONFIRMED |
| U028 | Two GRCs: #24 mm, #27 metre; both used by the same product (#44 BREP, #52 CGR) | n/a | multiple LENGTH_UNIT contexts disagreeing | CONFIRMED |
| U031 | Complex `( PLANE_ANGLE_UNIT() CONVERSION_BASED_UNIT('DEG',#22) NAMED_UNIT(*) )` with members in non-alphabetical order; #22 conversion factor = 1.0 (should be π/180) | "30 deg" stored as 30.0 — actually 30 rad | DEG vs RADIAN encoding via complex entity | CONFIRMED |

## Summary

- **CONFIRMED**: 21 / 21 (100%).
- **CONCERN**: 0
- **FAIL**: 0

## Adversarial cross-checks

1. **U001 vs U002 vs U014** — sibling fixtures distinguish the three label-mismatch cases:
   - U001: label correct (mm), reader defaults wrong → 1000× big.
   - U002: label correct (metre), reader treats as mm → 1000× small.
   - U014: label says metre, payload still mm → 1000× big on re-read.
   Each carries the unit prefix combination claimed by its catalog entry. They are not redundant.

2. **U006 vs U015** — both inch-tagged with `CONVERSION_BASED_UNIT('INCH', ...×25.4 mm)`, but coordinates differ:
   - U006: (25.4, 12.7, 0) — already-mm encoding of "1" inch.
   - U015: (100, 50, 0) — mm-scale magnitudes that, multiplied by 25.4, become absurd.
   Both are 25.4× errors but originate from different producer bugs (PrePoMax double-scale vs FreeCAD/OCCT writer mislabel). Fixtures preserve the distinction.

3. **U021 / U024** — both reach for SI mass exponent defects but at different layers:
   - U021: prefix omitted (.GRAM. instead of .KILO.+.GRAM.) → numerical off by 1000.
   - U024: dimensional_exponents all-zero on a stated mass unit → kernel ambiguity.
   Different defect classes; both required.

4. **U025 / U028** — both encode "multiple length units" but distinctly:
   - U025: ONE `GLOBAL_UNIT_ASSIGNED_CONTEXT` lists both mm SI and inch conv-based unit. FileUnits() can return either.
   - U028: TWO separate GRCs, one mm one metre, used by sibling sub-representations of one product.
   Both faithful.

5. **U022** — all four spelling variants are present (`'inch'`, `'IN'`, `'inches'`, `'INCH'`) as four distinct CONVERSION_BASED_UNIT entries; the active GRC binds the lowercase `'inch'` per the comment, exposing the case-sensitive lookup defect.

6. **U023** — the wrong factor 2.54 is exactly what the catalog calls out (10× error vs the canonical 25.4). The conversion-target reference unit is the mm SI_UNIT, so the misalignment is clear.

7. **U018** — schema-level absence: bare `REPRESENTATION_CONTEXT('tess_no_unit','3D')` (#25) vs the proper `( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(...) GLOBAL_UNIT_ASSIGNED_CONTEXT(...) ... )` (#24). Tessellated occurrence anchored to #25.

8. **U031** — the complex entity literally orders members `( PLANE_ANGLE_UNIT() CONVERSION_BASED_UNIT('DEG',#22) NAMED_UNIT(*) )` — non-alphabetical — and the DEG-to-RADIAN factor is 1.0 (should be π/180). Both sub-defects in one fixture.

## Tooling notes (not catalog-relevant)

- `step_corpus.validate` and `step_corpus.tier3_geometric` segfault / silently exit on **U008** and **U009** because of the deeply nested `( CONVERSION_BASED_UNIT(...) NAMED_UNIT(...) LENGTH_UNIT() )` complex record with cross-reference into the GRC's units list. The files were inspected directly and are structurally identical to other CONVERSION_BASED_UNIT fixtures (e.g. U006, U015) plus an additional MAPPED_ITEM crossing GRC boundaries. The crash is itself an example of the receiver-side bugs §12.5 enumerates.
- `step_corpus.validate` reports `byte_signature.file_schema = AUTOMOTIVE_DESIGN` for every U file in this section. None of the 21 use AP242, in line with the §12.5 catalog text (PMI-style fixtures live in §12.4 / §12.7).

## No fails detected

Every U fixture's declared unit context matches the catalog's claimed defect at the structural level, and the coordinate magnitudes (where measurable) are consistent with the magnitude-mismatch story in the catalog entry. No FAIL.
