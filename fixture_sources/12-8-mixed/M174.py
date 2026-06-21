"""M174 — AP238 milling_feed_rate varies along path with no F-code transition

Catalog claim: A MILLING_OPERATION references two MILLING_FEED_RATE
entities with different magnitudes (300 mm/min and 1200 mm/min) on
consecutive segments, but no F-code transition / acceleration profile
is declared. Controllers either snap discontinuously or silently use
one rate for the entire path.

Reproducer recipe: two MILLING_OPERATION entries in workplan order,
the first with feed_rate 300 mm/min and the second with feed_rate
1200 mm/min, with no transition operation between them.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MILLING_FEED_RATE')
  contains(b'1200.0')
  contains(b'300.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M174",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where two consecutive MILLING_OPERATION "
        "entries reference MILLING_FEED_RATE entities with abruptly different magnitudes "
        "(300.0 mm/min and 1200.0 mm/min) with no F-code transition or acceleration profile; "
        "input: AP238 STEP-NC file containing a WORKPLAN for a milling operation; "
        "the first MACHINING_WORKINGSTEP 'mill_step_slow' references a MILLING_OPERATION "
        "whose feed_rate is 300.0 mm/min via MILLING_FEED_RATE entity; "
        "the second MACHINING_WORKINGSTEP 'mill_step_fast' references a MILLING_OPERATION "
        "whose feed_rate is 1200.0 mm/min via a second MILLING_FEED_RATE entity; "
        "the two workingsteps are adjacent in the WORKPLAN without any transition operation; "
        "the feed rate jumps from 300.0 to 1200.0 mm/min (4x) with no ramp declared; "
        "controllers either snap discontinuously over-shooting the corner "
        "or silently use one rate for the entire path; "
        "per ISO 10303-238 §5.8 feedrate changes require an explicit transition or ramp; "
        "kernel must validate that feedrate changes carry an explicit transition; "
        "synonyms: AP238 feedrate jump no F-code, STEP-NC milling no acceleration profile, "
        "feed-rate change without transition, milling F-word missing between segments, "
        "AP238 feedrate step change, STEP-NC missing acceleration profile, "
        "milling feedrate snap from 300 to 1200"
    ),
    schema="AP242",
)


def _render_m174() -> str:
    """Render AP238 STEP-NC file with feedrate jump 300->1200 mm/min with no transition.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm/min velocity unit for MILLING_FEED_RATE
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN 'feedrate_jump_program' — AP238 top-level NC program
      #51       MACHINING_WORKINGSTEP 'mill_step_slow' — feed_rate 300 mm/min
      #52       MILLING_OPERATION 'mill_op_slow' — first operation
      #53       MILLING_FEED_RATE for 300.0 mm/min — DEFECT: no transition before next segment
      #61       MACHINING_WORKINGSTEP 'mill_step_fast' — feed_rate 1200 mm/min
      #62       MILLING_OPERATION 'mill_op_fast' — second operation (abrupt jump)
      #63       MILLING_FEED_RATE for 1200.0 mm/min — DEFECT: arrived with no ramp from 300
      #70       WORKPIECE 'mill_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M174: AP238 milling_feed_rate varies along path with no F-code transition */")
    lines.append("/* DEFECT: MILLING_FEED_RATE jumps from 300.0 to 1200.0 mm/min with no ramp declared */")
    lines.append("/* Adjacent MILLING_OPERATION entries in WORKPLAN; no transition operation between them */")
    lines.append("/* Controllers snap discontinuously or silently apply one rate for entire path */")
    lines.append("/* Per ISO 10303-238 §5.8 feedrate changes require an explicit transition */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MILLING_FEED_RATE') */")
    lines.append("/* Byte assertion: contains(b'1200.0') */")
    lines.append("/* Byte assertion: contains(b'300.0') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M174: AP238 milling_feed_rate jump 300 to 1200 mm/min no transition'),'2;1');")
    lines.append("FILE_NAME('M174.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* mm/min velocity unit for MILLING_FEED_RATE magnitude */")
    lines.append("#15=SI_UNIT(.MILLI.,.METRE.);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-milling-feed-rate-jump-no-transition',")
    lines.append("  (#52,#62,#70));")
    lines.append("/* Byte assertion: contains(b'MILLING_FEED_RATE') */")
    lines.append("/* DEFECT: MILLING_FEED_RATE 300.0 mm/min — first segment, no transition out */")
    lines.append("#53=MILLING_FEED_RATE(300.0,$,$,$,$);")
    lines.append("/* MILLING_OPERATION 'mill_op_slow': feed at 300.0 mm/min */")
    lines.append("#52=MILLING_OPERATION('mill_op_slow',$,(#53),$,$,$,$,$,$,$,$,$,$);")
    lines.append("/* DEFECT: MILLING_FEED_RATE 1200.0 mm/min — second segment, no ramp from 300.0 */")
    lines.append("#63=MILLING_FEED_RATE(1200.0,$,$,$,$);")
    lines.append("/* MILLING_OPERATION 'mill_op_fast': feed at 1200.0 mm/min (4x jump) */")
    lines.append("#62=MILLING_OPERATION('mill_op_fast',$,(#63),$,$,$,$,$,$,$,$,$,$);")
    lines.append("/* WORKPIECE 'mill_workpiece' */")
    lines.append("#70=WORKPIECE('mill_workpiece','Milling workpiece for feedrate jump test',$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'mill_step_slow' — first step at 300.0 mm/min */")
    lines.append("#51=MACHINING_WORKINGSTEP('mill_step_slow','Slow feedrate milling step',#52,#70,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'mill_step_fast' — adjacent, jumps to 1200.0 mm/min */")
    lines.append("#61=MACHINING_WORKINGSTEP('mill_step_fast','Fast feedrate milling step',#62,#70,$);")
    lines.append("/* WORKPLAN: two steps adjacent with no transition operation between them */")
    lines.append("#50=WORKPLAN('feedrate_jump_program','Feedrate jump workplan',(),$,(#51,#61));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M174','M174','M174',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m174(path) -> None:
    Path(path).write_text(_render_m174())


f.render = _render_m174  # type: ignore[method-assign]
f.write = _write_m174    # type: ignore[method-assign]
