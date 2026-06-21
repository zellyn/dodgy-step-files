"""M093 — AP238 machining_tool referenced without cutting-edge geometry.

Catalog claim: A MACHINING_OPERATION references a tool by id, and the
referenced entity is a bare MACHINING_TOOL shell with no associated
CUTTING_TOOL geometry, no diameter, no flute count. The controller has no
way to compute kinematics.

Reproducer recipe: MACHINING_TOOL('end_mill_10mm',$,$,$) referenced by
a MACHINING_OPERATION, with no associated CUTTING_TOOL_BODY /
MILLING_TOOL_DIMENSION providing the diameter and edges.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MACHINING_OPERATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M093",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 MACHINING_OPERATION referencing a bare "
        "MACHINING_TOOL stub with no CUTTING_TOOL geometry, diameter, or flute count; "
        "input: AP238 STEP-NC file where MACHINING_OPERATION('mill_slot') references "
        "MACHINING_TOOL('end_mill_10mm', $, $, $) — the tool entity has all optional "
        "attributes as NULL ($): no cutting_edges list, no CUTTING_TOOL_BODY, no "
        "MILLING_TOOL_DIMENSION providing diameter or number of flutes; "
        "per ISO 10303-238 §5.7 cutting_tool geometric attribution a tool referenced in "
        "an executable workingstep must carry complete geometric definition so a controller "
        "can compute kinematic offsets, feedrate, and cutter compensation; "
        "a bare MACHINING_TOOL stub provides only a name — no diameter for cutter "
        "compensation, no flute count for chip-load, no cutting geometry for verification; "
        "kernel must validate tool definitions are geometrically complete before accepting "
        "a workplan that references them; reject the workplan or warn that the tool is a "
        "placeholder; "
        "synonyms: tool stub, AP238 missing cutting edges, tool body geometry absent, "
        "STEP-NC tool has no geometry, AP238 cutting tool body empty, "
        "tool referenced but undefined"
    ),
    schema="AP242",
)


def _render_m093() -> str:
    """Render AP238 file with MACHINING_OPERATION referencing bare MACHINING_TOOL stub.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       MACHINED_FEATURE 'slot_a'
      #60       MACHINING_TOOL('end_mill_10mm',$,$,$) — bare stub, no geometry — defect
      #70       MACHINING_OPERATION('mill_slot') referencing stub tool #60
      #80       MACHINING_WORKINGSTEP wrapping the operation
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M093: AP238 machining_tool referenced without cutting-edge geometry */")
    lines.append("/* DEFECT: MACHINING_OPERATION references MACHINING_TOOL with all attrs NULL */")
    lines.append("/* No diameter, no flute count, no cutting geometry — tool is a bare name stub */")
    lines.append("/* Controller cannot compute cutter compensation or feedrate from stub tool */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_OPERATION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M093: AP238 MACHINING_TOOL stub without cutting-edge geometry'),'2;1');")
    lines.append("FILE_NAME('M093.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Target machined feature for the slot operation */")
    lines.append("#50=MACHINED_FEATURE('slot_a',$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'MACHINING_OPERATION') */")
    lines.append("/* DEFECT: MACHINING_TOOL with all optional attributes NULL — bare name stub */")
    lines.append("/* No cutting_edges, no CUTTING_TOOL_BODY, no MILLING_TOOL_DIMENSION */")
    lines.append("/* Tool name 'end_mill_10mm' implies 10mm diameter — but no geometry confirms it */")
    lines.append("#60=MACHINING_TOOL('end_mill_10mm',$,$,$);")
    lines.append("/* MACHINING_OPERATION references the stub tool #60 */")
    lines.append("/* Controller must know tool diameter for cutter compensation — impossible with stub */")
    lines.append("#70=MACHINING_OPERATION('mill_slot',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* Workingstep and workplan wrapping the operation */")
    lines.append("#80=MACHINING_WORKINGSTEP('slot_step',#50,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-machining-tool-stub-no-cutting-edge-geometry',")
    lines.append("  (#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M093','M093','M093',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m093(path) -> None:
    Path(path).write_text(_render_m093())


f.render = _render_m093  # type: ignore[method-assign]
f.write = _write_m093    # type: ignore[method-assign]
