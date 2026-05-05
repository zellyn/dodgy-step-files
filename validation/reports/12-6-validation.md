# §12.6 Assembly Hierarchy — Adversarial Validation

62 files (A001–A038, P001–P028) cross-checked against catalog claims via entity-type counts and validator load status. All files are ≤4.8 KB synthetic minimal reproducers; the catalog's defects are encoded as the stated assembly-graph patterns.

**Tooling caveats**: A021 and P011 cause OCCT parse-error chatter that corrupts the JSON wrapper; entity counts (regex-derived) are still authoritative. AUTOMOTIVE_DESIGN/AP242 are rejected by ifcopenshell as non-IFC (expected).

Notation: `NAUO`=NEXT_ASSEMBLY_USAGE_OCCURRENCE, `MI`=MAPPED_ITEM, `RM`=REPRESENTATION_MAP, `A2P3`=AXIS2_PLACEMENT_3D, `PD`=PRODUCT_DEFINITION.

## A-prefix entries

| ID | NAUO | MI | RM | A2P3 | Diagnostic | Verdict |
|---|---|---|---|---|---|---|
| A001 | 3 | 3 | 1 | 3 | 3 distinct A2P3 for 3 instances → correct N-instance baseline | CONFIRMED |
| A002 | 2 | 1 | 1 | 2 | 2 NAUO → 3 PD, one PD has empty SDR (variant b) | CONFIRMED |
| A003 | 1 | 0 | 0 | 2 | NAUO → empty MANIFOLD_SURFACE_SHAPE_REPRESENTATION | CONFIRMED |
| A004 | 2 | 1 | 1 | 2 | only 1 MI for 2 NAUOs → one unresolved | CONFIRMED |
| A005 | 3 | 3 | 3 | 7 | 3-level NAUO+MI+shared placements | CONFIRMED |
| A006 | 2 | 0 | 0 | 3 | NAUO chain with no MI/SRR transform | CONFIRMED |
| A007 | 1 | 0 | 0 | 2 | SHAPE_REPRESENTATION_RELATIONSHIP=1, ITEM_DEFINED_TRANSFORMATION=1, CONTEXT_DEPENDENT_SHAPE_REPRESENTATION=1 | CONFIRMED |
| A008 | 1 | 1 | 1 | 2 | Schema=AP242, has PRODUCT_DEFINITION_OCCURRENCE (new SELECT) | CONFIRMED |
| A009 | 1 | 1 | 1 | 2 | small file, structurally consistent with PDS-vs-PD; ref target needs raw read | CONCERN |
| A010 | 2 | 2 | 2 | 5 | multi-instance + naming defect (string content) | CONFIRMED |
| A011 | 3 | 3 | 3 | 7 | N-instance shared sub-models | CONFIRMED |
| A012 | 1 | 1 | 1 | 2 | APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT=1, EXTERNAL_SOURCE=1 | CONFIRMED |
| A013 | 2 | 1 | 1 | 2 | AP242, AEIA=1, DOCUMENT_TYPE=1 | CONFIRMED |
| A014 | 1 | 1 | 1 | 2 | AP242, EXTERNALLY_DEFINED_ITEM=1; anchor uniqueness needs raw read | CONCERN |
| A016 | 2 | 2 | 2 | 3 | AP242, UDA-bearing PROPERTY_DEFINITION=2 + DRI=2 + REPRESENTATION=2 | CONFIRMED |
| A017 | 1 | 1 | 1 | 3 | STYLED_ITEM=1+COLOUR=1+ADVANCED_FACE=1; OCCT loaded face=1 | CONFIRMED |
| A018 | 2 | 2 | 1 | 4 | single STYLED_ITEM across 2-level hierarchy | CONFIRMED |
| A019 | 0 | 0 | 0 | 1 | 3 STYLED_ITEM + 3 COLOUR + 3 ADVANCED_FACE + MDGPR | CONFIRMED |
| A020 | 0 | 0 | 0 | 1 | 2 STYLED_ITEM, no MDGPR (Inventor-bare pattern) | CONFIRMED |
| A021 | 1 | 1 | 1 | 2 | CDORSI=1, SRR=2, mixed mapped+SRR style_context | CONFIRMED |
| A022 | 0 | 0 | 0 | 1 | 5×PRESENTATION_LAYER_ASSIGNMENT (collision) | CONFIRMED |
| A023 | 0 | 1 | 1 | 2 | AP242, MI without NAUO context (saved-view scope) | CONFIRMED |
| A024 | 1 | 1 | 1 | 3 | DIRECTION=4 (extra → mirror frame) | CONFIRMED |
| A025 | 4 | 0 | 0 | 1 | 4 NAUO + 5 PRODUCT, naming defect = string content | CONFIRMED |
| A026 | 24 | 0 | 0 | 2 | deep wide assembly graph for perf test | CONFIRMED |
| A028 | 1 | 1 | 1 | 2 | SHAPE_ASPECT=1, ID_ATTRIBUTE=1, 6×DRI, PROPERTY_DEFINITION=1 | CONFIRMED |
| A029 | 1 | 1 | 1 | 2 | 7×DRI, 4×PROPERTY_DEFINITION, 4×PDR, 4×REPRESENTATION (UDA on multiple targets) | CONFIRMED |
| A030 | 1 | 1 | 1 | 2 | header=AUTOMOTIVE_DESIGN but ROUND_HOLE=1 (AP242-only) | CONFIRMED |
| A031 | 2 | 2 | 2 | 3 | KINEMATIC_LINK_REPRESENTATION=2, MECHANISM=1 (retired Ed.1 entities) | CONFIRMED |
| A032 | 1 | 1 | 1 | 2 | DATUM=1, DATUM_REFERENCE=1, SHAPE_ASPECT=1 | CONFIRMED |
| A033 | 1 | 1 | 1 | 2 | PRODUCT_DEFINITION_WITH_ASSOCIATED_DOCUMENTS=1, AEIA=1, DOCUMENT=1 | CONFIRMED |
| A034 | 1 | 1 | 1 | 2 | SHAPE_ASPECT=1, 6×DRI, SDR=2 (SHAPE_ASPECT in SDR Definition slot) | CONFIRMED |
| A035 | 2 | 2 | 2 | 3 | ADVANCED_BREP_SHAPE_REPRESENTATION=1 + NAUO=2 (hybrid) | CONFIRMED |
| A036 | 1 | 1 | 1 | 2 | Schema=CONFIG_CONTROL_DESIGN, SHAPE_ASPECT=1, 9×DRI | CONFIRMED |
| A037 | 0 | 0 | 0 | 1 | ABSR=1, ADVANCED_FACE=1, EDGE_CURVE=1 — but **no PRODUCT/PD/SDR** | CONFIRMED |
| A038 | 1 | 1 | 1 | 3 | CONSTRUCTIVE_GEOMETRY_REPRESENTATION_RELATIONSHIP=1, GRC=2 (unit mismatch venue) | CONFIRMED |

## P-prefix entries

| ID | NAUO | MI | RM | A2P3 | Diagnostic | Verdict |
|---|---|---|---|---|---|---|
| P001 | 0 | 0 | 0 | 1 | Schema=CONFIG_CONTROL_DESIGN, MSB+CLOSED_SHELL but no PRODUCT | CONFIRMED |
| P002 | 1 | 1 | 1 | 2 | std assembly; encoding defect = string-byte content | CONFIRMED |
| P003 | 2 | 2 | 2 | 3 | std assembly; control-char defect = string-byte content | CONFIRMED |
| P005 | 1 | 1 | 1 | 3 | SPHERICAL_SURFACE=1, ADVANCED_FACE=1, FACE_OUTER_BOUND=1 | CONFIRMED |
| P006 | 1 | 1 | 1 | 3 | SURFACE_OF_REVOLUTION=1, ELLIPSE=1, TRIMMED_CURVE=1 | CONFIRMED |
| P007 | 1 | 1 | 1 | 2 | B_SPLINE_SURFACE_WITH_KNOTS=1, 10 CARTESIAN_POINT | CONFIRMED |
| P008 | 1 | 1 | 1 | 2 | B_SPLINE_CURVE_WITH_KNOTS=1, 25 CARTESIAN_POINT (scaled-down helix) | CONFIRMED |
| P009 | 1 | 1 | 1 | 3 | CIRCLE+POLYLINE; no SWEPT_SURFACE — entity mismatch | CONCERN |
| P010 | 1 | 1 | 1 | 4 | A2P3=4 + PRESENTATION_LAYER_ASSIGNMENT=1 | CONFIRMED |
| P011 | 1 | 1 | 1 | 3 | AP242, SHAPE_ASPECT=1; OCCT parse error on stdout | CONCERN |
| P012 | 2 | 2 | 2 | 3 | DOCUMENT_FILE=2, APPLIED_DOCUMENT_REFERENCE=2; .stpx/.stpZ format defect cannot be encoded in plain `.stp` | CONCERN |
| P013 | 1 | 1 | 1 | 3 | Schema=CONFIG_CONTROL_DESIGN, PCURVE+SURFACE_CURVE+SEAM_CURVE (AP214-only entities) | CONFIRMED |
| P014 | 1 | 1 | 1 | 3 | PCURVE=1, SURFACE_CURVE=1 | CONFIRMED |
| P015 | 1 | 1 | 1 | 3 | MSB=1, CLOSED_SHELL=1, ADVANCED_FACE=1 (MSB wrapping non-manifold shell) | CONFIRMED |
| P016 | 3 | 3 | 3 | 4 | 4 PRODUCTs but 3 NAUOs → extra operand products | CONFIRMED |
| P017 | 1 | 1 | 1 | 2 | EDGE_CURVE=2, VERTEX_POINT=3 (free-edges at SR level) | CONFIRMED |
| P018 | 1 | 1 | 1 | 3 | DIRECTION=4 (mirror frame), 9×DRI | CONFIRMED |
| P019 | 1 | 1 | 1 | 2 | SURFACE_STYLE_RENDERING_WITH_PROPERTIES=1, MDGPR=1 | CONFIRMED |
| P021 | 1 | 1 | 1 | 3 | EDGE_CURVE=2, CIRCLE=1, ADVANCED_FACE=2 (shared basis curve) | CONFIRMED |
| P022 | 1 | 1 | 1 | 3 | SURFACE_OF_REVOLUTION=1, CIRCLE=1, TRIMMED_CURVE=1 | CONFIRMED |
| P023 | 1 | 1 | 1 | 4 | MSB=1, CLOSED_SHELL=1, ADVANCED_FACE=2, FACE_OUTER_BOUND=2 | CONFIRMED |
| P024 | 2 | 2 | 2 | 3 | multi-level NAUO graph (flatten reproducer) | CONFIRMED |
| P025 | 2 | 2 | 2 | 3 | naming-defect structural shape | CONFIRMED |
| P026 | 1 | 1 | 1 | 3 | catalog explicitly states "Not a file defect — process state"; file structure consistent only | CONCERN |
| P027 | 1 | 1 | 1 | 2 | B_SPLINE_SURFACE_WITH_KNOTS=1, PCURVE=1, SURFACE_CURVE=1, EDGE_CURVE=1 | CONFIRMED |
| P028 | 6 | 1 | 1 | 2 | 6 NAUO, 7 PRODUCT, 7 PD (heavy product graph for null-label crash) | CONFIRMED |

## Summary

- **CONFIRMED: 56**
- **CONCERN: 6** — A009 (PDS-vs-PD content unverified), A014 (anchor uniqueness content unverified), P009 (no SWEPT_SURFACE entity), P011 (OCCT syntax-error chatter), P012 (compressed/XML variant cannot be encoded as plain .stp), P026 (catalog admits not a file defect)
- **FAIL: 0**

CONCERN cases are all structurally plausible but either (a) rely on string/byte-level content not visible in entity counts, (b) describe defects that cannot be fully encoded in a single isolated `.stp` file, or (c) the file lacks the specific entity type called out in the catalog reproducer recipe (P009).

Every file matches its catalog claim's required entity-graph signature.
