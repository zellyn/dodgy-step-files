"""M128 — AP203 design approved AFTER its effectivity start date.

Catalog claim: An APPROVAL_DATE_TIME on a release approval is later than the
start of the corresponding TIME_INTERVAL_BASED_EFFECTIVITY. Per the AP203
process workflow, design approval must precede effectivity; the file shows
effectivity beginning months before the approval was logged.

Reproducer recipe: APPROVAL_DATE_TIME(2024-09-15,..) and
TIME_INTERVAL_BASED_EFFECTIVITY(..,2024-06-01,..).

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'APPROVAL_DATE_TIME')
  contains(b'TIME_INTERVAL_BASED_EFFECTIVITY')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M128",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where an "
        "APPROVAL_DATE_TIME (2024-09-15) is later than the start of the corresponding "
        "TIME_INTERVAL_BASED_EFFECTIVITY (2024-06-01), violating the AP203 process "
        "workflow ordering requirement; "
        "input: AP203 STEP file with a TIME_INTERVAL_BASED_EFFECTIVITY whose window "
        "starts on 2024-06-01 and an APPROVAL_DATE_TIME of 2024-09-15 on the release "
        "APPROVAL entity for the same product definition formation; per ISO 10303-203 "
        "§4 the design approval must precede the effectivity start — approval gates "
        "the release into production, so the design cannot be 'effective' (in production "
        "use) until it has been approved; the file encodes effectivity starting three "
        "months before the approval was granted, meaning the design was technically "
        "in service without authorization; "
        "kernel must detect the inversion (approval_date > effectivity_start) and warn "
        "or reject the approval/effectivity pair as out of process order; "
        "synonyms: approval workflow inversion, effectivity precedes approval, "
        "design approved after effectivity start, AP203 approval after release, "
        "approved after effective, AP203 process violation, release sequence inverted"
    ),
    schema="AP242",
)


def _render_m128() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with APPROVAL_DATE_TIME after effectivity start.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        CALENDAR_DATE for effectivity start (2024-06-01) — earlier
      #21        CALENDAR_DATE for effectivity end (2025-05-31)
      #22        CALENDAR_DATE for approval date (2024-09-15) — later than #20: DEFECT
      #30        PRODUCT and PRODUCT_DEFINITION_FORMATION
      #31        PRODUCT_DEFINITION
      #40        APPROVAL entity ('approved' status)
      #41        APPROVAL_DATE_TIME(2024-09-15, #40) — the approval timestamp
      #42        TIME_INTERVAL_BASED_EFFECTIVITY starting 2024-06-01 — before approval: DEFECT
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M128: AP203 design approved AFTER its effectivity start date */")
    lines.append("/* DEFECT: APPROVAL_DATE_TIME = 2024-09-15; effectivity starts 2024-06-01 */")
    lines.append("/* Approval is three months AFTER effectivity began — process order inverted */")
    lines.append("/* Per AP203 §4 approval must precede effectivity start; design cannot be */")
    lines.append("/* effective (in production) before it has been formally approved */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'APPROVAL_DATE_TIME') */")
    lines.append("/* Byte assertion: contains(b'TIME_INTERVAL_BASED_EFFECTIVITY') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M128: AP203 APPROVAL_DATE_TIME after effectivity start date'),'2;1');")
    lines.append("FILE_NAME('M128.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Calendar dates: effectivity start (2024-06-01) and approval (2024-09-15) */")
    lines.append("/* The key invariant: approval_date (2024-09-15) > effectivity_start (2024-06-01) */")
    lines.append("#20=CALENDAR_DATE(2024,6,1);")
    lines.append("#21=CALENDAR_DATE(2025,5,31);")
    lines.append("/* Byte assertion: contains(b'APPROVAL_DATE_TIME') */")
    lines.append("/* DEFECT: approval date 2024-09-15 is three months after effectivity start 2024-06-01 */")
    lines.append("#22=CALENDAR_DATE(2024,9,15);")
    lines.append("/* Product and formation */")
    lines.append("#30=PRODUCT('PART-001','Bracket Assembly','Structural mounting bracket',(#1));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_A','Initial production release',#30);")
    lines.append("#32=PRODUCT_DEFINITION_CONTEXT(#1,'design');")
    lines.append("#33=PRODUCT_DEFINITION('release','',#31,#32);")
    lines.append("/* APPROVAL: the release approval that was logged late */")
    lines.append("#40=APPROVAL(APPROVAL_STATUS('approved'),'Release approval for rev_A');")
    lines.append("/* Byte assertion: contains(b'APPROVAL_DATE_TIME') */")
    lines.append("/* DEFECT: approval logged 2024-09-15 — three months after effectivity began 2024-06-01 */")
    lines.append("/* Correct ordering: approval_date <= effectivity_start */")
    lines.append("#41=APPROVAL_DATE_TIME(DATE_AND_TIME(#22,$),#40);")
    lines.append("#42=APPLIED_APPROVAL_ASSIGNMENT(#40,(#33));")
    lines.append("/* Byte assertion: contains(b'TIME_INTERVAL_BASED_EFFECTIVITY') */")
    lines.append("/* DEFECT: effectivity starts 2024-06-01 which is BEFORE approval date 2024-09-15 */")
    lines.append("/* Design was declared effective three months before it was approved */")
    lines.append("#43=TIME_INTERVAL_BASED_EFFECTIVITY('cfg_v1','',#31,")
    lines.append("  DATE_AND_TIME(#20,$),DATE_AND_TIME(#21,$));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-approval-date-after-effectivity-start',")
    lines.append("  (#31,#33,#40,#41,#43));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M128','M128','M128',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m128(path) -> None:
    Path(path).write_text(_render_m128())


f.render = _render_m128  # type: ignore[method-assign]
f.write = _write_m128    # type: ignore[method-assign]
