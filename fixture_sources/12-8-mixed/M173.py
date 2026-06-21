"""M173 — AP238 milling_toolpath consecutive points spaced beyond tool diameter

Catalog claim: A MILLING_TOOLPATH lists consecutive points spaced
12 mm apart while the tool diameter is 6 mm. Linear interpolation
between samples leaves stock between passes; the toolpath has no
implicit guarantee of contiguous engagement.

Reproducer recipe: a MILLING_CUTTING_TOOL with diameter 6 mm; a
MILLING_TOOLPATH whose underlying POLYLINE has points 12 mm apart.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MILLING_TOOLPATH')
  contains(b'MILLING_CUTTING_TOOL')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M173",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where MILLING_TOOLPATH consecutive points "
        "are spaced 12.0 mm apart while MILLING_CUTTING_TOOL diameter is 6.0 mm; "
        "input: AP238 STEP-NC file containing a WORKPLAN for a milling operation; "
        "the MILLING_CUTTING_TOOL 'mill_6mm' has cutter_diameter = 6.0 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(6.0), mm); "
        "the MILLING_TOOLPATH 'sparse_mill_path' is backed by a POLYLINE with four points "
        "at (0,0,0), (12,0,0), (24,0,0), (36,0,0) — spaced 12.0 mm apart; "
        "with tool diameter 6.0 mm and point spacing 12.0 mm the ratio is 2.0 (> 1.0); "
        "linear interpolation between adjacent samples leaves 6.0 mm of uncut stock "
        "in the gap between the tool engagement zones; "
        "controllers either over-feed gouging the stock at sample points "
        "or leave uncut islands between consecutive samples; "
        "the STEP-NC programmer used a coarse sample density intended for rapid-traverse; "
        "per ISO 10303-238 §6.2 milling toolpath sample spacing must not exceed tool diameter; "
        "kernel must validate sample-density against tool diameter and warn or refine; "
        "synonyms: AP238 toolpath sample gap > tool diameter, STEP-NC sparse milling samples, "
        "milling path discontinuity, toolpath leaves uncut between points, "
        "AP238 milling sample distance > tool dia, STEP-NC toolpath skips"
    ),
    schema="AP242",
)


def _render_m173() -> str:
    """Render AP238 STEP-NC file with MILLING_TOOLPATH point spacing 12mm > tool diameter 6mm.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       CARTESIAN_POINT (0,0,0) — toolpath sample 0
      #31       CARTESIAN_POINT (12,0,0) — toolpath sample 1 (+12mm, > tool diameter)
      #32       CARTESIAN_POINT (24,0,0) — toolpath sample 2
      #33       CARTESIAN_POINT (36,0,0) — toolpath sample 3
      #34       POLYLINE backing the toolpath — points spaced 12mm apart
      #50       WORKPLAN 'sparse_mill_program' — top-level STEP-NC program
      #51       MACHINING_WORKINGSTEP 'sparse_mill_step'
      #52       MILLING_TOOLPATH 'sparse_mill_path' — DEFECT: sample spacing > tool diameter
      #54       MILLING_CUTTING_TOOL 'mill_6mm' — diameter = 6.0mm
      #55       MEASURE_WITH_UNIT for tool diameter = 6.0mm
      #60       WORKPIECE 'mill_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M173: AP238 milling_toolpath consecutive points spaced beyond tool diameter */")
    lines.append("/* DEFECT: MILLING_TOOLPATH points 12.0mm apart; MILLING_CUTTING_TOOL diameter 6.0mm */")
    lines.append("/* Ratio 2.0 — linear interpolation leaves 6mm uncut stock between samples */")
    lines.append("/* Controllers over-feed (gouge) or leave uncut islands between consecutive samples */")
    lines.append("/* Per ISO 10303-238 §6.2 milling toolpath sample spacing must not exceed tool diameter */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MILLING_TOOLPATH') */")
    lines.append("/* Byte assertion: contains(b'MILLING_CUTTING_TOOL') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M173: AP238 milling_toolpath sample spacing 12mm exceeds tool diameter 6mm'),'2;1');")
    lines.append("FILE_NAME('M173.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* POLYLINE backing the sparse toolpath — four points 12mm apart */")
    lines.append("/* Point spacing 12.0mm >> tool diameter 6.0mm: leaves uncut stock between samples */")
    lines.append("#30=CARTESIAN_POINT('sample_0',(0.0,0.0,0.0));")
    lines.append("#31=CARTESIAN_POINT('sample_1',(12.0,0.0,0.0));")
    lines.append("#32=CARTESIAN_POINT('sample_2',(24.0,0.0,0.0));")
    lines.append("#33=CARTESIAN_POINT('sample_3',(36.0,0.0,0.0));")
    lines.append("#34=POLYLINE('sparse_path_polyline',(#30,#31,#32,#33));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-milling-toolpath-sample-spacing-12mm-exceeds-tool-dia-6mm',")
    lines.append("  (#34,#52,#54,#60));")
    lines.append("/* WORKPLAN 'sparse_mill_program' — AP238 top-level NC program */")
    lines.append("#50=WORKPLAN('sparse_mill_program','Sparse milling toolpath workplan',(),$,(#51));")
    lines.append("/* MACHINING_WORKINGSTEP links workpiece to milling operation */")
    lines.append("#51=MACHINING_WORKINGSTEP('sparse_mill_step','Sparse milling workingstep',#52,#60,$);")
    lines.append("/* Byte assertion: contains(b'MILLING_CUTTING_TOOL') */")
    lines.append("/* MILLING_CUTTING_TOOL 'mill_6mm': cutter diameter = 6.0mm */")
    lines.append("#55=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(6.0),#15);")
    lines.append("#54=MILLING_CUTTING_TOOL('mill_6mm',$,#55,$,$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'MILLING_TOOLPATH') */")
    lines.append("/* DEFECT: MILLING_TOOLPATH backed by POLYLINE with 12mm spacing > 6mm diameter */")
    lines.append("#52=MILLING_TOOLPATH('sparse_mill_path',#34,$,#54,$);")
    lines.append("/* WORKPIECE 'mill_workpiece' */")
    lines.append("#60=WORKPIECE('mill_workpiece','Milling workpiece for sparse toolpath test',$,$,$,$,$);")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M173','M173','M173',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m173(path) -> None:
    Path(path).write_text(_render_m173())


f.render = _render_m173  # type: ignore[method-assign]
f.write = _write_m173    # type: ignore[method-assign]
