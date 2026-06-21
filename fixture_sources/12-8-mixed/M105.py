"""M105 — AP238 ISO 8601 timestamps on operations going backwards.

Catalog claim: Successive MACHINING_OPERATIONs carry time_stamp
attributes that go backwards: operation A's timestamp 2026-04-30T10:00:00,
operation B (next in workplan) 2026-04-30T09:00:00. Either the publisher
has a clock-skew issue, the ops were authored out of order and stamped at
authoring time, or the file was assembled from multiple jobs.

Reproducer recipe: Two MACHINING_OPERATIONs in workplan order with
monotonically *decreasing* ISO 8601 timestamps in their description /
approval attributes.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'2026-04-30T10:00:00')
  contains(b'2026-04-30T09:00:00')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M105",
    defect=(
        "GEOMETRIC_CURVE_SET containing two AP238 MACHINING_OPERATIONs with monotonically "
        "decreasing ISO 8601 timestamps — operation A at 2026-04-30T10:00:00, "
        "operation B (next in workplan) at 2026-04-30T09:00:00; "
        "input: AP238 STEP-NC file where WORKPLAN sequences two MACHINING_OPERATIONs: "
        "'op_a' described as authored at '2026-04-30T10:00:00' (earlier workplan position, "
        "later timestamp) and 'op_b' described as authored at '2026-04-30T09:00:00' "
        "(later workplan position, earlier timestamp); "
        "per ISO 10303-238 §6.4 operation chronology rules and ISO 8601 ordering, "
        "timestamps on successive operations in workplan order should be monotonically "
        "non-decreasing; backward timestamps indicate: clock-skew in publisher, "
        "operations authored out of order and stamped at authoring time, or the file "
        "was assembled from multiple jobs with different time sources; "
        "STEP-NC consumers using timestamps for cycle-time estimation or audit trail "
        "receive inconsistent chronology data; "
        "kernel must warn and accept: validate timestamp monotonicity along workplan order; "
        "emit a warning diagnostic on inversions and continue; "
        "synonyms: timestamp regression, AP238 chronology wrong, operation timestamps decreasing, "
        "ISO 8601 backwards across ops, machining operation time_stamp out of order, "
        "AP238 timestamps inverted, STEP-NC operation B before A, timestamps backwards"
    ),
    schema="AP242",
)


def _render_m105() -> str:
    """Render AP238 file with two MACHINING_OPERATIONs having decreasing timestamps.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       DATE_AND_TIME for op_a: 2026-04-30T10:00:00 — earlier workplan pos, later stamp
      #21       DATE_AND_TIME for op_b: 2026-04-30T09:00:00 — later workplan pos, earlier stamp
      #30       APPROVAL_STATUS for both operations
      #31       APPROVAL for op_a (timestamp 2026-04-30T10:00:00)
      #32       APPROVAL for op_b (timestamp 2026-04-30T09:00:00) — DEFECT: goes backwards
      #50       MACHINED_FEATURE 'feature_a'
      #51       MACHINED_FEATURE 'feature_b'
      #60       MACHINING_TOOL 'endmill_8mm'
      #70       MACHINING_OPERATION 'op_a' with approval #31 (10:00)
      #71       MACHINING_OPERATION 'op_b' with approval #32 (09:00) — DEFECT: timestamp regresses
      #80       MACHINING_WORKINGSTEP 'step_a'
      #81       MACHINING_WORKINGSTEP 'step_b'
      #90       WORKPLAN referencing step_a then step_b — chronology inverted
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M105: AP238 ISO 8601 timestamps on operations going backwards */")
    lines.append("/* DEFECT: op_a timestamp 2026-04-30T10:00:00, op_b (next) 2026-04-30T09:00:00 */")
    lines.append("/* Timestamp regression indicates clock-skew, authoring-order mismatch, or job merge */")
    lines.append("/* Violates ISO 10303-238 §6.4 operation chronology rules */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'2026-04-30T10:00:00') */")
    lines.append("/* Byte assertion: contains(b'2026-04-30T09:00:00') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M105: AP238 MACHINING_OPERATION timestamps going backwards'),'2;1');")
    lines.append("FILE_NAME('M105.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Byte assertion: contains(b'2026-04-30T10:00:00') */")
    lines.append("/* Timestamp for op_a — first in workplan order, later calendar time */")
    lines.append("#20=DATE_AND_TIME(DATE(2026,4,30),LOCAL_TIME(10,0,0.0,$));")
    lines.append("/* Byte assertion: contains(b'2026-04-30T09:00:00') */")
    lines.append("/* DEFECT: Timestamp for op_b — second in workplan order, EARLIER calendar time */")
    lines.append("/* 09:00 < 10:00 — timestamps regress along workplan sequence */")
    lines.append("#21=DATE_AND_TIME(DATE(2026,4,30),LOCAL_TIME(9,0,0.0,$));")
    lines.append("/* Approval status for both operations */")
    lines.append("#30=APPROVAL_STATUS('approved');")
    lines.append("/* Approval for op_a at 10:00 — first in workplan *)  */")
    lines.append("#31=APPROVAL(#30,'ap238-op-a-approved-at-10-00');")
    lines.append("#33=DATE_TIME_ROLE('creation_date');")
    lines.append("#34=APPLIED_DATE_AND_TIME_ASSIGNMENT(#20,#33,(#31));")
    lines.append("/* DEFECT: Approval for op_b at 09:00 — second in workplan but earlier timestamp */")
    lines.append("#32=APPROVAL(#30,'ap238-op-b-approved-at-09-00');")
    lines.append("#35=APPLIED_DATE_AND_TIME_ASSIGNMENT(#21,#33,(#32));")
    lines.append("/* Machined features for the two operations */")
    lines.append("#50=MACHINED_FEATURE('feature_a',$,$,$,$,$);")
    lines.append("#51=MACHINED_FEATURE('feature_b',$,$,$,$,$);")
    lines.append("/* Shared end mill for both operations */")
    lines.append("#60=MACHINING_TOOL('endmill_8mm',$,$,$);")
    lines.append("/* First MACHINING_OPERATION in workplan — timestamp 10:00 (later) */")
    lines.append("#70=MACHINING_OPERATION('op_a',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* DEFECT: Second MACHINING_OPERATION in workplan — timestamp 09:00 (earlier) */")
    lines.append("/* Workplan order: op_a THEN op_b, but op_b timestamp precedes op_a — regression */")
    lines.append("#71=MACHINING_OPERATION('op_b',#60,$,$,$,$,$,$,#51,$,$);")
    lines.append("/* Workingsteps */")
    lines.append("#80=MACHINING_WORKINGSTEP('step_a',#50,#70,$);")
    lines.append("#81=MACHINING_WORKINGSTEP('step_b',#51,#71,$);")
    lines.append("/* WORKPLAN: step_a (ts=10:00) comes BEFORE step_b (ts=09:00) — timestamps inverted */")
    lines.append("#90=WORKPLAN('main',(#80,#81),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-iso8601-timestamps-on-operations-going-backwards',")
    lines.append("  (#20,#21,#31,#32,#50,#51,#60,#70,#71,#80,#81,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M105','M105','M105',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m105(path) -> None:
    Path(path).write_text(_render_m105())


f.render = _render_m105  # type: ignore[method-assign]
f.write = _write_m105    # type: ignore[method-assign]
