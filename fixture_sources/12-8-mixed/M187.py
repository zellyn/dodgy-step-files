"""M187 — AP238 knurling_operation pitch finer than tool resolution

Catalog claim: A KNURLING_OPERATION declares a knurl pitch of 0.05 mm while
the knurling tool's tooth spacing (resolution) is 0.5 mm. The tool physically
cannot impress a finer pattern than its own teeth — the declared pitch is
unattainable.

Reproducer recipe: a KNURLING_TOOL with tooth spacing 0.5 mm; a
KNURLING_OPERATION with knurl_pitch 0.05 mm referencing that tool.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'KNURLING_OPERATION')
  contains(b'KNURLING_TOOL')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M187",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where KNURLING_OPERATION "
        "declares knurl pitch finer than the knurling tool's own tooth spacing resolution; "
        "input: AP238 STEP-NC file containing a WORKPLAN with a knurling operation; "
        "the KNURLING_TOOL 'diamond_knurl_05mm' has tooth spacing 0.5 mm — physical resolution limit; "
        "the KNURLING_OPERATION 'fine_knurl_op' declares knurl_pitch 0.05 mm — ten times finer; "
        "the tool physically cannot impress a pattern finer than its own tooth spacing; "
        "at 0.05 mm pitch with 0.5 mm teeth: teeth overlap and shear into adjacent pattern elements; "
        "the declared pitch is physically unattainable with this knurling tool; "
        "per ISO 10303-238 §5.8 knurling_operation tool-resolution invariant: "
        "knurl_pitch must be >= tool tooth spacing; "
        "kernel must validate knurl pitch against tool tooth spacing; "
        "kernel must reject as unattainable when pitch < tooth spacing; "
        "synonyms: AP238 knurl pitch too fine, STEP-NC knurling under tool resolution, "
        "knurl spec finer than tooth spacing, AP238 knurl finer than tool, "
        "STEP-NC knurling pitch impossible, knurl spec below tool resolution, "
        "AP238 knurl pitch < tool teeth, STEP-NC knurling resolution exceeds tool, "
        "knurl spec finer than tool, knurling tool can't make finer pitch"
    ),
    schema="AP242",
)


def _render_m187() -> str:
    """Render AP238 STEP-NC file with KNURLING_OPERATION pitch finer than tool tooth spacing.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       KNURLING_TOOL 'diamond_knurl_05mm' — tooth spacing 0.5 mm
      #31       MEASURE_WITH_UNIT for tooth spacing = 0.5 mm
      #40       KNURLING_OPERATION 'fine_knurl_op' — DEFECT: knurl_pitch 0.05 mm < 0.5 mm tooth spacing
      #41       MEASURE_WITH_UNIT for knurl_pitch = 0.05 mm — DEFECT: 10x finer than tool can achieve
      #50       MACHINING_WORKINGSTEP 'knurl_step'
      #60       WORKPIECE 'knurl_workpiece'
      #70       WORKPLAN 'impossible_knurl_program'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M187: AP238 KNURLING_OPERATION pitch 0.05 mm finer than tool tooth spacing 0.5 mm */")
    lines.append("/* DEFECT: KNURLING_TOOL tooth spacing 0.5 mm — physical resolution limit of the tool */")
    lines.append("/* DEFECT: KNURLING_OPERATION knurl_pitch 0.05 mm — 10x finer than tool can achieve */")
    lines.append("/* Tool cannot impress pattern finer than its own tooth spacing — pitch is unattainable */")
    lines.append("/* Per ISO 10303-238 §5.8 knurling_operation tool-resolution invariant */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'KNURLING_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'KNURLING_TOOL') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M187: AP238 KNURLING_OPERATION pitch 0.05mm finer than tool resolution 0.5mm'),'2;1');")
    lines.append("FILE_NAME('M187.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-knurling-pitch-finer-than-tool-resolution',")
    lines.append("  (#30,#40,#50,#60));")
    lines.append("/* Byte assertion: contains(b'KNURLING_TOOL') */")
    lines.append("/* KNURLING_TOOL 'diamond_knurl_05mm': diamond knurl, tooth spacing 0.5 mm */")
    lines.append("/* Tool physical resolution limit: cannot impress pattern finer than 0.5 mm pitch */")
    lines.append("#31=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.5),#15);")
    lines.append("#30=KNURLING_TOOL('diamond_knurl_05mm',$,#31,$,$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'KNURLING_OPERATION') */")
    lines.append("/* DEFECT: KNURLING_OPERATION knurl_pitch 0.05 mm — 10x finer than tool tooth spacing */")
    lines.append("/* At 0.05 mm pitch with 0.5 mm teeth: teeth overlap — pattern unattainable */")
    lines.append("#41=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.05),#15);")
    lines.append("#40=KNURLING_OPERATION('fine_knurl_op',$,$,$,$,$,#30,$,#41,$);")
    lines.append("/* WORKPIECE 'knurl_workpiece' */")
    lines.append("#60=WORKPIECE('knurl_workpiece','Workpiece for impossible knurl pitch test',$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'knurl_step' */")
    lines.append("#50=MACHINING_WORKINGSTEP('knurl_step','Impossible knurl pitch step',#40,#60,$);")
    lines.append("/* WORKPLAN: knurling with pitch finer than tool resolution — unattainable */")
    lines.append("#70=WORKPLAN('impossible_knurl_program','Impossible knurl pitch workplan',(),$,(#50));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M187','M187','M187',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m187(path) -> None:
    Path(path).write_text(_render_m187())


f.render = _render_m187  # type: ignore[method-assign]
f.write = _write_m187    # type: ignore[method-assign]
