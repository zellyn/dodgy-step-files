"""M074 — AP238 left-handed setup coordinate frame on multi-axis machine.

Catalog claim: A SETUP's csys is built from an AXIS2_PLACEMENT_3D whose
axis (Z) and ref_direction (X) yield Y = Z × X pointing in the opposite
direction from the intended right-handed Y. On a 3-axis machine the
consequence is a mirrored part; on a 5-axis machine, all rotary motions
invert and the resulting geometry is the geometric mirror of the design.

Reproducer recipe: AXIS2_PLACEMENT_3D with axis = DIRECTION(0,0,-1)
and ref_direction = DIRECTION(1,0,0) used as a setup origin; combined
with a multi-axis MACHINING_WORKINGSTEP.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MACHINING_WORKINGSTEP')
  contains(b'SETUP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M074",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where SETUP csys AXIS2_PLACEMENT_3D "
        "has Z-axis DIRECTION(0,0,-1) and ref_direction DIRECTION(1,0,0), yielding "
        "Y = Z × X = (0,-1,0) — a left-handed coordinate frame; "
        "input: AP238 STEP-NC file where SETUP('part_setup') uses AXIS2_PLACEMENT_3D "
        "with axis = DIRECTION('z_inverted',(0.0,0.0,-1.0)) and "
        "ref_direction = DIRECTION('x',(1.0,0.0,0.0)); "
        "implicit Y = Z × X = (0,0,-1) × (1,0,0) = (0,-1,0) is anti-parallel to +Y, "
        "making the frame left-handed rather than right-handed; "
        "on a 3-axis machine this mirrors the part; on a 5-axis machine all rotary "
        "motions invert and the resulting geometry is the mirror of the design; "
        "AP238 §3 requires setup coordinate frames to be right-handed; "
        "kernel must validate handedness via cross-product sign and reject as malformed "
        "or honor the explicit frame and warn; "
        "synonyms: mirrored toolpath, left-handed coordinate system, "
        "axis2_placement Z flipped, 5-axis output is reflection of design"
    ),
    schema="AP242",
)


def _render_m074() -> str:
    """Render AP238 STEP-NC file with left-handed SETUP coordinate frame.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context
      #20-#23   AXIS2_PLACEMENT_3D with left-handed Z-axis (the defect)
      #30       SETUP referencing the bad csys
      #40       MACHINING_WORKINGSTEP
      #50       GEOMETRIC_CURVE_SET model entity
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M074: AP238 left-handed setup coordinate frame on multi-axis machine */")
    lines.append("/* DEFECT: AXIS2_PLACEMENT_3D with axis (0,0,-1) yields left-handed Y = Z x X = (0,-1,0) */")
    lines.append("/* On 5-axis machine: all rotary motions invert, part is mirror of design */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_WORKINGSTEP') */")
    lines.append("/* Byte assertion: contains(b'SETUP') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M074: AP238 left-handed setup csys on 5-axis machine'),'2;1');")
    lines.append("FILE_NAME('M074.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Setup origin */")
    lines.append("#20=CARTESIAN_POINT('setup_origin',(0.0,0.0,0.0));")
    lines.append("/* DEFECT: Z-axis direction is (0,0,-1) — negated Z */")
    lines.append("/* Implied Y = Z x X = (0,0,-1) x (1,0,0) = (0,-1,0) — left-handed frame */")
    lines.append("#21=DIRECTION('z_inverted',(0.0,0.0,-1.0));")
    lines.append("#22=DIRECTION('x',(1.0,0.0,0.0));")
    lines.append("/* AXIS2_PLACEMENT_3D: axis=(0,0,-1), ref_direction=(1,0,0) => left-handed */")
    lines.append("#23=AXIS2_PLACEMENT_3D('setup_csys',#20,#21,#22);")
    lines.append("/* Byte assertion: contains(b'SETUP') */")
    lines.append("/* SETUP referencing the left-handed csys */")
    lines.append("#30=SETUP('part_setup',$,$,$,#23);")
    lines.append("/* Byte assertion: contains(b'MACHINING_WORKINGSTEP') */")
    lines.append("/* MACHINING_WORKINGSTEP — 5-axis workingstep referencing the bad setup */")
    lines.append("#40=MACHINING_WORKINGSTEP('ws1',$,$,$,#30);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#50=GEOMETRIC_CURVE_SET('ap238-left-handed-setup-csys-5axis-mirror',")
    lines.append("  (#20,#23,#30));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M074','M074','M074',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#50),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m074(path) -> None:
    Path(path).write_text(_render_m074())


f.render = _render_m074  # type: ignore[method-assign]
f.write = _write_m074    # type: ignore[method-assign]
