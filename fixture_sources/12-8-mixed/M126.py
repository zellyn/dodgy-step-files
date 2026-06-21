"""M126 — AP203 effectivity periods overlap with conflicting product configurations.

Catalog claim: Two TIME_INTERVAL_BASED_EFFECTIVITY entities cover an overlapping
date range while binding contradictory product configurations. A configuration
query at any date in the overlap window may return either configuration depending
on which effectivity was scanned first.

Reproducer recipe: TIME_INTERVAL_BASED_EFFECTIVITY('cfg_v1','rev_A', 2024-01-01,
2024-12-31) and a second covering 2024-06-01..2025-05-31 with rev_B.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  count_entity_def(b'TIME_INTERVAL_BASED_EFFECTIVITY') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M126",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where two "
        "TIME_INTERVAL_BASED_EFFECTIVITY entities cover an overlapping date range "
        "while binding contradictory product configurations; "
        "input: AP203 STEP file with two TIME_INTERVAL_BASED_EFFECTIVITY entities: "
        "the first (cfg_v1) covers 2024-01-01 to 2024-12-31 and binds product "
        "configuration rev_A; the second (cfg_v2) covers 2024-06-01 to 2025-05-31 "
        "and binds product configuration rev_B; the windows overlap from 2024-06-01 "
        "to 2024-12-31; any configuration query at a date in the overlap window may "
        "return either rev_A or rev_B depending on scan order; "
        "per ISO 10303-203 §4 effectivity windows for contradictory configurations "
        "must be non-overlapping and form a contiguous or gapped partition of the "
        "product lifecycle; overlapping effectivities make the configuration "
        "non-deterministic for any date in the overlap window; "
        "kernel must detect overlapping effectivity windows and reject the configuration "
        "set, or warn and pick the latest-released configuration deterministically; "
        "synonyms: effectivity ambiguity, configuration overlap, AP203 PDM date conflict, "
        "AP203 effectivity overlap, two configurations effective same date, "
        "PDM ambiguous effectivity"
    ),
    schema="AP242",
)


def _render_m126() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with two overlapping TIME_INTERVAL_BASED_EFFECTIVITYs.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20-#21    CALENDAR_DATE entities for effectivity start/end dates
      #30-#31    PRODUCT_DEFINITION_FORMATION rev_A and rev_B
      #32        PRODUCT for the part
      #40-#41    Two TIME_INTERVAL_BASED_EFFECTIVITY entities — DEFECT: overlapping windows
      #50-#51    PRODUCT_DEFINITION_WITH_ASSOCIATED_DOCUMENTS (not used; kept minimal)
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M126: AP203 effectivity periods overlap with conflicting product configurations */")
    lines.append("/* DEFECT: two TIME_INTERVAL_BASED_EFFECTIVITY windows overlap 2024-06-01..2024-12-31 */")
    lines.append("/* cfg_v1 (rev_A): 2024-01-01..2024-12-31; cfg_v2 (rev_B): 2024-06-01..2025-05-31 */")
    lines.append("/* Any query in the overlap window returns rev_A or rev_B non-deterministically */")
    lines.append("/* Per AP203 §4 effectivity windows for conflicting configs must not overlap */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'TIME_INTERVAL_BASED_EFFECTIVITY') >= 2 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M126: AP203 overlapping effectivity periods for conflicting configurations'),'2;1');")
    lines.append("FILE_NAME('M126.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Calendar dates for overlapping effectivity windows */")
    lines.append("/* Window 1: 2024-01-01 to 2024-12-31 */")
    lines.append("#20=CALENDAR_DATE(2024,1,1);")
    lines.append("#21=CALENDAR_DATE(2024,12,31);")
    lines.append("/* Window 2: 2024-06-01 to 2025-05-31 — overlaps window 1 from 2024-06-01..2024-12-31 */")
    lines.append("#22=CALENDAR_DATE(2024,6,1);")
    lines.append("#23=CALENDAR_DATE(2025,5,31);")
    lines.append("/* Product with two conflicting configurations */")
    lines.append("#30=PRODUCT('PART-001','Widget Assembly','Precision widget assembly',(#1));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_A','Initial release',#30);")
    lines.append("#32=PRODUCT_DEFINITION_FORMATION('rev_B','Engineering change rev_B',#30);")
    lines.append("/* Byte assertion: count_entity_def(b'TIME_INTERVAL_BASED_EFFECTIVITY') >= 2 */")
    lines.append("/* DEFECT: cfg_v1 window (2024-01-01..2024-12-31) overlaps cfg_v2 (2024-06-01..2025-05-31) */")
    lines.append("/* A valid file would use non-overlapping windows: e.g. 2024-01-01..2024-05-31, 2024-06-01.. */")
    lines.append("#40=TIME_INTERVAL_BASED_EFFECTIVITY('cfg_v1','',#31,")
    lines.append("  DATE_AND_TIME(#20,$),DATE_AND_TIME(#21,$));")
    lines.append("#41=TIME_INTERVAL_BASED_EFFECTIVITY('cfg_v2','',#32,")
    lines.append("  DATE_AND_TIME(#22,$),DATE_AND_TIME(#23,$));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-effectivity-periods-overlap-conflicting-configs',")
    lines.append("  (#31,#32,#40,#41));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M126','M126','M126',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m126(path) -> None:
    Path(path).write_text(_render_m126())


f.render = _render_m126  # type: ignore[method-assign]
f.write = _write_m126    # type: ignore[method-assign]
