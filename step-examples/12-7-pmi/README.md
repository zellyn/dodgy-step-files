# §12.7 — PMI / GD&T defects (Pmi-prefix)

PMI / GD&T defects: tolerance-zone definitions, datum-reference frames, geometric-tolerance-with-datum-reference issues, presentation/representation linkage, draughting-callout defects, and AP242 PMI-specific structures.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.7) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Pmi001](Pmi001.stp) | Hole emitted as two half-cylinders breaks PMI feature association |
| [Pmi002](Pmi002.stp) | Blank/hidden dimensions exported as semantic dimensions |
| [Pmi003](Pmi003.stp) | Stacked vs composite tolerance frames mis-tagged |
| [Pmi004](Pmi004.stp) | Non-coplanar leader collapsed onto annotation plane loses attachment |
| [Pmi005](Pmi005.stp) | Mixing Polyline and Tessellated PMI presentation in one file |
| [Pmi006](Pmi006.stp) | Saved-view name location ambiguous (camera_model_d3 vs model_geometric_view) |
| [Pmi008](Pmi008.stp) | Tolerance precision: missing decimal-place qualifier fallback chain |
| [Pmi009](Pmi009.stp) | Rounding mode unspecified (ASME banker's vs ISO half-up) |
| [Pmi010](Pmi010.stp) | Tolerance zone form name from AP242 Ed.2 used in Ed.1 file |
| [Pmi012](Pmi012.stp) | Identical id_attribute reused across shape_aspect / dimensional_location / dimensional_size / shape_aspect_relationship |
| [Pmi013](Pmi013.stp) | Counterbore/countersink emitted as separate dimensions with no compound link |
| [Pmi014](Pmi014.stp) | annotation_plane: plane vs planar_box ambiguity |
| [Pmi015](Pmi015.stp) | Annotation geometry must be in plane PARALLEL to annotation_plane (small offset) |
| [Pmi017](Pmi017.stp) | Saved-view supplemental geometry split via "supplemental geometry subset" |
| [Pmi018](Pmi018.stp) | Identical Graphic PMI duplicated across saved views |
| [Pmi019](Pmi019.stp) | camera_model_d3 viewpoint not modeled per RP §9 |
| [Pmi020](Pmi020.stp) | Saved view missing required mapped_item |
| [Pmi022](Pmi022.stp) | Duplicate UUID on multiple identified_item |
| [Pmi023](Pmi023.stp) | Multiple UUIDs for the same identified_item |
| [Pmi024](Pmi024.stp) | Illegal characters inside a UUID value |
| [Pmi025](Pmi025.stp) | Datum reference frame contains identical datums |
| [Pmi026](Pmi026.stp) | Datum letters not unique within product |
| [Pmi027](Pmi027.stp) | datum_reference (legacy) used instead of datum_system in AP242 |
| [Pmi028](Pmi028.stp) | common_datum vs common_datum_list (multi-feature datum) |
| [Pmi029](Pmi029.stp) | Datum system carries mixed Datum_System / Datum_Reference SELECT array |
| [Pmi030](Pmi030.stp) | Negative projected tolerance zone length |
| [Pmi031](Pmi031.stp) | Projected zone projection_end is not a plane |
| [Pmi032](Pmi032.stp) | Datum target dimension equals zero |
| [Pmi033](Pmi033.stp) | placed_datum_target_feature shape mismatch |
| [Pmi034](Pmi034.stp) | placed_datum_target_feature shared DatumTargetType_Area null deref |
| [Pmi036](Pmi036.stp) | relating_shape_aspect / related_shape_aspect reversed |
| [Pmi037](Pmi037.stp) | shape_aspect.product_definitional flag wrong polarity |
| [Pmi039](Pmi039.stp) | Multiple plus_minus_tolerance on a single dimension |
| [Pmi041](Pmi041.stp) | dimensional_size vs dimensional_location confusion |
| [Pmi042](Pmi042.stp) | Empty semantic-text string in PMI |
| [Pmi043](Pmi043.stp) | Lower-case relation names where RP requires lower-case keywords |
| [Pmi044](Pmi044.stp) | DimensionalSize/GeometricTolerance attached only via PropertyDefinition (legacy AP203+G&DT) |
| [Pmi045](Pmi045.stp) | Graphic-only PMI with no semantic backing |
| [Pmi046](Pmi046.stp) | characterized_object with non-PMI draughting subtypes for graphic PMI |
| [Pmi047](Pmi047.stp) | Annotation has no annotation_plane |
| [Pmi048](Pmi048.stp) | Graphic PMI annotation missing color |
| [Pmi049](Pmi049.stp) | Tessellated geometry with no styled_item / color |
| [Pmi053](Pmi053.stp) | annotation_curve_occurrence leader with single point |
| [Pmi054](Pmi054.stp) | basis_curve for leader/annotation not on allowed list |
| [Pmi055](Pmi055.stp) | AP242 hole feature missing required attribute / inconsistent dims |
| [Pmi056](Pmi056.stp) | Tessellated alongside curve annotations for the same callout (AP242 ed2 conflict) |
| [Pmi057](Pmi057.stp) | PMI semantic vs presentation associativity lost on round-trip |
| [Pmi058](Pmi058.stp) | PMI visibility / configuration loss across saved views |
| [Pmi059](Pmi059.stp) | Surface status (cosmetic / construction / blanked) preservation lost |
| [Pmi060](Pmi060.stp) | Tolerance datum description NULL on re-export |
| [Pmi061](Pmi061.stp) | DATUM→ADVANCED_FACE chain not resolved for some link patterns |
| [Pmi062](Pmi062.stp) | STEP-to-glTF balloon inflation on AP242 (mesh count explosion) |
| [Pmi063](Pmi063.stp) | FILE_DESCRIPTION missing references to CAx-IF Recommended Practices |
| [Pmi065](Pmi065.stp) | DDP / EER cross-file PMI references break on repackaging |
| [Pmi066](Pmi066.stp) | Compound-feature semantics (HTC counterbore/countersink/counterdrill) per Hole RP |
| [Pmi067](Pmi067.stp) | `'INCH'` named differently on conversion_based_unit |
| [Pmi068](Pmi068.stp) | Annotation_plane orientation flipped on import (mirror determinant) |
| [Pmi069](Pmi069.stp) | `DIMENSIONAL_LOCATION_WITH_PATH` whose path connects unrelated shape aspects |
| [Pmi070](Pmi070.stp) | `GEOMETRIC_TOLERANCE_RELATIONSHIP` cycle (A→B→C→A) |
| [Pmi071](Pmi071.stp) | `PROJECTED_ZONE_DEFINITION` with zero offset |
| [Pmi072](Pmi072.stp) | `DIMENSION_PAIR` with mismatched units between paired members |
| [Pmi073](Pmi073.stp) | Compound feature with self-referential pattern membership |
| [Pmi074](Pmi074.stp) | Hole feature whose `depth` exceeds host-part bounding-box thickness |
| [Pmi075](Pmi075.stp) | `KINEMATIC_JOINT` referencing the same link as both ends (self-loop) |
| [Pmi076](Pmi076.stp) | Composite-property layer stack with contradictory material attributes |
| [Pmi077](Pmi077.stp) | PMI text values wrong when document LENGTH_UNIT is METRE but DIMENSIONAL_VALUE is in inches/mm without unit conversion |
| [Pmi078](Pmi078.stp) | PMI text location wrong after import |
| [Pmi079](Pmi079.stp) | Dimension lost after STEP export round-trip |
| [Pmi080](Pmi080.stp) | GD&T tolerance frame missing tolerance-zone plane reference |
| [Pmi081](Pmi081.stp) | GD&T saved-views label name silently emptied |
| [Pmi082](Pmi082.stp) | Saved-views and clipping planes lost on STEP read |
| [Pmi083](Pmi083.stp) | Annotation plane orientation flipped on GD&T import |
| [Pmi084](Pmi084.stp) | Coordinate-system connection points for dimensions missing |
| [Pmi085](Pmi085.stp) | Dimension names dropped on round-trip |
| [Pmi086](Pmi086.stp) | Empty IGES/STEP write loses general attributes |
