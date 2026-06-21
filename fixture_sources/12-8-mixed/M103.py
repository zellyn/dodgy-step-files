"""M103 — AP238 tool trajectory passes through workpiece body before designated cut.

Catalog claim: A TRAJECTORY's approach segment passes from the
tool-change position straight through the workpiece volume to reach the
feature start; i.e., the line segment from (0,0,200) to (50,30,-5)
intersects the workpiece body at (50,30,0). The implicit retract is
missing. The controller either crashes the tool against the workpiece or
performs an unintended plunge.

Reproducer recipe: TRAJECTORY whose first segment is a straight
LINE from (0,0,200) to (50,30,-5), with workpiece geometry occupying
the box (0..100, 0..100, 0..50).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TRAJECTORY')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M103",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 TRAJECTORY whose approach segment is a straight "
        "LINE from (0,0,200) to (50,30,-5) that passes through the workpiece body at (50,30,0); "
        "input: AP238 STEP-NC file where a TRAJECTORY's first segment is a straight LINE "
        "from tool-change position (0.,0.,200.) directly to feature start (50.,30.,-5.) "
        "with no retract waypoint; this segment intersects the workpiece body which occupies "
        "the box bounded by (0.,100.,0.,100.,0.,50.) — the tool enters the workpiece at (50.,30.,0.) "
        "without a designated cutting operation, causing an unintended plunge; "
        "per ISO 10303-238 §6.2 toolpath safety / clearance invariants the approach segment "
        "must clear the workpiece at all points; a missing retract height means the tool travels "
        "through the part on the way to the cut start, either crashing the tool against the "
        "workpiece or performing an unintended plunge that ruins the workpiece surface; "
        "kernel must collision-check toolpath against workpiece envelope; "
        "reject the trajectory or warn loudly about the approach intersection; "
        "synonyms: AP238 tool crash, trajectory through part, missing retract, AP238 tool collision, "
        "STEP-NC plunge through part, approach trajectory hits workpiece"
    ),
    schema="AP242",
)


def _render_m103() -> str:
    """Render AP238 file with TRAJECTORY approach segment intersecting workpiece.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       CARTESIAN_POINT tool_change_pos (0.,0.,200.) — approach start
      #21       CARTESIAN_POINT feature_start (50.,30.,-5.) — approach end (below workpiece surface)
      #22       DIRECTION approach_dir (normalized (50,30,-205) vector)
      #23       VECTOR wrapping #22 with magnitude
      #24       LINE — the approach segment from #20 to #21 — DEFECT: passes through workpiece
      #25       TRAJECTORY wrapping the approach line — DEFECT
      #50       MACHINED_FEATURE 'pocket_c'
      #60       MACHINING_TOOL 'endmill_10mm'
      #70       MACHINING_OPERATION referencing #25 as its toolpath — DEFECT
      #80       MACHINING_WORKINGSTEP wrapping #70
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M103: AP238 tool trajectory passes through workpiece body before designated cut */")
    lines.append("/* DEFECT: TRAJECTORY approach LINE from (0,0,200) to (50,30,-5) intersects workpiece */")
    lines.append("/* Workpiece occupies box (0..100, 0..100, 0..50) — approach hits at (50,30,0) */")
    lines.append("/* Missing retract height — controller crashes or plunges unintentionally */")
    lines.append("/* Violates ISO 10303-238 §6.2 toolpath safety / clearance invariants */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TRAJECTORY') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M103: AP238 TRAJECTORY approach passes through workpiece'),'2;1');")
    lines.append("FILE_NAME('M103.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Tool-change position: above workpiece at Z=200 */")
    lines.append("#20=CARTESIAN_POINT('tool_change_pos',(0.,0.,200.));")
    lines.append("/* DEFECT: Feature start at Z=-5 (below workpiece surface at Z=0) */")
    lines.append("/* Approach from (0,0,200) to (50,30,-5) crosses workpiece surface at (50,30,0) */")
    lines.append("#21=CARTESIAN_POINT('feature_start',(50.,30.,-5.));")
    lines.append("/* Approach direction: from tool_change_pos toward feature_start */")
    lines.append("/* Vector: (50-0, 30-0, -5-200) = (50, 30, -205), normalized */")
    lines.append("#22=DIRECTION('approach_dir',(0.2357,0.1414,-0.9661));")
    lines.append("#23=VECTOR('approach_vec',#22,212.2);")
    lines.append("/* DEFECT: LINE approach segment passes through workpiece body */")
    lines.append("/* Workpiece box (0..100, 0..100, 0..50): line crosses Z=0 at (50,30,0) — inside box */")
    lines.append("/* Correct fix: add retract to Z=200 above feature, then plunge to feature start */")
    lines.append("#24=LINE('approach_line',#20,#23);")
    lines.append("/* Byte assertion: contains(b'TRAJECTORY') */")
    lines.append("/* TRAJECTORY wraps the approach line — defect propagates to motion planning */")
    lines.append("#25=TRAJECTORY('approach_traj',(#24),$,$,$);")
    lines.append("/* Target machined feature */")
    lines.append("#50=MACHINED_FEATURE('pocket_c',$,$,$,$,$);")
    lines.append("/* End mill used for the pocket operation */")
    lines.append("#60=MACHINING_TOOL('endmill_10mm',$,$,$);")
    lines.append("/* MACHINING_OPERATION references the unsafe trajectory #25 as its toolpath */")
    lines.append("#70=MACHINING_OPERATION('mill_pocket_c',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* Workingstep and workplan */")
    lines.append("#80=MACHINING_WORKINGSTEP('pocket_c_step',#50,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-tool-trajectory-passes-through-workpiece-body',")
    lines.append("  (#20,#21,#24,#25,#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M103','M103','M103',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m103(path) -> None:
    Path(path).write_text(_render_m103())


f.render = _render_m103  # type: ignore[method-assign]
f.write = _write_m103    # type: ignore[method-assign]
