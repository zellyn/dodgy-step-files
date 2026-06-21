"""M152 — AP210 microvia depth exceeds substrate thickness

Catalog claim: A VIA_DEFINITION has stackup_depth = 0.5 mm but the
laminate's total stackup thickness is 0.4 mm. The drilled microvia is
deeper than the board itself; the drill exits through the back of the
board.

Reproducer recipe: LAMINATE_TABLE summing to 0.4 mm; a
VIA_DEFINITION(..,LENGTH_MEASURE(0.5),..).

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
    catalog_id="M152",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a VIA_DEFINITION declares drill depth 0.5 mm but the LAMINATE_TABLE "
        "sums to only 0.4 mm total board thickness; "
        "input: AP210 STEP file containing a LAMINATE_TABLE 'pcb_stackup' whose plies total "
        "0.4 mm: two 0.015 mm copper layers, two 0.015 mm prepreg sheets, and one 0.355 mm "
        "core, summing to 0.015+0.015+0.015+0.015+0.355 = 0.415 mm rounded to 0.4 mm; "
        "a VIA_DEFINITION 'microvia_1' declares its drill depth as LENGTH_MEASURE(0.5), "
        "meaning the drill must travel 0.5 mm to complete the via; "
        "the board is only 0.4 mm thick, so the drill exits 0.1 mm through the back copper; "
        "fabrication is impossible — the drill tool destroys the reference plane on exit; "
        "per ISO 10303-210 §6 via_definition depth bounds must be validated against the "
        "laminate stackup thickness; "
        "kernel must validate via depth <= stackup thickness and reject or warn; "
        "synonyms: AP210 via depth violation, PCB drill through, via depth exceeds substrate, "
        "microvia exits back of board, drill_depth > stackup thickness, "
        "AP210 via deeper than board, microvia drill exits back side, ECAD via depth out of range"
    ),
    schema="AP242",
)


def _render_m152() -> str:
    """Render AP210 file with VIA_DEFINITION depth 0.5mm exceeding 0.4mm stackup.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      LAMINATE_OR_PLY_DEFINITION 'copper_top'    — 0.015 mm
      #101      LAMINATE_OR_PLY_DEFINITION 'prepreg_top'   — 0.015 mm
      #102      LAMINATE_OR_PLY_DEFINITION 'core'          — 0.355 mm
      #103      LAMINATE_OR_PLY_DEFINITION 'prepreg_bot'   — 0.015 mm
      #104      LAMINATE_OR_PLY_DEFINITION 'copper_bot'    — 0.015 mm
      #110      LAMINATE_TABLE 'pcb_stackup' total = 0.415 mm (~0.4 mm)
      #120      VIA_DEFINITION 'microvia_1' with drill depth LENGTH_MEASURE(0.5) — DEFECT
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M152: AP210 microvia depth exceeds substrate thickness */")
    lines.append("/* DEFECT: VIA_DEFINITION drill depth 0.5mm > LAMINATE_TABLE total 0.4mm */")
    lines.append("/* The drill exits 0.1mm through the back copper — physically impossible */")
    lines.append("/* Per ISO 10303-210 §6 via depth must not exceed stackup thickness */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* Byte assertion: contains(b'LAMINATE_TABLE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M152: AP210 microvia drill depth exceeds board thickness'),'2;1');")
    lines.append("FILE_NAME('M152.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Stackup layers: total = 0.015+0.015+0.355+0.015+0.015 = 0.415 mm */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('copper_top',LENGTH_MEASURE(0.015),$);")
    lines.append("#101=LAMINATE_OR_PLY_DEFINITION('prepreg_top',LENGTH_MEASURE(0.015),$);")
    lines.append("#102=LAMINATE_OR_PLY_DEFINITION('core',LENGTH_MEASURE(0.355),$);")
    lines.append("#103=LAMINATE_OR_PLY_DEFINITION('prepreg_bot',LENGTH_MEASURE(0.015),$);")
    lines.append("#104=LAMINATE_OR_PLY_DEFINITION('copper_bot',LENGTH_MEASURE(0.015),$);")
    lines.append("/* Byte assertion: contains(b'LAMINATE_TABLE') */")
    lines.append("/* LAMINATE_TABLE: ordered layer stack, total thickness ~0.4mm */")
    lines.append("#110=LAMINATE_TABLE('pcb_stackup',(#100,#101,#102,#103,#104));")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* DEFECT: microvia drill depth 0.5mm > board thickness 0.415mm */")
    lines.append("/* The drill exits through the back copper — fabrication is impossible */")
    lines.append("#120=VIA_DEFINITION('microvia_1',LENGTH_MEASURE(0.5),LENGTH_MEASURE(0.2),#100,#104);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-microvia-depth-exceeds-substrate-thickness',")
    lines.append("  (#100,#101,#102,#103,#104,#110,#120));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M152','M152','M152',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m152(path) -> None:
    Path(path).write_text(_render_m152())


f.render = _render_m152  # type: ignore[method-assign]
f.write = _write_m152    # type: ignore[method-assign]
