"""M096 — AP238 trajectory missing connecting curves between adjacent segments.

Catalog claim: A TRAJECTORY consists of two COMPOSITE_CURVE_SEGMENTs whose
endpoints don't coincide; segment A ends at (10,0,0) and segment B starts at
(20,0,0), with no connecting CURVE between them.

Reproducer recipe: COMPOSITE_CURVE with two segments (0,0,0)→(10,0,0) and
(20,0,0)→(30,0,0), with no third connecting segment, used as a TRAJECTORY
basis curve.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TRAJECTORY')
  contains(b'COMPOSITE_CURVE_SEGMENT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M096",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 TRAJECTORY with a gap between adjacent "
        "COMPOSITE_CURVE_SEGMENTs — segment A ends at (10,0,0) but segment B starts at (20,0,0); "
        "input: AP238 STEP-NC file where a TRAJECTORY basis curve is a COMPOSITE_CURVE "
        "composed of two LINE-based COMPOSITE_CURVE_SEGMENTs: "
        "segment A runs from (0,0,0) to (10,0,0) and segment B runs from (20,0,0) to (30,0,0); "
        "the 10 mm gap between (10,0,0) and (20,0,0) has no connecting CURVE or COMPOSITE_CURVE_SEGMENT; "
        "per ISO 10303-238 §6.2 trajectory G0/G1 continuity rules adjacent segments in a "
        "TRAJECTORY COMPOSITE_CURVE must share endpoints — the end point of segment N must "
        "coincide with the start point of segment N+1; "
        "the CAM post-processor intended a rapid-traverse retract/reposition between the two "
        "cutting passes but emitted no explicit connector segment for the traversal; "
        "a CNC controller either fails to plan motion through the gap (emergency stop) or "
        "executes a feed-rate move through the workpiece material (crashing the tool); "
        "kernel must validate adjacent-segment endpoint continuity in trajectory curves; "
        "insert a rapid-traverse connector and warn, or reject as discontinuous; "
        "synonyms: AP238 toolpath has gap, STEP-NC missing rapid move, trajectory segments "
        "don't connect, AP238 trajectory gap, missing rapid retract, trajectory segments "
        "don't connect, STEP-NC composite curve not chained, toolpath has unconnected segments"
    ),
    schema="AP242",
)


def _render_m096() -> str:
    """Render AP238 file with TRAJECTORY COMPOSITE_CURVE having a gap between segments.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20-#22   Points for segment A: (0,0,0), (10,0,0) and direction
      #23       LINE for segment A: (0,0,0)→(10,0,0)
      #24       COMPOSITE_CURVE_SEGMENT A
      #30-#32   Points for segment B: (20,0,0), (30,0,0) and direction
      #33       LINE for segment B: (20,0,0)→(30,0,0)
      #34       COMPOSITE_CURVE_SEGMENT B
      #40       COMPOSITE_CURVE with (segment A, segment B) — DEFECT: gap at (10,0,0)→(20,0,0)
      #50       TRAJECTORY referencing the gapped COMPOSITE_CURVE
      #60       MACHINING_TOOL 'drill_a'
      #70       MACHINING_OPERATION referencing the trajectory
      #80       MACHINING_WORKINGSTEP wrapping the operation
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M096: AP238 trajectory missing connecting curve between adjacent segments */")
    lines.append("/* DEFECT: COMPOSITE_CURVE segment A ends at (10,0,0); segment B starts at (20,0,0) */")
    lines.append("/* 10 mm gap has no connector — violates ISO 10303-238 §6.2 G0 continuity */")
    lines.append("/* Controller either E-stops at gap or drives tool through workpiece material */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TRAJECTORY') */")
    lines.append("/* Byte assertion: contains(b'COMPOSITE_CURVE_SEGMENT') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M096: AP238 TRAJECTORY with gap between composite curve segments'),'2;1');")
    lines.append("FILE_NAME('M096.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Segment A geometry: (0,0,0) → (10,0,0) */")
    lines.append("#20=CARTESIAN_POINT('seg_a_start',(0.,0.,0.));")
    lines.append("#21=CARTESIAN_POINT('seg_a_end',(10.,0.,0.));")
    lines.append("#22=DIRECTION('seg_a_dir',(1.,0.,0.));")
    lines.append("#23=LINE('seg_a_line',#20,VECTOR('seg_a_vec',#22,10.));")
    lines.append("/* Byte assertion: contains(b'COMPOSITE_CURVE_SEGMENT') */")
    lines.append("/* Segment A: cutting pass from (0,0,0) to (10,0,0) */")
    lines.append("#24=COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#23);")
    lines.append("/* Segment B geometry: (20,0,0) → (30,0,0) */")
    lines.append("/* DEFECT: starts at (20,0,0) — 10 mm gap from segment A endpoint (10,0,0) */")
    lines.append("#30=CARTESIAN_POINT('seg_b_start',(20.,0.,0.));")
    lines.append("#31=CARTESIAN_POINT('seg_b_end',(30.,0.,0.));")
    lines.append("#32=DIRECTION('seg_b_dir',(1.,0.,0.));")
    lines.append("#33=LINE('seg_b_line',#30,VECTOR('seg_b_vec',#32,10.));")
    lines.append("/* Segment B: cutting pass from (20,0,0) to (30,0,0) */")
    lines.append("/* Endpoint of #24 is (10,0,0); start of #34 is (20,0,0) — 10 mm gap — DEFECT */")
    lines.append("#34=COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#33);")
    lines.append("/* DEFECT: COMPOSITE_CURVE with only (#24, #34) — no connector between them */")
    lines.append("/* Adjacent segment endpoints: #24 ends at (10,0,0), #34 starts at (20,0,0) */")
    lines.append("/* Correct: add a third segment (10,0,0)→(20,0,0) for rapid traverse */")
    lines.append("#40=COMPOSITE_CURVE('gapped_toolpath',(#24,#34),.F.);")
    lines.append("/* Byte assertion: contains(b'TRAJECTORY') */")
    lines.append("/* TRAJECTORY uses the gapped COMPOSITE_CURVE as its basis curve */")
    lines.append("#50=TRAJECTORY('toolpath_a',#40,$,$,$,$,$);")
    lines.append("/* Machining setup */")
    lines.append("#60=MACHINING_TOOL('drill_a',$,$,$);")
    lines.append("#70=MACHINING_OPERATION('cut_path',#60,$,$,$,$,$,$,$,$,#50);")
    lines.append("#80=MACHINING_WORKINGSTEP('cut_step',$,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-trajectory-missing-connecting-curve-between-segments',")
    lines.append("  (#23,#33,#40,#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M096','M096','M096',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m096(path) -> None:
    Path(path).write_text(_render_m096())


f.render = _render_m096  # type: ignore[method-assign]
f.write = _write_m096    # type: ignore[method-assign]
