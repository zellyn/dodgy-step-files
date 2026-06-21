"""M179 — AP238 touch_probing tolerance smaller than probe stylus radius

Catalog claim: A TOUCH_PROBING op declares a measurement tolerance of
0.005 mm while the touch probe's stylus tip ball diameter is 4.0 mm
(radius 2.0 mm). The stylus radius compensation cannot resolve features
below the tip radius — the declared tolerance is fundamentally
unattainable with this probe.

Reproducer recipe: a TOUCH_PROBE with stylus diameter 4.0 mm; a
TOUCH_PROBING op with tolerance 0.005 mm referencing that probe.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TOUCH_PROBING(')
  contains(b'TOUCH_PROBE(')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M179",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where TOUCH_PROBING op declares "
        "measurement tolerance 0.005 mm but TOUCH_PROBE stylus tip ball diameter is 4.0 mm; "
        "input: AP238 STEP-NC file containing a WORKPLAN for a touch-probing inspection; "
        "the TOUCH_PROBE 'big_stylus_probe' has stylus_diameter 4.0 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(4.0), mm) — stylus radius is 2.0 mm; "
        "the TOUCH_PROBING 'overspec_probe_op' declares measurement_tolerance 0.005 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.005), mm); "
        "stylus radius (2.0 mm) is 400x larger than declared tolerance (0.005 mm); "
        "stylus radius compensation cannot resolve features below the tip radius; "
        "the declared tolerance is fundamentally unattainable with this probe tip; "
        "per ISO 10303-238 §5.8 touch_probing measurement-resolution invariant: "
        "measurement tolerance must be achievable with the declared probe stylus radius; "
        "kernel must validate measurement tolerance against probe stylus radius; "
        "synonyms: AP238 probe tolerance below stylus, STEP-NC inspection unattainable resolution, "
        "touch probe can't resolve sub-radius features, AP238 probe tolerance < stylus radius, "
        "STEP-NC inspection resolution impossible, touch probe tip too big, "
        "AP238 touch probe over-spec'd, inspection resolution exceeds probe capability, "
        "stylus diameter exceeds tolerance"
    ),
    schema="AP242",
)


def _render_m179() -> str:
    """Render AP238 STEP-NC file with TOUCH_PROBING tolerance 0.005mm vs stylus diameter 4.0mm.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #40       TOUCH_PROBE 'big_stylus_probe' — stylus diameter 4.0 mm
      #41       MEASURE_WITH_UNIT for stylus diameter = 4.0 mm
      #42       MEASURE_WITH_UNIT for tolerance = 0.005 mm — DEFECT: << stylus radius
      #50       WORKPLAN 'overspec_probe_program' — AP238 top-level NC program
      #51       MACHINING_WORKINGSTEP 'overspec_probe_step'
      #52       TOUCH_PROBING 'overspec_probe_op' — DEFECT: tolerance 0.005mm < stylus radius
      #60       WORKPIECE 'probe_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M179: AP238 touch_probing tolerance smaller than probe stylus radius */")
    lines.append("/* DEFECT: TOUCH_PROBING tolerance 0.005 mm; TOUCH_PROBE stylus diameter 4.0 mm */")
    lines.append("/* Stylus radius 2.0 mm is 400x larger than declared tolerance 0.005 mm */")
    lines.append("/* Stylus radius compensation cannot resolve features below tip radius */")
    lines.append("/* Declared tolerance is fundamentally unattainable with this probe tip */")
    lines.append("/* Per ISO 10303-238 §5.8 tolerance must be achievable with probe stylus radius */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TOUCH_PROBING(') */")
    lines.append("/* Byte assertion: contains(b'TOUCH_PROBE(') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M179: AP238 touch_probing tolerance 0.005mm < stylus radius 2.0mm'),'2;1');")
    lines.append("FILE_NAME('M179.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-touch-probing-tolerance-below-stylus-radius',")
    lines.append("  (#40,#52,#60));")
    lines.append("/* Byte assertion: contains(b'TOUCH_PROBE(') */")
    lines.append("/* TOUCH_PROBE 'big_stylus_probe': stylus_diameter 4.0 mm (radius 2.0 mm) */")
    lines.append("#41=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(4.0),#15);")
    lines.append("#40=TOUCH_PROBE('big_stylus_probe',$,#41,$,$,$);")
    lines.append("/* DEFECT: tolerance 0.005 mm << stylus radius 2.0 mm — unattainable resolution */")
    lines.append("#42=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.005),#15);")
    lines.append("/* Byte assertion: contains(b'TOUCH_PROBING(') */")
    lines.append("/* DEFECT: TOUCH_PROBING tolerance 0.005 mm with stylus diameter 4.0 mm probe */")
    lines.append("#52=TOUCH_PROBING('overspec_probe_op',$,#40,#42,$,$);")
    lines.append("/* WORKPIECE 'probe_workpiece' */")
    lines.append("#60=WORKPIECE('probe_workpiece','Workpiece for touch-probe tolerance test',$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'overspec_probe_step' links probing op to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('overspec_probe_step','Overspec probe workingstep',#52,#60,$);")
    lines.append("/* WORKPLAN: single touch-probing step with unattainable tolerance */")
    lines.append("#50=WORKPLAN('overspec_probe_program','Overspec touch probe workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M179','M179','M179',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m179(path) -> None:
    Path(path).write_text(_render_m179())


f.render = _render_m179  # type: ignore[method-assign]
f.write = _write_m179    # type: ignore[method-assign]
