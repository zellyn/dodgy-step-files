# §12.6 — Assembly-hierarchy defects (A and FreeCAD-origin P)

Assembly-hierarchy defects: `next_assembly_usage_occurrence` errors, product-definition cycles, missing/duplicate `mapped_item` references, transformation-matrix issues, `context_dependent_shape_representation` wiring failures, and FreeCAD-origin assembly defects (P-prefix).

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.6) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [A001](A001.stp) | Duplicated component instances collapsed to a single transform on export |
| [A002](A002.stp) | Hidden / suppressed bodies leak into export, or are dropped silently |
| [A003](A003.stp) | Empty / phantom assembly nodes (PRODUCT_DEFINITION with no shape) |
| [A004](A004.stp) | `NEXT_ASSEMBLY_USAGE_OCCURRENCE` references missing `PRODUCT_DEFINITION` (unresolved NAUO target) |
| [A005](A005.stp) | Lost assembly hierarchy on round-trip (flatten to single CATPart / single solid) |
| [A006](A006.stp) | Components collapse to (0,0,0) / placement transforms lost |
| [A007](A007.stp) | SHAPE_REPRESENTATION_RELATIONSHIP with swapped/mixed rep_1/rep_2 axis placements |
| [A008](A008.stp) | AP242 Ed.2 widened SELECT for product_definition_relationship.related/relating |
| [A009](A009.stp) | NAUO references PRODUCT_DEFINITION_SHAPE instead of PRODUCT_DEFINITION |
| [A010](A010.stp) | NAUO instance name lost on round-trip / re-export |
| [A011](A011.stp) | Naming collision: same component referenced by colliding `PRODUCT.name` across sub-assemblies |
| [A012](A012.stp) | Self-reference / cyclic external file reference |
| [A013](A013.stp) | STEP assembly reader returns success even when external-reference files are missing |
| [A014](A014.stp) | EXTERNAL_ANCHOR uniqueness (1:1 anchor↔entity) violated; orphan EER source |
| [A016](A016.stp) | UDA on multi-level reference designator (MLRD) ignored |
| [A017](A017.stp) | Component labels/colors/names lost when subshape carries a transform on round-trip |
| [A018](A018.stp) | STYLED_ITEM at wrong scope: assembly-level color override lost or misbound |
| [A019](A019.stp) | Per-face `STYLED_ITEM` colours collapse to a single hue when multiple `ADVANCED_FACE`s share one supporting `PLANE` |
| [A020](A020.stp) | Bare STYLED_ITEM at top level (no MDGPR / DRAUGHTING_MODEL parent) |
| [A021](A021.stp) | CDORSI WR1 violated by per-component styling in Saved View |
| [A022](A022.stp) | PRESENTATION_LAYER_ASSIGNMENT collisions / namespace abuse |
| [A023](A023.stp) | Mapped_item / representation_map identity transform requirement (Saved Views) |
| [A024](A024.stp) | `MAPPED_ITEM` `AXIS2_PLACEMENT_3D` with left-handed (mirrored, negative-determinant) frame |
| [A025](A025.stp) | Names with special / non-ASCII / encoded characters lost or corrupted |
| [A026](A026.stp) | Quadratic-time assembly graph traversal: many `NEXT_ASSEMBLY_USAGE_OCCURRENCE` siblings share a single leaf `PRODUCT_DEFINITION` |
| [A028](A028.stp) | Reference loss when defeaturing / simplifying for CAE |
| [A029](A029.stp) | User-Defined Attribute (UDA) target-binding inconsistency |
| [A030](A030.stp) | Edition-mixed Part 21 file (header schema vs instance schema) |
| [A031](A031.stp) | Schema migration: retired AP214/AP203 kinematics entities |
| [A032](A032.stp) | Schema migration: enum-value reordering between AP242 Ed.2 and Ed.3 |
| [A033](A033.stp) | `applied_external_identification_assignment` /`product_definition_with_associated_documents` name dropped |
| [A034](A034.stp) | CheckSRRReversesNAUO segfault on SDR with SHAPE_ASPECT instead of PROPERTY_DEFINITION |
| [A035](A035.stp) | Product with both sub-assemblies and direct shape |
| [A036](A036.stp) | Hybrid AP203 (≤1998) using ShapeAspect-attached SDR |
| [A037](A037.stp) | Implicit / minimalist product structure missing entirely |
| [A038](A038.stp) | Constructive Geometry Representation Relationship — assembly axis placements |
| [A064](A064.stp) | Subshape names not transferred on STEP import |
| [A065](A065.stp) | Empty `AppliedGroupAssignment` raises exception in writer |
| [A066](A066.stp) | `UpdateAssemblies` produces wrong compounds for located roots |
| [A067](A067.stp) | Baking placements into geometry breaks shared-subshape sharing |
| [A068](A068.stp) | Color of root label not exported through XCAF |
| [A069](A069.stp) | Material with zero density blocks STEP write |
| [A070](A070.stp) | Layers not imported from STEP file |
| [A071](A071.stp) | Visibility flag of free shapes lost on STEP write |
| [A072](A072.stp) | Compound with single vertex written as compound-of-two-points |
| [A073](A073.stp) | `Expand Compounds` loses sub-shape locations |
| [A074](A074.stp) | Texture lost when saving binary XBF after STEP import |
| [A075](A075.stp) | Free-shape-after-import is empty |
| [A076](A076.stp) | General attributes (AP242 GENERAL_PROPERTY) dropped on import |
| [A077](A077.stp) | Sub-assembly extraction loses XDE attributes |
| [A078](A078.stp) | Compound-with-vertex emitted as empty in non-manifold export |
| [A079](A079.stp) | Visibility / colour ignored for sub-shapes by `XCAFPrs_AISObject` |
| [A080](A080.stp) | Hierarchy & colours lost on partial-document IGES/STEP write |
| [A081](A081.stp) | Material attribute overridden by generic colour on round-trip |
| [A082](A082.stp) | Big-path STEP write fails with name >150 characters |
| [A083](A083.stp) | STEP exporter generates bad geometry for revolution / extrusion since 7.4.0 |
| [A084](A084.stp) | STEP exporter writes untrimmed curve where trimmed expected |
| [A085](A085.stp) | STEP exporter loses `COMPSOLID` in nonmanifold writes |
| [A086](A086.stp) | Step exporter not respecting `write.step.schema` configuration |
| [A087](A087.stp) | STEP exporter loses shapes after import-export cycle |
| [A088](A088.stp) | Empty assembly causes writer to throw |
| [A089](A089.stp) | Sub-shape names lost in non-manifold STEP output |
| [P001](P001.stp) | Schema variant: CONFIG_CONTROL_DESIGN with no PRODUCT entity |
| [P002](P002.stp) | Non-UTF-8 (GB18030 / locale code page) in string literals |
| [P003](P003.stp) | Control characters / illegal-XML bytes in name strings corrupt downstream documents |
| [P005](P005.stp) | Inverted spherical face on certain sweep orientations |
| [P006](P006.stp) | 360° revolution of arc-of-ellipse produces self-intersecting solid |
| [P007](P007.stp) | High-curvature B-spline surface flattens between OCCT versions |
| [P008](P008.stp) | Long helix represented as huge B-spline causes catastrophic import time |
| [P009](P009.stp) | Helical sweep tessellates with garbled facets at seam |
| [P010](P010.stp) | Standalone AXIS2_PLACEMENT_3D entities silently dropped |
| [P011](P011.stp) | AP242 PMI / GD&T / kinematics annotations silently discarded |
| [P012](P012.stp) | STEP-XML (`.stpx`) and compressed (`.stpz`) variants unsupported |
| [P013](P013.stp) | AP203-claimed file uses AP214/AP242-only entities |
| [P014](P014.stp) | `PCURVE` start point shifted in V from 3D `EDGE_CURVE` lift (UV drift beyond tolerance after Boolean) |
| [P015](P015.stp) | Non-manifold or open shell exported as `MANIFOLD_SOLID_BREP` |
| [P016](P016.stp) | Pre-Boolean operands shipped alongside result solid |
| [P017](P017.stp) | Free wires in a top-level COMPOUND silently dropped |
| [P018](P018.stp) | Improper rotation (negative determinant) in `AXIS2_PLACEMENT_3D` |
| [P019](P019.stp) | Default-emitted full transparency renders objects invisible |
| [P021](P021.stp) | Edge-curve geometry mismatches face geometry within tolerance |
| [P022](P022.stp) | Helical seam degeneracy from arc-by-3-points + 360° revolve |
| [P023](P023.stp) | Mixed `FACE_OUTER_BOUND` orientation flag (negative-volume pocket) |
| [P024](P024.stp) | Flattened sub-assembly hierarchy after merge |
| [P025](P025.stp) | Body name overwritten by last-operation label on export |
| [P026](P026.stp) | `LENGTH_UNIT(.MILLI., .METRE.)` context but `CARTESIAN_POINT` coordinates pre-scaled ×1000 (global OCCT unit setting contaminated across in-process clients) |
| [P027](P027.stp) | Boolean-history Faces with degenerate hole-loop pcurves crash writer |
| [P028](P028.stp) | Empty/null shape entries in OCAF document corrupt writer |
