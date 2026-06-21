"""M183 — AP238 workpiece_setup coordinate system not aligned with machine axes

Catalog claim: A WORKPIECE_SETUP's placement axes are rotated 17.3 degrees
about the machine Z-axis with no rotational fixturing declared. The machine
cannot drive its X/Y stages along the workpiece's local axes; every toolpath
issues compound moves that exceed acceleration limits.

Reproducer recipe: WORKPIECE_SETUP whose AXIS2_PLACEMENT_3D x-axis is
DIRECTION((0.9550, 0.2974, 0.0)) (17.3 deg rotation), with no rotary
fixturing referenced.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'WORKPIECE_SETUP')
  contains(b'workpiece_csys_rotated')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M183",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where WORKPIECE_SETUP declares "
        "an AXIS2_PLACEMENT_3D x-axis rotated 17.3 degrees from machine X-axis with no rotary fixturing; "
        "input: AP238 STEP-NC file containing a WORKPLAN with a WORKPIECE_SETUP; "
        "the WORKPIECE_SETUP 'workpiece_csys_rotated' uses AXIS2_PLACEMENT_3D 'rotated_csys' "
        "whose x-axis DIRECTION is (0.9550, 0.2974, 0.0) — a 17.3-degree rotation about Z; "
        "no rotary fixturing or rotary stage is referenced in the file; "
        "the machine cannot drive its linear X/Y stages along the workpiece's local axes; "
        "every toolpath requires compound simultaneous moves that exceed axis acceleration limits; "
        "per ISO 10303-238 §5.4 workpiece_setup machine-axis-alignment guidance: "
        "workpiece setup orientation must align with machine axes when no rotary stage is declared; "
        "kernel must validate workpiece-setup orientation against machine axes; "
        "synonyms: AP238 workpiece setup rotated, STEP-NC setup not square to machine, "
        "fixture skew without rotary axis, AP238 workpiece-setup rotated, "
        "STEP-NC fixture not square, setup CS skew without rotary stage, "
        "workpiece coords misaligned, AP238 workpiece-setup rotation without rotary axis, "
        "STEP-NC setup not aligned to machine, workpiece coords skewed"
    ),
    schema="AP242",
)


def _render_m183() -> str:
    """Render AP238 STEP-NC file with WORKPIECE_SETUP rotated 17.3 deg, no rotary fixturing.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       CARTESIAN_POINT 'setup_origin' — workpiece setup origin at (0,0,0)
      #31       DIRECTION 'machine_z' — machine Z-axis (0,0,1)
      #32       DIRECTION 'rotated_x' — x-axis rotated 17.3 deg: (0.9550, 0.2974, 0.0)
      #33       AXIS2_PLACEMENT_3D 'rotated_csys' — DEFECT: skewed coordinate system
      #40       WORKPIECE 'nc_workpiece' — the workpiece being set up
      #41       WORKPIECE_SETUP 'workpiece_csys_rotated' — DEFECT: skewed AXIS2_PLACEMENT
      #50       WORKPLAN 'skewed_setup_program'
      #51       MACHINING_WORKINGSTEP 'mill_step'
      #52       MILLING_OPERATION 'mill_op'
      #60       WORKPIECE 'mill_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M183: AP238 workpiece_setup coordinate system not aligned with machine axes */")
    lines.append("/* DEFECT: WORKPIECE_SETUP x-axis (0.9550, 0.2974, 0.0) — 17.3 deg rotation about Z */")
    lines.append("/* No rotary fixturing or rotary stage declared in this file */")
    lines.append("/* Machine cannot drive linear X/Y stages along skewed workpiece axes */")
    lines.append("/* Every toolpath requires compound simultaneous moves exceeding acceleration limits */")
    lines.append("/* Per ISO 10303-238 §5.4 setup orientation must align with machine axes (no rotary) */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'WORKPIECE_SETUP') */")
    lines.append("/* Byte assertion: contains(b'workpiece_csys_rotated') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M183: AP238 workpiece_setup rotated 17.3 deg with no rotary fixturing'),'2;1');")
    lines.append("FILE_NAME('M183.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-workpiece-setup-coordinate-system-not-aligned-with-machine-axes',")
    lines.append("  (#41,#52,#60));")
    lines.append("/* Setup origin at machine zero */")
    lines.append("#30=CARTESIAN_POINT('setup_origin',(0.0,0.0,0.0));")
    lines.append("/* Machine Z-axis (vertical) */")
    lines.append("#31=DIRECTION('machine_z',(0.0,0.0,1.0));")
    lines.append("/* DEFECT: x-axis rotated 17.3 degrees — cos(17.3 deg)=0.9550, sin(17.3 deg)=0.2974 */")
    lines.append("#32=DIRECTION('rotated_x',(0.9550,0.2974,0.0));")
    lines.append("/* DEFECT: skewed coordinate system — 17.3 deg rotation about Z-axis */")
    lines.append("#33=AXIS2_PLACEMENT_3D('rotated_csys',#30,#31,#32);")
    lines.append("/* NC workpiece being positioned in the skewed setup */")
    lines.append("#40=WORKPIECE('nc_workpiece','Workpiece for skewed setup test',$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'WORKPIECE_SETUP') */")
    lines.append("/* Byte assertion: contains(b'workpiece_csys_rotated') */")
    lines.append("/* DEFECT: WORKPIECE_SETUP using rotated_csys — 17.3 deg skew, no rotary stage */")
    lines.append("#41=WORKPIECE_SETUP('workpiece_csys_rotated',#33,#40,$,$,$);")
    lines.append("/* WORKPIECE 'mill_workpiece' for the milling step */")
    lines.append("#60=WORKPIECE('mill_workpiece','Workpiece for skewed-setup milling',$,$,$,$,$);")
    lines.append("/* MILLING_OPERATION for the skewed setup scenario */")
    lines.append("#52=MILLING_OPERATION('mill_op',$,$,$,$,$,$,$,$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP links milling op to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('mill_step','Skewed setup mill step',#52,#60,$);")
    lines.append("/* WORKPLAN: milling on skewed workpiece setup without rotary stage */")
    lines.append("#50=WORKPLAN('skewed_setup_program','Skewed setup milling workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M183','M183','M183',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m183(path) -> None:
    Path(path).write_text(_render_m183())


f.render = _render_m183  # type: ignore[method-assign]
f.write = _write_m183    # type: ignore[method-assign]
