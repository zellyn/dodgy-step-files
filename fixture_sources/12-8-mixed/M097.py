"""M097 — AP238 workingstep references a feature not on the workpiece.

Catalog claim: A MACHINING_WORKINGSTEP references a MACHINING_FEATURE by id;
the feature exists in the file but is associated with a different workpiece;
the workingstep's setup machines workpiece A while the cited feature lives
on workpiece B.

Reproducer recipe: Two WORKPIECEs declared; a WORKINGSTEP whose setup mounts
workpiece A but whose its_feature belongs to workpiece B.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MACHINING_WORKINGSTEP')
  count_entity_def(b'WORKPIECE') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M097",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 MACHINING_WORKINGSTEP referencing a "
        "MACHINING_FEATURE that belongs to a different WORKPIECE than the one mounted in the setup; "
        "input: AP238 STEP-NC file declaring two WORKPIECEs — workpiece_A and workpiece_B — "
        "where SETUP('fixture_a') mounts workpiece_A, but MACHINING_WORKINGSTEP('step_a') "
        "references its_feature = MACHINED_FEATURE('slot_on_b') which is a feature of workpiece_B; "
        "per ISO 10303-238 §6.4 a workingstep's its_feature must belong to the workpiece "
        "associated with the workingstep's setup; the feature's coordinate frame is defined "
        "relative to workpiece_B's coordinate system, but the controller executes the "
        "toolpath in workpiece_A's machine-space position; "
        "the toolpath is computed against feature slot_on_b's placement on workpiece_B, "
        "then executed against the fixture mounting workpiece_A — tool crashes into "
        "workpiece_A at a location that corresponds to slot_on_b's position on the wrong part; "
        "this defect commonly arises when a STEP-NC publisher exports a shared feature library "
        "across multiple parts without filtering features by workpiece; "
        "kernel must validate workingstep-feature-workpiece consistency; "
        "reject as malformed or warn that operation will miss its intended feature; "
        "synonyms: AP238 wrong feature link, workingstep cites foreign feature, "
        "machining step targets wrong workpiece feature, feature on different workpiece referenced, "
        "STEP-NC workingstep machines wrong feature, AP238 feature on wrong part, "
        "tool crash because wrong workpiece feature"
    ),
    schema="AP242",
)


def _render_m097() -> str:
    """Render AP238 file with WORKINGSTEP referencing a feature from the wrong workpiece.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       WORKPIECE A — the workpiece mounted in the setup
      #21       WORKPIECE B — a different part; feature belongs to this one
      #50       MACHINED_FEATURE 'slot_on_b' — belongs to workpiece B
      #55       MACHINED_FEATURE 'slot_on_a' — belongs to workpiece A (unused by workingstep)
      #60       AXIS2_PLACEMENT_3D for setup fixture
      #61       SETUP('fixture_a') mounting workpiece A (#20)
      #70       MACHINING_TOOL 'endmill_6mm'
      #75       MACHINING_OPERATION referencing feature slot_on_b (#50)
      #80       MACHINING_WORKINGSTEP('step_a') — its_feature=#50 (workpiece B) — DEFECT
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M097: AP238 workingstep references a feature not on the workpiece */")
    lines.append("/* DEFECT: MACHINING_WORKINGSTEP its_feature belongs to WORKPIECE B, not WORKPIECE A */")
    lines.append("/* Setup mounts workpiece A; feature 'slot_on_b' lives on workpiece B */")
    lines.append("/* Controller executes toolpath against wrong workpiece coordinate frame — tool crash */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_WORKINGSTEP') */")
    lines.append("/* Byte assertion: count_entity_def(b'WORKPIECE') >= 2 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M097: AP238 WORKINGSTEP feature on wrong workpiece'),'2;1');")
    lines.append("FILE_NAME('M097.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Byte assertion: count_entity_def(b'WORKPIECE') >= 2 */")
    lines.append("/* WORKPIECE A: the part mounted in the fixture — setup machines this one */")
    lines.append("#20=WORKPIECE('workpiece_A',(#14),$,$,$,$,$);")
    lines.append("/* WORKPIECE B: a different part from the shared feature library */")
    lines.append("#21=WORKPIECE('workpiece_B',(#14),$,$,$,$,$);")
    lines.append("/* MACHINED_FEATURE on workpiece B — the feature the publisher accidentally linked */")
    lines.append("#50=MACHINED_FEATURE('slot_on_b',$,$,$,$,$);")
    lines.append("/* MACHINED_FEATURE on workpiece A — the correct feature for this setup */")
    lines.append("#55=MACHINED_FEATURE('slot_on_a',$,$,$,$,$);")
    lines.append("/* Setup placement and SETUP mounting workpiece A */")
    lines.append("#60=AXIS2_PLACEMENT_3D('fixture_origin',CARTESIAN_POINT('',(0.,0.,0.)),")
    lines.append("  DIRECTION('',(0.,0.,1.)),$);")
    lines.append("#61=SETUP('fixture_a',#60,(#20),$);")
    lines.append("/* Machining tool */")
    lines.append("#70=MACHINING_TOOL('endmill_6mm',$,$,$);")
    lines.append("/* Machining operation targeting slot_on_b (workpiece B's feature) */")
    lines.append("#75=MACHINING_OPERATION('mill_slot_a',#70,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* Byte assertion: contains(b'MACHINING_WORKINGSTEP') */")
    lines.append("/* DEFECT: MACHINING_WORKINGSTEP its_feature = #50 ('slot_on_b') from WORKPIECE B */")
    lines.append("/* Setup #61 mounts WORKPIECE A; the feature must be on WORKPIECE A (e.g. #55) */")
    lines.append("/* Referencing #50 from WORKPIECE B causes toolpath to target wrong coordinate frame */")
    lines.append("#80=MACHINING_WORKINGSTEP('step_a',#50,#75,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-workingstep-feature-on-wrong-workpiece',")
    lines.append("  (#20,#21,#50,#55,#61,#70,#75,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M097','M097','M097',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m097(path) -> None:
    Path(path).write_text(_render_m097())


f.render = _render_m097  # type: ignore[method-assign]
f.write = _write_m097    # type: ignore[method-assign]
