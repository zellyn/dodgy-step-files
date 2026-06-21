"""M181 — AP238 workpiece_complete_for_nc missing required clamping references

Catalog claim: A WORKPIECE_COMPLETE_FOR_NC entity is declared with an
empty clamping_position list. AP238 requires that workpieces be tied
to their fixturing for collision-checking; an unfixed workpiece cannot
be safely machined. The controller has nothing to enforce keep-out
zones against.

Reproducer recipe: WORKPIECE_COMPLETE_FOR_NC('finished_part',$,$,$,$,$,$,(),$)
— empty parenthesised clamping list.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'WORKPIECE_COMPLETE_FOR_NC')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M181",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where WORKPIECE_COMPLETE_FOR_NC "
        "declares an empty clamping_position list; "
        "input: AP238 STEP-NC file containing a WORKPLAN with WORKPIECE_COMPLETE_FOR_NC; "
        "the entity 'finished_part' is declared as WORKPIECE_COMPLETE_FOR_NC with "
        "empty clamping_position list: WORKPIECE_COMPLETE_FOR_NC('finished_part',$,$,$,$,$,$,(),$); "
        "AP238 requires that workpieces be tied to their fixturing for collision-checking; "
        "an unfixed workpiece has no clamping references for the controller to enforce keep-out zones; "
        "the machine cannot perform collision-avoidance without knowing clamp positions; "
        "per ISO 10303-238 §5.4 workpiece_complete_for_nc clamping-mandatory invariant: "
        "at least one clamping reference must be declared for safe machining; "
        "kernel must validate that workpiece-complete entries declare at least one clamping reference; "
        "synonyms: AP238 workpiece has no clamps, STEP-NC fixturing missing, "
        "no keep-out zones for collision check, AP238 fixturing absent, "
        "STEP-NC clamps missing on workpiece, workpiece-complete with empty clamping list, "
        "no keep-out zones declared, AP238 workpiece-complete missing clamps, "
        "STEP-NC no fixturing references, workpiece floats with no clamping"
    ),
    schema="AP242",
)


def _render_m181() -> str:
    """Render AP238 STEP-NC file with WORKPIECE_COMPLETE_FOR_NC with empty clamping list.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #40       WORKPIECE 'raw_stock' — base workpiece
      #41       WORKPIECE_COMPLETE_FOR_NC 'finished_part' — DEFECT: empty clamping list
      #50       WORKPLAN 'unclamped_workpiece_program'
      #51       MACHINING_WORKINGSTEP 'mill_step'
      #52       MILLING_OPERATION 'mill_op'
      #60       WORKPIECE 'mill_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M181: AP238 workpiece_complete_for_nc missing required clamping references */")
    lines.append("/* DEFECT: WORKPIECE_COMPLETE_FOR_NC 'finished_part' has empty clamping_position list */")
    lines.append("/* AP238 requires workpieces tied to fixturing for collision-checking */")
    lines.append("/* Controller cannot enforce keep-out zones without clamping references */")
    lines.append("/* Per ISO 10303-238 §5.4 at least one clamping reference must be declared */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'WORKPIECE_COMPLETE_FOR_NC') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M181: AP238 workpiece_complete_for_nc with empty clamping list'),'2;1');")
    lines.append("FILE_NAME('M181.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 3 1 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
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
    lines.append("/* mm length unit reference for MEASURE_WITH_UNIT */")
    lines.append("#15=SI_UNIT(.MILLI.,.METRE.);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-workpiece-complete-for-nc-missing-clamping-references',")
    lines.append("  (#41,#52,#60));")
    lines.append("/* Base workpiece (raw stock) */")
    lines.append("#40=WORKPIECE('raw_stock','Raw stock for finished part',$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'WORKPIECE_COMPLETE_FOR_NC') */")
    lines.append("/* DEFECT: WORKPIECE_COMPLETE_FOR_NC with empty clamping_position list () */")
    lines.append("/* AP238 §5.4 invariant: clamping_position must be non-empty for safe machining */")
    lines.append("#41=WORKPIECE_COMPLETE_FOR_NC('finished_part',$,$,$,$,$,$,(),$);")
    lines.append("/* WORKPIECE 'mill_workpiece' for the milling step */")
    lines.append("#60=WORKPIECE('mill_workpiece','Workpiece for unclamped test',$,$,$,$,$);")
    lines.append("/* MILLING_OPERATION references the unclamped workpiece scenario */")
    lines.append("#52=MILLING_OPERATION('mill_op',$,$,$,$,$,$,$,$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP links milling op to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('mill_step','Unclamped workpiece mill step',#52,#60,$);")
    lines.append("/* WORKPLAN: single milling step on workpiece with missing clamps */")
    lines.append("#50=WORKPLAN('unclamped_workpiece_program','Unclamped workpiece milling workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M181','M181','M181',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m181(path) -> None:
    Path(path).write_text(_render_m181())


f.render = _render_m181  # type: ignore[method-assign]
f.write = _write_m181    # type: ignore[method-assign]
