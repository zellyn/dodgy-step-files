"""M137 — AP203 APPLIED_ACTION_ASSIGNMENT applies to mixed-class object list

Catalog claim: An APPLIED_ACTION_ASSIGNMENT distributes a single ACTION
(e.g. an engineering review) across a list that mixes incompatible classes —
both a PRODUCT_DEFINITION and a DOCUMENT_FILE. The action's domain semantics
are ambiguous: was the review of the design or of the document?

Reproducer recipe: APPLIED_ACTION_ASSIGNMENT(action_ref,
(product_def, document_file)).

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'APPLIED_ACTION_ASSIGNMENT')
  contains(b'DOCUMENT_FILE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M137",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where an "
        "APPLIED_ACTION_ASSIGNMENT distributes a single ACTION across a mixed-class "
        "items list containing both a PRODUCT_DEFINITION and a DOCUMENT_FILE, making "
        "the action domain semantics ambiguous; "
        "input: AP203 STEP file with an APPLIED_ACTION_ASSIGNMENT whose items list "
        "spans two incompatible classes — PRODUCT_DEFINITION (a design artifact) and "
        "DOCUMENT_FILE (a document artifact); per ISO 10303-41 the "
        "applied_action_assignment.items attribute carries a SELECT type with allowed "
        "subtypes that should be homogeneous within a single assignment; mixing a "
        "PRODUCT_DEFINITION and a DOCUMENT_FILE in the same ACTION assignment is "
        "semantically ambiguous: was the engineering review performed on the design "
        "model, or on the document? PDM tools that route action results back to their "
        "targets cannot determine which sub-system receives the review outcome; "
        "correct approach is to split into two separate homogeneous "
        "APPLIED_ACTION_ASSIGNMENT instances, one targeting the PRODUCT_DEFINITION "
        "and one targeting the DOCUMENT_FILE; "
        "kernel must detect mixed-class items list and reject or warn with request to "
        "split into homogeneous assignments; "
        "synonyms: AP203 multi-arity action, PDM action target ambiguity, "
        "applied_action mixes products and documents, ACTION_ASSIGNMENT crosses class "
        "boundary, AP203 action ambiguous arity, PDM action targets multiple kinds"
    ),
    schema="AP242",
)


def _render_m137() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with mixed-class APPLIED_ACTION_ASSIGNMENT.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        PRODUCT / PRODUCT_DEFINITION_FORMATION / PRODUCT_DEFINITION
      #30        DOCUMENT / DOCUMENT_TYPE / DOCUMENT_FILE — the document artifact
      #40        ACTION / ACTION_METHOD / ACTION_STATUS entities
      #50        APPLIED_ACTION_ASSIGNMENT — DEFECT: items=(#22, #32) mixes classes
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M137: AP203 APPLIED_ACTION_ASSIGNMENT with mixed-class items list */")
    lines.append("/* DEFECT: single ACTION assignment targets both PRODUCT_DEFINITION and DOCUMENT_FILE */")
    lines.append("/* Domain semantics are ambiguous: was the review of the design or the document? */")
    lines.append("/* Per ISO 10303-41 items should be homogeneous; fix: split into two assignments */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'APPLIED_ACTION_ASSIGNMENT') */")
    lines.append("/* Byte assertion: contains(b'DOCUMENT_FILE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M137: AP203 APPLIED_ACTION_ASSIGNMENT mixed-class items PRODUCT_DEFINITION DOCUMENT_FILE'),'2;1');")
    lines.append("FILE_NAME('M137.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Design artifact: PRODUCT and its PRODUCT_DEFINITION */")
    lines.append("#20=PRODUCT('PART-101','Bracket Assembly','Structural mounting bracket',(#1));")
    lines.append("#21=PRODUCT_DEFINITION_FORMATION('rev_C','Third revision',#20);")
    lines.append("#22=PRODUCT_DEFINITION('design','',#21,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* Byte assertion: contains(b'DOCUMENT_FILE') */")
    lines.append("/* Document artifact: DOCUMENT_FILE referencing a design specification PDF */")
    lines.append("#30=DOCUMENT('DOC-101','Bracket Assembly Design Spec',");
    lines.append("  'Technical specification for bracket assembly');")
    lines.append("#31=DOCUMENT_TYPE('design_specification');")
    lines.append("/* DEFECT contributor: DOCUMENT_FILE is an incompatible class to mix with PRODUCT_DEFINITION */")
    lines.append("#32=DOCUMENT_FILE('bracket-spec-rev-C.pdf',#30,$,$,$,#31);")
    lines.append("/* Engineering review ACTION targeting the rev_C release decision */")
    lines.append("#40=ACTION('review-2024-Q4','Engineering design review Q4 2024',$);")
    lines.append("#41=ACTION_METHOD('design_review','Standard design review procedure',$,'approved');")
    lines.append("#42=ACTION_STATUS('approved');")
    lines.append("/* Byte assertion: contains(b'APPLIED_ACTION_ASSIGNMENT') */")
    lines.append("/* DEFECT: items list mixes PRODUCT_DEFINITION (#22) and DOCUMENT_FILE (#32) */")
    lines.append("/* A correct file would use two separate APPLIED_ACTION_ASSIGNMENT instances: */")
    lines.append("/*   one with items=(#22) for the design, one with items=(#32) for the document */")
    lines.append("/* With a single mixed-class assignment the ACTION receiver cannot route correctly */")
    lines.append("#50=APPLIED_ACTION_ASSIGNMENT(#40,(#22,#32),ACTION_REQUEST_SOLUTION(#41,#40));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-applied-action-assignment-mixed-class-items',")
    lines.append("  (#20,#21,#22,#30,#31,#32,#40,#41,#42,#50));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M137','M137','M137',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m137(path) -> None:
    Path(path).write_text(_render_m137())


f.render = _render_m137  # type: ignore[method-assign]
f.write = _write_m137    # type: ignore[method-assign]
