"""M171 — AP238 thread_turning pitch differs from thread-spec pitch

Catalog claim: A THREAD_TURNING op declares a lead/pitch of 1.5 mm
while the referenced thread feature's spec is M10x1.0 (pitch 1.0 mm).
The controller cuts a thread whose pitch doesn't match the design
intent; the mating fastener won't thread in.

Reproducer recipe: a THREAD feature with spec pitch 1.0 mm and a
THREAD_TURNING op whose declared pitch is 1.5 mm.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'THREAD_TURNING')
  contains(b'THREAD(')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M171",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where THREAD_TURNING declares "
        "pitch 1.5 mm but the referenced THREAD feature spec is M10x1.0 (pitch 1.0 mm); "
        "input: AP238 STEP-NC file containing a WORKPLAN for cutting an M10x1.0 thread; "
        "the THREAD feature 'M10x1p0_thread' carries thread_spec pitch = 1.0 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(1.0), mm); "
        "the THREAD_TURNING op 'thread_turn_pass' declares op pitch = 1.5 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(1.5), mm); "
        "the op pitch 1.5 mm does not match the feature spec pitch 1.0 mm; "
        "the controller cuts a thread with 1.5mm lead (M10x1.5) instead of the specified M10x1.0; "
        "the mating M10x1.0 fastener will not thread in — the part must be scrapped; "
        "the STEP-NC programmer used the coarse-thread pitch template instead of fine-thread; "
        "per ISO 10303-238 §5.8 thread_turning pitch must match the referenced thread feature pitch; "
        "kernel must validate that thread-turning pitch matches thread feature spec and warn or reject; "
        "synonyms: AP238 thread pitch mismatch, STEP-NC thread-turn wrong lead, "
        "M10x1 cut as M10x1.5, AP238 thread pitch disagrees with spec, "
        "STEP-NC thread-turn lead wrong, thread feature vs op pitch mismatch"
    ),
    schema="AP242",
)


def _render_m171() -> str:
    """Render AP238 STEP-NC file with THREAD_TURNING pitch 1.5mm mismatching THREAD spec 1.0mm.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN 'thread_turn_program' — top-level STEP-NC program
      #51       MACHINING_WORKINGSTEP 'thread_turn_step'
      #52       THREAD_TURNING 'thread_turn_pass' — DEFECT: pitch = 1.5mm
      #53       MEASURE_WITH_UNIT for op pitch = 1.5mm
      #60       THREAD 'M10x1p0_thread' — feature spec pitch = 1.0mm
      #61       MEASURE_WITH_UNIT for feature pitch = 1.0mm
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M171: AP238 thread_turning pitch differs from thread-spec pitch */")
    lines.append("/* DEFECT: THREAD_TURNING pitch=1.5mm; THREAD feature spec pitch=1.0mm (M10x1.0) */")
    lines.append("/* Controller cuts M10x1.5 thread; M10x1.0 mating fastener won't engage */")
    lines.append("/* STEP-NC programmer used coarse-thread template instead of fine-thread */")
    lines.append("/* Per ISO 10303-238 §5.8 thread_turning pitch must match feature spec */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'THREAD_TURNING') */")
    lines.append("/* Byte assertion: contains(b'THREAD(') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M171: AP238 thread_turning pitch 1.5mm vs thread-spec M10x1.0'),'2;1');")
    lines.append("FILE_NAME('M171.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-thread-turning-pitch-1p5mm-vs-thread-spec-1p0mm',")
    lines.append("  (#52,#60));")
    lines.append("/* WORKPLAN 'thread_turn_program' — AP238 top-level NC program */")
    lines.append("#50=WORKPLAN('thread_turn_program','M10x1.0 thread turning workplan',(),$,(#51));")
    lines.append("/* MACHINING_WORKINGSTEP links workpiece to thread-turning operation */")
    lines.append("#51=MACHINING_WORKINGSTEP('thread_turn_step','Thread turning workingstep',#52,#60,$);")
    lines.append("/* Byte assertion: contains(b'THREAD(') */")
    lines.append("/* THREAD 'M10x1p0_thread': M10x1.0 feature — spec pitch = 1.0mm */")
    lines.append("#61=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(1.0),#15);")
    lines.append("#60=THREAD('M10x1p0_thread','M10x1.0 thread feature',$,#61,$);")
    lines.append("/* Byte assertion: contains(b'THREAD_TURNING') */")
    lines.append("/* DEFECT: THREAD_TURNING pitch = 1.5mm, but THREAD feature spec is 1.0mm */")
    lines.append("#53=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(1.5),#15);")
    lines.append("#52=THREAD_TURNING('thread_turn_pass',$,$,$,#53,#60,$);")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M171','M171','M171',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m171(path) -> None:
    Path(path).write_text(_render_m171())


f.render = _render_m171  # type: ignore[method-assign]
f.write = _write_m171    # type: ignore[method-assign]
