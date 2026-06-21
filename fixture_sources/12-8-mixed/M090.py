"""M090 — AP210 BoM line item with no PRODUCT_DEFINITION chain.

Catalog claim: A NEXT_ASSEMBLY_USAGE_OCCURRENCE in a PCB BoM names a
child PRODUCT (e.g. R0805_10K) but the child has no
PRODUCT_DEFINITION_FORMATION / PRODUCT_DEFINITION / SHAPE_DEFINITION_REPRESENTATION
chain. The BoM contains only a name.

Reproducer recipe: NAUO('R1','R1','at_corner', parent_PD, child_PRODUCT, $)
where the child PRODUCT has no PD.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M090",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP210 NEXT_ASSEMBLY_USAGE_OCCURRENCE with child "
        "PRODUCT that has no PRODUCT_DEFINITION chain; "
        "input: AP210 STEP file where a PCB assembly uses NEXT_ASSEMBLY_USAGE_OCCURRENCE "
        "('R1','R1','at_corner', parent_product_definition, child_product, $) where "
        "child_product is PRODUCT('R0805_10K','10k resistor 0805','0805 resistor',(#product_ctx)) "
        "but the child PRODUCT has no associated PRODUCT_DEFINITION_FORMATION, "
        "no PRODUCT_DEFINITION, and no SHAPE_DEFINITION_REPRESENTATION; "
        "the BoM line item contains only a component name/refdes — no geometry, no MPN "
        "association, no footprint reference, no mounting location; "
        "per AP210 §4 component_feature_joint_relationship rules a BoM entry must have a "
        "complete PD chain so receivers can resolve the component's footprint and placement; "
        "a name-only BoM entry cannot be placed in layout or used for procurement; "
        "kernel must detect missing PD chain, synthesize a placeholder PD, drop the line "
        "item, or reject the BoM; "
        "synonyms: BoM stub, PCB part definition missing, AP210 NAUO has no PRODUCT_DEFINITION "
        "chain, BoM line item is name-only, PDM child has no geometry, PCB BoM has refdes "
        "but no part, AP210 component without geometry, BoM strings only"
    ),
    schema="AP242",
)


def _render_m090() -> str:
    """Render AP210 file with NAUO child PRODUCT missing PRODUCT_DEFINITION chain.

    Uses ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       PRODUCT_CONTEXT
      #30       Parent PRODUCT (the board assembly)
      #31       Parent PRODUCT_DEFINITION_FORMATION
      #32       Parent PRODUCT_DEFINITION_CONTEXT
      #33       Parent PRODUCT_DEFINITION
      #40       Child PRODUCT ('R0805_10K') — NO PD chain, just a bare PRODUCT — defect
      #50       NEXT_ASSEMBLY_USAGE_OCCURRENCE referencing parent PD and child PRODUCT
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain for the assembly (parent side only)
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M090: AP210 BoM line item with no PRODUCT_DEFINITION chain */")
    lines.append("/* DEFECT: NEXT_ASSEMBLY_USAGE_OCCURRENCE child PRODUCT has no PD chain */")
    lines.append("/* BoM entry R0805_10K has name only — no geometry, footprint, or MPN */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M090: AP210 BoM NAUO child missing PRODUCT_DEFINITION chain'),'2;1');")
    lines.append("FILE_NAME('M090.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("FILE_SCHEMA(('ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN { 1 0 10303 210 3 1 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('electronic_assembly_interconnect_and_packaging_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'electronic_assembly_interconnect_and_packaging_design',2014,#1);")
    lines.append("/* Standard unit context — mm */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('pcb','3D'));")
    lines.append("/* PRODUCT_CONTEXT for the PCB application */")
    lines.append("#20=PRODUCT_CONTEXT('',#1,'electronic');")
    lines.append("/* Parent board assembly — has full PD chain */")
    lines.append("#30=PRODUCT('PCB_ASSEMBLY','PCB Assembly','Main PCB board',(#20));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('','',#30);")
    lines.append("#32=PRODUCT_DEFINITION_CONTEXT(#1,'assembly');")
    lines.append("#33=PRODUCT_DEFINITION('','',#31,#32);")
    lines.append("/* Byte assertion: child PRODUCT with NO PRODUCT_DEFINITION chain */")
    lines.append("/* DEFECT: R0805_10K is a bare PRODUCT with no PD formation, definition, or shape */")
    lines.append("/* A BoM receiver cannot resolve footprint, MPN, or placement from this stub */")
    lines.append("#40=PRODUCT('R0805_10K','10k resistor 0805','0805 resistor 10kohm',(#20));")
    lines.append("/* Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') */")
    lines.append("/* NAUO references parent PD (#33) and child PRODUCT (#40) */")
    lines.append("/* The child #40 has no PRODUCT_DEFINITION — this is the defect */")
    lines.append("#50=NEXT_ASSEMBLY_USAGE_OCCURRENCE('R1','R1','at_corner',#33,#40,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-bom-nauo-child-missing-product-definition-chain',")
    lines.append("  (#30,#33,#40,#50));")
    lines.append("/* Product chain — parent board assembly only */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M090','M090','M090',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m090(path) -> None:
    Path(path).write_text(_render_m090())


f.render = _render_m090  # type: ignore[method-assign]
f.write = _write_m090    # type: ignore[method-assign]
