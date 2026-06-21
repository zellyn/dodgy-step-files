"""M153 — AP210 buried via has only one terminating layer reference

Catalog claim: A buried VIA_DEFINITION is declared with a single
terminating LAMINATE_OR_PLY_DEFINITION. A buried via must terminate
at two distinct internal plies; with only one termination, the via is
dangling - it begins at one layer and goes nowhere.

Reproducer recipe: VIA_DEFINITION('dangling_via',..,(ply_inner_2))
with DESCRIPTIVE_REPRESENTATION_ITEM('via_kind','BURIED').

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'VIA_DEFINITION')
  contains(b'BURIED')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M153",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a buried VIA_DEFINITION is declared with only one terminating "
        "LAMINATE_OR_PLY_DEFINITION instead of the required two distinct internal plies; "
        "input: AP210 STEP file containing a 4-layer stackup with plies: "
        "'copper_top' (layer 1), 'inner_1' (layer 2), 'inner_2' (layer 3), 'copper_bot' (layer 4); "
        "a VIA_DEFINITION 'dangling_via' is declared as buried (via_kind='BURIED') via "
        "DESCRIPTIVE_REPRESENTATION_ITEM; "
        "the via references only one termination ply '#103' (inner_2, layer 3) but omits the "
        "second termination; a properly formed buried via must reference both start and stop "
        "plies — e.g. inner_1 (layer 2) to inner_2 (layer 3); "
        "with only one termination the via begins at inner_2 and goes nowhere; "
        "drill simulation tools cannot compute a valid via barrel — they fail silently or crash; "
        "per ISO 10303-210 §6 buried via two-endpoint invariant requires exactly two distinct "
        "internal ply references; "
        "kernel must validate buried vias have exactly two termination plies and reject or warn; "
        "synonyms: buried via dangling, AP210 via half-defined, ECAD via single endpoint, "
        "AP210 buried via one end, PCB via dangling layer, ECAD buried via missing termination, "
        "AP210 buried via single end, PCB via missing endpoint"
    ),
    schema="AP242",
)


def _render_m153() -> str:
    """Render AP210 file with buried VIA_DEFINITION missing one termination ply.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      LAMINATE_OR_PLY_DEFINITION 'copper_top' — layer 1
      #101      LAMINATE_OR_PLY_DEFINITION 'inner_1'    — layer 2
      #102      LAMINATE_OR_PLY_DEFINITION 'core'       — dielectric
      #103      LAMINATE_OR_PLY_DEFINITION 'inner_2'    — layer 3
      #104      LAMINATE_OR_PLY_DEFINITION 'copper_bot' — layer 4
      #110      LAMINATE_TABLE 'pcb_stackup' — 4-layer board
      #120      VIA_DEFINITION 'dangling_via' — DEFECT: only one ply ref (#103)
      #121      DESCRIPTIVE_REPRESENTATION_ITEM 'via_kind' = 'BURIED'
      #122      REPRESENTATION holding the via_kind item
      #123      PROPERTY_DEFINITION 'via_kind' on dangling_via
      #124      PROPERTY_DEFINITION_REPRESENTATION
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M153: AP210 buried via has only one terminating layer reference */")
    lines.append("/* DEFECT: VIA_DEFINITION 'dangling_via' declares via_kind=BURIED */")
    lines.append("/* but references only one ply (inner_2) instead of two (inner_1 + inner_2) */")
    lines.append("/* A buried via needs start-ply and stop-ply; with one ply it goes nowhere */")
    lines.append("/* Per ISO 10303-210 §6 buried via two-endpoint invariant requires 2 plies */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* Byte assertion: contains(b'BURIED') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M153: AP210 buried via with single termination ply'),'2;1');")
    lines.append("FILE_NAME('M153.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* 4-layer stackup plies */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('copper_top',LENGTH_MEASURE(0.035),$);")
    lines.append("#101=LAMINATE_OR_PLY_DEFINITION('inner_1',LENGTH_MEASURE(0.018),$);")
    lines.append("#102=LAMINATE_OR_PLY_DEFINITION('core',LENGTH_MEASURE(0.360),$);")
    lines.append("#103=LAMINATE_OR_PLY_DEFINITION('inner_2',LENGTH_MEASURE(0.018),$);")
    lines.append("#104=LAMINATE_OR_PLY_DEFINITION('copper_bot',LENGTH_MEASURE(0.035),$);")
    lines.append("#110=LAMINATE_TABLE('pcb_stackup',(#100,#101,#102,#103,#104));")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* DEFECT: dangling_via only references #103 (inner_2) as termination *)")
    lines.append("/* A buried via from inner_1 to inner_2 must reference both #101 and #103 */")
    lines.append("#120=VIA_DEFINITION('dangling_via',LENGTH_MEASURE(0.1),LENGTH_MEASURE(0.1),$,#103);")
    lines.append("/* Byte assertion: contains(b'BURIED') */")
    lines.append("/* via_kind='BURIED' property marks this as a buried via — requires 2 plies */")
    lines.append("#121=DESCRIPTIVE_REPRESENTATION_ITEM('via_kind','BURIED');")
    lines.append("#122=REPRESENTATION('via_props',(#121),#14);")
    lines.append("#123=PROPERTY_DEFINITION('via_kind','Via type classification',#120);")
    lines.append("#124=PROPERTY_DEFINITION_REPRESENTATION(#123,#122);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-buried-via-single-termination-ply-dangling',")
    lines.append("  (#100,#101,#102,#103,#104,#110,#120,#121,#122,#123,#124));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M153','M153','M153',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m153(path) -> None:
    Path(path).write_text(_render_m153())


f.render = _render_m153  # type: ignore[method-assign]
f.write = _write_m153    # type: ignore[method-assign]
