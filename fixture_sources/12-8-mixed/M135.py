"""M135 — AP203 declares CONFIG_CONTROL_DESIGN (CC1) but uses CC2-only entities.

Catalog claim: A file declares the legacy CONFIG_CONTROL_DESIGN schema in its
FILE_SCHEMA yet uses entities such as DESIGN_CONTEXT and MECHANICAL_CONTEXT that
were introduced in the AP203 second-edition (CC2 / CCD2) schema. CC1-strict
readers reject the unknown entities; lax readers accept and produce inconsistent
results.

Reproducer recipe: FILE_SCHEMA(('CONFIG_CONTROL_DESIGN')) with DESIGN_CONTEXT /
MECHANICAL_CONTEXT instances in DATA section.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'DESIGN_CONTEXT')
  contains(b'MECHANICAL_CONTEXT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M135",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN (CC1) file that "
        "incorrectly uses DESIGN_CONTEXT and MECHANICAL_CONTEXT entities which "
        "were only introduced in the AP203 second-edition (CC2/CCD2) schema; "
        "input: AP203 STEP file declaring FILE_SCHEMA(('CONFIG_CONTROL_DESIGN')) — "
        "the first-edition CC1 schema identifier — but whose DATA section contains "
        "instances of DESIGN_CONTEXT and MECHANICAL_CONTEXT; these entity types did "
        "not exist in CC1 and were added in the AP203 Ed.2 (CC2) schema update; "
        "CC1-strict readers (legacy PDM importers, validators targeting ISO 10303-203 "
        "Ed.1) reject the file with 'unknown entity type' errors; lax readers that "
        "silently accept the CC2 entities produce an inconsistently-declared file "
        "where the schema version header no longer describes the actual content; "
        "two corrective paths exist: (a) upgrade FILE_SCHEMA to declare CC2/CCD2, "
        "or (b) replace DESIGN_CONTEXT and MECHANICAL_CONTEXT with their CC1 "
        "equivalents and remove any other CC2-only attributes; "
        "kernel must warn on schema-version mismatch; "
        "synonyms: AP203 schema version mismatch, CC1/CC2 mix, "
        "legacy schema with newer entities, AP203 CC1 with CC2 entities, "
        "CONFIG_CONTROL_DESIGN strict reader rejects DESIGN_CONTEXT, "
        "AP203 first edition with second edition entities"
    ),
    schema="AP242",
)


def _render_m135() -> str:
    """Render AP203 CC1 file that uses CC2-only DESIGN_CONTEXT and MECHANICAL_CONTEXT.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION (CC1 form)
      #10-#14    Unit context (mm)
      #20        MECHANICAL_CONTEXT — CC2-only entity: DEFECT in CC1 file
      #21        DESIGN_CONTEXT — CC2-only entity: DEFECT in CC1 file
      #30-#32    PRODUCT / PRODUCT_DEFINITION_FORMATION / PRODUCT_DEFINITION
                 (PRODUCT_DEFINITION uses #21 DESIGN_CONTEXT as frame_of_reference)
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M135: AP203 CC1 file using CC2-only DESIGN_CONTEXT and MECHANICAL_CONTEXT */")
    lines.append("/* DEFECT: FILE_SCHEMA declares CONFIG_CONTROL_DESIGN (CC1 / Ed.1) */")
    lines.append("/* DATA section uses DESIGN_CONTEXT and MECHANICAL_CONTEXT added in CC2 (Ed.2) */")
    lines.append("/* CC1-strict readers reject with 'unknown entity type'; lax readers get inconsistency */")
    lines.append("/* Correct fix: upgrade FILE_SCHEMA to CC2, or strip CC2-only entities */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'DESIGN_CONTEXT') */")
    lines.append("/* Byte assertion: contains(b'MECHANICAL_CONTEXT') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M135: AP203 CC1 schema declaration with CC2-only entities DESIGN_CONTEXT MECHANICAL_CONTEXT'),'2;1');")
    lines.append("FILE_NAME('M135.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* CC1 / Ed.1 schema declaration — does NOT include CC2-only entity types */")
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
    lines.append("/* Byte assertion: contains(b'MECHANICAL_CONTEXT') */")
    lines.append("/* DEFECT: MECHANICAL_CONTEXT is a CC2-only entity; CC1 does not define this type */")
    lines.append("/* CC1 equivalent is PRODUCT_CONTEXT with discipline_type='mechanical' */")
    lines.append("/* A legacy PDM exporter that switched from CC2 to CC1 header but forgot to strip entities */")
    lines.append("#20=MECHANICAL_CONTEXT('MECH',#1,'mechanical');")
    lines.append("/* Byte assertion: contains(b'DESIGN_CONTEXT') */")
    lines.append("/* DEFECT: DESIGN_CONTEXT is a CC2-only entity; not present in CC1 schema *)   ")
    lines.append("/* CC1 equivalent is PRODUCT_DEFINITION_CONTEXT with lifecycle_stage='design' */")
    lines.append("#21=DESIGN_CONTEXT('DESIGN',#1,'design');")
    lines.append("/* Product using the CC2-only context entities in a CC1-declared file */")
    lines.append("#30=PRODUCT('PART-099','Valve Body','Main flow control body',(#20));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_A','Production release',#30);")
    lines.append("/* PRODUCT_DEFINITION references DESIGN_CONTEXT (#21) — another CC2-only type *)  ")
    lines.append("#32=PRODUCT_DEFINITION('design','',#31,#21);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-cc1-schema-with-cc2-only-entities',")
    lines.append("  (#20,#21,#30,#31,#32));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M135','M135','M135',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m135(path) -> None:
    Path(path).write_text(_render_m135())


f.render = _render_m135  # type: ignore[method-assign]
f.write = _write_m135    # type: ignore[method-assign]
