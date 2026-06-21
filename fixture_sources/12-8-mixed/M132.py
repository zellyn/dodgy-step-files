"""M132 — AP203 material-class APPLIED_GROUP_ASSIGNMENT without a material reference.

Catalog claim: An APPLIED_GROUP_ASSIGNMENT classifies a part as belonging to a
'material' GROUP, but the GROUP has no associated MATERIAL_DESIGNATION or
specification reference. The part is tagged as having a material without
identifying which material.

Reproducer recipe: GROUP('material_class',..) with no MATERIAL_DESIGNATION link;
APPLIED_GROUP_ASSIGNMENT(group,(part_PD)).

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'APPLIED_GROUP_ASSIGNMENT')
  count_entity_def(b'MATERIAL_DESIGNATION') == 0

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M132",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where an "
        "APPLIED_GROUP_ASSIGNMENT classifies a part as belonging to a 'material' "
        "GROUP but the GROUP has no associated MATERIAL_DESIGNATION, leaving the "
        "material specification empty; "
        "input: AP203 STEP file with a GROUP entity whose name is 'material_class', "
        "assigned to a PRODUCT_DEFINITION via APPLIED_GROUP_ASSIGNMENT, but no "
        "MATERIAL_DESIGNATION entity exists anywhere in the file; per ISO 10303-203 "
        "§5.6 a material GROUP assignment must be accompanied by a MATERIAL_DESIGNATION "
        "that identifies the specific material grade or specification; without the "
        "designation the receiver knows only that a material is intended but has no "
        "way to look up grade, supplier, heat-treatment requirements, or any material "
        "property; BOM processors and FEA tools will either silently inherit a default "
        "material (producing wrong analysis results) or raise an error; "
        "kernel must detect material groups missing a designation and warn, drop "
        "the assignment, or reject; "
        "synonyms: AP203 material missing, material spec stub, PDM material grade absent, "
        "AP203 material group has no material, PDM part says steel but no grade, "
        "material classification incomplete, APPLIED_GROUP_ASSIGNMENT no designation, "
        "material group without MATERIAL_DESIGNATION"
    ),
    schema="AP242",
)


def _render_m132() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with material GROUP missing MATERIAL_DESIGNATION.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20-#22    PRODUCT / PRODUCT_DEFINITION_FORMATION / PRODUCT_DEFINITION
      #30        GROUP('material_class','Steel alloy material group') — no MATERIAL_DESIGNATION
      #31        APPLIED_GROUP_ASSIGNMENT linking the group to the product definition
      (no MATERIAL_DESIGNATION entity anywhere — that is the DEFECT)
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M132: AP203 material-class APPLIED_GROUP_ASSIGNMENT without a material reference */")
    lines.append("/* DEFECT: GROUP tagged 'material_class' has no MATERIAL_DESIGNATION entity */")
    lines.append("/* Part claims to be steel alloy but grade/spec is entirely absent from the file */")
    lines.append("/* Per AP203 §5.6 material GROUP must be accompanied by a MATERIAL_DESIGNATION */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'APPLIED_GROUP_ASSIGNMENT') */")
    lines.append("/* Byte assertion: count_entity_def(b'MATERIAL_DESIGNATION') == 0 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M132: AP203 material GROUP assignment missing MATERIAL_DESIGNATION'),'2;1');")
    lines.append("FILE_NAME('M132.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Product to which the material group is assigned */")
    lines.append("#20=PRODUCT('PART-042','Structural Flange','Flange for pipe connection',(#1));")
    lines.append("#21=PRODUCT_DEFINITION_FORMATION('rev_A','',#20);")
    lines.append("#22=PRODUCT_DEFINITION('design','',#21,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* GROUP entity classifies part as 'material_class' — no MATERIAL_DESIGNATION follows */")
    lines.append("/* A correct file would have a MATERIAL_DESIGNATION linking this group to a spec */")
    lines.append("/* e.g. MATERIAL_DESIGNATION('304 stainless steel',$,(#22)) *)  <- ABSENT in this file */")
    lines.append("/* Byte assertion: count_entity_def(b'MATERIAL_DESIGNATION') == 0 */")
    lines.append("#30=GROUP('material_class','Steel alloy material group — no grade specified');")
    lines.append("/* Byte assertion: contains(b'APPLIED_GROUP_ASSIGNMENT') */")
    lines.append("/* DEFECT: assigns material group to part but the group has no MATERIAL_DESIGNATION */")
    lines.append("/* Receivers cannot determine which steel alloy, heat treatment, or standard applies */")
    lines.append("#31=APPLIED_GROUP_ASSIGNMENT(#30,(#22));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-material-group-no-designation',")
    lines.append("  (#20,#21,#22,#30,#31));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M132','M132','M132',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m132(path) -> None:
    Path(path).write_text(_render_m132())


f.render = _render_m132  # type: ignore[method-assign]
f.write = _write_m132    # type: ignore[method-assign]
