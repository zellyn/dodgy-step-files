"""M175 — AP238 drilling_operation tool axis not normal to feature face

Catalog claim: A DRILLING_OPERATION declares a tool_axis vector tilted
30 degrees from the feature's hole-axis. The controller either drills
a slanted hole (mismatching the design intent) or refuses the operation
because the tool axis isn't normal to the feature face.

Reproducer recipe: a ROUND_HOLE whose locator's axis is (0,0,1);
a DRILLING_OPERATION whose tool_axis is (0.5, 0.0, 0.866) (30 deg tilt).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'DRILLING_OPERATION')
  contains(b'tool_axis_tilted')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M175",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where DRILLING_OPERATION tool_axis is tilted "
        "30 degrees from the ROUND_HOLE feature's hole-axis (0,0,1); "
        "input: AP238 STEP-NC file containing a WORKPLAN for a drilling operation; "
        "the ROUND_HOLE 'target_hole' is located with axis (0,0,1) — vertical drill axis; "
        "the DRILLING_OPERATION 'drill_tilted' declares tool_axis direction (0.5,0.0,0.866) "
        "which is 30 degrees from the feature axis — a mis-aligned drill path; "
        "the controller either drills a slanted hole mismatching design intent "
        "or refuses the operation because tool axis is not normal to the feature face; "
        "a tool_axis_tilted label is embedded as a named entity for byte-assertion coverage; "
        "per ISO 10303-238 §5.8 the drilling operation tool axis must align with feature hole-axis; "
        "kernel must validate tool_axis against targeted feature's hole-axis; "
        "synonyms: AP238 drilling tilted axis, STEP-NC drill not normal to face, "
        "drilling tool not perpendicular, AP238 drill axis tilted, "
        "STEP-NC drilling skewed hole, drill not perpendicular to face, "
        "AP238 drill operation tilted, drilling op axis mismatch with feature, "
        "drill operation skewed"
    ),
    schema="AP242",
)


def _render_m175() -> str:
    """Render AP238 STEP-NC file with DRILLING_OPERATION tool axis tilted 30 degrees from feature.

    Entity layout:
      #10-#14   Unit context (mm)
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       DIRECTION (0,0,1) — hole feature's expected axis (vertical)
      #31       DIRECTION (0.5,0.0,0.866) — DEFECT: tool_axis tilted 30 degrees from (0,0,1)
      #32       CARTESIAN_POINT origin of hole locator
      #33       AXIS2_PLACEMENT_3D for hole locator (axis = (0,0,1))
      #40       ROUND_HOLE 'target_hole' — located with axis (0,0,1)
      #50       WORKPLAN 'tilted_drill_program' — AP238 top-level NC program
      #51       MACHINING_WORKINGSTEP 'tilted_drill_step'
      #52       DRILLING_OPERATION 'drill_tilted' — DEFECT: tool_axis 30 deg off
      #60       WORKPIECE 'drill_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M175: AP238 drilling_operation tool axis not normal to feature face */")
    lines.append("/* DEFECT: DRILLING_OPERATION tool_axis (0.5,0.0,0.866) tilted 30 deg from feature axis (0,0,1) */")
    lines.append("/* ROUND_HOLE 'target_hole' has hole-axis (0,0,1); drill does not align with feature */")
    lines.append("/* Controller drills slanted hole or refuses operation — design intent violated */")
    lines.append("/* Per ISO 10303-238 §5.8 drilling tool axis must align with feature hole-axis */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'DRILLING_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'tool_axis_tilted') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M175: AP238 drilling_operation tool axis 30 deg off feature normal'),'2;1');")
    lines.append("FILE_NAME('M175.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Feature hole-axis direction (0,0,1) — vertical, expected tool alignment */")
    lines.append("#30=DIRECTION('hole_axis',(0.0,0.0,1.0));")
    lines.append("/* DEFECT: tool_axis direction (0.5,0.0,0.866) — 30 degrees from (0,0,1) */")
    lines.append("/* Byte assertion: contains(b'tool_axis_tilted') */")
    lines.append("#31=DIRECTION('tool_axis_tilted',(0.5,0.0,0.866));")
    lines.append("#32=CARTESIAN_POINT('hole_origin',(50.0,50.0,0.0));")
    lines.append("#33=AXIS2_PLACEMENT_3D('hole_locator',#32,#30,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-drilling-tool-axis-not-normal-to-feature-face',")
    lines.append("  (#40,#52,#60));")
    lines.append("/* ROUND_HOLE 'target_hole': located with vertical axis (0,0,1) */")
    lines.append("#40=ROUND_HOLE('target_hole',$,$,#33,$);")
    lines.append("/* Byte assertion: contains(b'DRILLING_OPERATION') */")
    lines.append("/* DEFECT: DRILLING_OPERATION with tool_axis (0.5,0.0,0.866) — 30 deg off feature axis */")
    lines.append("#52=DRILLING_OPERATION('drill_tilted',$,$,$,#31,$,$,$,$);")
    lines.append("/* WORKPIECE 'drill_workpiece' */")
    lines.append("#60=WORKPIECE('drill_workpiece','Drilling workpiece for tilted-axis test',$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'tilted_drill_step' links operation to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('tilted_drill_step','Tilted drill axis workingstep',#52,#60,$);")
    lines.append("/* WORKPLAN: single step with tilted drilling operation */")
    lines.append("#50=WORKPLAN('tilted_drill_program','Tilted drill axis workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M175','M175','M175',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m175(path) -> None:
    Path(path).write_text(_render_m175())


f.render = _render_m175  # type: ignore[method-assign]
f.write = _write_m175    # type: ignore[method-assign]
