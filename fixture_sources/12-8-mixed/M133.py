"""M133 — AP203 inconsistent ISO 8601 date formats within the same file.

Catalog claim: One DATE_AND_TIME in the file captures a LOCAL_TIME with no
COORDINATED_UNIVERSAL_TIME_OFFSET (timezone-naive); another in the same file
uses an explicit UTC offset. Comparing the two requires assuming a timezone
for the naive value.

Reproducer recipe: DATE_AND_TIME(..,LOCAL_TIME(14,30,0.0,$)) and
DATE_AND_TIME(..,LOCAL_TIME(14,30,0.0,COORDINATED_UNIVERSAL_TIME_OFFSET(0,0,.AHEAD.)))
in the same file.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  count_entity_def(b'DATE_AND_TIME') >= 2
  contains(b'COORDINATED_UNIVERSAL_TIME_OFFSET')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M133",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where two "
        "DATE_AND_TIME instances use inconsistent timezone representations — one "
        "LOCAL_TIME is timezone-naive (offset=$) and another uses an explicit "
        "COORDINATED_UNIVERSAL_TIME_OFFSET — making temporal comparison ambiguous; "
        "input: AP203 STEP file containing two DATE_AND_TIME entities: the first "
        "records a creation date using LOCAL_TIME(14,30,0.0,$) where the $ null "
        "offset indicates no timezone is declared (timezone-naive); the second "
        "records a modification date using LOCAL_TIME(14,30,0.0,"
        "COORDINATED_UNIVERSAL_TIME_OFFSET(0,0,.AHEAD.)) with an explicit UTC+0 "
        "offset (timezone-aware); per ISO 10303-203 §5.7 and ISO 8601, comparing "
        "or ordering timestamps requires a common reference frame; the naive "
        "timestamp cannot be reliably converted to UTC without knowing the local "
        "timezone of the system that created it, so PDM tools that compare creation "
        "vs modification dates may get the ordering wrong; "
        "kernel must warn on mixed timezone-aware/timezone-naive timestamps within "
        "the same file, or reject if it cannot determine ordering; "
        "synonyms: AP203 timezone mismatch, STEP timestamp naive vs aware, "
        "AP203 date format inconsistent, naive vs aware timestamp, timezone-mixing, "
        "AP203 mixed date format, naive timestamp in PDM file, "
        "LOCAL_TIME null offset mixed with UTC offset"
    ),
    schema="AP242",
)


def _render_m133() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with mixed timezone-naive/aware DATE_AND_TIME.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        CALENDAR_DATE for creation (2024-03-15)
      #21        CALENDAR_DATE for modification (2024-07-22)
      #22        LOCAL_TIME(14,30,0.0,$) — TIMEZONE-NAIVE: DEFECT contributor
      #23        COORDINATED_UNIVERSAL_TIME_OFFSET(0,0,.AHEAD.) — UTC+0
      #24        LOCAL_TIME(09,15,0.0,#23) — timezone-aware
      #25        DATE_AND_TIME(#20,#22) — naive timestamp (creation)
      #26        DATE_AND_TIME(#21,#24) — aware timestamp (modification)
      #30-#32    PRODUCT / PRODUCT_DEFINITION_FORMATION / PRODUCT_DEFINITION
      #40        APPLIED_DATE_AND_TIME_ASSIGNMENT linking both timestamps
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M133: AP203 inconsistent ISO 8601 date formats — mixed naive/aware timestamps */")
    lines.append("/* DEFECT: one DATE_AND_TIME is timezone-naive (offset=$); another has explicit UTC offset */")
    lines.append("/* Comparing or ordering these timestamps requires assuming a timezone for the naive one */")
    lines.append("/* Per AP203 §5.7 consistent timezone handling is required for reliable PDM audit trails */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'DATE_AND_TIME') >= 2 */")
    lines.append("/* Byte assertion: contains(b'COORDINATED_UNIVERSAL_TIME_OFFSET') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M133: AP203 mixed timezone-naive and timezone-aware DATE_AND_TIME'),'2;1');")
    lines.append("FILE_NAME('M133.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Calendar dates for creation and modification events */")
    lines.append("#20=CALENDAR_DATE(2024,3,15);")
    lines.append("#21=CALENDAR_DATE(2024,7,22);")
    lines.append("/* Byte assertion: count_entity_def(b'DATE_AND_TIME') >= 2 */")
    lines.append("/* DEFECT: LOCAL_TIME with null offset — timezone-naive, cannot determine UTC equivalent */")
    lines.append("/* This was written by a legacy PDM system that did not record timezone information */")
    lines.append("#22=LOCAL_TIME(14,30,0.0,$);")
    lines.append("/* Byte assertion: contains(b'COORDINATED_UNIVERSAL_TIME_OFFSET') */")
    lines.append("/* UTC+0 offset used by the newer system for the modification timestamp */")
    lines.append("#23=COORDINATED_UNIVERSAL_TIME_OFFSET(0,0,.AHEAD.);")
    lines.append("/* Timezone-aware LOCAL_TIME with explicit UTC+0 offset */")
    lines.append("#24=LOCAL_TIME(9,15,0.0,#23);")
    lines.append("/* First DATE_AND_TIME: creation date 2024-03-15T14:30:00 — NAIVE (no tz) */")
    lines.append("/* DEFECT contributor: this timestamp cannot be compared with #26 without tz assumption */")
    lines.append("#25=DATE_AND_TIME(#20,#22);")
    lines.append("/* Second DATE_AND_TIME: modification date 2024-07-22T09:15:00+00:00 — AWARE */")
    lines.append("/* This is timezone-aware; comparing #25 vs #26 requires guessing tz for #25 */")
    lines.append("#26=DATE_AND_TIME(#21,#24);")
    lines.append("/* Product that has both timestamps attached */")
    lines.append("#30=PRODUCT('PART-055','Control Housing','Main housing for control unit',(#1));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_A','Initial release',#30);")
    lines.append("#32=PRODUCT_DEFINITION('design','',#31,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* DATE role assignments: 'creation_date' (naive) and 'last_modified' (aware) */")
    lines.append("#40=APPLIED_DATE_AND_TIME_ASSIGNMENT(#25,DATE_TIME_ROLE('creation_date'),(#32));")
    lines.append("#41=APPLIED_DATE_AND_TIME_ASSIGNMENT(#26,DATE_TIME_ROLE('last_modified'),(#32));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-mixed-timezone-naive-aware-dates',")
    lines.append("  (#22,#23,#24,#25,#26,#30,#32,#40,#41));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M133','M133','M133',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m133(path) -> None:
    Path(path).write_text(_render_m133())


f.render = _render_m133  # type: ignore[method-assign]
f.write = _write_m133    # type: ignore[method-assign]
