"""M149 — AP210 component pin numbering doesn't match physical pin sequence

Catalog claim: A 4-pin SOT-23 package declares pins 1, 2, 3, 4 around
the package perimeter, but the geometric order of TERMINAL placements
walks counterclockwise (1, 4, 3, 2) instead of the package datasheet's
clockwise order. Soldering follows the geometric placement; the
netlist's pin assignment is rotated 180 deg.

Reproducer recipe: four TERMINAL entries with names 'pin1' .. 'pin4'
placed at coordinates that walk CCW instead of CW.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  count_entity_def(b'TERMINAL') >= 4

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M149",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where four TERMINAL placements for a SOT-23 package walk counterclockwise "
        "(pin1, pin4, pin3, pin2) instead of the datasheet clockwise sequence (pin1, pin2, pin3, pin4); "
        "input: AP210 STEP file containing PRODUCT 'SOT23' representing a 4-pin SOT-23 package; "
        "four TERMINAL entities are placed at physical coordinates: "
        "pin1 at (0.0, 0.0), pin4 at (0.95, 0.0), pin3 at (0.95, 2.9), pin2 at (0.0, 2.9); "
        "geometric traversal order is CCW: 1->4->3->2, but the package datasheet specifies "
        "CW order 1->2->3->4 when viewed from the component top side; "
        "the netlist assigns signals to pin indices that are rotated 180 degrees from the "
        "physical copper pads — a drain may be soldered to a gate pad; "
        "per ISO 10303-210 §6 terminal physical_location ordering must match the package "
        "datasheet's declared pin sequence; "
        "kernel must validate terminal indexing against package datasheet conventions and "
        "reject or warn on inconsistent ordering; "
        "synonyms: AP210 pin order swapped, PCB pin numbering CCW, ECAD pin sequence wrong, "
        "PCB pin order CCW vs CW, AP210 pin sequence inverted, pin numbering CW vs CCW, "
        "package pin geometric order wrong"
    ),
    schema="AP242",
)


def _render_m149() -> str:
    """Render AP210 file with SOT-23 TERMINAL placements walking CCW instead of CW.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       PRODUCT 'SOT23' — the 4-pin package
      #100      CARTESIAN_POINT pin1 (0.0, 0.0, 0.0)
      #101      TERMINAL 'pin1' at origin
      #102      CARTESIAN_POINT pin4 (0.95, 0.0, 0.0)  <- CCW step 2 (should be pin2)
      #103      TERMINAL 'pin4' — DEFECT: second in geometric order, index 4
      #104      CARTESIAN_POINT pin3 (0.95, 2.9, 0.0)  <- CCW step 3
      #105      TERMINAL 'pin3' — DEFECT: third in geometric order, index 3
      #106      CARTESIAN_POINT pin2 (0.0, 2.9, 0.0)   <- CCW step 4 (should be pin4)
      #107      TERMINAL 'pin2' — DEFECT: fourth in geometric order, index 2
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M149: AP210 component pin numbering doesn't match physical pin sequence */")
    lines.append("/* DEFECT: SOT-23 TERMINAL placements walk CCW (1,4,3,2) not CW (1,2,3,4) */")
    lines.append("/* Soldering follows geometric order; netlist pin assignments are rotated 180 deg */")
    lines.append("/* Per ISO 10303-210 §6 terminal ordering must match package datasheet pin sequence */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'TERMINAL') >= 4 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M149: AP210 SOT-23 pin order CCW vs CW'),'2;1');")
    lines.append("FILE_NAME('M149.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* SOT-23 package product */")
    lines.append("#50=PRODUCT('SOT23','SOT23','4-pin SOT-23 package',(#1));")
    lines.append("/* Byte assertion: count_entity_def(b'TERMINAL') >= 4 */")
    lines.append("/* Pin 1: bottom-left corner — correct starting point */")
    lines.append("#100=CARTESIAN_POINT('pin1_loc',(0.0,0.0,0.0));")
    lines.append("#101=TERMINAL('pin1',#100);")
    lines.append("/* DEFECT: CCW step 2 is pin4 at bottom-right — CW expects pin2 here */")
    lines.append("#102=CARTESIAN_POINT('pin4_loc',(0.95,0.0,0.0));")
    lines.append("#103=TERMINAL('pin4',#102);")
    lines.append("/* DEFECT: CCW step 3 is pin3 at top-right — CW expects pin3 here (coincidence) */")
    lines.append("#104=CARTESIAN_POINT('pin3_loc',(0.95,2.9,0.0));")
    lines.append("#105=TERMINAL('pin3',#104);")
    lines.append("/* DEFECT: CCW step 4 is pin2 at top-left — CW expects pin4 here */")
    lines.append("#106=CARTESIAN_POINT('pin2_loc',(0.0,2.9,0.0));")
    lines.append("#107=TERMINAL('pin2',#106);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-pin-numbering-ccw-vs-cw-sot23-package',")
    lines.append("  (#100,#101,#102,#103,#104,#105,#106,#107));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M149','M149','M149',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m149(path) -> None:
    Path(path).write_text(_render_m149())


f.render = _render_m149  # type: ignore[method-assign]
f.write = _write_m149    # type: ignore[method-assign]
