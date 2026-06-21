"""M131 — AP203 PRODUCT_DEFINITION linked to wrong PRODUCT_CONTEXT frame_of_reference.

Catalog claim: A PRODUCT is declared with frame_of_reference pointing at a mechanical
PRODUCT_CONTEXT but its PRODUCT_DEFINITION uses an electrical PRODUCT_CONTEXT.
The class hierarchy is mis-wired: a mechanical product appears under an electrical
discipline. Discipline-filtered queries return the wrong set.

Reproducer recipe: PRODUCT('bracket',..,(#3)) where #3 is a mechanical context;
matching PRODUCT_DEFINITION('design','',pdf,#4) where #4 is an electrical context.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  count_entity_def(b'PRODUCT_CONTEXT') >= 2
  contains(b'PRODUCT_DEFINITION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M131",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where a PRODUCT "
        "declares frame_of_reference pointing at a mechanical PRODUCT_CONTEXT but "
        "its corresponding PRODUCT_DEFINITION uses an electrical PRODUCT_CONTEXT, "
        "mis-wiring the product class hierarchy; "
        "input: AP203 STEP file with two PRODUCT_CONTEXT instances — one mechanical "
        "('mechanical') and one electrical ('electrical') — where the PRODUCT entity "
        "lists only the mechanical context in its frame_of_reference set, but the "
        "PRODUCT_DEFINITION.frame_of_reference attribute points at the electrical "
        "context; per ISO 10303-203 §4.2 the discipline_type of a product_definition "
        "must be consistent with the frame_of_reference declared by its parent PRODUCT; "
        "discipline-filtered queries (e.g. 'find all mechanical parts') will either "
        "miss this part or incorrectly include it depending on which attribute the "
        "reader uses, leading to incomplete assemblies or wrong BOM counts; "
        "kernel must validate that PRODUCT_DEFINITION.frame_of_reference.discipline_type "
        "is consistent with the parent PRODUCT.frame_of_reference set and reject or warn "
        "if a mismatch is detected; "
        "synonyms: AP203 discipline mis-classification, PDM product context mis-wired, "
        "mechanical part under electrical context, frame_of_reference disagreement, "
        "AP203 product class mismatch, context discipline type conflict, "
        "product definition discipline mismatch"
    ),
    schema="AP242",
)


def _render_m131() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with mismatched PRODUCT_CONTEXT discipline.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        PRODUCT_CONTEXT mechanical ('mechanical') — correct for PRODUCT
      #21        PRODUCT_CONTEXT electrical ('electrical') — wrong in PRODUCT_DEFINITION
      #30        PRODUCT('bracket',..) with frame_of_reference = (#20) — mechanical
      #31        PRODUCT_DEFINITION_FORMATION
      #32        PRODUCT_DEFINITION using #21 (electrical) as frame_of_reference — DEFECT
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M131: AP203 PRODUCT_DEFINITION linked to wrong PRODUCT_CONTEXT frame_of_reference */")
    lines.append("/* DEFECT: PRODUCT declares mechanical context; PRODUCT_DEFINITION uses electrical context */")
    lines.append("/* Per AP203 §4.2 PRODUCT_DEFINITION.frame_of_reference must match parent PRODUCT's context */")
    lines.append("/* Discipline-filtered queries return wrong set; mechanical part filed under electrical */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'PRODUCT_CONTEXT') >= 2 */")
    lines.append("/* Byte assertion: contains(b'PRODUCT_DEFINITION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M131: AP203 PRODUCT_DEFINITION frame_of_reference context mismatch'),'2;1');")
    lines.append("FILE_NAME('M131.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Byte assertion: count_entity_def(b'PRODUCT_CONTEXT') >= 2 */")
    lines.append("/* Two PRODUCT_CONTEXTs: one mechanical (correct for PRODUCT), one electrical (wrong in PD) */")
    lines.append("#20=PRODUCT_CONTEXT('mechanical_context',#1,'mechanical');")
    lines.append("#21=PRODUCT_CONTEXT('electrical_context',#1,'electrical');")
    lines.append("/* PRODUCT declares mechanical frame_of_reference — correct */")
    lines.append("#30=PRODUCT('bracket','Mounting Bracket','Structural mounting bracket',(#20));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_A','Initial release',#30);")
    lines.append("/* Byte assertion: contains(b'PRODUCT_DEFINITION') */")
    lines.append("/* DEFECT: PRODUCT_DEFINITION.frame_of_reference = #21 (electrical) */")
    lines.append("/* but parent PRODUCT.frame_of_reference = (#20) which is mechanical */")
    lines.append("/* A valid file would use #20 here so both contexts agree on 'mechanical' */")
    lines.append("#32=PRODUCT_DEFINITION('design','Bracket design definition',#31,#21);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-product-context-discipline-mismatch',")
    lines.append("  (#20,#21,#30,#31,#32));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M131','M131','M131',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m131(path) -> None:
    Path(path).write_text(_render_m131())


f.render = _render_m131  # type: ignore[method-assign]
f.write = _write_m131    # type: ignore[method-assign]
