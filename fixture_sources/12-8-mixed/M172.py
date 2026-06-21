"""M172 — AP238 turning_operation on workpiece without rotation axis

Catalog claim: A TURNING_OPERATION targets a WORKPIECE that has no
rotational-axis declaration (no spindle_axis, no axis_of_revolution
placement). The controller has no axis to spin the stock around;
turning is meaningless on a non-rotating workpiece.

Reproducer recipe: a WORKPIECE declared with no axis_of_revolution;
a TURNING_OPERATION whose workingstep mounts that workpiece.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TURNING_OPERATION(')
  contains(b'WORKPIECE(')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M172",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where TURNING_OPERATION targets "
        "a WORKPIECE with no axis_of_revolution or spindle_axis declaration; "
        "input: AP238 STEP-NC file containing a WORKPLAN for a turning operation; "
        "the WORKPIECE 'prismatic_block' has no rotational axis: "
        "all axis_of_revolution and spindle_axis fields are null ($); "
        "the TURNING_OPERATION 'turn_no_axis' targets this workpiece via MACHINING_WORKINGSTEP; "
        "turning requires the workpiece to rotate about a spindle axis; "
        "without a declared rotation axis the controller has no axis to spin the stock; "
        "turning a prismatic block is geometrically meaningless and physically dangerous; "
        "the STEP-NC programmer applied a lathe operation template to a milling-machine workpiece; "
        "per ISO 10303-238 §5.8 a turning operation's workpiece must declare a rotational axis; "
        "kernel must validate that turning operations target rotationally-declared workpieces; "
        "synonyms: AP238 turn op on prismatic block, STEP-NC missing rotation axis on lathe op, "
        "block targeted by turning operation, turn op without spindle axis, "
        "AP238 turning prismatic part, STEP-NC missing rotation axis"
    ),
    schema="AP242",
)


def _render_m172() -> str:
    """Render AP238 STEP-NC file with TURNING_OPERATION on workpiece without rotation axis.

    Entity layout:
      #10-#14   Unit context (mm)
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN 'turn_no_axis_program' — top-level STEP-NC program
      #51       MACHINING_WORKINGSTEP 'turn_no_axis_step'
      #52       TURNING_OPERATION 'turn_no_axis' — targets workpiece with no rotation axis
      #60       WORKPIECE 'prismatic_block' — DEFECT: no axis_of_revolution (all null)
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M172: AP238 turning_operation on workpiece without rotation axis */")
    lines.append("/* DEFECT: WORKPIECE 'prismatic_block' has no axis_of_revolution or spindle_axis */")
    lines.append("/* Turning requires workpiece to rotate about spindle axis — none declared */")
    lines.append("/* STEP-NC programmer applied lathe op template to milling-machine workpiece */")
    lines.append("/* Per ISO 10303-238 §5.8 turning op workpiece must declare rotational axis */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TURNING_OPERATION(') */")
    lines.append("/* Byte assertion: contains(b'WORKPIECE(') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M172: AP238 turning_operation on workpiece with no rotation axis'),'2;1');")
    lines.append("FILE_NAME('M172.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-turning-operation-on-workpiece-without-rotation-axis',")
    lines.append("  (#52,#60));")
    lines.append("/* WORKPLAN 'turn_no_axis_program' — AP238 top-level NC program */")
    lines.append("#50=WORKPLAN('turn_no_axis_program','Turning no-axis defect workplan',(),$,(#51));")
    lines.append("/* MACHINING_WORKINGSTEP links workpiece to turning operation */")
    lines.append("#51=MACHINING_WORKINGSTEP('turn_no_axis_step','No-rotation-axis turning workingstep',#52,#60,$);")
    lines.append("/* Byte assertion: contains(b'TURNING_OPERATION(') */")
    lines.append("#52=TURNING_OPERATION('turn_no_axis',$,$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'WORKPIECE(') */")
    lines.append("/* DEFECT: WORKPIECE has no axis_of_revolution — all optional axis fields are null */")
    lines.append("/* A prismatic block with no rotation axis is an invalid target for turning operations */")
    lines.append("#60=WORKPIECE('prismatic_block','Prismatic block workpiece no rotation axis',$,$,$,$,$);")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M172','M172','M172',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m172(path) -> None:
    Path(path).write_text(_render_m172())


f.render = _render_m172  # type: ignore[method-assign]
f.write = _write_m172    # type: ignore[method-assign]
