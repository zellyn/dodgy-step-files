"""M169 — AP238 turning_roughing stepover exceeds tool nose radius

Catalog claim: A TURNING_ROUGHING op declares a radial stepover
(4.0 mm) larger than the cutting tool's nose radius (0.8 mm). Each
successive pass leaves an unsupported scallop the nose can't reach,
producing a stair-stepped surface.

Reproducer recipe: a TURNING_MACHINING_TOOL with nose_radius = 0.8 mm;
a TURNING_ROUGHING op with stepover = 4.0 mm.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TURNING_ROUGHING')
  contains(b'TURNING_MACHINING_TOOL')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M169",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where TURNING_ROUGHING declares "
        "radial stepover 4.0 mm while TURNING_MACHINING_TOOL nose_radius is 0.8 mm; "
        "input: AP238 STEP-NC file containing a WORKPLAN for rough-turning a cylindrical part; "
        "the TURNING_MACHINING_TOOL 'turn_rough_tool' has nose_radius = 0.8 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.8), mm); "
        "the TURNING_ROUGHING 'roughing_pass' declares stepover = 4.0 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(4.0), mm); "
        "with stepover 4.0 mm and nose radius 0.8 mm each pass leaves a 3.2 mm scallop "
        "the nose cannot reach — the surface shows visible stair-steps between passes; "
        "the next pass either gouges into the scallop wall or leaves uncut material; "
        "the STEP-NC programmer used tool-diameter-based stepover instead of nose-radius rule; "
        "per ISO 10303-238 §5.8 turning stepover must not exceed nose radius to avoid scallops; "
        "kernel must validate stepover against tool nose radius and warn or reject; "
        "synonyms: AP238 stepover gouge, STEP-NC turning rough pass scallops, "
        "stepover larger than nose radius, lathe stair-step finish, "
        "AP238 turning stepover > nose r, STEP-NC roughing scallops"
    ),
    schema="AP242",
)


def _render_m169() -> str:
    """Render AP238 STEP-NC file with TURNING_ROUGHING stepover 4.0mm > nose radius 0.8mm.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN 'rough_turn_program' — top-level STEP-NC program
      #51       MACHINING_WORKINGSTEP 'rough_turn_step'
      #52       TURNING_ROUGHING 'roughing_pass' — DEFECT: stepover = 4.0mm
      #53       MEASURE_WITH_UNIT for stepover = 4.0mm
      #54       TURNING_MACHINING_TOOL 'turn_rough_tool' — nose_radius = 0.8mm
      #55       MEASURE_WITH_UNIT for nose_radius = 0.8mm
      #60       WORKPIECE 'cyl_rough_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M169: AP238 turning_roughing stepover exceeds tool nose radius */")
    lines.append("/* DEFECT: TURNING_ROUGHING stepover=4.0mm; TURNING_MACHINING_TOOL nose_radius=0.8mm */")
    lines.append("/* Each pass leaves 3.2mm scallop nose cannot reach — stair-step surface */")
    lines.append("/* STEP-NC programmer used tool-diameter-based stepover instead of nose-radius rule */")
    lines.append("/* Per ISO 10303-238 §5.8 turning stepover must not exceed nose radius */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TURNING_ROUGHING') */")
    lines.append("/* Byte assertion: contains(b'TURNING_MACHINING_TOOL') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M169: AP238 turning_roughing stepover 4.0mm exceeds nose radius 0.8mm'),'2;1');")
    lines.append("FILE_NAME('M169.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-turning-roughing-stepover-exceeds-tool-nose-radius',")
    lines.append("  (#52,#54,#60));")
    lines.append("/* WORKPLAN 'rough_turn_program' — AP238 top-level NC program */")
    lines.append("#50=WORKPLAN('rough_turn_program','Rough turning workplan',(),$,(#51));")
    lines.append("/* MACHINING_WORKINGSTEP links workpiece to roughing operation */")
    lines.append("#51=MACHINING_WORKINGSTEP('rough_turn_step','Rough turning workingstep',#52,#60,$);")
    lines.append("/* Byte assertion: contains(b'TURNING_MACHINING_TOOL') */")
    lines.append("/* TURNING_MACHINING_TOOL 'turn_rough_tool': nose_radius = 0.8mm */")
    lines.append("#55=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.8),#15);")
    lines.append("#54=TURNING_MACHINING_TOOL('turn_rough_tool',$,#55,$,$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'TURNING_ROUGHING') */")
    lines.append("/* DEFECT: TURNING_ROUGHING stepover = 4.0mm > nose_radius 0.8mm */")
    lines.append("/* stepover = MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(4.0), mm) */")
    lines.append("#53=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(4.0),#15);")
    lines.append("#52=TURNING_ROUGHING('roughing_pass',$,$,$,#53,$,#54);")
    lines.append("/* WORKPIECE 'cyl_rough_workpiece' */")
    lines.append("#60=WORKPIECE('cyl_rough_workpiece','Cylindrical workpiece for rough turning',$,$,$,$,$);")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M169','M169','M169',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m169(path) -> None:
    Path(path).write_text(_render_m169())


f.render = _render_m169  # type: ignore[method-assign]
f.write = _write_m169    # type: ignore[method-assign]
