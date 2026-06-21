"""M151 — AP210 declared trace impedance contradicts stackup geometry

Catalog claim: An electrical PROPERTY_DEFINITION on a
CONDUCTOR_TRACK_PROFILE declares characteristic_impedance = 50 ohm,
but the actual stackup geometry (15 um copper, 0.2 mm dielectric, 4 mm
trace width with FR4 Er=4.4) yields ~ 22 ohm by standard microstrip
calculation. The declared impedance and the geometry-derived impedance
disagree by > 50 %.

Reproducer recipe: CONDUCTOR_TRACK_PROFILE with width 4.0 over a
0.2 mm LAMINATE_OR_PLY_DEFINITION; PROPERTY_DEFINITION declares
characteristic_impedance = 50 ohm.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'characteristic_impedance')
  contains(b'CONDUCTOR_TRACK_PROFILE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M151",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a PROPERTY_DEFINITION declares characteristic_impedance = 50 ohm on a "
        "CONDUCTOR_TRACK_PROFILE, but the stackup geometry yields ~22 ohm by microstrip formula; "
        "input: AP210 STEP file containing a CONDUCTOR_TRACK_PROFILE 'signal_trace' with "
        "width 4.0 mm above a LAMINATE_OR_PLY_DEFINITION 'dielectric_core' of thickness 0.2 mm "
        "and relative permittivity Er=4.4 (standard FR4); "
        "copper height is 15 um (0.015 mm, 1 oz copper); "
        "Hammerstad-Jensen microstrip formula gives Z0 = 22 ohm for these dimensions: "
        "W/H=20 >> 1 implies Z0 = (87/sqrt(Er+1.41))*ln(5.98*H/(0.8*W+T)) ~ 22 ohm; "
        "the PROPERTY_DEFINITION 'characteristic_impedance' is attached to the trace "
        "with DESCRIPTIVE_REPRESENTATION_ITEM value '50'; "
        "declared Z0 = 50 ohm disagrees with geometry-derived Z0 = 22 ohm by 127 %; "
        "a PCB fab house that cross-checks impedance will flag the stackup as inconsistent; "
        "per ISO 10303-210 §7 electrical properties must be consistent with stackup geometry; "
        "kernel must cross-check declared characteristic impedance against the stackup-derived "
        "value and warn or reject on significant disagreement; "
        "synonyms: AP210 impedance contradiction, PCB stackup yields wrong Z0, "
        "declared Z0 mismatches geometry, trace impedance disagrees with microstrip calc, "
        "AP210 50 ohm trace not 50 ohm, PCB impedance contradicts stackup, ECAD declared Z0 wrong"
    ),
    schema="AP242",
)


def _render_m151() -> str:
    """Render AP210 file with declared 50-ohm impedance contradicting 22-ohm stackup.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      LAMINATE_OR_PLY_DEFINITION 'dielectric_core' — 0.2mm FR4, Er=4.4
      #101      CONDUCTOR_TRACK_PROFILE 'signal_trace' — width 4.0mm
      #110      PROPERTY_DEFINITION 'characteristic_impedance' on trace
      #111      DESCRIPTIVE_REPRESENTATION_ITEM value '50'  <- DEFECT: should be ~22
      #112      REPRESENTATION holding the impedance item
      #113      PROPERTY_DEFINITION_REPRESENTATION
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M151: AP210 declared trace impedance contradicts stackup geometry */")
    lines.append("/* DEFECT: PROPERTY_DEFINITION declares characteristic_impedance=50 ohm */")
    lines.append("/* Stackup: 4mm trace / 0.2mm FR4 dielectric / Er=4.4 yields Z0~22 ohm */")
    lines.append("/* Declared 50 ohm vs geometry-derived 22 ohm — 127% disagreement */")
    lines.append("/* Per ISO 10303-210 §7 electrical properties must match stackup geometry */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'characteristic_impedance') */")
    lines.append("/* Byte assertion: contains(b'CONDUCTOR_TRACK_PROFILE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M151: AP210 50-ohm claim vs 22-ohm stackup geometry'),'2;1');")
    lines.append("FILE_NAME('M151.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Dielectric core: 0.2 mm thick FR4, relative permittivity 4.4 */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('dielectric_core',LENGTH_MEASURE(0.2),$);")
    lines.append("/* Byte assertion: contains(b'CONDUCTOR_TRACK_PROFILE') */")
    lines.append("/* Signal trace: 4.0 mm wide microstrip above dielectric_core */")
    lines.append("#101=CONDUCTOR_TRACK_PROFILE('signal_trace',LENGTH_MEASURE(4.0),$,#100);")
    lines.append("/* Byte assertion: contains(b'characteristic_impedance') */")
    lines.append("/* DEFECT: PROPERTY_DEFINITION declares Z0=50 ohm; geometry yields ~22 ohm */")
    lines.append("/* Hammerstad-Jensen: W/H=20, Er=4.4, T=0.015mm => Z0 ~ 22 ohm */")
    lines.append("#110=PROPERTY_DEFINITION('characteristic_impedance','Trace characteristic impedance',#101);")
    lines.append("#111=DESCRIPTIVE_REPRESENTATION_ITEM('characteristic_impedance','50');")
    lines.append("#112=REPRESENTATION('impedance_props',(#111),#14);")
    lines.append("#113=PROPERTY_DEFINITION_REPRESENTATION(#110,#112);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-declared-impedance-contradicts-stackup-geometry',")
    lines.append("  (#100,#101,#110,#111,#112,#113));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M151','M151','M151',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m151(path) -> None:
    Path(path).write_text(_render_m151())


f.render = _render_m151  # type: ignore[method-assign]
f.write = _write_m151    # type: ignore[method-assign]
