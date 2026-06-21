"""M140 — AP203 make-or-buy declaration contradicts external supplier record

Catalog claim: A PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE declares
source = .MADE. (made in-house) but an APPLIED_ORGANIZATION_ASSIGNMENT of role
'supplier' designates an external organization for the same part. The make-or-buy
declaration contradicts the supplier record.

Reproducer recipe: PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE
('rev','..',product,.MADE.) and
APPLIED_ORGANIZATION_ASSIGNMENT(org,'supplier',(pd)).

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE')
  contains(b'.MADE.')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M140",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where a "
        "PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE declares source=.MADE. "
        "(manufactured in-house) while an APPLIED_ORGANIZATION_ASSIGNMENT of role "
        "'supplier' simultaneously designates an external organization as supplier "
        "for the same part, creating a make-or-buy contradiction; "
        "input: AP203 STEP file with PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE "
        "carrying the .MADE. enumeration value — meaning the part is produced internally "
        "by the design organization; the same file also contains an "
        "APPLIED_ORGANIZATION_ASSIGNMENT with role='supplier' pointing an external "
        "organization (ExtSupplierCo) at the same PRODUCT_DEFINITION; per ISO 10303-203 "
        "§5.4 the specified_source attribute governs procurement classification: .MADE. "
        "means no external supplier should be declared; .BOUGHT. would permit a supplier "
        "record; the contradiction causes procurement management systems to generate "
        "conflicting purchase orders for a part that should never have been sourced "
        "externally; "
        "kernel must detect the contradiction between specified_source=.MADE. and the "
        "presence of a 'supplier' organization assignment, and reject or warn; "
        "synonyms: AP203 source/supplier mismatch, PDM make-or-buy ambiguity, "
        "MADE part has external supplier, make-or-buy contradicts supplier record, "
        "AP203 make-or-buy contradiction, in-house part has supplier, "
        "PDM source attribute wrong"
    ),
    schema="AP242",
)


def _render_m140() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with make-or-buy contradiction.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        PRODUCT
      #21        PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE(.MADE.) — in-house
      #22        PRODUCT_DEFINITION
      #30        ORGANIZATION — external supplier
      #31        ORGANIZATION_ROLE — 'supplier'
      #32        APPLIED_ORGANIZATION_ASSIGNMENT — DEFECT: supplier assigned to .MADE. part
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M140: AP203 make-or-buy declaration contradicts external supplier record */")
    lines.append("/* DEFECT: PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE(.MADE.) but */")
    lines.append("/*         APPLIED_ORGANIZATION_ASSIGNMENT role='supplier' designates external org */")
    lines.append("/* Per ISO 10303-203 §5.4: .MADE. means no external supplier should be declared */")
    lines.append("/* Procurement systems receive conflicting signals: make it AND buy it */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE') */")
    lines.append("/* Byte assertion: contains(b'.MADE.') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M140: AP203 make-or-buy MADE contradicts supplier APPLIED_ORGANIZATION_ASSIGNMENT'),'2;1');")
    lines.append("FILE_NAME('M140.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Part declared as made in-house */")
    lines.append("#20=PRODUCT('PART-404','Mounting Flange','Precision-machined mounting flange',(#1));")
    lines.append("/* Byte assertion: contains(b'PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE') */")
    lines.append("/* Byte assertion: contains(b'.MADE.') */")
    lines.append("/* DEFECT: .MADE. declares this part is manufactured by the design organization */")
    lines.append("/* A .BOUGHT. source enumeration would permit an external supplier designation */")
    lines.append("/* A .NOT_SPECIFIED. value would be ambiguous but not strictly contradictory */")
    lines.append("#21=PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE(")
    lines.append("  'rev_A','Production specification',#20,.MADE.);")
    lines.append("#22=PRODUCT_DEFINITION('design','',#21,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* External organization designated as supplier — contradicts .MADE. above */")
    lines.append("#30=ORGANIZATION('SUP-999','ExtSupplierCo','External precision machining supplier');")
    lines.append("/* Organization role: 'supplier' — this role is only valid for .BOUGHT. parts *)  ")
    lines.append("#31=ORGANIZATION_ROLE('supplier');")
    lines.append("/* DEFECT: APPLIED_ORGANIZATION_ASSIGNMENT assigns an external supplier (#30) */")
    lines.append("/* to PRODUCT_DEFINITION #22 which was formed with source=.MADE. (#21) */")
    lines.append("/* Contradiction: the part is simultaneously declared made in-house AND has a supplier */")
    lines.append("/* A procurement system would generate both a shop order AND a purchase order */")
    lines.append("#32=APPLIED_ORGANIZATION_ASSIGNMENT(#30,#31,(#22));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-make-or-buy-MADE-contradicts-supplier-assignment',")
    lines.append("  (#20,#21,#22,#30,#31,#32));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M140','M140','M140',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m140(path) -> None:
    Path(path).write_text(_render_m140())


f.render = _render_m140  # type: ignore[method-assign]
f.write = _write_m140    # type: ignore[method-assign]
