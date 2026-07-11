"""M141 — AP203 PRODUCT_CATEGORY hierarchy contains a cycle

Catalog claim: PRODUCT_CATEGORY_RELATIONSHIP entries form a cycle: category
'electronics' is sub-of 'mechanical_assembly' which is sub-of 'electronics'.
Walking the category tree to discover a part's parent class loops indefinitely.

Reproducer recipe: two PRODUCT_CATEGORY_RELATIONSHIP entries forming an
A -> B -> A cycle.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  count_entity_def(b'PRODUCT_CATEGORY_RELATIONSHIP') >= 2
  count_entity_def(b'PRODUCT_CATEGORY') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M141",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where "
        "PRODUCT_CATEGORY_RELATIONSHIP entries form a two-node cycle: "
        "category 'electronics' is declared sub-category-of 'mechanical_assembly' "
        "and simultaneously 'mechanical_assembly' is declared sub-category-of "
        "'electronics', creating an infinite loop in the category tree; "
        "input: AP203 STEP file with two PRODUCT_CATEGORY instances (#20 = "
        "'electronics', #21 = 'mechanical_assembly') and two "
        "PRODUCT_CATEGORY_RELATIONSHIP instances: #30 declares electronics as "
        "sub-category of mechanical_assembly, and #31 declares mechanical_assembly "
        "as sub-category of electronics; per ISO 10303-44 the "
        "PRODUCT_CATEGORY_RELATIONSHIP graph must be acyclic (a DAG); a cycle "
        "causes any algorithm that walks the category hierarchy upward to find root "
        "classes to loop indefinitely; PDM classification tools, bill-of-materials "
        "explodersand part search engines that traverse PRODUCT_CATEGORY_RELATIONSHIP "
        "chains hang or stack-overflow when they encounter this cycle; "
        "the defect is produced by a PDM exporter that generated category links from "
        "a graph rather than a tree without running cycle detection; "
        "kernel must detect cycles in the PRODUCT_CATEGORY_RELATIONSHIP graph and "
        "reject or break the cycle with a warning; "
        "synonyms: AP203 hierarchy loop, category infinite recursion, "
        "PRODUCT_CATEGORY contains cycle, PDM category tree loops, "
        "category sub-of forms cycle, AP203 category cycle, "
        "product category infinite loop, PDM classification cycle"
    ),
    schema="AP242",
)


def _render_m141() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with cyclic PRODUCT_CATEGORY_RELATIONSHIP.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        PRODUCT_CATEGORY('electronics') — first node of cycle
      #21        PRODUCT_CATEGORY('mechanical_assembly') — second node of cycle
      #30        PRODUCT_CATEGORY_RELATIONSHIP: electronics sub-of mechanical_assembly
      #31        PRODUCT_CATEGORY_RELATIONSHIP: mechanical_assembly sub-of electronics
                 DEFECT: #30 + #31 together form the cycle A->B->A
      #35        PRODUCT, PRODUCT_DEFINITION_FORMATION, PRODUCT_DEFINITION
      #40        APPLIED_CLASSIFICATION_ASSIGNMENT binds part to 'electronics' category
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M141: AP203 PRODUCT_CATEGORY hierarchy contains a cycle */")
    lines.append("/* DEFECT: electronics sub-of mechanical_assembly sub-of electronics */")
    lines.append("/* Two PRODUCT_CATEGORY_RELATIONSHIP entries form cycle: A->B->A */")
    lines.append("/* Category tree walkers loop indefinitely; PDM tools hang or stack-overflow */")
    lines.append("/* Per ISO 10303-44 PRODUCT_CATEGORY_RELATIONSHIP graph must be acyclic */  ")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'PRODUCT_CATEGORY_RELATIONSHIP') >= 2 */")
    lines.append("/* Byte assertion: count_entity_def(b'PRODUCT_CATEGORY') >= 2 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M141: AP203 PRODUCT_CATEGORY hierarchy cycle electronics mechanical_assembly'),'2;1');")
    lines.append("FILE_NAME('M141.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("FILE_SCHEMA(('CONFIG_CONTROL_DESIGN { 1 0 10303 203 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('configuration controlled 3D designs of mechanical parts and assemblies');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'config_control_design',1994,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('ctx','3D'));")
    lines.append("/* Byte assertion: count_entity_def(b'PRODUCT_CATEGORY') >= 2 */")
    lines.append("/* First category node: 'electronics' — typically a leaf or mid-level category */  ")
    lines.append("#20=PRODUCT_CATEGORY('electronics','Electronic components and sub-assemblies');")
    lines.append("/* Second category node: 'mechanical_assembly' — normally a parent category */")
    lines.append("#21=PRODUCT_CATEGORY('mechanical_assembly','Mechanical assembly components');")
    lines.append("/* Byte assertion: count_entity_def(b'PRODUCT_CATEGORY_RELATIONSHIP') >= 2 */")
    lines.append("/* DEFECT leg 1: 'electronics' declared as sub-category of 'mechanical_assembly' */")
    lines.append("/* This makes electronics appear as a specialization of mechanical_assembly */")
    lines.append("#30=PRODUCT_CATEGORY_RELATIONSHIP('elec-sub-mech',")
    lines.append("  'electronics is sub-category of mechanical_assembly',#20,#21);")
    lines.append("/* DEFECT leg 2: 'mechanical_assembly' declared as sub-category of 'electronics' */")
    lines.append("/* This makes mechanical_assembly appear as a specialization of electronics */   ")
    lines.append("/* Together #30 and #31 form the cycle: electronics->mechanical_assembly->electronics */")
    lines.append("/* Walking parent links from either node never reaches a root — infinite loop */  ")
    lines.append("#31=PRODUCT_CATEGORY_RELATIONSHIP('mech-sub-elec',")
    lines.append("  'mechanical_assembly is sub-category of electronics',#21,#20);")
    lines.append("/* Part assigned to the 'electronics' category — triggers the cycle on class lookup */")
    lines.append("#35=PRODUCT('PART-505','Sensor PCB','Printed circuit board for sensor module',(#1));")
    lines.append("#36=PRODUCT_DEFINITION_FORMATION('rev_B','Rev B sensor board',#35);")
    lines.append("#37=PRODUCT_DEFINITION('design','',#36,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* Classification assignment binds #37 to category 'electronics' (#20) */")
    lines.append("/* A BOM exploder walking the hierarchy from #20 enters the A->B->A cycle */  ")
    lines.append("#40=APPLIED_CLASSIFICATION_ASSIGNMENT(#20,CLASSIFICATION_ROLE('classification'),(#37));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-product-category-relationship-cycle-A-B-A',")
    lines.append("  (#20,#21,#30,#31,#35,#36,#37,#40));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M141','M141','M141',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m141(path) -> None:
    Path(path).write_text(_render_m141())


f.render = _render_m141  # type: ignore[method-assign]
f.write = _write_m141    # type: ignore[method-assign]
