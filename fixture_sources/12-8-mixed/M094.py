"""M094 — AP238 setup placement inconsistent with workpiece coordinate system.

Catalog claim: A SETUP's placement transform expresses the workpiece origin
in machine coordinates, but the actual workpiece geometry's AXIS2_PLACEMENT_3D
puts the part origin in a different physical location. The toolpath is computed
in workpiece-local coordinates but executed against the setup-implied origin;
the part is machined at a position offset from where it actually sits in the
fixture.

Reproducer recipe: A SETUP whose placement origin is (100,0,0) and a
WORKPIECE whose own placement origin is (0,0,0), with no relating entity
reconciling the offset.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'SETUP')
  contains(b'AXIS2_PLACEMENT_3D')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M094",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 SETUP placement inconsistent with workpiece "
        "coordinate system — setup origin at (100,0,0) but workpiece own placement at (0,0,0); "
        "input: AP238 STEP-NC file where SETUP('fixture_a') declares its placement via "
        "AXIS2_PLACEMENT_3D at machine coordinates (100,0,0), meaning the workpiece origin "
        "should sit at x=100 in machine space, while the WORKPIECE entity's own geometry "
        "placement AXIS2_PLACEMENT_3D sits at (0,0,0) — a 100 mm offset exists between "
        "the setup-implied workpiece origin and the actual workpiece geometry origin; "
        "per ISO 10303-238 §5.4 the setup placement transform maps workpiece-local coordinates "
        "to machine coordinates; no reconciling entity bridges the 100 mm discrepancy; "
        "toolpath computed in workpiece-local coordinates is executed by controller against "
        "the setup-implied origin at (100,0,0), but the workpiece sits at (0,0,0) — "
        "every toolpath position is 100 mm off from the actual workpiece; "
        "part is machined in the wrong location — tool misses the workpiece or gouges fixture; "
        "kernel must detect the inconsistency between setup and workpiece placements; "
        "reject as malformed or warn that toolpath origin is ambiguous; "
        "synonyms: AP238 setup vs part origin mismatch, fixture coordinate confusion, "
        "workpiece origin wrong in setup, setup placement contradicts workpiece axis, "
        "AP238 setup origin wrong, fixture transform doesn't match workpiece"
    ),
    schema="AP242",
)


def _render_m094() -> str:
    """Render AP238 file with SETUP placement inconsistent with workpiece placement.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       CARTESIAN_POINT origin (0,0,0) — workpiece geometry placement
      #21       DIRECTION z-axis
      #22       DIRECTION x-axis
      #23       AXIS2_PLACEMENT_3D at (0,0,0) — workpiece geometry placement
      #30       CARTESIAN_POINT (100,0,0) — setup machine-space origin
      #31       DIRECTION z-axis for setup
      #32       DIRECTION x-axis for setup
      #33       AXIS2_PLACEMENT_3D at (100,0,0) — setup placement (defect: offset from workpiece)
      #50       WORKPIECE referencing geometry placement #23
      #60       SETUP referencing placement #33 — DEFECT: (100,0,0) != workpiece (0,0,0)
      #70       MACHINING_WORKINGSTEP referencing the setup
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M094: AP238 setup placement inconsistent with workpiece coordinate system */")
    lines.append("/* DEFECT: SETUP placement origin (100,0,0) != WORKPIECE geometry origin (0,0,0) */")
    lines.append("/* 100 mm offset between setup-implied workpiece location and actual workpiece */")
    lines.append("/* Toolpath executes at wrong location — part machined 100 mm from intended position */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'SETUP') */")
    lines.append("/* Byte assertion: contains(b'AXIS2_PLACEMENT_3D') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M094: AP238 setup placement inconsistent with workpiece CS'),'2;1');")
    lines.append("FILE_NAME('M094.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Workpiece geometry placement at (0,0,0) — the actual part coordinate origin */")
    lines.append("#20=CARTESIAN_POINT('workpiece_origin',(0.,0.,0.));")
    lines.append("#21=DIRECTION('wp_z',(0.,0.,1.));")
    lines.append("#22=DIRECTION('wp_x',(1.,0.,0.));")
    lines.append("/* AXIS2_PLACEMENT_3D at (0,0,0): this is where the workpiece geometry lives */")
    lines.append("#23=AXIS2_PLACEMENT_3D('workpiece_placement',#20,#21,#22);")
    lines.append("/* Setup placement at (100,0,0) — machine-space position of workpiece origin */")
    lines.append("/* DEFECT: setup says workpiece sits at x=100 in machine space */")
    lines.append("/* But workpiece geometry placement (#23) says its origin is at (0,0,0) */")
    lines.append("#30=CARTESIAN_POINT('setup_machine_origin',(100.,0.,0.));")
    lines.append("#31=DIRECTION('setup_z',(0.,0.,1.));")
    lines.append("#32=DIRECTION('setup_x',(1.,0.,0.));")
    lines.append("/* Byte assertion: contains(b'AXIS2_PLACEMENT_3D') */")
    lines.append("/* DEFECT AXIS2_PLACEMENT_3D: setup claims workpiece origin is at (100,0,0) */")
    lines.append("/* This contradicts the workpiece entity's own placement at (0,0,0) */")
    lines.append("#33=AXIS2_PLACEMENT_3D('setup_placement',#30,#31,#32);")
    lines.append("/* WORKPIECE: the physical part being machined — geometry at (0,0,0) */")
    lines.append("#50=WORKPIECE('part_a',(#14),$,#23,$,$,$);")
    lines.append("/* Byte assertion: contains(b'SETUP') */")
    lines.append("/* SETUP: declares fixture mounting — claims workpiece origin at (100,0,0) */")
    lines.append("/* DEFECT: setup placement #33 at (100,0,0) disagrees with workpiece placement #23 at (0,0,0) */")
    lines.append("/* No relating entity reconciles the 100 mm offset */")
    lines.append("#60=SETUP('fixture_a',#33,(#50),$);")
    lines.append("/* Machining workingstep and workplan over the misplaced setup */")
    lines.append("#70=MACHINING_WORKINGSTEP('locate_step',$,$,$);")
    lines.append("#90=WORKPLAN('main',(#70),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-setup-placement-inconsistent-with-workpiece-cs',")
    lines.append("  (#23,#33,#50,#60,#70,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M094','M094','M094',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m094(path) -> None:
    Path(path).write_text(_render_m094())


f.render = _render_m094  # type: ignore[method-assign]
f.write = _write_m094    # type: ignore[method-assign]
