# §12.5 — Unit & coordinate-system defects (U-prefix)

Unit and coordinate-system defects: missing/conflicting `length_unit` / `plane_angle_unit` / `solid_angle_unit`, named-unit / SI-unit confusion, conversion-based-unit errors, `unit_assigned_context` mismatches, and coordinate-frame inconsistencies.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.5) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [U001](U001.stp) | Solid Edge mm exported STEP read as meters by Inventor (imported part 1000 times bigger than expected) |
| [U002](U002.stp) | Onshape always emits METRE; NX rescales as if mm (1000× too small) |
| [U003](U003.stp) | Onshape inch workspace exports metric STEP (inch-shaped coordinates in mm `LENGTH_UNIT` context) |
| [U004](U004.stp) | Inventor STEP export switches angle unit from DEGREE to RADIAN, breaks doc preference on round-trip |
| [U005](U005.stp) | Plant 3D exports STEP whose `LENGTH_UNIT` context disagrees with authored drawing units (sub-mm coordinates in mm context) |
| [U006](U006.stp) | PrePoMax double-applies inch→mm scaling on inch STEP (25.4× too large) |
| [U008](U008.stp) | NX subassemblies with mixed inch + mm — inconsistent per-part scaling |
| [U009](U009.stp) | KiCad assembly: board mm + component model in inch, naive merge breaks scale |
| [U014](U014.stp) | `LENGTH_UNIT` is bare `SI_UNIT(METRE)` but coordinates are mm-sized (`STEP Export` ignores `write.units` since OCCT 7.8 regression) |
| [U015](U015.stp) | FreeCAD/OCCT 7.8.1: model in mm but file labelled as inches (re-import 25.4× too large) |
| [U016](U016.stp) | Duplicate `CONVERSION_BASED_UNIT` 'INCH' instances (factor 25.4) cause invalid cross-references in dimension export |
| [U018](U018.stp) | Tessellated annotation coordinates with no global unit context (silent 25.4×) |
| [U020](U020.stp) | Validation properties (mass / area / volume) emitted with units mismatched to GRC |
| [U021](U021.stp) | KILO prefix REQUIRED on `mass_unit` referenced from a derived SI unit (Newton) |
| [U022](U022.stp) | `'INCH'` spelled as `'inch'` / `'IN'` / `'inches'` on `CONVERSION_BASED_UNIT` |
| [U023](U023.stp) | Conversion factor for `'INCH'` is wrong / omitted |
| [U024](U024.stp) | `dimensional_exponents` inconsistent with declared unit |
| [U025](U025.stp) | Reader API reports wrong primary length unit on multi-context files |
| [U026](U026.stp) | `derived_unit` / non-SI unit handling incomplete (BRL-CAD step-g) |
| [U028](U028.stp) | Two `GEOMETRIC_REPRESENTATION_CONTEXT` instances with different `LENGTH_UNIT` (mm BRep vs metre PMI/CGR) |
| [U031](U031.stp) | `CONVERSION_BASED_UNIT('DEG',#9)` / DEG vs RADIAN encoding via complex entity |
| [U033](U033.stp) | Unit-default flag silently overridden by file's first unit-record |
| [U034](U034.stp) | Mile-to-millimetre conversion factor mis-applied on export |
| [U035](U035.stp) | Exporting ellipse with non-mm unit corrupts geometry |
| [U036](U036.stp) | `BinXCAF` does not preserve length unit |
| [U037](U037.stp) | `RescaleGeometry` does not rescale triangulations |
| [U038](U038.stp) | STEP read produces unexpectedly enormous scaling on parts (MAPPED_ITEM target uses MM while source REPRESENTATION_MAP context uses METRE: cross-context unit composition error) |
