"""M167 — AP238 turning operation cut depth exceeds workpiece radius

Catalog claim: A TURNING_OPERATION declares a radial depth-of-cut
(30.0 mm) that exceeds the stock cylinder's radius (12.5 mm on a
25 mm bar). The single-pass move passes through the spindle axis and
out the far side, parting the workpiece with no support.

Reproducer recipe: TURNING_OPERATION with a depth-of-cut
MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(30.0), mm_unit) on a
workpiece whose stock-cylinder radius is 12.5 mm.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TURNING_OPERATION(')
  contains(b'30.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M167",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where TURNING_OPERATION declares "
        "radial depth-of-cut 30.0 mm exceeding the workpiece stock cylinder radius 12.5 mm; "
        "input: AP238 STEP-NC file containing a WORKPLAN for turning a 25mm diameter bar stock "
        "(radius 12.5 mm); the workpiece is defined as a cylinder with radius 12.5 mm; "
        "the TURNING_OPERATION 'rough_turn_pass' declares depth_of_cut via "
        "MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(30.0), mm_unit) — 30.0mm radial cut; "
        "30.0mm depth on a 12.5mm radius workpiece passes through the spindle axis "
        "and exits the opposite side of the bar by 17.5 mm; "
        "this single pass would part the workpiece mid-cut with no tailstock support; "
        "the controller either crashes the tool into the chuck jaw or severs the bar; "
        "the STEP-NC programmer specified tool-travel depth instead of radial material depth; "
        "per ISO 10303-238 §5.8 depth-of-cut must not exceed stock radius; "
        "kernel must validate depth-of-cut against stock geometry and reject as malformed "
        "or warn that the operation severs the workpiece; "
        "synonyms: AP238 turning cuts through stock, lathe depth exceeds radius, "
        "STEP-NC parting cut unintended, turning depth-of-cut > workpiece radius, "
        "AP238 turning cut-through, STEP-NC depth bigger than radius, lathe op slices bar in half"
    ),
    schema="AP242",
)


def _render_m167() -> str:
    """Render AP238 STEP-NC file with TURNING_OPERATION depth 30mm > workpiece radius 12.5mm.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN 'turn_bar_program' — top-level STEP-NC program
      #51       MACHINING_WORKINGSTEP 'rough_turn_step'
      #52       TURNING_OPERATION 'rough_turn_pass' — DEFECT: depth_of_cut = 30.0mm
      #53       MEASURE_WITH_UNIT for depth_of_cut = 30.0mm
      #60       WORKPIECE 'bar_stock_25mm' — cylinder radius = 12.5mm
      #61       MEASURE_WITH_UNIT for workpiece radius = 12.5mm
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M167: AP238 turning operation cut depth exceeds workpiece radius */")
    lines.append("/* DEFECT: TURNING_OPERATION depth_of_cut=30.0mm; workpiece radius=12.5mm */")
    lines.append("/* The cut passes through the spindle axis and 17.5mm beyond — parts the bar */")
    lines.append("/* Programmer specified tool-travel depth instead of radial material removal */")
    lines.append("/* Per ISO 10303-238 §5.8 depth-of-cut must not exceed stock radius */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TURNING_OPERATION(') */")
    lines.append("/* Byte assertion: contains(b'30.0') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M167: AP238 turning depth 30.0mm exceeds bar radius 12.5mm'),'2;1');")
    lines.append("FILE_NAME('M167.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-turning-depth-exceeds-workpiece-radius-30mm-vs-12-5mm',")
    lines.append("  (#52,#60));")
    lines.append("/* WORKPLAN 'turn_bar_program' — AP238 top-level NC program */")
    lines.append("#50=WORKPLAN('turn_bar_program','Turn 25mm bar stock workplan',(),$,(#51));")
    lines.append("/* MACHINING_WORKINGSTEP links the workpiece to the operation */")
    lines.append("#51=MACHINING_WORKINGSTEP('rough_turn_step','Rough turning workingstep',#52,#60,$);")
    lines.append("/* Byte assertion: contains(b'TURNING_OPERATION(') */")
    lines.append("/* DEFECT: TURNING_OPERATION depth_of_cut = 30.0mm; workpiece radius = 12.5mm */")
    lines.append("/* Byte assertion: contains(b'30.0') */")
    lines.append("/* depth_of_cut = MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(30.0), mm) */")
    lines.append("#53=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(30.0),#15);")
    lines.append("/* TURNING_OPERATION: ($=tool,$=spindle speed,$=feed,$=cutting_depth,depth_of_cut,retract) */")
    lines.append("#52=TURNING_OPERATION('rough_turn_pass',$,$,$,#53,$);")
    lines.append("/* WORKPIECE 'bar_stock_25mm': 25mm diameter bar (radius 12.5mm) */")
    lines.append("/* The depth-of-cut 30.0mm > radius 12.5mm — the defect */")
    lines.append("#61=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(12.5),#15);")
    lines.append("#60=WORKPIECE('bar_stock_25mm','25mm diameter bar stock 250mm length',$,#61,$,$,$);")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M167','M167','M167',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m167(path) -> None:
    Path(path).write_text(_render_m167())


f.render = _render_m167  # type: ignore[method-assign]
f.write = _write_m167    # type: ignore[method-assign]
