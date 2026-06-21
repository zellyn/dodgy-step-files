"""M100 — AP238 spindle-on issued after first tool-workpiece contact.

Catalog claim: A workplan's MACHINING_OPERATION chain begins with a
CUTTING_OPERATION (tool descends into workpiece) and only afterwards
issues SPINDLE_SPEED / START_SPINDLE. The first contact occurs with the
spindle stopped, breaking the tool or marring the workpiece surface.

Reproducer recipe: A WORKPLAN listing a DRILLING_OPERATION *before*
any explicit spindle-control operation.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'DRILLING_OPERATION')
  contains(b'WORKPLAN')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M100",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 WORKPLAN where DRILLING_OPERATION precedes "
        "any spindle-control operation — spindle is stopped during first tool-workpiece contact; "
        "input: AP238 STEP-NC file where the WORKPLAN lists a DRILLING_OPERATION as its first "
        "workingstep with no prior SPINDLE_SPEED or START_SPINDLE control operation; "
        "per ISO 10303-238 §6.4 the spindle must be commanded on before the first cutting contact; "
        "tool descends into the workpiece with spindle stopped, breaking the tool or marring "
        "the workpiece surface finish; "
        "kernel must validate that spindle is commanded on before first cutting contact; "
        "warn or reject when a cutting operation is sequenced before spindle-on control; "
        "synonyms: spindle off during cut, AP238 ordering hazard, missing spindle-on prefix, "
        "AP238 spindle starts after cut begins, STEP-NC contact without spindle, "
        "machining without spindle on"
    ),
    schema="AP242",
)


def _render_m100() -> str:
    """Render AP238 file with DRILLING_OPERATION before any spindle-on command.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       MACHINED_FEATURE 'hole_a' — the drilling target
      #60       MACHINING_TOOL 'drill_10mm'
      #70       DRILLING_OPERATION referencing #60 — DEFECT: executes before spindle is on
      #80       MACHINING_WORKINGSTEP wrapping #70 (first in workplan — no spindle-on precedes)
      #90       WORKPLAN with only #80 — no spindle-on workingstep before #80
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M100: AP238 spindle-on issued after first tool-workpiece contact */")
    lines.append("/* DEFECT: DRILLING_OPERATION precedes any spindle-control operation */")
    lines.append("/* Spindle stopped at first tool-workpiece contact — breaks tool or mars surface */")
    lines.append("/* Violates ISO 10303-238 §6.4 spindle / coolant / approach ordering */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'DRILLING_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'WORKPLAN') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M100: AP238 DRILLING_OPERATION before spindle-on'),'2;1');")
    lines.append("FILE_NAME('M100.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Target machined feature — a drilled hole */")
    lines.append("#50=MACHINED_FEATURE('hole_a',$,$,$,$,$);")
    lines.append("/* 10mm drill bit — will break if spindle is not rotating at contact */")
    lines.append("#60=MACHINING_TOOL('drill_10mm',$,$,$);")
    lines.append("/* Byte assertion: contains(b'DRILLING_OPERATION') */")
    lines.append("/* DEFECT: DRILLING_OPERATION is the first (and only) operation in the workplan */")
    lines.append("/* No spindle-on control operation precedes this cutting operation */")
    lines.append("/* When controller executes this, spindle is stopped during plunge — tool breaks */")
    lines.append("#70=DRILLING_OPERATION('drill_plunge',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* First workingstep in the WORKPLAN — no spindle-on workingstep before this */")
    lines.append("#80=MACHINING_WORKINGSTEP('drill_step',#50,#70,$);")
    lines.append("/* Byte assertion: contains(b'WORKPLAN') */")
    lines.append("/* WORKPLAN has only the drilling step — missing a spindle-on step as first entry */")
    lines.append("/* Correct ordering: spindle-on workingstep FIRST, then drilling workingstep *)  */")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-spindle-on-after-first-tool-workpiece-contact',")
    lines.append("  (#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M100','M100','M100',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m100(path) -> None:
    Path(path).write_text(_render_m100())


f.render = _render_m100  # type: ignore[method-assign]
f.write = _write_m100    # type: ignore[method-assign]
