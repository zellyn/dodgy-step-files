"""M142 — AP203 CHANGE_REQUEST targets revision already superseded

Catalog claim: A CHANGE_REQUEST_ITEM (APPLIED_ACTION_ASSIGNMENT of role
'change_request') points at PRODUCT_DEFINITION rev_A for which a successor
rev_B has already been released (per PRODUCT_DEFINITION_RELATIONSHIP). Changes
targeting the obsolete revision cannot be applied without re-baselining.

Reproducer recipe: PRODUCT_DEFINITION_RELATIONSHIP('eco','derived_from',
rev_A_pd, rev_B_pd) plus an APPLIED_ACTION_ASSIGNMENT(change_action, (rev_A_pd)).

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'APPLIED_ACTION_ASSIGNMENT')
  contains(b'PRODUCT_DEFINITION_RELATIONSHIP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M142",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where an "
        "APPLIED_ACTION_ASSIGNMENT acting as a CHANGE_REQUEST_ITEM targets a "
        "PRODUCT_DEFINITION (rev_A) that has already been superseded by a released "
        "successor rev_B, declared via a PRODUCT_DEFINITION_RELATIONSHIP of name "
        "'derived_from'; the change request is stale and cannot be applied; "
        "input: AP203 STEP file containing two PRODUCT_DEFINITION instances: #22 "
        "(rev_A, the original design) and #24 (rev_B, the successor released via "
        "engineering change); a PRODUCT_DEFINITION_RELATIONSHIP #30 records the "
        "succession: name='eco', description='derived_from', relating_id=#22 "
        "(rev_A), related_id=#24 (rev_B); additionally an APPLIED_ACTION_ASSIGNMENT "
        "#40 with an ACTION of role 'change_request' still targets #22 (rev_A) — "
        "the now-superseded revision; per ISO 10303-203 §4.5 change requests should "
        "target the current (non-superseded) revision; when rev_B is the released "
        "baseline, change requests aimed at rev_A cannot be applied without first "
        "re-baselining against rev_B; PDM change management tools that check "
        "effective revision before routing an engineering change order (ECO) must "
        "detect this staleness and reject or redirect; "
        "kernel must detect change requests targeting superseded revisions and warn "
        "or reject; "
        "synonyms: AP203 ECO obsolete target, PDM change against old rev, "
        "change request stale, AP203 ECO targets old revision, "
        "change request on obsolete part, PDM change against superseded rev"
    ),
    schema="AP242",
)


def _render_m142() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with stale CHANGE_REQUEST targeting superseded rev.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        PRODUCT
      #21        PRODUCT_DEFINITION_FORMATION for rev_A
      #22        PRODUCT_DEFINITION for rev_A — the superseded revision
      #23        PRODUCT_DEFINITION_FORMATION for rev_B
      #24        PRODUCT_DEFINITION for rev_B — the released successor
      #30        PRODUCT_DEFINITION_RELATIONSHIP — declares rev_B derived from rev_A
      #35        ACTION representing the change request
      #36        ACTION_METHOD for the ECO workflow
      #40        APPLIED_ACTION_ASSIGNMENT — DEFECT: targets rev_A (#22), not rev_B (#24)
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M142: AP203 CHANGE_REQUEST targets revision already superseded */")
    lines.append("/* DEFECT: APPLIED_ACTION_ASSIGNMENT (change_request) targets #22 (rev_A) */")
    lines.append("/* but PRODUCT_DEFINITION_RELATIONSHIP records rev_B (#24) as successor of rev_A */")
    lines.append("/* The change request is stale: it targets an obsolete revision */")
    lines.append("/* Per ISO 10303-203 §4.5 ECOs must target the current released baseline revision */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'APPLIED_ACTION_ASSIGNMENT') */")
    lines.append("/* Byte assertion: contains(b'PRODUCT_DEFINITION_RELATIONSHIP') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M142: AP203 CHANGE_REQUEST APPLIED_ACTION_ASSIGNMENT targets superseded revision'),'2;1');")
    lines.append("FILE_NAME('M142.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Product with two revisions: rev_A (old) and rev_B (current released baseline) */")
    lines.append("#20=PRODUCT('PART-606','Gear Housing Cover','Sealed housing for gear assembly',(#1));")
    lines.append("/* rev_A: the original design that has been superseded */")
    lines.append("#21=PRODUCT_DEFINITION_FORMATION('rev_A','Original design release',#20);")
    lines.append("/* #22 is the superseded PRODUCT_DEFINITION — the stale target of the change request */")
    lines.append("#22=PRODUCT_DEFINITION('design','original release',#21,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* rev_B: the released successor created by engineering change ECO-2024-047 */")
    lines.append("#23=PRODUCT_DEFINITION_FORMATION('rev_B','ECO-2024-047 material change',#20);")
    lines.append("/* #24 is the current PRODUCT_DEFINITION — the one the change request SHOULD target */")
    lines.append("#24=PRODUCT_DEFINITION('design','material change applied',#23,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* Byte assertion: contains(b'PRODUCT_DEFINITION_RELATIONSHIP') */")
    lines.append("/* Succession record: rev_B (#24) is derived from rev_A (#22) */")
    lines.append("/* This relationship formally marks #22 (rev_A) as superseded */")
    lines.append("/* Any change request that targets #22 is by definition stale *)  ")
    lines.append("#30=PRODUCT_DEFINITION_RELATIONSHIP('eco','derived_from',#22,#24);")
    lines.append("/* ACTION representing the in-flight engineering change request ECO-2024-099 */")
    lines.append("#35=ACTION('ECO-2024-099','Update sealing gasket specification',$);")
    lines.append("#36=ACTION_METHOD('change_request','Standard ECO review procedure',$,'open');")
    lines.append("/* Byte assertion: contains(b'APPLIED_ACTION_ASSIGNMENT') */")
    lines.append("/* DEFECT: items=(#22) targets rev_A — the superseded PRODUCT_DEFINITION */")
    lines.append("/* The correct target is #24 (rev_B, the current baseline) *)   ")
    lines.append("/* A PDM tool checking effective revision before routing ECO-2024-099 would */")
    lines.append("/* detect that #22 is no longer the head revision and reject or re-target */")
    lines.append("#40=APPLIED_ACTION_ASSIGNMENT(#35,(#22),ACTION_REQUEST_SOLUTION(#36,#35));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-change-request-targets-superseded-revision-rev-A',")
    lines.append("  (#20,#21,#22,#23,#24,#30,#35,#36,#40));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M142','M142','M142',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m142(path) -> None:
    Path(path).write_text(_render_m142())


f.render = _render_m142  # type: ignore[method-assign]
f.write = _write_m142    # type: ignore[method-assign]
