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
| [Pmi087](Pmi087.stp) | `GEOMETRIC_VALIDATION_PROPERTY` claimed volume disagrees with geometry |
| [Pmi088](Pmi088.stp) | `GEOMETRIC_VALIDATION_PROPERTY` claimed surface area disagrees with geometry |
| [Pmi089](Pmi089.stp) | `GEOMETRIC_VALIDATION_PROPERTY` claimed centroid disagrees with geometry |
| [Pmi090](Pmi090.stp) | Persistent UUID lost on round-trip (PMI association breaks) |
| [Pmi091](Pmi091.stp) | `ROUND_HOLE` feature whose `internal_diameter` exceeds host face's bounded extent |
| [Pmi092](Pmi092.stp) | `COUNTERBORE_HOLE` feature with counterbore diameter smaller than thru-hole diameter |
| [Pmi093](Pmi093.stp) | `RECTANGULAR_PATTERN` with zero spacing in one direction |
| [Pmi094](Pmi094.stp) | XCAF GD&T data does not round-trip to STEP AP242 PMI |
| [Pmi095](Pmi095.stp) | `SLOT` feature with length less than width (degenerate slot) |
| [Pmi096](Pmi096.stp) | `SLOT` blind depth exceeds host face thickness (through-slot in non-through context) |
| [Pmi097](Pmi097.stp) | `SLOT` end-condition declared `round_end` but profile is rectangular |
| [Pmi098](Pmi098.stp) | `SLOT` axis not perpendicular to host face |
| [Pmi099](Pmi099.stp) | Three coaxial `SLOT` features instead of a `RECTANGULAR_PATTERN` |
| [Pmi100](Pmi100.stp) | `GROOVE` feature with width = 0 (degenerate) |
| [Pmi101](Pmi101.stp) | `GROOVE` sweep does not close (open path on cylindrical host) |
| [Pmi102](Pmi102.stp) | `GROOVE` radial depth exceeds cylindrical host radius (depth wraps past axis) |
| [Pmi103](Pmi103.stp) | `BOSS` diameter smaller than host plate thickness (feature-class mismatch) |
| [Pmi104](Pmi104.stp) | `BOSS` height = 0 (zero-protrusion boss) |
| [Pmi105](Pmi105.stp) | `BOSS` base not coplanar with host face (boss floats above substrate) |
| [Pmi106](Pmi106.stp) | `SLOT`/`GROOVE`/`BOSS` reference non-existent host face (dangling GISU target) |
| [Pmi110](Pmi110.stp) | `COMPOSITE_FEATURE` wrapping sub-features that share no host-shape boundary |
| [Pmi111](Pmi111.stp) | `COMPOSITE_FEATURE` with cyclic sub-feature reference (A → B → A) |
| [Pmi112](Pmi112.stp) | `COMPOSITE_FEATURE` depth-attribute conflict between parent and sub-feature |
| [Pmi113](Pmi113.stp) | `COMPOSITE_FEATURE` with empty sub-features list |
| [Pmi114](Pmi114.stp) | `FLAT_PATTERN` bend-angle exceeding 180° |
| [Pmi115](Pmi115.stp) | `FLAT_PATTERN` bend-radius below material thickness |
| [Pmi116](Pmi116.stp) | `FLAT_PATTERN` with disjoint sub-features (no connecting bend line) |
| [Pmi117](Pmi117.stp) | `FLAT_PATTERN` reference to non-sheet host (host is solid, not surface) |
| [Pmi118](Pmi118.stp) | `FLAT_PATTERN` bend axis not parallel to bend line |
| [Pmi119](Pmi119.stp) | `PROFILE_FEATURE` with non-closed profile (open polyline used as boundary) |
| [Pmi120](Pmi120.stp) | `PROFILE_FEATURE` with self-intersecting profile (figure-eight loop) |
| [Pmi121](Pmi121.stp) | `PROFILE_FEATURE` depth direction not perpendicular to profile plane |
| [Pmi122](Pmi122.stp) | `PROFILE_FEATURE` with conflicting profile + draft angles (negative draft + closed profile) |
| [Pmi123](Pmi123.stp) | `PROFILE_FEATURE` used for sweep with no path |
| [Pmi125](Pmi125.stp) | `LOCATING_FEATURE` referencing a non-existent shape aspect (dangling target) |
| [Pmi126](Pmi126.stp) | `LOCATING_FEATURE` tolerance zone larger than the locator feature itself |
| [Pmi127](Pmi127.stp) | `MARKING` with empty inscribed text but non-zero font size |
| [Pmi128](Pmi128.stp) | `MARKING` placement plane perpendicular to the marked surface (text drawn into part) |
| [Pmi129](Pmi129.stp) | `MARKING` with multi-line text but no `line_spacing` attribute |
| [Pmi130](Pmi130.stp) | `THREAD` feature with non-positive pitch (negative or zero) |
| [Pmi131](Pmi131.stp) | `THREAD` claimed-fit class string outside the standard set (e.g. `'X1'`) |
| [Pmi132](Pmi132.stp) | `INTERNAL_THREAD` declared on an EXTERNAL_THREAD-shaped host (gender mismatch) |
| [Pmi133](Pmi133.stp) | `CHAMFER` size larger than the adjacent edge length (over-chamfer) |
| [Pmi134](Pmi134.stp) | `CHAMFER` with two contradictory `chamfer_angle` attributes (45 deg and 60 deg) |
| [Pmi135](Pmi135.stp) | `FILLET` feature with non-positive radius (zero or negative) |
| [Pmi136](Pmi136.stp) | `FILLET` radius larger than the adjacent face's smallest extent (rolling-ball doesn't fit) |
| [Pmi137](Pmi137.stp) | `COMPOUND_REPRESENTATION_ITEM` with `SET_REPRESENTATION_ITEM` null children |
| [Pmi138](Pmi138.stp) | `GEOMETRIC_TOLERANCE` magnitude encoded via `MEASURE_REPRESENTATION_ITEM` indirect chain |
| [Pmi139](Pmi139.stp) | Orphan `DRAUGHTING_ANNOTATION_OCCURRENCE` with broken STEP syntax |
| [Pmi140](Pmi140.stp) | OCCT V8 `PROPERTY_DEFINITION` string-metadata chain invisible to V7 readers |
| [Pmi141](Pmi141.stp) | AP242 coordinate-system connection-point entity silently dropped under OCCT V7.x |
| [Pmi142](Pmi142.stp) | AP242 Ed.2 `DIMENSION_SIZE` entity silently dropped by Ed.1 readers |
| [Pmi143](Pmi143.stp) | AP242 Ed.2 `SURFACE_TEXTURE_REPRESENTATION` entity dropped by Ed.1/AP214 readers |
| [Pmi144](Pmi144.stp) | AP242 Ed.3 `ANNOTATION_TO_ANNOTATION_LEADER_LINE` entity dropped by Ed.2/AP214 readers |
| [Pmi145](Pmi145.stp) | AP242 Ed.3 `BASIC_ROUND_HOLE` feature entity dropped by Ed.2/AP214 readers |
| [Pmi146](Pmi146.stp) | AP242 Ed.3 `TOPOLOGY_TO_GEOMETRY_MODEL_ASSOCIATION` bidirectional link dropped by Ed.2/AP214 readers |
| [Pmi147](Pmi147.stp) | AP242 Ed.3 `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION` per-item geometry reference dropped by Ed.2/AP214 readers |
| [Pmi148](Pmi148.stp) | AP242 Ed.3 `ANNOTATION_PLACEHOLDER_LEADER_LINE` entity dropped by Ed.2/AP214 readers |
| [Pmi149](Pmi149.stp) | AP242 Ed.3 `BASIC_ROUND_HOLE_OCCURRENCE_IN_ASSEMBLY` assembly-level occurrence dropped by Ed.2/AP214 readers |
| [Pmi150](Pmi150.stp) | AP242 Ed.3 `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE` atomic entity dropped by Ed.2/AP214 readers |
| [Pmi151](Pmi151.stp) | AP242 Ed.3 `ANNOTATION_TO_MODEL_LEADER_LINE` (2D annotation → 3D face) dropped by Ed.2/AP214 readers |
| [Pmi152](Pmi152.stp) | AP242 Ed.3 `AUXILIARY_LEADER_LINE` (secondary/mirror leader) dropped by Ed.2/AP214 readers |
| [Pmi153](Pmi153.stp) | AP242 Ed.3 `APLL_POINT` and `APLL_POINT_WITH_SURFACE` leader-endpoint types dropped by Ed.2/AP214 readers |
| [Pmi154](Pmi154.stp) | AP242 Ed.3 item-level topology-geometry association pair (`TOPOLOGY_TO_GEOMETRY_ITEM_ASSOCIATION` + `GEOMETRY_TO_TOPOLOGY_ITEM_ASSOCIATION`) dropped by Ed.2/AP214 readers |
| [Pmi155](Pmi155.stp) | AP242 Ed.3 data-equivalence assertion+inspection pair (`DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION` + `DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION`) dropped by Ed.2/AP214 readers |
| [Pmi156](Pmi156.stp) | `CIRCULAR_RUNOUT_TOLERANCE` + `TOTAL_RUNOUT_TOLERANCE` with datum-axis reference (semantic runout family) [VALID-BUT-HARD] |
| [Pmi157](Pmi157.stp) | `CIRCULAR_RUNOUT_TOLERANCE` with no datum reference (GD&T-illegal) [DEFECT] |
| [Pmi158](Pmi158.stp) | `SURFACE_PROFILE_TOLERANCE` + `LINE_PROFILE_TOLERANCE` with `ALL_AROUND_SHAPE_ASPECT` scope [VALID-BUT-HARD] |
| [Pmi159](Pmi159.stp) | `GEOMETRIC_TOLERANCE_WITH_MODIFIERS` carrying MMC / LMC / free-state / tangent-plane modifiers [VALID-BUT-HARD] |
| [Pmi160](Pmi160.stp) | `.MAXIMUM_MATERIAL_REQUIREMENT.` modifier applied to a `FLATNESS_TOLERANCE` (form tolerance, no size feature) [DEFECT] |
| [Pmi161](Pmi161.stp) | `DATUM_REFERENCE_COMPARTMENT` / `DATUM_REFERENCE_ELEMENT` with per-datum material modifier (MMC on datum B) [VALID-BUT-HARD] |
| [Pmi162](Pmi162.stp) | Full GD&T form/orientation/location symbol set beyond position/perpendicularity/flatness [VALID-BUT-HARD] |
| [Pmi163](Pmi163.stp) | `ANGULAR_SIZE` / `ANGULAR_LOCATION` semantic dimension with plane-angle unit [VALID-BUT-HARD] |
| [Pmi164](Pmi164.stp) | Single shared `COORDINATES_LIST` for a whole `TESSELLATED_SHELL`, 1-based integer indices [VALID-BUT-HARD] |
