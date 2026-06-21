"""M158 — AP210 assembly footprint pitch conflicts with component-library footprint

Catalog claim: An assembly's local PRODUCT_DEFINITION declares an
SOIC-8 footprint with 1.27 mm pitch but the component library's
PRODUCT_DEFINITION for the same MPN declares 0.65 mm pitch (SSOP).
The assembly's pads will not align with the component pins.

Reproducer recipe: two PRODUCT_DEFINITIONs for the same MPN with
different declared pin pitch via DESCRIPTIVE_REPRESENTATION_ITEM.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'library_pin_pitch_mm')
  contains(b'assembly_pin_pitch_mm')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M158",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where assembly footprint pin pitch (1.27 mm SOIC-8) conflicts with "
        "library footprint pin pitch (0.65 mm SSOP) for the same MPN 'U2_MPN'; "
        "input: AP210 STEP file containing two PRODUCT_DEFINITION entities for MPN 'U2_MPN': "
        "PRODUCT 'U2_LIBRARY' is the component-library entry declaring library_pin_pitch_mm='0.65' "
        "via DESCRIPTIVE_REPRESENTATION_ITEM — this is an SSOP-8 package at 0.65 mm pitch; "
        "PRODUCT 'U2_ASSEMBLY' is the per-design assembly footprint declaring "
        "assembly_pin_pitch_mm='1.27' via DESCRIPTIVE_REPRESENTATION_ITEM — this is SOIC-8 pitch; "
        "a NEXT_ASSEMBLY_USAGE_OCCURRENCE 'U2_placement' links U2_ASSEMBLY to U2_LIBRARY; "
        "the SOIC-8 pads at 1.27 mm pitch will not align with SSOP pins at 0.65 mm pitch; "
        "the board will be unassemblable — components bridge neighboring pads or sit off-center; "
        "the ECAD exporter wrote a per-design footprint override from a different package; "
        "per ISO 10303-210 §6 assembly and library footprint pitch must agree; "
        "kernel must cross-check assembly vs library pitch and reject or warn on conflict; "
        "synonyms: AP210 footprint override conflict, PCB SOIC vs SSOP, "
        "ECAD pitch mismatch, AP210 pin pitch wrong, PCB SOIC pads don't match SSOP component"
    ),
    schema="AP242",
)


def _render_m158() -> str:
    """Render AP210 file with SOIC-8 assembly pitch conflicting with SSOP library pitch.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       PRODUCT 'U2_LIBRARY' — component library entry (SSOP-8, 0.65 mm pitch)
      #51       PROPERTY_DEFINITION 'library_pin_pitch_mm' on U2_LIBRARY
      #52       DESCRIPTIVE_REPRESENTATION_ITEM 'library_pin_pitch_mm' = '0.65'
      #53       REPRESENTATION for library pitch property
      #54       PROPERTY_DEFINITION_REPRESENTATION
      #60       PRODUCT 'U2_ASSEMBLY' — per-design footprint (SOIC-8, 1.27 mm pitch DEFECT)
      #61       PROPERTY_DEFINITION 'assembly_pin_pitch_mm' on U2_ASSEMBLY
      #62       DESCRIPTIVE_REPRESENTATION_ITEM 'assembly_pin_pitch_mm' = '1.27'
      #63       REPRESENTATION for assembly pitch property
      #64       PROPERTY_DEFINITION_REPRESENTATION
      #70       NEXT_ASSEMBLY_USAGE_OCCURRENCE 'U2_placement' linking them
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M158: AP210 assembly footprint pitch conflicts with component-library footprint */")
    lines.append("/* DEFECT: U2_ASSEMBLY declares SOIC-8 pitch 1.27mm; U2_LIBRARY is SSOP-8 pitch 0.65mm */")
    lines.append("/* The pads at 1.27mm pitch cannot align with SSOP component pins at 0.65mm pitch */")
    lines.append("/* ECAD exporter used a SOIC-8 template override for an SSOP-8 library component */")
    lines.append("/* Per ISO 10303-210 §6 assembly and library footprint pitch must agree */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'library_pin_pitch_mm') */")
    lines.append("/* Byte assertion: contains(b'assembly_pin_pitch_mm') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M158: AP210 SOIC-8 assembly pitch 1.27mm vs SSOP library pitch 0.65mm'),'2;1');")
    lines.append("FILE_NAME('M158.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* U2_LIBRARY: component library entry for MPN 'U2_MPN' — SSOP-8 at 0.65mm pitch */")
    lines.append("#50=PRODUCT('U2_LIBRARY','U2_MPN','SSOP-8 component library entry',(#1));")
    lines.append("/* Byte assertion: contains(b'library_pin_pitch_mm') */")
    lines.append("/* library declares 0.65mm pitch — SSOP-8 package standard */")
    lines.append("#51=PROPERTY_DEFINITION('library_pin_pitch_mm','Library footprint pin pitch',#50);")
    lines.append("#52=DESCRIPTIVE_REPRESENTATION_ITEM('library_pin_pitch_mm','0.65');")
    lines.append("#53=REPRESENTATION('lib_pitch',(#52),#14);")
    lines.append("#54=PROPERTY_DEFINITION_REPRESENTATION(#51,#53);")
    lines.append("/* U2_ASSEMBLY: per-design footprint for U2 placement — SOIC-8 at 1.27mm (DEFECT) */")
    lines.append("#60=PRODUCT('U2_ASSEMBLY','U2_MPN','SOIC-8 assembly footprint override',(#1));")
    lines.append("/* Byte assertion: contains(b'assembly_pin_pitch_mm') */")
    lines.append("/* DEFECT: assembly declares 1.27mm pitch — SOIC-8 pitch, wrong for SSOP-8 component */")
    lines.append("#61=PROPERTY_DEFINITION('assembly_pin_pitch_mm','Assembly footprint pin pitch',#60);")
    lines.append("#62=DESCRIPTIVE_REPRESENTATION_ITEM('assembly_pin_pitch_mm','1.27');")
    lines.append("#63=REPRESENTATION('asm_pitch',(#62),#14);")
    lines.append("#64=PROPERTY_DEFINITION_REPRESENTATION(#61,#63);")
    lines.append("/* U2_placement: NEXT_ASSEMBLY_USAGE_OCCURRENCE linking library to assembly footprint */")
    lines.append("#70=NEXT_ASSEMBLY_USAGE_OCCURRENCE('U2_placement','U2','U2 SSOP vs SOIC placement',#60,#50,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-assembly-pitch-conflicts-library-soic8-vs-ssop8',")
    lines.append("  (#50,#51,#52,#53,#54,#60,#61,#62,#63,#64,#70));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M158','M158','M158',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m158(path) -> None:
    Path(path).write_text(_render_m158())


f.render = _render_m158  # type: ignore[method-assign]
f.write = _write_m158    # type: ignore[method-assign]
