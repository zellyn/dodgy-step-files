"""M154 — AP210 placement footprint pin count conflicts with library footprint

Catalog claim: A NEXT_ASSEMBLY_USAGE_OCCURRENCE places component U1
with a 4-pin layout, but the referenced PRODUCT 'BGA_84' has 84 pins
in its package model. The placement footprint and the component-
library footprint disagree on pin count.

Reproducer recipe: PRODUCT('BGA_84',..) with
library_pin_count='84'; placement assigning only 4 TERMINALs.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
  contains(b'library_pin_count')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M154",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a NEXT_ASSEMBLY_USAGE_OCCURRENCE places component U1 using a 4-pin "
        "layout, but the referenced PRODUCT 'BGA_84' declares library_pin_count='84'; "
        "input: AP210 STEP file containing a PRODUCT 'BGA_84' representing an 84-pin BGA; "
        "a PROPERTY_DEFINITION 'library_pin_count' on BGA_84 carries "
        "DESCRIPTIVE_REPRESENTATION_ITEM value '84' — the library declares 84 pads; "
        "the NEXT_ASSEMBLY_USAGE_OCCURRENCE 'U1_placement' places BGA_84 on the board; "
        "the placement footprint assigns only 4 TERMINAL entities (T1..T4) on the board; "
        "the library says 84 pins; the placement has 4 pads; "
        "84 unconnected component pads float to unknown potentials; "
        "netlist connectivity is broken for 80 signals; "
        "the ECAD exporter copied a placement template from a small 4-pin SOT-23 design "
        "without updating the footprint for the BGA_84 component; "
        "per ISO 10303-210 §6 component vs library consistency requires placement footprint "
        "pin count to match the library declaration; "
        "kernel must validate placement footprint pin count against library declaration "
        "and reject or warn; "
        "synonyms: AP210 footprint pin count wrong, BGA library 84 pins placement 4, "
        "ECAD package mismatch, AP210 package mismatch, PCB footprint vs library, "
        "ECAD pin count contradiction"
    ),
    schema="AP242",
)


def _render_m154() -> str:
    """Render AP210 file with BGA_84 library declaring 84 pins but placement has 4.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       PRODUCT 'BGA_84' — the 84-pin BGA library component
      #51       PROPERTY_DEFINITION 'library_pin_count' on BGA_84
      #52       DESCRIPTIVE_REPRESENTATION_ITEM 'library_pin_count' = '84'
      #53       REPRESENTATION holding the library_pin_count item
      #54       PROPERTY_DEFINITION_REPRESENTATION
      #60       PRODUCT 'PCB_BOARD' — the parent assembly
      #70       NEXT_ASSEMBLY_USAGE_OCCURRENCE 'U1_placement' — DEFECT: 4-pin layout
      #100      CARTESIAN_POINT for T1 at (5.0, 5.0, 0.0)
      #101      TERMINAL 'T1' — placement pad 1 of 4 (library has 84)
      #102      CARTESIAN_POINT for T2 at (6.0, 5.0, 0.0)
      #103      TERMINAL 'T2' — placement pad 2 of 4
      #104      CARTESIAN_POINT for T3 at (5.0, 6.0, 0.0)
      #105      TERMINAL 'T3' — placement pad 3 of 4
      #106      CARTESIAN_POINT for T4 at (6.0, 6.0, 0.0)
      #107      TERMINAL 'T4' — placement pad 4 of 4  (library declares 84)
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M154: AP210 placement footprint pin count conflicts with library footprint */")
    lines.append("/* DEFECT: PRODUCT 'BGA_84' library_pin_count='84' but U1 placement has only 4 TERMINALs */")
    lines.append("/* 80 BGA pads are unconnected — netlist broken for 80 signals */")
    lines.append("/* Exporter used a 4-pin SOT-23 template for an 84-pin BGA component */")
    lines.append("/* Per ISO 10303-210 §6 placement footprint pin count must match library */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') */")
    lines.append("/* Byte assertion: contains(b'library_pin_count') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M154: AP210 BGA_84 library 84 pins vs placement 4 pins'),'2;1');")
    lines.append("FILE_NAME('M154.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("FILE_SCHEMA(('ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN { 1 0 10303 210 3 1 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('electronic_assembly_interconnect_and_packaging_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'electronic_assembly_interconnect_and_packaging_design',2014,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('pcb','3D'));")
    lines.append("/* BGA_84 library component: 84-pin BGA package */")
    lines.append("#50=PRODUCT('BGA_84','BGA_84','84-pin BGA package',(#1));")
    lines.append("/* Byte assertion: contains(b'library_pin_count') */")
    lines.append("/* library_pin_count property declares the component has 84 pins */")
    lines.append("#51=PROPERTY_DEFINITION('library_pin_count','Component library pin count',#50);")
    lines.append("#52=DESCRIPTIVE_REPRESENTATION_ITEM('library_pin_count','84');")
    lines.append("#53=REPRESENTATION('lib_props',(#52),#14);")
    lines.append("#54=PROPERTY_DEFINITION_REPRESENTATION(#51,#53);")
    lines.append("/* PCB board assembly product */")
    lines.append("#60=PRODUCT('PCB_BOARD','PCB_BOARD','Main PCB assembly',(#1));")
    lines.append("/* Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') */")
    lines.append("/* NEXT_ASSEMBLY_USAGE_OCCURRENCE places BGA_84 as U1 on the board */")
    lines.append("#70=NEXT_ASSEMBLY_USAGE_OCCURRENCE('U1_placement','U1','U1 BGA_84 placement',#60,#50,$);")
    lines.append("/* DEFECT: placement footprint has only 4 TERMINALs; library declares 84 */")
    lines.append("#100=CARTESIAN_POINT('T1_loc',(5.0,5.0,0.0));")
    lines.append("#101=TERMINAL('T1',#100);")
    lines.append("#102=CARTESIAN_POINT('T2_loc',(6.0,5.0,0.0));")
    lines.append("#103=TERMINAL('T2',#102);")
    lines.append("#104=CARTESIAN_POINT('T3_loc',(5.0,6.0,0.0));")
    lines.append("#105=TERMINAL('T3',#104);")
    lines.append("#106=CARTESIAN_POINT('T4_loc',(6.0,6.0,0.0));")
    lines.append("#107=TERMINAL('T4',#106);")
    lines.append("/* 80 BGA pads unaccounted for — connectivity broken for 80 signals */")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-placement-pin-count-conflicts-library-bga84',")
    lines.append("  (#50,#51,#52,#53,#54,#60,#70,#100,#101,#102,#103,#104,#105,#106,#107));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M154','M154','M154',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m154(path) -> None:
    Path(path).write_text(_render_m154())


f.render = _render_m154  # type: ignore[method-assign]
f.write = _write_m154    # type: ignore[method-assign]
