"""M127 — AP203 DOCUMENT_FILE referenced with empty URI / path field.

Catalog claim: A DOCUMENT_FILE is referenced as a specification document but
its identifier, name, and description fields are all empty strings. Consumers
cannot resolve the referenced document to any URI or path; the reference is
effectively unreachable.

Reproducer recipe: DOCUMENT_FILE('','','',doc_type) referenced via
APPLIED_DOCUMENT_REFERENCE.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'DOCUMENT_FILE')
  contains(b"DOCUMENT_FILE('','','',")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M127",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where a DOCUMENT_FILE "
        "entity has empty identifier, name, and description fields making it "
        "unresolvable; "
        "input: AP203 STEP file where a DOCUMENT_FILE entity is referenced via "
        "APPLIED_DOCUMENT_REFERENCE as the specification document for a product "
        "definition, but all three string fields — identifier, name, and description "
        "— are empty strings: DOCUMENT_FILE('','','',doc_type); consumers performing "
        "a document lookup cannot identify, locate, or retrieve the referenced document "
        "because there is no identifier to match against a document management system "
        "and no name or description to disambiguate the reference; "
        "per ISO 10303-203 §5.4 document reference completeness, DOCUMENT_FILE requires "
        "a non-empty identifier so that the referenced document can be resolved; an "
        "empty-identifier DOCUMENT_FILE is an incomplete dangling reference; "
        "kernel must detect empty document references and warn, drop the reference, "
        "or reject as malformed; "
        "synonyms: AP203 doc URI missing, empty document ref, PDM dangling spec link, "
        "DOCUMENT_FILE has no URI, AP203 document reference is empty, "
        "spec link points to nothing"
    ),
    schema="AP242",
)


def _render_m127() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with DOCUMENT_FILE having empty fields.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        DOCUMENT_TYPE ('specification')
      #21        DOCUMENT_FILE('','','',#20) — DEFECT: all string fields empty
      #22        PRODUCT and PRODUCT_DEFINITION_FORMATION for the part
      #23        PRODUCT_DEFINITION
      #24        APPLIED_DOCUMENT_REFERENCE linking #21 to #23 — references unresolvable doc
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M127: AP203 DOCUMENT_FILE referenced with empty URI / path field */")
    lines.append("/* DEFECT: DOCUMENT_FILE('','','',doc_type) — identifier, name, description all empty */")
    lines.append("/* APPLIED_DOCUMENT_REFERENCE links the part to an unresolvable document */")
    lines.append("/* Consumers cannot retrieve the referenced spec because no URI or identifier exists */")
    lines.append("/* Per AP203 §5.4 DOCUMENT_FILE must have a non-empty identifier for resolution */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'DOCUMENT_FILE') */")
    lines.append("/* Byte assertion: contains(b\"DOCUMENT_FILE('','','',\") */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M127: AP203 DOCUMENT_FILE with empty identifier name and description'),'2;1');")
    lines.append("FILE_NAME('M127.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Document type for the referenced specification */")
    lines.append("#20=DOCUMENT_TYPE('specification');")
    lines.append("/* Byte assertion: contains(b'DOCUMENT_FILE') */")
    lines.append("/* Byte assertion: contains(b\"DOCUMENT_FILE('','','',\") */")
    lines.append("/* DEFECT: all three string fields are empty — document is unresolvable */")
    lines.append("/* A valid DOCUMENT_FILE would have: DOCUMENT_FILE('SPEC-001','Widget Spec','Rev A drawing',#20) */")
    lines.append("#21=DOCUMENT_FILE('','','',#20);")
    lines.append("/* Product being documented */")
    lines.append("#22=PRODUCT('PART-001','Widget','Precision widget',(#1));")
    lines.append("#23=PRODUCT_DEFINITION_FORMATION('A','Initial',#22);")
    lines.append("#24=PRODUCT_DEFINITION_CONTEXT(#1,'design');")
    lines.append("#25=PRODUCT_DEFINITION('release','',#23,#24);")
    lines.append("/* APPLIED_DOCUMENT_REFERENCE: links product definition to the empty DOCUMENT_FILE */")
    lines.append("#26=APPLIED_DOCUMENT_REFERENCE(#21,'specification',(#25));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-document-file-empty-uri-path-field',")
    lines.append("  (#21,#22,#23,#25,#26));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M127','M127','M127',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m127(path) -> None:
    Path(path).write_text(_render_m127())


f.render = _render_m127  # type: ignore[method-assign]
f.write = _write_m127    # type: ignore[method-assign]
