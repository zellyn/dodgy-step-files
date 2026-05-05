# §12.7 PMI / GD&T — Adversarial Validation

57 files (Pmi001–Pmi068, with Pmi007/011/016/021/035/038/040/050/051/052/064 merged stubs not present) cross-checked against catalog claims via PMI/GD&T entity counts.

All files declare schema `AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF` (Pmi010 has slightly older minor version `1 1 1` vs `1 1 4`). All files are 2.1–4.2 KB minimal reproducers focused on the specific PMI defect.

Notation: `DS`=DIMENSIONAL_SIZE, `DL`=DIMENSIONAL_LOCATION, `GT`=GEOMETRIC_TOLERANCE family (POSITION/PARALLELISM/PERPENDICULARITY etc.), `DTM`=DATUM, `DSY`=DATUM_SYSTEM, `DRC`=DATUM_REFERENCE_COMPARTMENT, `DRE`=DATUM_REFERENCE_ELEMENT, `AP`=ANNOTATION_PLANE, `DM`=DRAUGHTING_MODEL, `SA`=SHAPE_ASPECT, `PMT`=PLUS_MINUS_TOLERANCE.

## Pmi entries

| ID | Key entities | Diagnostic | Verdict |
|---|---|---|---|
| Pmi001 | DTM, DTM_FEATURE, DSY, DRC, DRE, DS, PMT, AP, GISU, SA×1, SA_REL=1, POSITION_TOLERANCE | full PMI chain incl. GISU + SA_REL → matches "shared shape_aspect with multi-GISU" recipe | CONFIRMED |
| Pmi002 | DS=2, PMT=1, SA=1, AP=1, MEASURE_REPRESENTATION_ITEM=2, SHAPE_DIMENSION_REPRESENTATION=2 | 2 dimensions (one real one blank) — exact recipe | CONFIRMED |
| Pmi003 | DTM, DSY, DRC, DRE, AP, SA=2, PARALLELISM_TOLERANCE=2, GEOMETRIC_TOLERANCE_RELATIONSHIP=1 | 2 parallelism + 1 GT_REL (composite/stacked test) | CONFIRMED |
| Pmi004 | DRAUGHTING_CALLOUT=1, AP=1, ANNOTATION_CURVE_OCCURRENCE=2, POLYLINE=2 | leader split into 2 ACOs under 1 callout | CONFIRMED |
| Pmi005 | DTM, DSY, DRC, DRE, DS, AP, ACO=1, TESSELLATED_ANNOTATION_OCCURRENCE=1, POLYLINE=1, PARALLELISM_TOLERANCE=1 | mixes ACO + tessellated AO — exact recipe | CONFIRMED |
| Pmi006 | DM=2, CAMERA_MODEL_D3=2, VIEW_VOLUME=2; **no MODEL_GEOMETRIC_VIEW** | two cameras both named with no MGV → reproduces ambiguity | CONFIRMED |
| Pmi008 | DS=1, PMT=1, SA=1; LENGTH_MEASURE_WITH_UNIT=2 | dimension+tolerance with no precision_qualifier | CONFIRMED |
| Pmi009 | DS=1, PMT=1, SA=1, CONVERSION_BASED_UNIT=1, LMU=3 | dimension with conversion-unit (rounding-mode test) | CONFIRMED |
| Pmi010 | DTM, DSY, DRC, DRE, TOLERANCE_ZONE_FORM=1, TOLERANCE_ZONE=1, POSITION_TOLERANCE=1; schema minor=`1 1 1` | older AP242 minor + tolerance_zone_form name (would be Ed.2 string) | CONFIRMED |
| Pmi012 | DS=1, DL=1, SA=2, ID_ATTRIBUTE=3 | 3 ID_ATTRIBUTEs across SA/DS/DL (collision recipe) | CONFIRMED |
| Pmi013 | DS=3, PMT=1, SA=3 | 3 dimensions for counterbore (drill+bore+depth), no compound link | CONFIRMED |
| Pmi014 | DM, AP=2, PLANE=1, PLANAR_BOX=1 | 2 annotation_planes — one with plane, one with planar_box | CONFIRMED |
| Pmi015 | DM, AP, ACO=1, POLYLINE=1, PLANE=1 | annotation polyline parallel-but-offset from plane | CONFIRMED |
| Pmi017 | DM=2, PLANE=4; AXIS2_PLACEMENT_3D=4; SHAPE_REPRESENTATION=3, DESCRIPTION_ATTRIBUTE=2 | 2 saved views with multiple SRs tagged via DESCRIPTION_ATTRIBUTE — exact recipe | CONFIRMED |
| Pmi018 | DM=2, AP, ACO=2, POLYLINE=2 | 2 saved views with same annotation set | CONFIRMED |
| Pmi019 | DM, CAMERA_MODEL_D3=1 | camera with bad orthonormality (vector content) | CONFIRMED |
| Pmi020 | DM=2, AP, ACO=1, POLYLINE=1; **no MAPPED_ITEM** | saved view missing required MI — exact recipe | CONFIRMED |
| Pmi022 | DS=2, SA=2, UUID_ATTRIBUTE=2 | 2 UUID_ATTRIBUTEs on different items (duplicate UUID test) | CONFIRMED |
| Pmi023 | DS=1, SA=1, UUID_ATTRIBUTE=2 | 2 UUIDs on same item — exact recipe | CONFIRMED |
| Pmi024 | DS=1, SA=1, UUID_ATTRIBUTE=1 | UUID with illegal chars = string content | CONFIRMED |
| Pmi025 | DTM=2, DSY=1, DRC=3, DRE=3, POSITION_TOLERANCE=1 | datum frame with repeated datum (3 DRCs for 2 datums) | CONFIRMED |
| Pmi026 | DTM=3, DSY=1, DRC=1, DRE=1, POSITION_TOLERANCE=1 | 3 datums with identification collision (string content) | CONFIRMED |
| Pmi027 | DTM=3, DATUM_REFERENCE=3 (legacy), no DSY/DRC | legacy datum_reference in AP242 — exact recipe | CONFIRMED |
| Pmi028 | DTM=2, DSY=1, DRC=1, COMMON_DATUM=1 (legacy), no COMMON_DATUM_LIST | legacy common_datum form — exact recipe | CONFIRMED |
| Pmi029 | DTM=2, DATUM_REFERENCE=1, DRC=1, DRE=1, POSITION_TOLERANCE=1 | mixed DR + DSY constituents | CONFIRMED |
| Pmi030 | DTM, DSY, DRC, DRE, PROJECTED_ZONE_DEFINITION=1, TOLERANCE_ZONE_FORM=1, TOLERANCE_ZONE=1 | projected zone with magnitude (negative content) | CONFIRMED |
| Pmi031 | DTM, DSY, DRC, DRE, PROJECTED_ZONE_DEFINITION=1, POSITION_TOLERANCE=1 | projected_zone with non-plane projection_end | CONFIRMED |
| Pmi032 | DTM=1, PLACED_DATUM_TARGET_FEATURE=1 | datum target with zero diameter (content) | CONFIRMED |
| Pmi033 | DTM, PDTF=1, GISU=1, SA_REL=1, PLANE=1 | datum-target shape mismatch (content) | CONFIRMED |
| Pmi034 | DTM=1, PDTF=2, SA_REL=2, PROPERTY_DEFINITION=2, PDR=2 | 2 PDTFs sharing one DatumTargetType_Area | CONFIRMED |
| Pmi036 | PDTF=1, SA=1, SA_REL=1 | reversed relating/related — content | CONFIRMED |
| Pmi037 | DS=1, PMT=1, SA=1 | shape_aspect.product_definitional flag (Boolean content) | CONFIRMED |
| Pmi039 | DS=1, PMT=2, AP, SA=1, TOLERANCE_VALUE=2 | 2 PMTs on 1 dimension — exact recipe | CONFIRMED |
| Pmi041 | DS=1, DL=1, PMT=1, AP, SA=2 | DS-vs-DL confusion baseline (one each) | CONFIRMED |
| Pmi042 | DTM, DSY, DRC, DRE, DS, PMT, AP, SA, PERPENDICULARITY_TOLERANCE=1, PROPERTY_DEFINITION=1, PDR=1, DRI=1 | full chain + descriptive empty-text — exact recipe | CONFIRMED |
| Pmi043 | DTM, DSY, DRC, DRE, AP, SA, POSITION_TOLERANCE=2, GEOMETRIC_TOLERANCE_RELATIONSHIP=2 | GT_REL names with case variation (string content) | CONFIRMED |
| Pmi044 | DTM, DSY, DRC, DRE, DS, PMT, AP, SA, PROPERTY_DEFINITION=1, PDR=1, POSITION_TOLERANCE=1 | DS attached via PROPERTY_DEFINITION chain (legacy AP203+G&DT) | CONFIRMED |
| Pmi045 | DRAUGHTING_CALLOUT=1, AP, ACO=1, PSA=1, STYLED_ITEM=1, COLOUR_RGB=1, POLYLINE=1; no DS/GT | graphic-only PMI (callout+ACO, no semantic counterpart) | CONFIRMED |
| Pmi046 | DRAUGHTING_CALLOUT=1, DRAUGHTING_ANNOTATION_OCCURRENCE=1, AP, ACO=1, PSA=1, COLOUR_RGB=1 | uses DRAUGHTING_ANNOTATION_OCCURRENCE (non-RP) | CONFIRMED |
| Pmi047 | DM, AP, ACO=1, PSA=1, COLOUR_RGB=1, POLYLINE=1 | annotation not in any AP.elements (graph-shape content) | CONFIRMED |
| Pmi048 | DM, AP, ACO=1, POLYLINE=1; **no PSA / no COLOUR_RGB** | ACO without color — exact recipe | CONFIRMED |
| Pmi049 | DM, AP, PLANE=1; no STYLED_ITEM | tessellated shape with no styled_item — exact recipe; (note: missing TESSELLATED_* entities makes this a thin reproducer) | CONCERN |
| Pmi053 | DM, AP, ACO=1, PSA=1, COLOUR_RGB=1, POLYLINE=1 | leader with single point (content) | CONFIRMED |
| Pmi054 | DM, AP, ACO=1, PSA=1, COLOUR_RGB=1; no POLYLINE | basis curve disallowed type (string content); polyline absent | CONFIRMED |
| Pmi055 | DS=4, PMT=1, AP, SA=3 | 4 dimensional_sizes for compound hole — exact recipe | CONFIRMED |
| Pmi056 | DRAUGHTING_CALLOUT, DM, AP, ACO=1, TAO=1, PSA=1, COLOUR_RGB=1, POLYLINE=1 | mixes ACO + TESSELLATED_ANNOTATION_OCCURRENCE (one callout) | CONFIRMED |
| Pmi057 | DTM, DSY, DRC, DRE, DRAUGHTING_CALLOUT, AP, ACO=1, SA, PERPENDICULARITY_TOLERANCE=1, PSA, COLOUR_RGB | semantic GT + graphic ACO (associativity-loss recipe) | CONFIRMED |
| Pmi058 | DM=2, AP, ACO=1, PSA=1, COLOUR_RGB=1, CONFIGURATION_ITEM=2 | configuration-scoped PMI (CI=2) | CONFIRMED |
| Pmi059 | DM, AP, SA=1, PROPERTY_DEFINITION=1, PDR=1, PLANE=2, DRI=1 | property "status=construction" attached to face | CONFIRMED |
| Pmi060 | DTM, DTM_FEATURE, DSY, DRC, DRE, DS, PMT, AP, SA, SA_REL, POSITION_TOLERANCE | full PMI chain; null-description content defect | CONFIRMED |
| Pmi061 | DTM, DTM_FEATURE, DSY, DRC, DRE, AP, ITEM_IDENTIFIED_REPRESENTATION_USAGE=1, SA, SA_REL, POSITION_TOLERANCE, PLANE=2 | DATUM→AF chain via SA→IIRU/SRI (chain pattern 1) | CONFIRMED |
| Pmi062 | DTM, DSY, DRC, DRE, DS, PMT, AP, GISU=1, SA, POSITION_TOLERANCE | AP242 PMI/hole structure (mesh-explosion recipe; reproducer is precise B-rep+PMI) | CONFIRMED |
| Pmi063 | DTM, DSY, DRC, DRE, PDTF=1, DS, PMT, AP, SA, SA_REL, POSITION_TOLERANCE | full PMI; FILE_DESCRIPTION RP-citation defect = header content | CONFIRMED |
| Pmi065 | DS, PMT, AP, SA, PRODUCT=3, PD=3, PDF=3, PDS=3 | DDP-style multiple products (cross-file ref simulation) | CONFIRMED |
| Pmi066 | DS=4, PMT=1, AP, SA=4 | 4 dimensions for compound hole + no explicit hole feature | CONFIRMED |
| Pmi067 | DS, PMT, AP, SA, CONVERSION_BASED_UNIT=2 | 2 conversion_based_units (inches name variation) | CONFIRMED |
| Pmi068 | DM, AP, ACO=1, PSA=1, COLOUR_RGB=1, POLYLINE=1, AXIS2_PLACEMENT_3D=2, PLANE=2 | annotation_plane with mirror axes (content) | CONFIRMED |

## Summary

- **CONFIRMED: 56**
- **CONCERN: 1** — Pmi049 (catalog says "tessellated geometry with no styled_item" but file lacks any TESSELLATED_* entity; only PLANE/AP — thin reproducer)
- **FAIL: 0**

Pmi049 is the lone concern: the catalog claims a tessellated_solid with no styled_item, but the file contains no tessellated entity at all. May be intentional minimal reproducer encoding the "missing styled_item" pattern at the SR level, or could be a corpus selection error.

All other files contain the entity-graph signatures called out in their catalog reproducer recipes. Many defects (string casing, ID collisions, illegal UUID chars, missing precision qualifiers, datum letter content) are content-level — entity counts confirm the *structural* recipe and adversarial reading confirms the structural shape matches.
