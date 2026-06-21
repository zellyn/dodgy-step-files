"""M156 — AP210 power net carries only mechanical placement constraint

Catalog claim: A NETWORK named 'PWR_5V' is annotated with a mechanical
placement constraint (component-spacing rule) but no electrical-class
constraint (current capacity, impedance, voltage rating). A power-
distribution net needs an electrical attribute for current-carrying
capacity validation; the file is incomplete.

Reproducer recipe: NETWORK('PWR_5V',..) with
PROPERTY_DEFINITION('mechanical_placement_constraint',..,network)
and no electrical PROPERTY_DEFINITION.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b"NETWORK('PWR_5V'")
  contains(b'mechanical_placement_constraint')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M156",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where NETWORK 'PWR_5V' has only a mechanical placement constraint and no "
        "electrical constraint (current capacity, voltage rating, impedance); "
        "input: AP210 STEP file containing a NETWORK 'PWR_5V' (5V power rail) "
        "annotated with PROPERTY_DEFINITION 'mechanical_placement_constraint' declaring "
        "a component-spacing rule of 0.2 mm minimum clearance; "
        "the NETWORK has no electrical-class PROPERTY_DEFINITION: no current_capacity, "
        "no voltage_rating, no impedance_class property is present; "
        "per ISO 10303-210 §7 a power-distribution net requires an electrical attribute "
        "for current-carrying capacity validation; "
        "the ECAD exporter retained the mechanical placement rules but dropped all "
        "electrical-class constraints during export; "
        "kernel must detect power nets without electrical constraints and warn or reject; "
        "synonyms: AP210 power net incomplete, PCB net missing electrical, "
        "ECAD constraint coverage, AP210 power net no electrical constraint, "
        "PCB 5V net mechanical only, ECAD missing current rating"
    ),
    schema="AP242",
)


def _render_m156() -> str:
    """Render AP210 file with PWR_5V NETWORK having only mechanical constraint.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       TERMINAL 'VCC_PIN' — power entry terminal
      #51       CARTESIAN_POINT for VCC_PIN
      #60       NETWORK 'PWR_5V' — the 5V power net (DEFECT: no electrical constraint)
      #70       PROPERTY_DEFINITION 'mechanical_placement_constraint' on NETWORK #60
      #71       DESCRIPTIVE_REPRESENTATION_ITEM value '0.2mm_min_clearance'
      #72       REPRESENTATION holding the mechanical property
      #73       PROPERTY_DEFINITION_REPRESENTATION
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M156: AP210 power net carries only mechanical placement constraint */")
    lines.append("/* DEFECT: NETWORK 'PWR_5V' has mechanical_placement_constraint but no electrical constraint */")
    lines.append("/* Power rail needs current_capacity / voltage_rating for validation */")
    lines.append("/* ECAD exporter dropped electrical-class constraints during export */")
    lines.append("/* Per ISO 10303-210 §7 power-distribution net requires electrical attribute */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b\"NETWORK('PWR_5V'\") */")
    lines.append("/* Byte assertion: contains(b'mechanical_placement_constraint') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M156: AP210 PWR_5V net has only mechanical constraint, no electrical'),'2;1');")
    lines.append("FILE_NAME('M156.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* VCC entry terminal on the power connector */")
    lines.append("#51=CARTESIAN_POINT('VCC_PIN_loc',(2.0,2.0,0.0));")
    lines.append("#50=TERMINAL('VCC_PIN',#51);")
    lines.append("/* Byte assertion: contains(b\"NETWORK('PWR_5V'\") */")
    lines.append("/* DEFECT: NETWORK 'PWR_5V' — 5V power rail — will receive only a mechanical property */")
    lines.append("#60=NETWORK('PWR_5V',(#50));")
    lines.append("/* Byte assertion: contains(b'mechanical_placement_constraint') */")
    lines.append("/* PROPERTY_DEFINITION with only a mechanical placement constraint — missing electrical */")
    lines.append("#70=PROPERTY_DEFINITION('mechanical_placement_constraint',")
    lines.append("  'Component spacing rule for 5V rail',#60);")
    lines.append("#71=DESCRIPTIVE_REPRESENTATION_ITEM('mechanical_placement_constraint',")
    lines.append("  '0.2mm_min_clearance');")
    lines.append("#72=REPRESENTATION('mech_props',(#71),#14);")
    lines.append("#73=PROPERTY_DEFINITION_REPRESENTATION(#70,#72);")
    lines.append("/* NOTE: no current_capacity, voltage_rating, or impedance PROPERTY_DEFINITION */")
    lines.append("/* The absence of electrical constraint is the defect per ISO 10303-210 §7 */")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-power-net-no-electrical-constraint-pwr5v-mechanical-only',")
    lines.append("  (#50,#51,#60,#70,#71,#72,#73));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M156','M156','M156',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m156(path) -> None:
    Path(path).write_text(_render_m156())


f.render = _render_m156  # type: ignore[method-assign]
f.write = _write_m156    # type: ignore[method-assign]
