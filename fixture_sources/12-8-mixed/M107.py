"""M107 — AP238 cutting tool diameter declared as zero or negative.

Catalog claim: A milling tool's diameter MEASURE_WITH_UNIT carries the
numeric value 0.0 (or worse, a negative). The controller either rejects
the file or generates a toolpath with zero radial offset, producing
contour-on-contour passes with no material removal.

Reproducer recipe: MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.0),
mm_unit) attached as the diameter of a milling tool referenced by a
MACHINING_OPERATION.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'POSITIVE_LENGTH_MEASURE(0.0)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M107",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 milling tool whose diameter is declared "
        "as POSITIVE_LENGTH_MEASURE(0.0) — a zero-diameter cutting tool; "
        "input: AP238 STEP-NC file where a MILLING_CUTTER entity has its diameter "
        "attribute set to MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.0), mm_unit); "
        "per ISO 10303-238 §5.7 cutting_tool_dimension positivity rules, tool diameter "
        "must be strictly positive; zero diameter violates the POSITIVE_LENGTH_MEASURE "
        "constraint declared in the type name itself; "
        "a controller receiving this file either rejects the tool definition outright or "
        "generates toolpath offsets using zero radial compensation, producing "
        "contour-on-contour passes with no material removal — stock is left entirely "
        "un-cut and finished part dimensions are wrong; "
        "kernel must reject zero/negative tool diameters as malformed; "
        "or warn loudly that a POSITIVE_LENGTH_MEASURE of zero violates the attribute "
        "positivity constraint; "
        "synonyms: zero-diameter tool, AP238 tool dimension missing, "
        "milling tool diameter is zero or negative, STEP-NC bad tool size, "
        "cutting tool has no radial offset, AP238 tool zero diameter, "
        "STEP-NC milling tool size missing, zero diameter cutter"
    ),
    schema="AP242",
)


def _render_m107() -> str:
    """Render AP238 file with MILLING_CUTTER diameter set to POSITIVE_LENGTH_MEASURE(0.0).

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       LENGTH_UNIT for mm diameter measurement
      #21       MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.0), #20) — defect: zero diameter
      #50       MACHINED_FEATURE 'slot_a'
      #60       MILLING_CUTTER 'endmill_bad' with diameter #21 — DEFECT: zero diameter
      #70       MACHINING_OPERATION 'op_slot' using zero-diameter tool #60
      #80       MACHINING_WORKINGSTEP 'step_slot'
      #90       WORKPLAN 'main'
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M107: AP238 cutting tool diameter declared as zero or negative */")
    lines.append("/* DEFECT: POSITIVE_LENGTH_MEASURE(0.0) — zero diameter violates positivity */")
    lines.append("/* Controller rejects or generates contour-on-contour passes with no material removal */")
    lines.append("/* Violates ISO 10303-238 §5.7 cutting_tool_dimension positivity rules */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'POSITIVE_LENGTH_MEASURE(0.0)') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M107: AP238 cutting tool diameter declared as zero'),'2;1');")
    lines.append("FILE_NAME('M107.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('step_nc_mim');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'ap238_step_nc_mim',2007,#1);")
    lines.append("/* Standard unit context — mm */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('nc','3D'));")
    lines.append("/* Byte assertion: contains(b'POSITIVE_LENGTH_MEASURE(0.0)') */")
    lines.append("/* DEFECT: diameter = 0.0 mm — violates POSITIVE_LENGTH_MEASURE constraint */")
    lines.append("/* A milling cutter with zero diameter cannot remove any material */")
    lines.append("/* Typical cause: CAM system using uninitialised tool template default value */")
    lines.append("#21=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.0),#10);")
    lines.append("/* Machined feature — a slot requiring nonzero tool radius offset */")
    lines.append("#50=MACHINED_FEATURE('slot_a',$,$,$,$,$);")
    lines.append("/* DEFECT: MILLING_CUTTER with zero diameter — cannot produce radial offset */")
    lines.append("/* Tool template left at default 0.0; should be e.g. 12.0 mm for this slot op */")
    lines.append("#60=MILLING_CUTTER('endmill_bad',$,$,#21,$,$,$,$);")
    lines.append("/* MACHINING_OPERATION references zero-diameter tool #60 */")
    lines.append("#70=MACHINING_OPERATION('op_slot',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("#80=MACHINING_WORKINGSTEP('step_slot',#50,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-cutting-tool-diameter-zero-or-negative',")
    lines.append("  (#21,#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M107','M107','M107',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m107(path) -> None:
    Path(path).write_text(_render_m107())


f.render = _render_m107  # type: ignore[method-assign]
f.write = _write_m107    # type: ignore[method-assign]
