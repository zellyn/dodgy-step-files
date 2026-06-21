"""M077 — AP238 fixture references different workpiece than the setup is machining.

Catalog claim: A SETUP's its_workpiece_setup chain wires a fixture (vise
jaw, clamp, tombstone) to one WORKPIECE, but the WORKINGSTEP beneath
that setup names a different WORKPIECE as the part being machined. The
fixture is geometrically constraining a part that isn't in the cut.

Reproducer recipe: WORKPIECE_SETUP(#100, .., (#110), ..) (fixture to
plate_a) but WORKINGSTEP(.., #101, #200) (machining plate_b).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'WORKPIECE_SETUP')
  contains(b'WORKPIECE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M077",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where SETUP's WORKPIECE_SETUP "
        "references plate_a (#100) but the MACHINING_WORKINGSTEP under that SETUP "
        "references plate_b (#101) as the machined workpiece — fixture orphaned; "
        "input: AP238 STEP-NC file with two WORKPIECEs ('plate_a' #100 and 'plate_b' #101) "
        "and a vise jaw WORKPIECE (#110); WORKPIECE_SETUP(#100,$,$,(#110),$) attaches "
        "the vise jaw as fixture for plate_a; SETUP('main_setup',(#120),$,$,$) uses "
        "that workpiece_setup; but MACHINING_WORKINGSTEP('ws',$,$,#101,#200) names "
        "plate_b as its part being machined, not plate_a; "
        "AP238 §3.4 setup/workpiece_setup invariants require the workpiece in the "
        "workpiece_setup to match the workpiece in the workingstep; "
        "the vise jaws are constraining plate_a, but plate_b is being machined — "
        "the fixture is orphaned and cannot constrain the actual workpiece; "
        "kernel must cross-validate workpiece references between setup and workingstep "
        "and reject the inconsistency or warn; "
        "synonyms: fixture orphaned, wrong workpiece in setup, "
        "AP238 fixture-workpiece mismatch, setup fixture wires to different part"
    ),
    schema="AP242",
)


def _render_m077() -> str:
    """Render AP238 STEP-NC file with fixture referencing wrong workpiece.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#16   Unit context
      #100      WORKPIECE 'plate_a' (fixture is attached to this)
      #101      WORKPIECE 'plate_b' (workingstep actually machines this)
      #110      WORKPIECE 'vise_jaw' (the fixture)
      #120      WORKPIECE_SETUP linking vise_jaw to plate_a
      #200      SETUP referencing the workpiece_setup (for plate_a)
      #210      MACHINING_WORKINGSTEP referencing plate_b — the defect
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M077: AP238 fixture references different workpiece than the setup is machining */")
    lines.append("/* DEFECT: WORKPIECE_SETUP attaches fixture to plate_a, but MACHINING_WORKINGSTEP */")
    lines.append("/*   names plate_b as the machined part — fixture is orphaned */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'WORKPIECE_SETUP') */")
    lines.append("/* Byte assertion: contains(b'WORKPIECE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M077: AP238 fixture references wrong workpiece'),'2;1');")
    lines.append("FILE_NAME('M077.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 3 1 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('numerical_control_machining');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'numerical_control_machining',2007,#1);")
    lines.append("/* Standard unit context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('ctx','3D'));")
    lines.append("/* Byte assertion: contains(b'WORKPIECE') */")
    lines.append("/* Two workpieces: plate_a and plate_b */")
    lines.append("#100=WORKPIECE('plate_a',$,$,$,$,$,$);")
    lines.append("#101=WORKPIECE('plate_b',$,$,$,$,$,$);")
    lines.append("/* Fixture: vise jaw */")
    lines.append("#110=WORKPIECE('vise_jaw',$,$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'WORKPIECE_SETUP') */")
    lines.append("/* WORKPIECE_SETUP: attaches vise_jaw (#110) as fixture for plate_a (#100) */")
    lines.append("#120=WORKPIECE_SETUP(#100,$,$,(#110),$);")
    lines.append("/* SETUP uses the workpiece_setup for plate_a */")
    lines.append("#200=SETUP('main_setup',(#120),$,$,$);")
    lines.append("/* DEFECT: MACHINING_WORKINGSTEP references plate_b (#101), not plate_a (#100) */")
    lines.append("/* The fixture constrains plate_a, but plate_b is being machined */")
    lines.append("#210=MACHINING_WORKINGSTEP('ws',$,$,#101,#200);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-fixture-references-wrong-workpiece-orphaned',")
    lines.append("  (#100,#101,#110,#120,#200,#210));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M077','M077','M077',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m077(path) -> None:
    Path(path).write_text(_render_m077())


f.render = _render_m077  # type: ignore[method-assign]
f.write = _write_m077    # type: ignore[method-assign]
