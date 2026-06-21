"""M168 — AP238 turning_finishing_face with feed direction inverted

Catalog claim: A TURNING_FINISHING_FACE declares a feed_direction
vector pointing OUTWARD (away from the spindle axis) where face-turning
requires inward feed (toward the axis). The tool retracts during what
should be the finishing pass, leaving uncut stock and a witness mark
from the entry point.

Reproducer recipe: TURNING_FINISHING_FACE with
feed_direction = DIRECTION('feed_outward_WRONG',(1.0,0.0,0.0))
(outward +X) instead of inward (-X) toward the spindle axis.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TURNING_FINISHING_FACE')
  contains(b'feed_outward_WRONG')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M168",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where TURNING_FINISHING_FACE declares "
        "feed_direction pointing OUTWARD (+X) away from the spindle axis instead of inward (-X); "
        "input: AP238 STEP-NC file containing a WORKPLAN for face-turning a cylindrical part; "
        "the TURNING_FINISHING_FACE 'face_finish_pass' carries "
        "feed_direction = DIRECTION('feed_outward_WRONG',(1.0,0.0,0.0)) — outward +X; "
        "face-turning requires inward feed (toward spindle axis, i.e. -X direction); "
        "with outward feed the tool retracts during the finishing pass, "
        "leaving uncut stock on the face and a witness mark at the entry point; "
        "the STEP-NC programmer negated the feed vector sign when transcribing the path; "
        "per ISO 10303-238 §5.8 face-turning feed_direction must point inward toward spindle axis; "
        "kernel must validate feed_direction against operation semantics for face-turning "
        "and reject as malformed or warn; "
        "synonyms: AP238 face-turn feed reversed, STEP-NC feed_direction wrong sign, "
        "turning finish pass goes outward, lathe retracts during finish cut, "
        "AP238 turning finishing direction wrong, feed_direction outward on face turn"
    ),
    schema="AP242",
)


def _render_m168() -> str:
    """Render AP238 STEP-NC file with TURNING_FINISHING_FACE feed_direction inverted.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN 'face_turn_program' — top-level STEP-NC program
      #51       MACHINING_WORKINGSTEP 'face_finish_step'
      #52       TURNING_FINISHING_FACE 'face_finish_pass' — DEFECT: outward feed_direction
      #53       DIRECTION 'feed_outward_WRONG' — (1.0,0.0,0.0) outward, should be -X
      #60       WORKPIECE 'cyl_face_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M168: AP238 turning_finishing_face with feed direction inverted */")
    lines.append("/* DEFECT: TURNING_FINISHING_FACE feed_direction = (1.0,0.0,0.0) outward */")
    lines.append("/* Face-turning requires inward feed toward spindle axis (-X direction) */")
    lines.append("/* Outward feed causes tool retraction during finishing pass — uncut stock remains */")
    lines.append("/* Per ISO 10303-238 §5.8 face-turning feed_direction must be inward */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TURNING_FINISHING_FACE') */")
    lines.append("/* Byte assertion: contains(b'feed_outward_WRONG') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M168: AP238 turning_finishing_face feed direction inverted outward'),'2;1');")
    lines.append("FILE_NAME('M168.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* mm length unit reference */")
    lines.append("#15=SI_UNIT(.MILLI.,.METRE.);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-turning-finishing-face-feed-direction-inverted',")
    lines.append("  (#52,#60));")
    lines.append("/* WORKPLAN 'face_turn_program' — AP238 top-level NC program */")
    lines.append("#50=WORKPLAN('face_turn_program','Face turning finish program',(),$,(#51));")
    lines.append("/* MACHINING_WORKINGSTEP links workpiece to finishing operation */")
    lines.append("#51=MACHINING_WORKINGSTEP('face_finish_step','Face finishing workingstep',#52,#60,$);")
    lines.append("/* Byte assertion: contains(b'TURNING_FINISHING_FACE') */")
    lines.append("/* Byte assertion: contains(b'feed_outward_WRONG') */")
    lines.append("/* DEFECT: feed_direction = DIRECTION('feed_outward_WRONG',(1.0,0.0,0.0)) */")
    lines.append("/* Correct direction for face-turning is (-1.0,0.0,0.0) inward toward spindle */")
    lines.append("#53=DIRECTION('feed_outward_WRONG',(1.0,0.0,0.0));")
    lines.append("#52=TURNING_FINISHING_FACE('face_finish_pass',$,$,$,$,#53,$);")
    lines.append("/* WORKPIECE 'cyl_face_workpiece': cylindrical part being face-turned */")
    lines.append("#60=WORKPIECE('cyl_face_workpiece','Cylindrical workpiece for face turning',$,$,$,$,$);")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M168','M168','M168',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m168(path) -> None:
    Path(path).write_text(_render_m168())


f.render = _render_m168  # type: ignore[method-assign]
f.write = _write_m168    # type: ignore[method-assign]
