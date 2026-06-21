"""M159 — AP210 connector keying / polarization missing

Catalog claim: A connector PRODUCT (e.g. a 4-pin power harness) has
no polarization or keying property and no
DESCRIPTIVE_REPRESENTATION_ITEM indicating shell orientation. The
component can be inserted rotated 180 deg, swapping VCC and GND.

Reproducer recipe: PRODUCT('PWR_HDR_4',..) with four TERMINALs
(VCC / SIG / SIG2 / GND) and no keying / polarization PROPERTY.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'PWR_HDR_4')
  count_entity_def(b'TERMINAL') >= 4

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M159",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where PRODUCT 'PWR_HDR_4' (4-pin power harness connector) has four TERMINALs "
        "VCC / SIG / SIG2 / GND but no polarization or keying property; "
        "input: AP210 STEP file containing a PRODUCT 'PWR_HDR_4' 4-pin power harness connector "
        "with TERMINAL 'T1_VCC' at pin-1 (3.3V supply), TERMINAL 'T2_SIG' (signal), "
        "TERMINAL 'T3_SIG2' (signal), TERMINAL 'T4_GND' (ground return); "
        "the connector has no polarization PROPERTY_DEFINITION and no "
        "DESCRIPTIVE_REPRESENTATION_ITEM indicating shell keying or orientation; "
        "a mating connector can be inserted at 180 degrees, mapping T1_VCC to T4_GND pin "
        "and T4_GND to T1_VCC — shorting the power rail to ground; "
        "per ISO 10303-210 §6 connectors with asymmetric pin assignments should carry "
        "a polarization or keying attribute; "
        "the ECAD exporter copied the connector PRODUCT from the library "
        "without including the polarization property; "
        "kernel must detect connectors lacking polarization attributes and warn or reject; "
        "synonyms: AP210 connector no key, PCB header reversible, "
        "ECAD connector polarization missing, AP210 connector reversible, "
        "PCB harness unkeyed, ECAD safety-attribute missing"
    ),
    schema="AP242",
)


def _render_m159() -> str:
    """Render AP210 file with PWR_HDR_4 connector missing polarization property.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       PRODUCT 'PWR_HDR_4' — 4-pin power harness connector
      #60       CARTESIAN_POINT for T1_VCC at (0.0, 0.0, 0.0)
      #61       TERMINAL 'T1_VCC' — pin 1, 3.3V supply
      #62       CARTESIAN_POINT for T2_SIG at (2.54, 0.0, 0.0)
      #63       TERMINAL 'T2_SIG' — pin 2, signal
      #64       CARTESIAN_POINT for T3_SIG2 at (5.08, 0.0, 0.0)
      #65       TERMINAL 'T3_SIG2' — pin 3, signal
      #66       CARTESIAN_POINT for T4_GND at (7.62, 0.0, 0.0)
      #67       TERMINAL 'T4_GND' — pin 4, ground return
      #200      GEOMETRIC_CURVE_SET model entity
      NOTE: no polarization PROPERTY_DEFINITION — that is the defect
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M159: AP210 connector keying / polarization missing */")
    lines.append("/* DEFECT: PRODUCT 'PWR_HDR_4' has VCC/SIG/SIG2/GND TERMINALs but no polarization property */")
    lines.append("/* Connector can be inserted 180deg reversed, swapping VCC and GND — power short risk */")
    lines.append("/* ECAD exporter omitted polarization/keying attribute from connector PRODUCT */")
    lines.append("/* Per ISO 10303-210 §6 asymmetric connectors require polarization attribute */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'PWR_HDR_4') */")
    lines.append("/* Byte assertion: count_entity_def(b'TERMINAL') >= 4 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M159: AP210 PWR_HDR_4 connector missing polarization keying'),'2;1');")
    lines.append("FILE_NAME('M159.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Byte assertion: contains(b'PWR_HDR_4') */")
    lines.append("/* PRODUCT 'PWR_HDR_4': 4-pin power harness connector, 2.54mm pitch */")
    lines.append("#50=PRODUCT('PWR_HDR_4','PWR_HDR_4','4-pin power harness connector',(#1));")
    lines.append("/* Byte assertion: count_entity_def(b'TERMINAL') >= 4 */")
    lines.append("/* Four TERMINALs at 2.54mm pitch: VCC / SIG / SIG2 / GND */")
    lines.append("/* Pin 1 at origin — 3.3V supply */")
    lines.append("#60=CARTESIAN_POINT('T1_VCC_loc',(0.0,0.0,0.0));")
    lines.append("#61=TERMINAL('T1_VCC',#60);")
    lines.append("/* Pin 2 — signal */")
    lines.append("#62=CARTESIAN_POINT('T2_SIG_loc',(2.54,0.0,0.0));")
    lines.append("#63=TERMINAL('T2_SIG',#62);")
    lines.append("/* Pin 3 — signal */")
    lines.append("#64=CARTESIAN_POINT('T3_SIG2_loc',(5.08,0.0,0.0));")
    lines.append("#65=TERMINAL('T3_SIG2',#64);")
    lines.append("/* Pin 4 — ground return */")
    lines.append("#66=CARTESIAN_POINT('T4_GND_loc',(7.62,0.0,0.0));")
    lines.append("#67=TERMINAL('T4_GND',#66);")
    lines.append("/* NOTE: no PROPERTY_DEFINITION for 'polarization' or 'keying' — that is the defect */")
    lines.append("/* Without polarization, reversed insertion maps T1_VCC onto T4_GND: power short *)");
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-connector-keying-polarization-missing-pwr-hdr-4',")
    lines.append("  (#50,#60,#61,#62,#63,#64,#65,#66,#67));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M159','M159','M159',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m159(path) -> None:
    Path(path).write_text(_render_m159())


f.render = _render_m159  # type: ignore[method-assign]
f.write = _write_m159    # type: ignore[method-assign]
