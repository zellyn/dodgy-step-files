"""M104 — AP238 producer emits SETUP where WORKPIECE_SETUP is required.

Catalog claim: AP238 distinguishes SETUP (machine-fixture configuration:
vise, palette, tombstone) from WORKPIECE_SETUP (workpiece-on-fixture
placement and clamping). A producer emits a single SETUP and references it
from contexts that expect a WORKPIECE_SETUP. Consumers conflate the two
and lose either the fixture geometry or the workpiece-clamp data.

Reproducer recipe: A MACHINING_WORKINGSTEP's its_setup attribute
references a SETUP (rather than the WORKPIECE_SETUP per AP238 schema).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'SETUP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M104",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 MACHINING_WORKINGSTEP whose its_setup attribute "
        "references a SETUP entity where a WORKPIECE_SETUP is required; "
        "input: AP238 STEP-NC file where MACHINING_WORKINGSTEP('face_step') carries "
        "its_setup referencing SETUP('vise_config') — a machine-fixture configuration entity; "
        "per ISO 10303-238 §5.4 the its_setup attribute of MACHINING_WORKINGSTEP must reference "
        "a WORKPIECE_SETUP (workpiece-on-fixture placement and clamping data), not a bare SETUP "
        "(which describes machine-fixture configuration: vise type, palette, tombstone geometry); "
        "AP238 distinguishes these two entity types: SETUP captures fixture configuration, "
        "WORKPIECE_SETUP captures workpiece placement relative to fixture including clamp data; "
        "a consumer receiving SETUP where WORKPIECE_SETUP is expected either conflates the two "
        "and loses workpiece clamp data, or rejects the file, or loses fixture geometry; "
        "the workpiece-on-fixture placement becomes undefined, causing incorrect tool-origin offset; "
        "kernel must detect type mismatch; reject or coerce with diagnostic; "
        "synonyms: setup type mismatch, AP238 fixture vs workpiece confusion, "
        "SETUP used where WORKPIECE_SETUP needed, AP238 wrong setup class"
    ),
    schema="AP242",
)


def _render_m104() -> str:
    """Render AP238 file with MACHINING_WORKINGSTEP.its_setup referencing SETUP not WORKPIECE_SETUP.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       SETUP 'vise_config' — machine-fixture configuration — DEFECT: wrong type
      #55       MACHINED_FEATURE 'face_d'
      #60       MACHINING_TOOL 'facemill_50mm'
      #70       MACHINING_OPERATION referencing #60 and #55
      #80       MACHINING_WORKINGSTEP with its_setup=#50 (SETUP) — DEFECT: should be WORKPIECE_SETUP
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M104: AP238 SETUP emitted where WORKPIECE_SETUP is required */")
    lines.append("/* DEFECT: MACHINING_WORKINGSTEP.its_setup references SETUP not WORKPIECE_SETUP */")
    lines.append("/* SETUP = machine-fixture config; WORKPIECE_SETUP = workpiece-on-fixture placement */")
    lines.append("/* Consumers lose workpiece clamp data or fixture geometry — wrong tool-origin offset */")
    lines.append("/* Violates ISO 10303-238 §5.4 setup vs workpiece_setup distinction */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'SETUP') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M104: AP238 SETUP where WORKPIECE_SETUP required'),'2;1');")
    lines.append("FILE_NAME('M104.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Byte assertion: contains(b'SETUP') */")
    lines.append("/* DEFECT: SETUP entity for machine-fixture configuration (vise on tombstone) */")
    lines.append("/* This should be WORKPIECE_SETUP (workpiece-on-fixture placement with clamp data) */")
    lines.append("/* The publisher merged both concepts into a single SETUP entity — type mismatch */")
    lines.append("#50=SETUP('vise_config',$,$,$);")
    lines.append("/* Target machined feature — a face milling pass */")
    lines.append("#55=MACHINED_FEATURE('face_d',$,$,$,$,$);")
    lines.append("/* 50mm face mill */")
    lines.append("#60=MACHINING_TOOL('facemill_50mm',$,$,$);")
    lines.append("/* Machining operation for face milling */")
    lines.append("#70=MACHINING_OPERATION('face_op',#60,$,$,$,$,$,$,#55,$,$);")
    lines.append("/* DEFECT: MACHINING_WORKINGSTEP.its_setup references SETUP #50 */")
    lines.append("/* Per AP238 §5.4 its_setup must reference WORKPIECE_SETUP, not bare SETUP */")
    lines.append("/* Correct fix: replace #50 with WORKPIECE_SETUP('vise_config_wp',...) */")
    lines.append("#80=MACHINING_WORKINGSTEP('face_step',#55,#70,#50);")
    lines.append("/* WORKPLAN referencing the workingstep with the mistyped setup reference */")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-setup-emitted-where-workpiece-setup-required',")
    lines.append("  (#50,#55,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M104','M104','M104',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m104(path) -> None:
    Path(path).write_text(_render_m104())


f.render = _render_m104  # type: ignore[method-assign]
f.write = _write_m104    # type: ignore[method-assign]
