"""M076 — AP238 cutting-tool feedrate stated in wrong dimensional unit.

Catalog claim: A MACHINING_TOOL_FEEDSPEED's feedrate is given as a
MEASURE_WITH_UNIT whose unit's DIMENSIONAL_EXPONENTS are (1, 0, -2, ..)
(length/time^2 — acceleration) instead of (1, 0, -1, ..) (length/time —
velocity). A consumer mapping the value to the machine's feed register
either silently scales by an unintended factor or rejects.

Reproducer recipe: DERIVED_UNIT composed of LENGTH^1 and SECOND^-2,
used as the unit on a MEASURE_WITH_UNIT(LENGTH_MEASURE(500.0), ..) for
feed.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'CUTTING_TOOL')
  contains(b'MACHINING_TOOL_FEEDSPEED')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M076",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where MACHINING_TOOL_FEEDSPEED "
        "feedrate unit has DIMENSIONAL_EXPONENTS (1,0,-2,...) — acceleration (length/time^2) "
        "instead of velocity (length/time, exponents (1,0,-1,...)); "
        "input: AP238 STEP-NC file where CUTTING_TOOL references a "
        "MACHINING_TOOL_FEEDSPEED('feed500_per_s2') whose feedrate is "
        "MEASURE_WITH_UNIT(LENGTH_MEASURE(500.0), derived_unit) and the "
        "derived_unit is composed of LENGTH_UNIT^1 and TIME_UNIT^-2 — "
        "DIMENSIONAL_EXPONENTS(1.0,0.0,-2.0,0.0,0.0,0.0,0.0); "
        "a feedrate is a velocity (length per time): correct exponents are (1,0,-1,...); "
        "with acceleration units the value 500 mm/s^2 would be mapped to a wildly wrong "
        "machine feed rate instead of 500 mm/s; "
        "kernel must validate dimensional_exponents against the expected dimension class "
        "for the property and reject as malformed or warn and refuse to scale; "
        "synonyms: feedrate dimensional exponent wrong, wrong physical unit on toolpath, "
        "AP238 feedrate is acceleration unit, feedrate units mismatch length/time"
    ),
    schema="AP242",
)


def _render_m076() -> str:
    """Render AP238 STEP-NC file with feedrate using acceleration unit instead of velocity.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20-#27   DERIVED_UNIT with acceleration dimensional exponents — the defect
      #30       MEASURE_WITH_UNIT for feedrate using wrong unit
      #40       GEOMETRIC_CURVE_SET model entity
      #50       CUTTING_TOOL
      #51       MACHINING_TOOL_FEEDSPEED referencing the bad unit measure
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M076: AP238 cutting-tool feedrate stated in wrong dimensional unit */")
    lines.append("/* DEFECT: DERIVED_UNIT has DIMENSIONAL_EXPONENTS (1,0,-2,...) = acceleration */")
    lines.append("/* Feedrate must be velocity: DIMENSIONAL_EXPONENTS (1,0,-1,...) */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'CUTTING_TOOL') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_TOOL_FEEDSPEED') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M076: AP238 feedrate stated in wrong dimensional unit'),'2;1');")
    lines.append("FILE_NAME('M076.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 3 1 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('numerical_control_machining');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'numerical_control_machining',2007,#1);")
    lines.append("/* Standard unit context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)TIME_UNIT()SI_UNIT($,.SECOND.));")
    lines.append("#12=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#13=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#15=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#16=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#15))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12,#13))")
    lines.append("  REPRESENTATION_CONTEXT('ctx','3D'));")
    lines.append("/* DEFECT: DIMENSIONAL_EXPONENTS for acceleration (1,0,-2,...) */")
    lines.append("/* Correct velocity exponents would be (1,0,-1,...) */")
    lines.append("#20=DIMENSIONAL_EXPONENTS(1.0,0.0,-2.0,0.0,0.0,0.0,0.0);")
    lines.append("/* DERIVED_UNIT_ELEMENTs: LENGTH^1 and TIME^-2 — acceleration, not velocity */")
    lines.append("#21=DERIVED_UNIT_ELEMENT(#10,1.0);")
    lines.append("#22=DERIVED_UNIT_ELEMENT(#11,-2.0);")
    lines.append("/* DERIVED_UNIT composed of length/time^2 — the wrong unit class */")
    lines.append("#23=DERIVED_UNIT((#21,#22));")
    lines.append("/* Feedrate value 500.0 in acceleration unit (mm/s^2) instead of mm/s */")
    lines.append("#30=MEASURE_WITH_UNIT(LENGTH_MEASURE(500.0),#23);")
    lines.append("/* Byte assertion: contains(b'CUTTING_TOOL') */")
    lines.append("#50=CUTTING_TOOL('endmill_6mm',$,$,$);")
    lines.append("/* Byte assertion: contains(b'MACHINING_TOOL_FEEDSPEED') */")
    lines.append("/* MACHINING_TOOL_FEEDSPEED referencing the wrong-unit measure */")
    lines.append("#51=MACHINING_TOOL_FEEDSPEED('feed500_per_s2',#30,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#60=GEOMETRIC_CURVE_SET('ap238-feedrate-wrong-dimensional-unit-acceleration',")
    lines.append("  (#50,#51,#30));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M076','M076','M076',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#60),#16);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m076(path) -> None:
    Path(path).write_text(_render_m076())


f.render = _render_m076  # type: ignore[method-assign]
f.write = _write_m076    # type: ignore[method-assign]
