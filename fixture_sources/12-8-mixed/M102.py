"""M102 — AP238 drilling sequence with coincident hole positions.

Catalog claim: A workplan emits two DRILLING_OPERATIONs targeting features
whose locator placements are coincident (within tolerance). The second drill
attempts to enter an already-fully-drilled hole and breaks the tool from a
zero-load entry, or wastes cycle time.

Reproducer recipe: Two DRILLING_OPERATIONs whose feature locator
AXIS2_PLACEMENT_3Ds have identical origins (50,30,0).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  count_entity_def(b'DRILLING_OPERATION') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M102",
    defect=(
        "GEOMETRIC_CURVE_SET containing two AP238 DRILLING_OPERATIONs whose feature locator "
        "AXIS2_PLACEMENT_3Ds have coincident origins (50.,30.,0.) — redundant drill on same hole; "
        "input: AP238 STEP-NC file where a WORKPLAN sequences two DRILLING_OPERATIONs ('drill_a' "
        "and 'drill_b') each targeting separate MACHINED_FEATUREs whose locator placements "
        "AXIS2_PLACEMENT_3D both have origin CARTESIAN_POINT at (50.,30.,0.) — identical positions; "
        "per ISO 10303-238 §5.8 drilling_operation positional uniqueness convention each drilling "
        "operation in a workplan must target a distinct hole position; "
        "the second drill attempts to enter an already-fully-drilled hole: either breaks the tool "
        "from a zero-load entry (no material to cut, tool slams through) or wastes cycle time "
        "re-drilling without material removal; "
        "arises from CAM publisher producing drill-table from CAD with duplicate hole features "
        "that were not de-duplicated before export; "
        "kernel must detect coincident hole positions; warn or collapse duplicate operations; "
        "synonyms: duplicate hole drill, coincident drilling targets, AP238 two drills at same point, "
        "STEP-NC redundant drill, drill-on-drill collision, drilling same hole twice, "
        "STEP-NC duplicate hole position"
    ),
    schema="AP242",
)


def _render_m102() -> str:
    """Render AP238 file with two DRILLING_OPERATIONs at coincident positions.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       CARTESIAN_POINT origin_a (50.,30.,0.) — locator for first hole
      #21       DIRECTION z_axis_a
      #22       AXIS2_PLACEMENT_3D locator_a at (50.,30.,0.)
      #23       CARTESIAN_POINT origin_b (50.,30.,0.) — SAME position — DEFECT
      #24       DIRECTION z_axis_b
      #25       AXIS2_PLACEMENT_3D locator_b at (50.,30.,0.) — coincident with #22
      #50       MACHINED_FEATURE 'hole_a' with locator #22
      #51       MACHINED_FEATURE 'hole_b' with locator #25 — at same location
      #60       MACHINING_TOOL 'drill_8mm'
      #70       DRILLING_OPERATION 'drill_a' targeting #50
      #71       DRILLING_OPERATION 'drill_b' targeting #51 — DEFECT: same position as #70
      #80       MACHINING_WORKINGSTEP 'drill_step_a'
      #81       MACHINING_WORKINGSTEP 'drill_step_b'
      #90       WORKPLAN referencing both workingsteps in sequence
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M102: AP238 drilling sequence with coincident hole positions */")
    lines.append("/* DEFECT: two DRILLING_OPERATIONs target features at identical position (50,30,0) */")
    lines.append("/* Second drill enters already-drilled hole — breaks tool or wastes cycle time */")
    lines.append("/* Violates ISO 10303-238 §5.8 drilling_operation positional uniqueness */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: count_entity_def(b'DRILLING_OPERATION') >= 2 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M102: AP238 two DRILLING_OPERATIONs at coincident positions'),'2;1');")
    lines.append("FILE_NAME('M102.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* First hole locator at (50,30,0) */")
    lines.append("#20=CARTESIAN_POINT('origin_a',(50.,30.,0.));")
    lines.append("#21=DIRECTION('z_a',(0.,0.,1.));")
    lines.append("#22=AXIS2_PLACEMENT_3D('locator_a',#20,#21,$);")
    lines.append("/* DEFECT: Second hole locator at IDENTICAL position (50,30,0) */")
    lines.append("/* Correct fix: use a distinct position for hole_b, e.g. (100.,30.,0.) */")
    lines.append("#23=CARTESIAN_POINT('origin_b',(50.,30.,0.));")
    lines.append("#24=DIRECTION('z_b',(0.,0.,1.));")
    lines.append("#25=AXIS2_PLACEMENT_3D('locator_b',#23,#24,$);")
    lines.append("/* Feature declarations — hole_a and hole_b at same position */")
    lines.append("#50=MACHINED_FEATURE('hole_a',$,$,$,$,#22);")
    lines.append("/* hole_b has same locator position — this is the coincident defect */")
    lines.append("#51=MACHINED_FEATURE('hole_b',$,$,$,$,#25);")
    lines.append("/* Drill bit — 8mm diameter */")
    lines.append("#60=MACHINING_TOOL('drill_8mm',$,$,$);")
    lines.append("/* Byte assertion: count_entity_def(b'DRILLING_OPERATION') >= 2 */")
    lines.append("/* First DRILLING_OPERATION on hole_a */")
    lines.append("#70=DRILLING_OPERATION('drill_a',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* DEFECT: Second DRILLING_OPERATION on hole_b — same position as hole_a */")
    lines.append("/* Enters already-drilled hole: tool slams through or zero material removal */")
    lines.append("#71=DRILLING_OPERATION('drill_b',#60,$,$,$,$,$,$,#51,$,$);")
    lines.append("/* Workingsteps in sequence */")
    lines.append("#80=MACHINING_WORKINGSTEP('drill_step_a',#50,#70,$);")
    lines.append("#81=MACHINING_WORKINGSTEP('drill_step_b',#51,#71,$);")
    lines.append("/* WORKPLAN sequences both steps — second step drills into already-finished hole */")
    lines.append("#90=WORKPLAN('main',(#80,#81),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-drilling-sequence-coincident-hole-positions',")
    lines.append("  (#22,#25,#50,#51,#60,#70,#71,#80,#81,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M102','M102','M102',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m102(path) -> None:
    Path(path).write_text(_render_m102())


f.render = _render_m102  # type: ignore[method-assign]
f.write = _write_m102    # type: ignore[method-assign]
