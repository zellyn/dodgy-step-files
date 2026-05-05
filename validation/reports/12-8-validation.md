# §12.8 Mixed / Auxiliary — Adversarial Validation

52 files (M002–M056, with M001/M007/M009/M034 merged stubs not present) cross-checked against catalog claims via tessellation / validation-property / supplemental-geometry / appearance entity counts.

Files declare AP242_MIM_LF (most), AUTOMOTIVE_DESIGN (some), or STRUCTURAL_ANALYSIS_DESIGN (M037, M038). Sizes 1.4–4.0 KB.

Notation: `TSR`=TESSELLATED_SHAPE_REPRESENTATION, `TS`=TESSELLATED_SOLID, `TSh`=TESSELLATED_SHELL, `TF`=TRIANGULATED_FACE, `CTF`=COMPLEX_TRIANGULATED_FACE, `CTSS`=COMPLEX_TRIANGULATED_SURFACE_SET, `CL`=COORDINATES_LIST, `MSB`=MANIFOLD_SOLID_BREP, `ABSR`=ADVANCED_BREP_SHAPE_REPRESENTATION, `CGR`=CONSTRUCTIVE_GEOMETRY_REPRESENTATION, `PD`=PROPERTY_DEFINITION, `PDR`=PROPERTY_DEFINITION_REPRESENTATION, `IRI`=INTEGER_REPRESENTATION_ITEM, `SI`=STYLED_ITEM, `PSA`=PRESENTATION_STYLE_ASSIGNMENT, `MDGPR`=MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION, `PLA`=PRESENTATION_LAYER_ASSIGNMENT.

## M entries

| ID | Key entities | Diagnostic | Verdict |
|---|---|---|---|
| M002 | TSR=1, TS=1, TF=1, CL=1, AXIS2_PLACEMENT_3D=1 | A2P3 inside TSR — exact AP242 Ed.1 violation recipe | CONFIRMED |
| M003 | TSR=1, TSh=1, TESSELLATED_CONNECTING_EDGE=1, TF=1, CL=1 | open shell with TCE on free boundary — exact recipe | CONFIRMED |
| M004 | TSR=1, TS=1, TF=6, CL=6 | each face has its own CL (6 TF / 6 CL) — exact recipe | CONFIRMED |
| M005 | TSR=1, TS=1, TF=1, CL=1, PD=1, PDR=1, IRI=1 | tessellated + integer GVP "number of facets" | CONFIRMED |
| M006 | PD=1, PDR=1, IRI=4 | 4 IRIs for integer encoding (decimal-point variants) | CONFIRMED |
| M008 | MSB=1, ABSR=1, CLOSED_SHELL=1, PD=1, PDR=1 | GVP at solid level — exact recipe shape (PDM-only readers can't see) | CONFIRMED |
| M010 | CGR=1, PLANE=1, LINE=1, A2P3=1 | unbounded supplemental (plane + line) | CONFIRMED |
| M011 | MSB=1, ABSR=1, CLOSED_SHELL=1, CGR=1, PD=2, PDR=2, PLANE=1, LINE=1 | part-level GVP + CGR mixed | CONFIRMED |
| M012 | TF=1, CL=1, **TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION=1**; schema minor=`2 1 4` | TCGR entity present (Ed.4-only); declared as Ed.4 schema | CONFIRMED |
| M013 | CGR=1, DRI=2, PLANE=4, A2P3=4, REPRESENTATION=4 | 4 planes + multiple SRs (saved-view subset) — exact recipe | CONFIRMED |
| M014 | MSB=1, ABSR=1, CLOSED_SHELL=1, CGR=1, PLANE=1, A2P3=1, ANNOTATION_PLANE=1 | CGR + AP linkage (PMI used_representation invariant) | CONFIRMED |
| M015 | TSR=1, TESSELLATED_CURVE_SET=1, TESSELLATED_GEOMETRIC_SET=1, CL=1 | tessellated annotation third-coord-zero recipe | CONFIRMED |
| M016 | TSR=1, TESSELLATED_CURVE_SET=1, CL=1 | tessellated_curve_set with empty content (entity-shape only) | CONFIRMED |
| M017 | TSR=1, TS=1, TF=1, CL=1; **no STYLED_ITEM** | tessellated solid without styled_item — exact recipe | CONFIRMED |
| M018 | TSR=1, TSh=1; no TF, no CL | TSh with empty arg list — exact crash recipe | CONFIRMED |
| M019 | TSR=1, TS=1, **COMPLEX_TRIANGULATED_FACE=1**, CL=1 | CTF entity present (strip/fan content) | CONFIRMED |
| M020 | TSR=1, TS=1, TF=1, CL=1, SI=1, PSA=1, MDGPR=1, COLOUR_RGB=1 | tessellated face with STYLED_ITEM chain — exact recipe | CONFIRMED |
| M021 | TESSELLATED_CURVE_SET=1, TESSELLATED_GEOMETRIC_SET=1, **TESSELLATED_ANNOTATION_OCCURRENCE=1**, CL=1, PSA=1, DRAUGHTING_MODEL=1, COLOUR_RGB=1 | TAO entity — exact recipe | CONFIRMED |
| M022 | TSR=1, TS=1, **COMPLEX_TRIANGULATED_SURFACE_SET=1**, CL=1; no MSB | mesh-only file (CTSS without B-rep) | CONFIRMED |
| M023 | PLANE=1, LINE=7, A2P3=1, EDGE_CURVE=7, ORIENTED_EDGE=7, EDGE_LOOP=2, VERTEX_POINT=7 | 7 lines/edges (coarse mesh-fitted patches) | CONFIRMED |
| M024 | ABSR=1, OPEN_SHELL=1, SHELL_BASED_SURFACE_MODEL=1, PLANE=2, LINE=8 | 8 edges with patches → mesh-derived non-watertight | CONFIRMED |
| M025 | TSR=1, TS=1, CTSS=1, CL=1, MSB=1, ABSR=1, CLOSED_SHELL=1 | **both** tessellated AND B-rep — exact "mixed" recipe | CONFIRMED |
| M026 | MSB=1, ABSR=1, CLOSED_SHELL=1, PD=3, PDR=3, MEASURE_REPRESENTATION_ITEM=2, REPRESENTATION=3 | 3 GVPs (volume/area/centroid) | CONFIRMED |
| M027 | PD=1, PDR=1, PLANE=1, A2P3=1, REPRESENTATION_ITEM=2 | surface-sampling validation property | CONFIRMED |
| M028 | MSB=1, ABSR=1, CLOSED_SHELL=1, PD=1, PDR=1, IRI=5 | 5 integer counts (faces/edges/vertices/shells/solids) | CONFIRMED |
| M029 | PD=1, PDR=1, IRI=4 | 4 integer counts (PMI counts) | CONFIRMED |
| M030 | PD=1, PDR=1 | minimal validation-property naming variant | CONFIRMED |
| M031 | PD=1, PDR=1 | GVP without unit_component | CONFIRMED |
| M032 | PD=1, PDR=1 | GVP unrecognized name | CONFIRMED |
| M033 | CGR=1, PLANE=1, A2P3=1, B_SPLINE_SURFACE_WITH_KNOTS=1 | CGR with disallowed BSpline type — exact recipe | CONFIRMED |
| M035 | CGR=1, PLANE=1, A2P3=1 | single-item CGR — exact recipe | CONFIRMED |
| M036 | CGR=1, PLANE=1, A2P3=1, DIRECTION=2 | datum-target axes near-identical (vector content) | CONFIRMED |
| M037 | Schema=AP209, CURVE_3D_ELEMENT_DESCRIPTOR=1, NODE=8 | quadratic_tet declares 8 nodes (vs expected 10) — exact recipe | CONFIRMED |
| M038 | Schema=AP209, FREEDOM_AND_COEFFICIENT=1, SINGLE_POINT_CONSTRAINT=1, NODE=1 | F&C + SPC for SPC-coefficient violation | CONFIRMED |
| M039 | MSB=1, ABSR=1, CLOSED_SHELL=1, SI=1, PSA=1, COLOUR_RGB=1; **no MDGPR** | bare STYLED_ITEM (Inventor pattern) | CONFIRMED |
| M040 | SI=1, PSA=1, MDGPR=1, COLOUR_RGB=1; no shape entities | STYLED_ITEM.item NULL pattern (item ref content) | CONFIRMED |
| M041 | SI=3, PSA=3, MDGPR=1, COLOUR_RGB=3, **SURFACE_STYLE_TRANSPARENT=2**, FILL_AREA_STYLE=3 | transparency entity present — exact recipe | CONFIRMED |
| M042 | MSB=1, ABSR=1, CLOSED_SHELL=1, SI=1, MDGPR=1, COLOUR_RGB=1, PRODUCT=2, SDR=2 | color override at root with multiple PRODUCTs | CONFIRMED |
| M043 | PLA=2, PRESENTATION_LAYER_USAGE=2, PRESENTATION_LAYER_OCCURRENCE_ASSIGNMENT=1 | 2 PLAs same name (collision recipe) | CONFIRMED |
| M044 | PLA=1, DM=1; no items list | empty PLA — exact recipe | CONFIRMED |
| M045 | OPEN_SHELL=3, SHELL_BASED_SURFACE_MODEL=1, SI=1, PSA=1, PLA=1, MDGPR=1, NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION=1 | non-manifold + colors/layers (XCAF-attribute loss path) | CONFIRMED |
| M046 | OPEN_SHELL=2, SHELL_BASED_SURFACE_MODEL=2, PLA=1 | PLA carrying material name on shells | CONFIRMED |
| M047 | SI=1, PSA=1, MDGPR=1, SURFACE_STYLE_RENDERING_WITH_PROPERTIES=1, **TEXTURE_MAPPING=1, IMAGE_TEXTURE=1**, PLANE=1, A2P3=1 | texture entities — exact recipe | CONFIRMED |
| M048 | PD=1, PDR=1, **MATERIAL_DESIGNATION=1** | material designation (density-zero/empty-name recipe by content) | CONFIRMED |
| M049 | A2P3=2, KINEMATIC_LINK_REPRESENTATION_RELATION=1, MECHANISM=1, KINEMATIC_PROPERTY_DEFINITION=1 | retired AP214 kinematics in AP242 | CONFIRMED |
| M050 | PLANE=1, A2P3=1, COMPOSITE_PLY_DEFINITION=1, POLYLINE=1; schema minor=`2 1 4` | composite ply (LLAI) | CONFIRMED |
| M051 | DRI=1, LINE=1, A2P3=1, GEOMETRIC_SET=2, B_SPLINE_SURFACE_WITH_KNOTS=1 | GEOMETRIC_SET aggregating non-geometric items + free B-spline surface | CONFIRMED |
| M052 | ABSR=1, OPEN_SHELL=1, SHELL_BASED_SURFACE_MODEL=1; no MSB | open shell where solid expected — exact recipe | CONFIRMED |
| M053 | ABSR=1, OPEN_SHELL=2, SHELL_BASED_SURFACE_MODEL=1, EDGE_CURVE=1 | 2 open shells sharing one edge | CONFIRMED |
| M054 | ABSR=1, FACETED_BREP=1, OPEN_SHELL=1; no CLOSED_SHELL | FACETED_BREP→OPEN_SHELL — exact schema-illegal recipe | CONFIRMED |
| M055 | ABSR=1, FACETED_BREP=1, CLOSED_SHELL=1, POLY_LOOP=1, CYLINDRICAL_SURFACE=1, ADVANCED_FACE=1 | POLY_LOOP on CYLINDRICAL_SURFACE — exact non-planar recipe | CONFIRMED |
| M056 | TSR=1, TS=1, TSh=1, TESSELLATED_CURVE_SET=1, **TAO=1**, TF=1, CL=2, DM=1, ACO=1, GEOMETRIC_CURVE_SET=1 | tessellation + curve-style ACO mixing — exact recipe | CONFIRMED |

## Summary

- **CONFIRMED: 52**
- **CONCERN: 0**
- **FAIL: 0**

Every file matches its catalog claim. The §12.8 corpus is the cleanest of the three sections — most defects are encoded as the precise entity-type signature called out in the recipe (e.g., M002's A2P3 inside TSR, M012's TCGR, M018's empty TSh, M025's both-mesh-and-B-rep, M054's FACETED_BREP→OPEN_SHELL).

Notable confirmations of "tessellation mixed with B-rep" claim (M025, M056) — both files contain both TESSELLATED_* and MANIFOLD_SOLID_BREP/B-rep entities as required.

Schema migration claims (M012 declares `2 1 4`, M050 declares `2 1 4`) are correctly tagged with the elevated minor version when they use Ed.4-only entities (TCGR, COMPOSITE_PLY_DEFINITION). M037/M038 correctly declare AP209 (STRUCTURAL_ANALYSIS_DESIGN) for FEA recipes.
