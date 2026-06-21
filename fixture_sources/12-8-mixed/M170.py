"""M170 — AP238 turning feed-direction ambiguous (radial vs axial conflict)

Catalog claim: A TURNING_OPERATION carries two contradictory
feed-direction attributes: one says radial (X-axis), the other says
axial (Z-axis). The controller has no way to decide whether to perform
a face-turning or longitudinal-turning move.

Reproducer recipe: a TURNING_OPERATION populated with both
radial_feed = DIRECTION((1.0,0.0,0.0)) and
axial_feed = DIRECTION((0.0,0.0,1.0)) as separate non-null
feed_direction-class attributes.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TURNING_OPERATION(')
  contains(b'radial_feed')
  contains(b'axial_feed')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M170",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where TURNING_OPERATION declares "
        "both radial_feed DIRECTION (X-axis) and axial_feed DIRECTION (Z-axis) simultaneously; "
        "input: AP238 STEP-NC file containing a WORKPLAN for a turning operation; "
        "the TURNING_OPERATION 'turn_ambiguous_feed' carries two non-null feed_direction attributes: "
        "radial_feed = DIRECTION('radial_feed',(1.0,0.0,0.0)) for face-turning direction "
        "and axial_feed = DIRECTION('axial_feed',(0.0,0.0,1.0)) for longitudinal-turning direction; "
        "per ISO 10303-238 §5.8 a turning operation must declare a single feed_direction invariant; "
        "with both attributes populated the controller cannot determine whether to perform "
        "face-turning (radial) or longitudinal-turning (axial); "
        "implementations diverge: some pick the first attribute, some pick the second, some refuse; "
        "the STEP-NC programmer copied fields from two different template operations; "
        "kernel must detect contradictory feed-direction attributes and reject as malformed or warn; "
        "synonyms: AP238 feed direction conflict, STEP-NC turning has two feeds, "
        "radial vs axial ambiguity, turning operation feed axis undecidable, "
        "AP238 turning feed direction ambiguous, STEP-NC radial-vs-axial feed conflict"
    ),
    schema="AP242",
)


def _render_m170() -> str:
    """Render AP238 STEP-NC file with TURNING_OPERATION having both radial and axial feeds.

    Entity layout:
      #10-#14   Unit context (mm)
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN 'turn_ambiguous_program' — top-level STEP-NC program
      #51       MACHINING_WORKINGSTEP 'ambiguous_feed_step'
      #52       TURNING_OPERATION 'turn_ambiguous_feed' — DEFECT: two feed_direction attrs
      #53       DIRECTION 'radial_feed' — (1.0,0.0,0.0) radial/face-turning direction
      #54       DIRECTION 'axial_feed' — (0.0,0.0,1.0) axial/longitudinal direction
      #60       WORKPIECE 'turn_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M170: AP238 turning feed-direction ambiguous (radial vs axial conflict) */")
    lines.append("/* DEFECT: TURNING_OPERATION has both radial_feed (X) and axial_feed (Z) populated */")
    lines.append("/* Per ISO 10303-238 §5.8 a turning op must have a single feed_direction invariant */")
    lines.append("/* Controller cannot decide face-turning vs longitudinal-turning — behaviour diverges */")
    lines.append("/* STEP-NC programmer merged two template operations, leaving both attributes non-null */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TURNING_OPERATION(') */")
    lines.append("/* Byte assertion: contains(b'radial_feed') */")
    lines.append("/* Byte assertion: contains(b'axial_feed') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M170: AP238 turning_operation radial vs axial feed direction conflict'),'2;1');")
    lines.append("FILE_NAME('M170.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-turning-operation-radial-vs-axial-feed-conflict',")
    lines.append("  (#52,#60));")
    lines.append("/* WORKPLAN 'turn_ambiguous_program' — AP238 top-level NC program */")
    lines.append("#50=WORKPLAN('turn_ambiguous_program','Ambiguous feed turning program',(),$,(#51));")
    lines.append("/* MACHINING_WORKINGSTEP links workpiece to turning operation */")
    lines.append("#51=MACHINING_WORKINGSTEP('ambiguous_feed_step','Ambiguous feed workingstep',#52,#60,$);")
    lines.append("/* Byte assertion: contains(b'radial_feed') */")
    lines.append("/* Byte assertion: contains(b'axial_feed') */")
    lines.append("/* DEFECT: both feed_direction attributes non-null simultaneously */")
    lines.append("/* radial_feed: (1.0,0.0,0.0) — face-turning direction */")
    lines.append("#53=DIRECTION('radial_feed',(1.0,0.0,0.0));")
    lines.append("/* axial_feed: (0.0,0.0,1.0) — longitudinal-turning direction */")
    lines.append("#54=DIRECTION('axial_feed',(0.0,0.0,1.0));")
    lines.append("/* Byte assertion: contains(b'TURNING_OPERATION(') */")
    lines.append("/* TURNING_OPERATION: tool=$ speed=$ feed=radial_feed feed2=axial_feed ... */")
    lines.append("#52=TURNING_OPERATION('turn_ambiguous_feed',$,$,#53,#54,$,$);")
    lines.append("/* WORKPIECE 'turn_workpiece' */")
    lines.append("#60=WORKPIECE('turn_workpiece','Workpiece for ambiguous-feed turning',$,$,$,$,$);")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M170','M170','M170',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m170(path) -> None:
    Path(path).write_text(_render_m170())


f.render = _render_m170  # type: ignore[method-assign]
f.write = _write_m170    # type: ignore[method-assign]
