"""M145 — AP210 fixed-side reference inverts top/bottom semantics

Catalog claim: A board with stackup top -> top_signal -> .. -> bottom
is exported with the 'top_signal' ply annotated as fixed_side = 'BOTTOM'.
Components placed by the assembly using fixed_side to disambiguate
top/bottom land on the wrong PCB face.

Reproducer recipe: a LAMINATE_OR_PLY_DEFINITION named 'top_signal'
with a PROPERTY_DEFINITION('layer_side_reference','..',ply) and
DESCRIPTIVE_REPRESENTATION_ITEM('fixed_side','BOTTOM').

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'fixed_side')
  contains(b"'BOTTOM'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M145",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a LAMINATE_OR_PLY_DEFINITION named 'top_signal' is the first signal "
        "ply below the top surface ply in the physical stackup but is incorrectly annotated "
        "with fixed_side = 'BOTTOM' via a DESCRIPTIVE_REPRESENTATION_ITEM; "
        "input: AP210 STEP file with a four-ply stackup — #100 'top_copper' (1st, topmost), "
        "#101 'top_signal' (2nd), #102 'core' (3rd), #103 'bot_copper' (4th, bottommost) — "
        "declared in LAMINATE_TABLE #110 in physical top-to-bottom order; "
        "a PROPERTY_DEFINITION #120 'layer_side_reference' attached to #101 ('top_signal') "
        "is represented by DESCRIPTIVE_REPRESENTATION_ITEM #121 with value 'BOTTOM'; "
        "components placed by the assembly using fixed_side='BOTTOM' to disambiguate "
        "PCB faces land on the wrong PCB face — on the bottom instead of the top signal layer; "
        "per ISO 10303-210 §5 the fixed_side attribute must agree with the ply's position "
        "in the LAMINATE_TABLE stackup order; "
        "kernel must validate fixed_side against the ply's position in the LAMINATE_TABLE "
        "and reject or warn; "
        "synonyms: PCB top side mirrored, AP210 fixed-side reference inverted, "
        "AP210 top side mirrored, PCB side reference inverted, ECAD layer fixed_side wrong, "
        "PCB top/bottom inverted, AP210 side reference flipped, fixed_side semantic wrong, "
        "stackup top labeled BOTTOM"
    ),
    schema="AP242",
)


def _render_m145() -> str:
    """Render AP210 file where top_signal ply is annotated fixed_side='BOTTOM'.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      LAMINATE_OR_PLY_DEFINITION 'top_copper' (topmost ply)
      #101      LAMINATE_OR_PLY_DEFINITION 'top_signal' (2nd ply — near top)
      #102      LAMINATE_OR_PLY_DEFINITION 'core' (dielectric core)
      #103      LAMINATE_OR_PLY_DEFINITION 'bot_copper' (bottommost ply)
      #110      LAMINATE_TABLE — physical order: top_copper, top_signal, core, bot_copper
      #120      PROPERTY_DEFINITION 'layer_side_reference' attached to top_signal (#101)
      #121      DESCRIPTIVE_REPRESENTATION_ITEM 'fixed_side' = 'BOTTOM'  — DEFECT
      #122      PROPERTY_DEFINITION_REPRESENTATION
      #130      REPRESENTATION holding the property item
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M145: AP210 fixed-side reference inverts top/bottom semantics */")
    lines.append("/* DEFECT: 'top_signal' ply is 2nd from top in LAMINATE_TABLE */")
    lines.append("/* but DESCRIPTIVE_REPRESENTATION_ITEM annotates it fixed_side='BOTTOM' */")
    lines.append("/* Components using fixed_side to resolve placement land on the wrong PCB face */")
    lines.append("/* Per ISO 10303-210 §5 fixed_side must match ply position in stackup */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'fixed_side') */")
    lines.append("/* Byte assertion: contains(b\"'BOTTOM'\") */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M145: AP210 fixed-side reference inverts top/bottom'),'2;1');")
    lines.append("FILE_NAME('M145.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Four-ply stackup (top to bottom) */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('top_copper',$,$,$,LENGTH_MEASURE(0.035));")
    lines.append("/* top_signal is the 2nd ply — physically near the top face of the board */")
    lines.append("#101=LAMINATE_OR_PLY_DEFINITION('top_signal',$,$,$,LENGTH_MEASURE(0.035));")
    lines.append("#102=LAMINATE_OR_PLY_DEFINITION('core',$,$,$,LENGTH_MEASURE(0.2));")
    lines.append("#103=LAMINATE_OR_PLY_DEFINITION('bot_copper',$,$,$,LENGTH_MEASURE(0.035));")
    lines.append("/* LAMINATE_TABLE: physical order is top_copper -> top_signal -> core -> bot_copper */")
    lines.append("#110=LAMINATE_TABLE('stackup',(#100,#101,#102,#103));")
    lines.append("/* PROPERTY_DEFINITION records the layer side reference for top_signal ply */")
    lines.append("#120=PROPERTY_DEFINITION('layer_side_reference','PCB side annotation',#101);")
    lines.append("/* Byte assertion: contains(b'fixed_side') */")
    lines.append("/* Byte assertion: contains(b\"'BOTTOM'\") */")
    lines.append("/* DEFECT: top_signal (2nd from top) labelled fixed_side='BOTTOM' — inverted */")
    lines.append("/* Correct value for the 2nd-from-top ply would be 'TOP' */")
    lines.append("#121=DESCRIPTIVE_REPRESENTATION_ITEM('fixed_side','BOTTOM');")
    lines.append("#130=REPRESENTATION('side_ref',(#121),#14);")
    lines.append("#122=PROPERTY_DEFINITION_REPRESENTATION(#120,#130);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-fixed-side-reference-inverts-top-bottom-semantics',")
    lines.append("  (#100,#101,#102,#103,#110,#120,#121,#130,#122));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M145','M145','M145',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m145(path) -> None:
    Path(path).write_text(_render_m145())


f.render = _render_m145  # type: ignore[method-assign]
f.write = _write_m145    # type: ignore[method-assign]
