"""M139 — AP203 effectivity start date is AFTER its end date

Catalog claim: A TIME_INTERVAL_BASED_EFFECTIVITY declares effectivity_start
later than effectivity_end. The interval is empty, or — taken literally — runs
backward in time. No date is ever within the effectivity window, making the
configuration permanently unavailable.

Reproducer recipe: TIME_INTERVAL_BASED_EFFECTIVITY('rev','rev_A',
2025-06-01, 2024-12-31).

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'TIME_INTERVAL_BASED_EFFECTIVITY')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M139",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where a "
        "TIME_INTERVAL_BASED_EFFECTIVITY entity has its start date (2025-06-01) "
        "after its end date (2024-12-31), creating an empty or backward-running "
        "effectivity window that permanently disqualifies the configuration; "
        "input: AP203 STEP file with a TIME_INTERVAL_BASED_EFFECTIVITY whose "
        "effectivity_start_date is 2025-06-01 and effectivity_end_date is "
        "2024-12-31; per ISO 10303-203 §4 the EFFECTIVITY invariant requires "
        "start <= end; when start > end the interval is empty: no calendar date "
        "falls within the window, so the product configuration governed by this "
        "effectivity is permanently unavailable; a PDM configuration resolver "
        "that checks whether an effectivity covers a given date will always "
        "return false, silently making the bill-of-materials incomplete; "
        "the defect is typically produced by a PDM exporter that swapped the "
        "start and end date fields when the effectivity was authored in reverse "
        "chronological order; "
        "two corrective paths: (a) reject the file with an invariant-violation "
        "error, or (b) swap start and end with a warning and re-emit; "
        "kernel must detect reversed interval and reject or warn; "
        "synonyms: AP203 effectivity backwards, negative-duration effectivity, "
        "empty effectivity window, AP203 effectivity reversed, start after end, "
        "PDM effectivity window empty"
    ),
    schema="AP242",
)


def _render_m139() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with reversed TIME_INTERVAL_BASED_EFFECTIVITY.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20-#22    PRODUCT / PRODUCT_DEFINITION_FORMATION / PRODUCT_DEFINITION
      #30-#31    CALENDAR_DATEs for start (2025-06-01) and end (2024-12-31)
      #32        TIME_INTERVAL_BASED_EFFECTIVITY — DEFECT: start > end
      #33        PRODUCT_DEFINITION_EFFECTIVITY binding effectivity to pd
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M139: AP203 effectivity start date AFTER end date — reversed interval */")
    lines.append("/* DEFECT: TIME_INTERVAL_BASED_EFFECTIVITY start=2025-06-01 > end=2024-12-31 */")
    lines.append("/* The effectivity window is empty: no date falls within [2025-06-01, 2024-12-31] */")
    lines.append("/* Configuration governed by this effectivity is permanently unavailable */")
    lines.append("/* Per ISO 10303-203 §4 invariant: effectivity_start_date <= effectivity_end_date */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'TIME_INTERVAL_BASED_EFFECTIVITY') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M139: AP203 TIME_INTERVAL_BASED_EFFECTIVITY reversed start after end'),'2;1');")
    lines.append("FILE_NAME('M139.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("FILE_SCHEMA(('CONFIG_CONTROL_DESIGN { 1 0 10303 203 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('configuration controlled 3D designs of mechanical parts and assemblies');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'config_control_design',1994,#1);")
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
    lines.append("/* Product under effectivity control */")
    lines.append("#20=PRODUCT('PART-303','Fuel Injector','High-pressure fuel injection nozzle',(#1));")
    lines.append("#21=PRODUCT_DEFINITION_FORMATION('rev_A','Initial release rev A',#20);")
    lines.append("#22=PRODUCT_DEFINITION('design','',#21,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* CALENDAR_DATE for effectivity_start: 2025-06-01 (year=2025, month=6, day=1) */")
    lines.append("/* DEFECT contributor: this date is LATER than the end date below */")
    lines.append("#30=CALENDAR_DATE(2025,6,1);")
    lines.append("/* CALENDAR_DATE for effectivity_end: 2024-12-31 (year=2024, month=12, day=31) */")
    lines.append("/* This end date is EARLIER than start — the exporter swapped the two fields */")
    lines.append("#31=CALENDAR_DATE(2024,12,31);")
    lines.append("/* Byte assertion: contains(b'TIME_INTERVAL_BASED_EFFECTIVITY') */")
    lines.append("/* DEFECT: TIME_INTERVAL_BASED_EFFECTIVITY with reversed dates */")
    lines.append("/* start_date=#30 (2025-06-01) is AFTER end_date=#31 (2024-12-31) */")
    lines.append("/* ISO 10303-203 §4 invariant violated: start must be <= end */")
    lines.append("/* A PDM resolver checking if today falls within this window always returns false */")
    lines.append("#32=TIME_INTERVAL_BASED_EFFECTIVITY('eff-rev-A','rev_A effectivity window',#30,#31);")
    lines.append("/* PRODUCT_DEFINITION_EFFECTIVITY ties the reversed effectivity to the product definition */")
    lines.append("#33=PRODUCT_DEFINITION_EFFECTIVITY(#32,(#22));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-time-interval-effectivity-reversed-start-after-end',")
    lines.append("  (#20,#21,#22,#30,#31,#32,#33));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M139','M139','M139',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m139(path) -> None:
    Path(path).write_text(_render_m139())


f.render = _render_m139  # type: ignore[method-assign]
f.write = _write_m139    # type: ignore[method-assign]
