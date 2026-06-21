"""M106 — AP238 workplan total execution time exceeds shift length.

Catalog claim: The summed EXECUTION_TIME of the operations in a WORKPLAN
exceeds 28800 seconds (8-hour shift); e.g., a single workplan declaring
50 hours of continuous machining. While not formally a STEP error, it
indicates a unit-confusion or feedrate-stuck-at-zero condition upstream
worth flagging.

Reproducer recipe: A MACHINING_OPERATION with EXECUTION_TIME of
180000.0 seconds (50 hours) attached.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TIME_MEASURE')
  contains(b'180000.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M106",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 WORKPLAN whose single MACHINING_OPERATION "
        "carries an EXECUTION_TIME of 180000.0 seconds (50 hours), far exceeding the "
        "28800-second (8-hour) shift length; "
        "input: AP238 STEP-NC file where a MACHINING_OPERATION attribute "
        "'op_long_cut' has an associated TIME_MEASURE of 180000.0 seconds; "
        "per ISO 10303-238 §5.6 cycle-time / shift-length practicality, individual "
        "operation execution times that exceed a shift length indicate upstream error: "
        "feedrate stuck at near-zero, units declared as mm/min but value interpreted as "
        "mm/rev (slow travel over long path), or copy-paste error multiplying time by 1000; "
        "STEP-NC consumers using EXECUTION_TIME for scheduling receive absurd cycle estimates "
        "and may attempt to schedule across multiple shifts incorrectly; "
        "kernel must warn and accept: emit a warning diagnostic when any individual operation "
        "exceeds shift length, treating this as a signal of upstream feedrate or unit error, "
        "and continue; "
        "synonyms: STEP-NC cycle time too long, AP238 unrealistic execution time, "
        "workplan exceeds shift length, machining time impossibly long, "
        "feedrate units wrong (cycle time 50h), AP238 cycle time absurdly long"
    ),
    schema="AP242",
)


def _render_m106() -> str:
    """Render AP238 file with MACHINING_OPERATION having 180000.0 s execution time.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm + seconds)
      #20       LENGTH_UNIT for mm
      #21       TIME_UNIT for seconds
      #50       MACHINED_FEATURE 'pocket_a'
      #60       MACHINING_TOOL 'endmill_12mm'
      #61       MEASURE_WITH_UNIT holding 180000.0 TIME_MEASURE — the defect
      #70       MACHINING_OPERATION 'op_long_cut' — references #61 execution time
      #80       MACHINING_WORKINGSTEP 'step_a'
      #90       WORKPLAN 'main' — total time 180000.0 s (50 h) >> 28800 s (8 h)
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M106: AP238 workplan total execution time exceeds shift length */")
    lines.append("/* DEFECT: single MACHINING_OPERATION declares 180000.0 s (50 h) execution time */")
    lines.append("/* 180000 s >> 28800 s (8-hour shift) — indicates feedrate or unit confusion */")
    lines.append("/* Violates ISO 10303-238 §5.6 cycle-time / shift-length practicality */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TIME_MEASURE') */")
    lines.append("/* Byte assertion: contains(b'180000.0') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M106: AP238 workplan execution time exceeds shift length'),'2;1');")
    lines.append("FILE_NAME('M106.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Time unit — seconds — for execution time measurement */")
    lines.append("#20=(NAMED_UNIT(*)SI_UNIT($,.SECOND.)TIME_UNIT());")
    lines.append("/* Byte assertion: contains(b'TIME_MEASURE') */")
    lines.append("/* Byte assertion: contains(b'180000.0') */")
    lines.append("/* DEFECT: 180000.0 seconds = 50 hours; shift length is 28800 s (8 h) */")
    lines.append("/* Feedrate stuck at near-zero or units mm/rev instead of mm/min cause this */")
    lines.append("#21=MEASURE_WITH_UNIT(TIME_MEASURE(180000.0),#20);")
    lines.append("/* Machined feature — a pocket requiring the absurdly long cut */")
    lines.append("#50=MACHINED_FEATURE('pocket_a',$,$,$,$,$);")
    lines.append("/* 12mm end mill used for the long pocket milling pass */")
    lines.append("#60=MACHINING_TOOL('endmill_12mm',$,$,$);")
    lines.append("/* DEFECT: MACHINING_OPERATION declares execution_time of 180000.0 s (50 h) */")
    lines.append("/* Correct shift length would cap at 28800 s; 180000 s signals feedrate error */")
    lines.append("#70=MACHINING_OPERATION('op_long_cut',#60,$,#21,$,$,$,$,#50,$,$);")
    lines.append("#80=MACHINING_WORKINGSTEP('step_a',#50,#70,$);")
    lines.append("/* WORKPLAN: single step; total scheduled time = 180000.0 s */")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-workplan-execution-time-exceeds-shift-length',")
    lines.append("  (#21,#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M106','M106','M106',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m106(path) -> None:
    Path(path).write_text(_render_m106())


f.render = _render_m106  # type: ignore[method-assign]
f.write = _write_m106    # type: ignore[method-assign]
