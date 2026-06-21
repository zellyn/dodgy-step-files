"""M095 — AP238 machining_operation declares negative execution time.

Catalog claim: A MACHINING_OPERATION's associated EXECUTION_TIME (a
TIME_MEASURE_WITH_UNIT) carries a negative numeric value, e.g. -12.5
seconds. STEP-NC consumers using execution time for cycle-time estimation
produce nonsensical totals.

Reproducer recipe: MEASURE_WITH_UNIT(TIME_MEASURE(-12.5), seconds_unit)
attached to a MACHINING_OPERATION as its execution time.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TIME_MEASURE')
  contains(b'MACHINING_OPERATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M095",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 MACHINING_OPERATION with negative execution time "
        "— TIME_MEASURE value is -12.5 seconds, violating ISO 10303-238 §5.6 non-negativity; "
        "input: AP238 STEP-NC file where MACHINING_OPERATION('mill_pocket') carries an "
        "EXECUTION_TIME attribute pointing to MEASURE_WITH_UNIT(TIME_MEASURE(-12.5), seconds_unit); "
        "the negative value arises from a timestamp-arithmetic bug in the CAM post-processor "
        "that computes end_time minus start_time with arguments swapped; "
        "per ISO 10303-238 §5.6 time_measure values must be non-negative; a negative duration "
        "is physically impossible and indicates a programming error in the publisher; "
        "STEP-NC consumers using execution time for cycle-time estimation accumulate negative "
        "totals, producing nonsensical results — a 4-hour program may report as 3h47m; "
        "some implementations roll the value modulo zero and report a one-pass cycle as multi-hour; "
        "kernel must reject negative time values or take absolute value and warn; "
        "synonyms: STEP-NC cycle time negative, AP238 operation duration wrong sign, "
        "negative time in NC file, negative duration, AP238 time goes backwards, "
        "machining operation negative time, execution_time below zero, STEP-NC negative duration"
    ),
    schema="AP242",
)


def _render_m095() -> str:
    """Render AP238 file with MACHINING_OPERATION having negative execution time.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       SI_UNIT for seconds (time)
      #21       TIME_MEASURE(-12.5) — the negative duration value
      #22       MEASURE_WITH_UNIT wrapping #21 with seconds unit #20
      #50       MACHINED_FEATURE 'pocket_b'
      #60       MACHINING_TOOL 'endmill_8mm'
      #70       MACHINING_OPERATION referencing #60 and #22 as execution time — DEFECT
      #80       MACHINING_WORKINGSTEP wrapping the operation
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M095: AP238 machining_operation declares negative execution time */")
    lines.append("/* DEFECT: EXECUTION_TIME = TIME_MEASURE(-12.5) seconds — negative duration */")
    lines.append("/* ISO 10303-238 §5.6 requires non-negative time_measure values */")
    lines.append("/* Arises from timestamp arithmetic bug: end_time - start_time with args swapped */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TIME_MEASURE') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_OPERATION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M095: AP238 MACHINING_OPERATION with negative execution time'),'2;1');")
    lines.append("FILE_NAME('M095.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Seconds unit for EXECUTION_TIME */")
    lines.append("#20=(NAMED_UNIT(*)SI_UNIT($,.SECOND.)TIME_UNIT());")
    lines.append("/* Byte assertion: contains(b'TIME_MEASURE') */")
    lines.append("/* DEFECT: TIME_MEASURE(-12.5) — negative duration violates §5.6 non-negativity */")
    lines.append("/* Correct value would be a positive number of seconds, e.g. TIME_MEASURE(45.0) */")
    lines.append("#21=TIME_MEASURE_WITH_UNIT(TIME_MEASURE(-12.5),#20);")
    lines.append("/* Target machined feature */")
    lines.append("#50=MACHINED_FEATURE('pocket_b',$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'MACHINING_OPERATION') */")
    lines.append("/* Machining tool for the operation */")
    lines.append("#60=MACHINING_TOOL('endmill_8mm',$,$,$);")
    lines.append("/* DEFECT: MACHINING_OPERATION references #21 (negative TIME_MEASURE) as execution time */")
    lines.append("/* The -12.5 s duration causes cycle-time totals to go negative in downstream tooling */")
    lines.append("#70=MACHINING_OPERATION('mill_pocket',#60,$,#21,$,$,$,$,#50,$,$);")
    lines.append("/* Workingstep and workplan */")
    lines.append("#80=MACHINING_WORKINGSTEP('pocket_step',#50,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-machining-operation-negative-execution-time',")
    lines.append("  (#21,#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M095','M095','M095',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m095(path) -> None:
    Path(path).write_text(_render_m095())


f.render = _render_m095  # type: ignore[method-assign]
f.write = _write_m095    # type: ignore[method-assign]
