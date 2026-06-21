"""M092 — AP238 workplan workingsteps in non-executable order.

Catalog claim: A WORKPLAN lists its its_elements in an order that violates
feature dependencies: a finishing pass appears before the roughing pass on
the same feature. Per AP238 §6.4 a workplan's element list is the
executable sequence; order is semantic, not editorial.

Reproducer recipe: WORKPLAN('main',(#finish_step, #rough_step),$,$,$)
where #finish_step is a finishing MACHINING_OPERATION referencing the same
feature as #rough_step (a roughing operation), with finishing listed first.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'WORKPLAN(')
  contains(b'MACHINING_OPERATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M092",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 WORKPLAN with workingsteps in non-executable "
        "order — finishing pass listed before roughing pass on the same feature; "
        "input: AP238 STEP-NC file where WORKPLAN('main') declares its_elements list as "
        "( #finish_step, #rough_step ) with the finishing MACHINING_WORKINGSTEP listed "
        "first and the roughing MACHINING_WORKINGSTEP listed second; "
        "both workingsteps reference the same MACHINED_FEATURE ('pocket_a'), so the "
        "finishing pass runs before the roughing pass creates material clearance; "
        "per ISO 10303-238 §6.4 workplan execution semantics the its_elements list is "
        "the executable sequence — order is semantic, not merely editorial; "
        "a controller running the file as-written produces a part where the finishing "
        "tool engages the full pocket depth before roughing removes the bulk material, "
        "breaking the tool or producing a gouged surface; "
        "kernel must validate workingstep ordering against feature dependency graph; "
        "warn on suspicious orderings (finishing before roughing on the same feature) "
        "or reject as malformed; "
        "synonyms: STEP-NC bad workingstep sequence, workplan order semantically wrong, "
        "finishing before roughing, STEP-NC workingsteps run in wrong order, "
        "AP238 finishing before roughing, workplan order doesn't make sense"
    ),
    schema="AP242",
)


def _render_m092() -> str:
    """Render AP238 file with WORKPLAN listing finishing step before roughing step.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       MACHINED_FEATURE 'pocket_a' (shared by both workingsteps)
      #60       MACHINING_TOOL for roughing ('roughing_endmill')
      #61       MACHINING_TOOL for finishing ('finishing_endmill')
      #70       MACHINING_OPERATION (roughing pass on pocket_a)
      #71       MACHINING_OPERATION (finishing pass on pocket_a)
      #80       MACHINING_WORKINGSTEP wrapping roughing operation
      #81       MACHINING_WORKINGSTEP wrapping finishing operation
      #90       WORKPLAN('main', (#81, #80)) — defect: finish (#81) before rough (#80)
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M092: AP238 workplan workingsteps in non-executable order */")
    lines.append("/* DEFECT: WORKPLAN lists finish_step before rough_step on same feature */")
    lines.append("/* Per AP238 §6.4, its_elements list is the executable sequence */")
    lines.append("/* Controller runs finish pass before roughing creates clearance — tool breakage */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'WORKPLAN(') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_OPERATION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M092: AP238 WORKPLAN with finishing before roughing'),'2;1');")
    lines.append("FILE_NAME('M092.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Shared MACHINED_FEATURE that both workingsteps operate on */")
    lines.append("/* Both roughing and finishing target the same pocket */")
    lines.append("#50=MACHINED_FEATURE('pocket_a',$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'MACHINING_OPERATION') */")
    lines.append("/* Roughing pass: removes bulk material from pocket_a */")
    lines.append("#60=MACHINING_TOOL('roughing_endmill',$,$,$);")
    lines.append("#70=MACHINING_OPERATION('rough_pocket_a',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* Finishing pass: light cuts to achieve final tolerance on pocket_a */")
    lines.append("#61=MACHINING_TOOL('finishing_endmill',$,$,$);")
    lines.append("#71=MACHINING_OPERATION('finish_pocket_a',#61,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* Workingsteps wrapping each operation */")
    lines.append("#80=MACHINING_WORKINGSTEP('rough_step',#50,#70,$);")
    lines.append("#81=MACHINING_WORKINGSTEP('finish_step',#50,#71,$);")
    lines.append("/* Byte assertion: contains(b'WORKPLAN(') */")
    lines.append("/* DEFECT: WORKPLAN lists (#81 finish, #80 rough) — finishing before roughing */")
    lines.append("/* Executable order is: finish_step THEN rough_step — physically wrong */")
    lines.append("/* Correct order would be: (#80 rough, #81 finish) */")
    lines.append("#90=WORKPLAN('main',(#81,#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-workplan-finishing-before-roughing-wrong-order',")
    lines.append("  (#50,#60,#61,#70,#71,#80,#81,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M092','M092','M092',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m092(path) -> None:
    Path(path).write_text(_render_m092())


f.render = _render_m092  # type: ignore[method-assign]
f.write = _write_m092    # type: ignore[method-assign]
