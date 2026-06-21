"""M098 — AP238 tool feedrate exceeds manufacturer rated maximum.

Catalog claim: A MACHINING_TOOL_FEEDSPEED declares a feed-rate of 50000.0
mm/min for a 6mm carbide end-mill whose rated maximum is roughly 3000 mm/min.

Reproducer recipe: MACHINING_TOOL_FEEDSPEED($, MEASURE_WITH_UNIT(
POSITIVE_RATIO_MEASURE(50000.0), mm_per_min_unit), $) on a 6mm end-mill.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MACHINING_TOOL_FEEDSPEED')
  contains(b'50000.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M098",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 MACHINING_TOOL_FEEDSPEED declaring an "
        "unrealistically high feedrate of 50000.0 mm/min for a 6mm carbide end-mill; "
        "input: AP238 STEP-NC file where MACHINING_TOOL_FEEDSPEED declares feedrate via "
        "MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(50000.0), mm_per_min_unit) — "
        "50000.0 mm/min is approximately 16.7x the realistic maximum for a 6mm carbide "
        "end-mill in steel (typical maximum ~3000 mm/min); "
        "per ISO 10303-238 §5.8 machining_tool_feedspeed values must be within reasonable "
        "bounds for the tool family and material; "
        "this defect arises when a CAM post-processor copies feedrate parameters from a "
        "different tool family (e.g. a large router bit rated for high-speed foam cutting) "
        "without checking applicability to the current tool; "
        "a CNC controller that clips at machine maximum silently changes the program; "
        "a controller that attempts the rate breaks the tool and may damage the machine; "
        "kernel must range-check feedrate against tool family expected envelope; "
        "warn loudly on out-of-envelope values, reject if catastrophic; "
        "synonyms: feedrate too high, STEP-NC unrealistic feedspeed, tool will break, "
        "AP238 feedrate insanely high, STEP-NC tool runs too fast, feedspeed exceeds tool limit"
    ),
    schema="AP242",
)


def _render_m098() -> str:
    """Render AP238 file with MACHINING_TOOL_FEEDSPEED set to 50000.0 mm/min.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       SI_UNIT for mm/min feed rate (LENGTH / TIME derived)
      #21       POSITIVE_RATIO_MEASURE(50000.0) feed value
      #22       MEASURE_WITH_UNIT wrapping #21 with mm_per_min unit
      #23       MACHINING_TOOL_FEEDSPEED — DEFECT: 50000.0 mm/min
      #50       MACHINED_FEATURE 'slot_c'
      #60       MACHINING_TOOL('endmill_6mm') — 6mm carbide end-mill
      #70       MACHINING_OPERATION referencing #23 as its feedspeed
      #80       MACHINING_WORKINGSTEP wrapping the operation
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M098: AP238 tool feedrate exceeds manufacturer rated maximum */")
    lines.append("/* DEFECT: MACHINING_TOOL_FEEDSPEED = 50000.0 mm/min on 6mm carbide end-mill */")
    lines.append("/* Realistic maximum for 6mm end-mill in steel is ~3000 mm/min */")
    lines.append("/* Arises from copying feedrate from a different (larger/faster) tool family */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_TOOL_FEEDSPEED') */")
    lines.append("/* Byte assertion: contains(b'50000.0') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M098: AP238 MACHINING_TOOL_FEEDSPEED exceeds rated maximum'),'2;1');")
    lines.append("FILE_NAME('M098.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Feed rate unit: mm per minute — derived from mm and seconds */")
    lines.append("#20=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("/* Byte assertion: contains(b'MACHINING_TOOL_FEEDSPEED') */")
    lines.append("/* Byte assertion: contains(b'50000.0') */")
    lines.append("/* DEFECT: POSITIVE_RATIO_MEASURE(50000.0) mm/min — 16.7x the 6mm end-mill maximum */")
    lines.append("/* A feedspeed of 50000 mm/min will break the tool or clip at machine maximum */")
    lines.append("#21=MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(50000.0),#20);")
    lines.append("/* MACHINING_TOOL_FEEDSPEED with the absurdly high feed value */")
    lines.append("#23=MACHINING_TOOL_FEEDSPEED($,#21,$);")
    lines.append("/* Target machined feature */")
    lines.append("#50=MACHINED_FEATURE('slot_c',$,$,$,$,$);")
    lines.append("/* The 6mm carbide end-mill that will break at 50000 mm/min */")
    lines.append("#60=MACHINING_TOOL('endmill_6mm',$,$,$);")
    lines.append("/* MACHINING_OPERATION carries the over-limit feedspeed #23 */")
    lines.append("#70=MACHINING_OPERATION('cut_slot_c',#60,#23,$,$,$,$,$,#50,$,$);")
    lines.append("#80=MACHINING_WORKINGSTEP('slot_c_step',#50,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-tool-feedrate-exceeds-manufacturer-rated-maximum',")
    lines.append("  (#21,#23,#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M098','M098','M098',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m098(path) -> None:
    Path(path).write_text(_render_m098())


f.render = _render_m098  # type: ignore[method-assign]
f.write = _write_m098    # type: ignore[method-assign]
