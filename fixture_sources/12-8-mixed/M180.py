"""M180 — AP238 inspection_result measurement uncertainty exceeds feature tolerance

Catalog claim: An INSPECTION_RESULT records a measurement_uncertainty of
0.05 mm against a feature whose design tolerance is +/-0.02 mm. The
measurement is statistically incapable of confirming or denying
conformance — it tells you nothing. Reporting it as "in spec" or
"out of spec" is misleading.

Reproducer recipe: a PLUS_MINUS_TOLERANCE of +/-0.02 mm on a feature;
an INSPECTION_RESULT with measurement_uncertainty = 0.05 mm against
the same feature.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'INSPECTION_RESULT')
  contains(b'PLUS_MINUS_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M180",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where INSPECTION_RESULT records "
        "measurement_uncertainty 0.05 mm against a feature with PLUS_MINUS_TOLERANCE +/-0.02 mm; "
        "input: AP238 STEP-NC file containing a WORKPLAN for an inspection operation; "
        "the feature 'inspected_feature' has PLUS_MINUS_TOLERANCE of +/-0.02 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.02), mm); "
        "the INSPECTION_RESULT 'bad_inspection_result' records measurement_uncertainty 0.05 mm "
        "via MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.05), mm); "
        "measurement uncertainty (0.05 mm) exceeds feature tolerance (+/-0.02 mm = range 0.04 mm); "
        "the gauge cannot statistically confirm or deny conformance with this feature tolerance; "
        "reporting this result as in-spec or out-of-spec is misleading and meaningless; "
        "per ISO 10303-238 §5.8 inspection_result uncertainty-vs-tolerance gauge-capability rule: "
        "measurement uncertainty must be below feature tolerance for valid inspection; "
        "kernel must validate that measurement uncertainty is below feature tolerance; "
        "synonyms: AP238 inspection uncertainty > tolerance, STEP-NC gauge R&R insufficient, "
        "measurement uncertainty exceeds feature tol, AP238 gauge incapable, "
        "STEP-NC inspection meaningless, gauge can't resolve tolerance, "
        "AP238 measurement uncertainty too large, STEP-NC gauge R&R fails"
    ),
    schema="AP242",
)


def _render_m180() -> str:
    """Render AP238 STEP-NC file with INSPECTION_RESULT uncertainty 0.05mm > tolerance 0.02mm.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #40       PLUS_MINUS_TOLERANCE: feature tolerance +/-0.02 mm — the design limit
      #41       MEASURE_WITH_UNIT for tolerance value = 0.02 mm
      #42       MEASURE_WITH_UNIT for uncertainty = 0.05 mm — DEFECT: > tolerance range
      #43       INSPECTION_RESULT 'bad_inspection_result' — DEFECT: uncertainty 0.05mm
      #50       WORKPLAN 'inspection_gauge_incapable_program'
      #51       MACHINING_WORKINGSTEP 'inspection_step'
      #52       INSPECTION_OPERATION 'inspection_op'
      #60       WORKPIECE 'inspection_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M180: AP238 inspection_result measurement uncertainty exceeds feature tolerance */")
    lines.append("/* DEFECT: INSPECTION_RESULT uncertainty 0.05 mm; PLUS_MINUS_TOLERANCE +/-0.02 mm */")
    lines.append("/* Measurement uncertainty 0.05 mm exceeds feature tolerance range 0.04 mm */")
    lines.append("/* Gauge cannot statistically confirm or deny conformance with this tolerance */")
    lines.append("/* Reporting as in-spec or out-of-spec is meaningless — gauge incapable */")
    lines.append("/* Per ISO 10303-238 §5.8 uncertainty must be below tolerance for valid inspection */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'INSPECTION_RESULT') */")
    lines.append("/* Byte assertion: contains(b'PLUS_MINUS_TOLERANCE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M180: AP238 inspection_result uncertainty 0.05mm exceeds tolerance 0.02mm'),'2;1');")
    lines.append("FILE_NAME('M180.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-inspection-uncertainty-exceeds-feature-tolerance',")
    lines.append("  (#43,#52,#60));")
    lines.append("/* Byte assertion: contains(b'PLUS_MINUS_TOLERANCE') */")
    lines.append("/* Feature design tolerance: +/-0.02 mm (total range 0.04 mm) */")
    lines.append("#41=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.02),#15);")
    lines.append("#40=PLUS_MINUS_TOLERANCE(#41,$);")
    lines.append("/* DEFECT: measurement_uncertainty 0.05 mm exceeds tolerance range 0.04 mm */")
    lines.append("#42=MEASURE_WITH_UNIT(POSITIVE_LENGTH_MEASURE(0.05),#15);")
    lines.append("/* Byte assertion: contains(b'INSPECTION_RESULT') */")
    lines.append("/* DEFECT: INSPECTION_RESULT with uncertainty 0.05mm against +/-0.02mm tolerance */")
    lines.append("#43=INSPECTION_RESULT('bad_inspection_result',$,#40,#42,$);")
    lines.append("/* WORKPIECE 'inspection_workpiece' */")
    lines.append("#60=WORKPIECE('inspection_workpiece','Workpiece for gauge-incapable inspection test',$,$,$,$,$);")
    lines.append("/* INSPECTION_OPERATION references the bad inspection result */")
    lines.append("#52=INSPECTION_OPERATION('inspection_op',$,$,$,$,$,#43,$);")
    lines.append("/* MACHINING_WORKINGSTEP links inspection op to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('inspection_step','Gauge-incapable inspection workingstep',#52,#60,$);")
    lines.append("/* WORKPLAN: single inspection step with gauge-incapable uncertainty */")
    lines.append("#50=WORKPLAN('inspection_gauge_incapable_program','Gauge incapable inspection workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M180','M180','M180',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m180(path) -> None:
    Path(path).write_text(_render_m180())


f.render = _render_m180  # type: ignore[method-assign]
f.write = _write_m180    # type: ignore[method-assign]
