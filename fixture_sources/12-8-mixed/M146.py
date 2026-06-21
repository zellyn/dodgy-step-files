"""M146 — AP210 drill diameter exceeds pad diameter (annular ring inverted)

Catalog claim: A VIA_DEFINITION declares a drill_diameter (0.5 mm)
larger than the surrounding pad_diameter (0.3 mm). The drilled hole
is wider than the copper pad — there is no annular ring of copper
around the drill. The via cannot be electrically connected.

Reproducer recipe: VIA_DEFINITION('inverted_via', LENGTH_MEASURE(0.5),..)
with pad geometry of diameter 0.3 declared via PROPERTY_DEFINITION.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'VIA_DEFINITION')
  contains(b'pad_diameter')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M146",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a VIA_DEFINITION declares a drill diameter larger than the surrounding pad "
        "diameter, eliminating the annular copper ring required for electrical connection; "
        "input: AP210 STEP file containing a VIA_DEFINITION 'inverted_via' at position "
        "(10.0, 10.0, 0.0) with drill_diameter = LENGTH_MEASURE(0.5) mm; "
        "a PROPERTY_DEFINITION 'pad_diameter' attached to the same VIA_DEFINITION "
        "carries MEASURE_REPRESENTATION_ITEM value 0.3 mm — smaller than the drill; "
        "the drilled hole (0.5 mm) is wider than the copper pad (0.3 mm); "
        "there is no annular ring of copper around the drill; "
        "the via cannot form an electrical connection between layers; "
        "per ISO 10303-210 §6 via_definition drill_diameter must be strictly less than "
        "the pad_diameter to guarantee an annular copper ring; per IPC-2222 annular ring rules "
        "the minimum annular ring is (pad_diameter - drill_diameter) / 2 > 0; "
        "kernel must validate drill_diameter < pad_diameter and reject or warn; "
        "synonyms: AP210 annular ring inverted, PCB drill bigger than pad, "
        "PCB via no annular ring, ECAD via cuts through pad, annular ring negative, "
        "PCB pad cut through, AP210 drill > pad"
    ),
    schema="AP242",
)


def _render_m146() -> str:
    """Render AP210 file with VIA_DEFINITION drill_diameter > pad_diameter.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      CARTESIAN_POINT for via center at (10.0, 10.0, 0.0)
      #101      AXIS2_PLACEMENT_3D for via drill axis
      #110      VIA_DEFINITION 'inverted_via' — drill_diameter=0.5 mm  (DEFECT)
      #120      PROPERTY_DEFINITION 'pad_diameter' attached to via
      #121      MEASURE_REPRESENTATION_ITEM pad_diameter = 0.3 mm
      #122      REPRESENTATION holding pad_diameter item
      #123      PROPERTY_DEFINITION_REPRESENTATION
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M146: AP210 drill diameter exceeds pad diameter (annular ring inverted) */")
    lines.append("/* DEFECT: VIA_DEFINITION drill_diameter=0.5 mm > pad_diameter=0.3 mm */")
    lines.append("/* The drilled hole is wider than the copper pad — no annular ring exists */")
    lines.append("/* The via cannot be electrically connected; IPC-2222 annular ring rule violated */")
    lines.append("/* Per ISO 10303-210 §6 drill_diameter must be < pad_diameter */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* Byte assertion: contains(b'pad_diameter') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M146: AP210 drill diameter exceeds pad diameter'),'2;1');")
    lines.append("FILE_NAME('M146.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Via drill axis at board position (10.0, 10.0, 0.0) */")
    lines.append("#100=CARTESIAN_POINT('via_loc',(10.0,10.0,0.0));")
    lines.append("#101=AXIS2_PLACEMENT_3D('via_axis',#100,$,$);")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* DEFECT: drill_diameter=0.5 mm is larger than pad_diameter=0.3 mm */")
    lines.append("/* Annular ring = (0.3 - 0.5) / 2 = -0.1 mm — negative, no copper ring */")
    lines.append("#110=VIA_DEFINITION('inverted_via',$,#101,LENGTH_MEASURE(0.5));")
    lines.append("/* Byte assertion: contains(b'pad_diameter') */")
    lines.append("/* PROPERTY_DEFINITION declares pad_diameter = 0.3 mm for this via */")
    lines.append("#120=PROPERTY_DEFINITION('pad_diameter','Pad outer diameter for via_a',#110);")
    lines.append("#121=MEASURE_REPRESENTATION_ITEM('pad_diameter',LENGTH_MEASURE(0.3),#10);")
    lines.append("#122=REPRESENTATION('pad_dims',(#121),#14);")
    lines.append("#123=PROPERTY_DEFINITION_REPRESENTATION(#120,#122);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-drill-diameter-exceeds-pad-diameter-annular-ring-inverted',")
    lines.append("  (#100,#101,#110,#120,#121,#122,#123));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M146','M146','M146',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m146(path) -> None:
    Path(path).write_text(_render_m146())


f.render = _render_m146  # type: ignore[method-assign]
f.write = _write_m146    # type: ignore[method-assign]
