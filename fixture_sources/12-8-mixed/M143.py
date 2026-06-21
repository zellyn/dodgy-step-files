"""M143 — AP210 vias declared with stack-up positions out of board-layer order

Catalog claim: A LAMINATE_TABLE declares plies in physical order
(top -> bottom) but VIA_DEFINITION entries cite their terminating
layers in reversed order: the bottom layer is named first, the top
last. A stackup-aware layer router walking the via stack visits
layers in inverted Z sequence; the manufacturer receives bogus drill
ordering instructions.

Reproducer recipe: LAMINATE_TABLE('stackup',(top,mid,bot)) plus
VIA_DEFINITION(.., (bot, top)) with reversed termination list.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'VIA_DEFINITION')
  contains(b'LAMINATE_TABLE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M143",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a LAMINATE_TABLE declares plies in physical order (top -> mid -> bot) "
        "but VIA_DEFINITION entries cite terminating layers in reversed order (bot first, "
        "top last); "
        "input: AP210 STEP file containing a LAMINATE_TABLE named 'stackup' with ply order "
        "(#100 'top_ply', #101 'mid_ply', #102 'bot_ply') representing the physical "
        "top-to-bottom stackup; a VIA_DEFINITION 'via_inverted' at position (5.0,5.0,0.0) "
        "declares its terminating layer pair as (#102, #100) — bot first, top last — "
        "inverting the intended drill traversal direction; "
        "a stackup-aware layer router walking via_inverted visits layers in inverted Z "
        "sequence; the manufacturer receives bogus drill-ordering instructions and may "
        "fabricate vias in the wrong direction causing continuity failures; "
        "per ISO 10303-210 §6 via_definition terminating layers must be listed in the "
        "same physical order as the LAMINATE_TABLE stackup; "
        "kernel must detect the reversed via termination order and reject or warn; "
        "synonyms: AP210 via stackup inversion, PCB drill order wrong, "
        "via terminating layers reversed, AP210 layer-order inconsistent, "
        "PCB via terminating layers reversed, ECAD drill ordering wrong"
    ),
    schema="AP242",
)


def _render_m143() -> str:
    """Render AP210 file with VIA_DEFINITION terminating layers in reversed stackup order.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100-#102 LAMINATE_OR_PLY_DEFINITION for top/mid/bot plies
      #110      LAMINATE_TABLE declaring physical order: top, mid, bot
      #200      CARTESIAN_POINT for via center
      #201      AXIS2_PLACEMENT_3D for via drill axis
      #210      VIA_DEFINITION — DEFECT: termination list reversed (bot, top)
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M143: AP210 vias declared with stack-up positions out of board-layer order */")
    lines.append("/* DEFECT: LAMINATE_TABLE order is (top, mid, bot) but VIA_DEFINITION */")
    lines.append("/* terminating layers are listed reversed: (bot, top) */")
    lines.append("/* Stackup-aware routers visit layers in inverted Z sequence */")
    lines.append("/* Per ISO 10303-210 §6 via termination order must match LAMINATE_TABLE */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* Byte assertion: contains(b'LAMINATE_TABLE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M143: AP210 via stackup termination order inverted'),'2;1');")
    lines.append("FILE_NAME('M143.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Three PCB plies in physical top-to-bottom order */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('top_ply',$,$,$,LENGTH_MEASURE(0.035));")
    lines.append("#101=LAMINATE_OR_PLY_DEFINITION('mid_ply',$,$,$,LENGTH_MEASURE(0.2));")
    lines.append("#102=LAMINATE_OR_PLY_DEFINITION('bot_ply',$,$,$,LENGTH_MEASURE(0.035));")
    lines.append("/* Byte assertion: contains(b'LAMINATE_TABLE') */")
    lines.append("/* LAMINATE_TABLE declares physical stackup order: top_ply, mid_ply, bot_ply */")
    lines.append("#110=LAMINATE_TABLE('stackup',(#100,#101,#102));")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* Via drill axis at board position (5.0, 5.0, 0.0) */")
    lines.append("#200=CARTESIAN_POINT('via_loc',(5.0,5.0,0.0));")
    lines.append("#201=AXIS2_PLACEMENT_3D('via_axis',#200,$,$);")
    lines.append("/* DEFECT: terminating layers listed as (#102, #100) — bot first, top last */")
    lines.append("/* Correct order matching LAMINATE_TABLE would be (#100, #102) — top first */")
    lines.append("/* A stackup-aware router walks via layers in inverted Z sequence */")
    lines.append("#210=VIA_DEFINITION('via_inverted',(#102,#100),#201,LENGTH_MEASURE(0.3));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-via-stackup-termination-order-inverted',")
    lines.append("  (#100,#101,#102,#110,#200,#201,#210));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M143','M143','M143',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m143(path) -> None:
    Path(path).write_text(_render_m143())


f.render = _render_m143  # type: ignore[method-assign]
f.write = _write_m143    # type: ignore[method-assign]
