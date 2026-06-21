"""M176 — AP238 boring tool diameter exceeds start-hole diameter

Catalog claim: A BORING_OPERATION declares a boring-bar tool diameter
(15 mm) larger than the pre-drilled start-hole diameter (10 mm). The
boring bar physically cannot enter the hole — the operation is
impossible. The controller either crashes the tool against the workpiece
face or refuses to plunge.

Reproducer recipe: a ROUND_HOLE of diameter 10 mm; a BORING_TOOL of
diameter 15 mm referenced by a BORING_OPERATION targeting that hole.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'BORING_OPERATION')
  contains(b'BORING_TOOL')
  contains(b'15.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M176",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where BORING_OPERATION references a "
        "BORING_TOOL with diameter 15.0 mm targeting a ROUND_HOLE of diameter 10.0 mm; "
        "input: AP238 STEP-NC file containing a WORKPLAN for a boring operation; "
        "the ROUND_HOLE 'start_hole' has diameter 10.0 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(10.0), mm); "
        "the BORING_TOOL 'boring_bar_15mm' has cutter_diameter 15.0 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(15.0), mm); "
        "the BORING_OPERATION 'bore_oversized' references boring_bar_15mm targeting start_hole; "
        "boring bar diameter (15.0 mm) exceeds start-hole diameter (10.0 mm): "
        "the boring bar physically cannot enter the pre-drilled hole; "
        "the controller either crashes the boring bar against the workpiece face "
        "or refuses to plunge the oversized tool; "
        "per ISO 10303-238 §5.8 boring tool diameter must be less than start-hole diameter; "
        "kernel must validate boring tool diameter against start-hole diameter and reject; "
        "synonyms: AP238 boring tool larger than hole, STEP-NC bore-bar won't fit, "
        "boring insertion impossible, tool diameter exceeds start-hole, "
        "AP238 boring bar bigger than hole, STEP-NC boring insertion impossible, "
        "boring bar exceeds start-hole dia, AP238 bore tool too big for hole"
    ),
    schema="AP242",
)


def _render_m176() -> str:
    """Render AP238 STEP-NC file with BORING_TOOL diameter 15mm > ROUND_HOLE diameter 10mm.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       CARTESIAN_POINT origin of hole locator
      #31       DIRECTION axis for hole locator (0,0,1)
      #32       AXIS2_PLACEMENT_3D for hole locator
      #40       ROUND_HOLE 'start_hole' — diameter 10.0 mm
      #41       MEASURE_WITH_UNIT for hole diameter = 10.0 mm
      #50       WORKPLAN 'boring_oversize_program' — AP238 top-level NC program
      #51       MACHINING_WORKINGSTEP 'bore_step'
      #52       BORING_OPERATION 'bore_oversized' — DEFECT: tool too large for hole
      #53       BORING_TOOL 'boring_bar_15mm' — diameter 15.0 mm
      #54       MEASURE_WITH_UNIT for tool diameter = 15.0 mm — DEFECT: 15mm > 10mm hole
      #60       WORKPIECE 'bore_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M176: AP238 boring tool diameter exceeds start-hole diameter */")
    lines.append("/* DEFECT: BORING_TOOL diameter 15.0 mm > ROUND_HOLE diameter 10.0 mm */")
    lines.append("/* Boring bar physically cannot enter the pre-drilled start hole */")
    lines.append("/* Controller crashes tool against workpiece face or refuses to plunge */")
    lines.append("/* Per ISO 10303-238 §5.8 boring tool diameter must be less than start-hole diameter */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'BORING_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'BORING_TOOL') */")
    lines.append("/* Byte assertion: contains(b'15.0') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M176: AP238 boring_tool diameter 15mm exceeds start-hole diameter 10mm'),'2;1');")
    lines.append("FILE_NAME('M176.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Start hole locator geometry */")
    lines.append("#30=CARTESIAN_POINT('hole_origin',(50.0,50.0,10.0));")
    lines.append("#31=DIRECTION('hole_axis',(0.0,0.0,1.0));")
    lines.append("#32=AXIS2_PLACEMENT_3D('hole_locator',#30,#31,$);")
    lines.append("/* ROUND_HOLE 'start_hole': diameter 10.0 mm (smaller than boring tool) */")
    lines.append("#41=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(10.0),#15);")
    lines.append("#40=ROUND_HOLE('start_hole',$,#41,#32,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-boring-tool-diameter-exceeds-start-hole-diameter',")
    lines.append("  (#40,#52,#60));")
    lines.append("/* Byte assertion: contains(b'BORING_TOOL') */")
    lines.append("/* DEFECT: BORING_TOOL 'boring_bar_15mm' with diameter 15.0 mm — exceeds 10.0 mm hole */")
    lines.append("#54=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(15.0),#15);")
    lines.append("#53=BORING_TOOL('boring_bar_15mm',$,#54,$,$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'BORING_OPERATION') */")
    lines.append("/* DEFECT: BORING_OPERATION references oversized tool: bar cannot enter start hole */")
    lines.append("#52=BORING_OPERATION('bore_oversized',$,$,$,$,$,#53,$,$,$,$,$,$);")
    lines.append("/* WORKPIECE 'bore_workpiece' */")
    lines.append("#60=WORKPIECE('bore_workpiece','Boring workpiece for oversized-tool test',$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'bore_step' links boring op to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('bore_step','Oversized boring workingstep',#52,#60,$);")
    lines.append("/* WORKPLAN: single boring step with oversized tool */")
    lines.append("#50=WORKPLAN('boring_oversize_program','Boring oversized tool workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M176','M176','M176',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m176(path) -> None:
    Path(path).write_text(_render_m176())


f.render = _render_m176  # type: ignore[method-assign]
f.write = _write_m176    # type: ignore[method-assign]
