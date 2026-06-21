"""M185 — AP238 machining_tool_feedspeed product exceeds tool envelope

Catalog claim: A MACHINING_TOOL_FEEDSPEED declares spindle 12000 rpm
and feed-per-tooth 0.10 mm with a 4-flute end-mill, giving an effective
feed of 12000 x 4 x 0.10 = 4800 mm/min. Tool manufacturer's rated
chip-load for a 6 mm carbide cutter at this RPM is closer to 0.04 mm
per tooth; the tool will fracture.

Reproducer recipe: MACHINING_TOOL_FEEDSPEED with spindle_speed 12000 rpm,
feed_per_tooth 0.10 mm, on a 4-flute carbide end-mill rated for
0.04 mm/tooth at that RPM.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MACHINING_TOOL_FEEDSPEED')
  contains(b'12000.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M185",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where MACHINING_TOOL_FEEDSPEED "
        "declares feedspeed product exceeding tool manufacturer envelope; "
        "input: AP238 STEP-NC file containing a WORKPLAN with a milling operation; "
        "the END_MILL_TOOL 'carbide_endmill_6mm' is a 4-flute carbide end-mill, 6 mm diameter; "
        "tool manufacturer rated chip-load at 12000 rpm is 0.04 mm per tooth maximum; "
        "the MACHINING_TOOL_FEEDSPEED 'aggressive_feedspeed' declares "
        "spindle_speed 12000.0 rpm via MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(12000.0), rpm); "
        "feed_per_tooth 0.10 mm via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.10), mm); "
        "effective feed = 12000 rpm x 4 flutes x 0.10 mm/tooth = 4800 mm/min; "
        "chip-load 0.10 mm/tooth is 2.5x the rated maximum 0.04 mm/tooth at this RPM; "
        "the carbide end-mill will fracture under this aggressive chip-load; "
        "per ISO 10303-238 §5.8 machining_tool_feedspeed manufacturer-envelope cross-check: "
        "feedspeed product must not exceed tool-family rated envelope; "
        "kernel must validate feedspeed product against tool-family envelope; "
        "synonyms: AP238 chipload too aggressive, STEP-NC feed-per-tooth above max, "
        "tool will fracture from rpm x ipt, AP238 feedrate x rpm too high, "
        "STEP-NC chipload exceeds tool max, feed-per-tooth x spindle exceeds envelope, "
        "AP238 aggressive chipload, STEP-NC feed-per-tooth x rpm too high, "
        "feedspeed exceeds tool envelope, milling tool overspeed"
    ),
    schema="AP242",
)


def _render_m185() -> str:
    """Render AP238 STEP-NC file with MACHINING_TOOL_FEEDSPEED exceeding tool envelope.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #16       rpm unit reference (CONVERSION_BASED_UNIT via CONTEXT_DEPENDENT_UNIT)
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       END_MILL_TOOL 'carbide_endmill_6mm' — 4-flute, 6 mm diameter
      #31       MEASURE_WITH_UNIT for tool diameter = 6.0 mm
      #40       MACHINING_TOOL_FEEDSPEED 'aggressive_feedspeed' — DEFECT: 12000 rpm x 0.10mm/tooth
      #41       MEASURE_WITH_UNIT for spindle_speed = 12000.0 rpm — 12000 rpm
      #42       MEASURE_WITH_UNIT for feed_per_tooth = 0.10 mm — DEFECT: 2.5x rated max
      #50       WORKPLAN 'overspeed_endmill_program'
      #51       MACHINING_WORKINGSTEP 'mill_step'
      #52       MILLING_OPERATION 'mill_op' — uses aggressive_feedspeed
      #60       WORKPIECE 'mill_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M185: AP238 machining_tool_feedspeed product exceeds tool envelope */")
    lines.append("/* DEFECT: spindle 12000 rpm x 4 flutes x 0.10 mm/tooth = 4800 mm/min feed */")
    lines.append("/* Rated chip-load at 12000 rpm for 6mm carbide: 0.04 mm/tooth maximum */")
    lines.append("/* Declared feed-per-tooth 0.10 mm is 2.5x the rated maximum 0.04 mm/tooth */")
    lines.append("/* The 6 mm carbide end-mill will fracture under this aggressive chip-load */")
    lines.append("/* Per ISO 10303-238 §5.8 feedspeed product must not exceed tool-family envelope */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_TOOL_FEEDSPEED') */")
    lines.append("/* Byte assertion: contains(b'12000.0') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M185: AP238 machining_tool_feedspeed 12000rpm x 0.10mm/tooth exceeds envelope'),'2;1');")
    lines.append("FILE_NAME('M185.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 3 1 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('ctx','3D'));")
    lines.append("/* mm length unit reference for MEASURE_WITH_UNIT */")
    lines.append("#15=SI_UNIT(.MILLI.,.METRE.);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-machining-tool-feedspeed-exceeds-tool-envelope',")
    lines.append("  (#30,#40,#52,#60));")
    lines.append("/* END_MILL_TOOL 'carbide_endmill_6mm': 4-flute carbide, 6 mm diameter */")
    lines.append("/* Manufacturer rated chip-load at 12000 rpm: 0.04 mm/tooth maximum */")
    lines.append("#31=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(6.0),#15);")
    lines.append("#30=END_MILL_TOOL('carbide_endmill_6mm',$,#31,$,4,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'MACHINING_TOOL_FEEDSPEED') */")
    lines.append("/* Byte assertion: contains(b'12000.0') */")
    lines.append("/* DEFECT: spindle_speed 12000.0 rpm — at rated chip-load limit */")
    lines.append("#41=MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(12000.0),#11);")
    lines.append("/* DEFECT: feed_per_tooth 0.10 mm — 2.5x rated maximum of 0.04 mm/tooth */")
    lines.append("#42=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.10),#15);")
    lines.append("/* DEFECT: MACHINING_TOOL_FEEDSPEED with 12000 rpm x 4-flute x 0.10 mm/tooth */")
    lines.append("/* Effective feed 4800 mm/min — tool will fracture from excessive chip-load */")
    lines.append("#40=MACHINING_TOOL_FEEDSPEED('aggressive_feedspeed',#41,#42,$,$);")
    lines.append("/* WORKPIECE 'mill_workpiece' */")
    lines.append("#60=WORKPIECE('mill_workpiece','Workpiece for overspeed feed test',$,$,$,$,$);")
    lines.append("/* MILLING_OPERATION references the carbide end-mill with aggressive feedspeed */")
    lines.append("#52=MILLING_OPERATION('mill_op',$,$,$,$,$,#30,$,$,$,#40,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP links milling op to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('mill_step','Overspeed milling workingstep',#52,#60,$);")
    lines.append("/* WORKPLAN: milling step with aggressive feedspeed exceeding tool envelope */")
    lines.append("#50=WORKPLAN('overspeed_endmill_program','Overspeed end-mill milling workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M185','M185','M185',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m185(path) -> None:
    Path(path).write_text(_render_m185())


f.render = _render_m185  # type: ignore[method-assign]
f.write = _write_m185    # type: ignore[method-assign]
