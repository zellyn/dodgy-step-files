"""M177 — AP238 coolant_operation requests through-tool flow on tool with no internal cooling

Catalog claim: A COOLANT_OPERATION specifies through-spindle /
through-tool coolant delivery, but the referenced milling tool has no
internal-cooling channel attribute. Activating through-tool flood on a
solid-shank tool either floods the spindle bearings or stalls the
coolant pump.

Reproducer recipe: a MILLING_CUTTING_TOOL declared without an
internal_cooling attribute; a COOLANT_OPERATION with mode .THROUGH_TOOL.
targeting that tool.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'COOLANT_OPERATION')
  contains(b'.THROUGH_TOOL.')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M177",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where COOLANT_OPERATION specifies "
        ".THROUGH_TOOL. coolant delivery mode on a MILLING_CUTTING_TOOL with no "
        "internal_cooling channel attribute; "
        "input: AP238 STEP-NC file containing a WORKPLAN for a milling operation; "
        "the MILLING_CUTTING_TOOL 'solid_endmill' has no internal_cooling attribute declared "
        "(all coolant-channel fields are null — it is a solid-shank tool); "
        "the COOLANT_OPERATION 'thru_tool_coolant' specifies coolant_type .THROUGH_TOOL. "
        "targeting solid_endmill; "
        "activating through-tool flood on a solid-shank tool without internal channels "
        "either floods the spindle bearings or stalls the coolant pump; "
        "per ISO 10303-238 §5.8 coolant-mode capability must be cross-checked against tool attributes; "
        "kernel must validate coolant-mode capability against tool attributes and reject; "
        "synonyms: AP238 through-tool coolant on solid shank, STEP-NC coolant floods spindle, "
        "tool has no internal channel, AP238 through-tool on solid endmill, "
        "STEP-NC coolant capability mismatch, internal cooling not declared, "
        "coolant through-tool stalls pump, AP238 coolant capability mismatch"
    ),
    schema="AP242",
)


def _render_m177() -> str:
    """Render AP238 STEP-NC file with COOLANT_OPERATION .THROUGH_TOOL. on tool with no channel.

    Entity layout:
      #10-#14   Unit context (mm)
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN 'thru_tool_coolant_program' — AP238 top-level NC program
      #51       MACHINING_WORKINGSTEP 'coolant_step'
      #52       MILLING_OPERATION 'mill_with_thru_coolant'
      #53       COOLANT_OPERATION 'thru_tool_coolant' — DEFECT: .THROUGH_TOOL. on solid-shank tool
      #54       MILLING_CUTTING_TOOL 'solid_endmill' — DEFECT: no internal_cooling channel
      #60       WORKPIECE 'coolant_workpiece'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M177: AP238 coolant_operation requests through-tool flow on tool with no internal cooling */")
    lines.append("/* DEFECT: COOLANT_OPERATION mode .THROUGH_TOOL. on MILLING_CUTTING_TOOL with no channel */")
    lines.append("/* MILLING_CUTTING_TOOL 'solid_endmill' is solid-shank — no internal cooling channels */")
    lines.append("/* Through-tool coolant on solid shank floods spindle bearings or stalls coolant pump */")
    lines.append("/* Per ISO 10303-238 §5.8 coolant capability must be cross-checked against tool attributes */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'COOLANT_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'.THROUGH_TOOL.') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M177: AP238 coolant_operation THROUGH_TOOL on solid-shank tool'),'2;1');")
    lines.append("FILE_NAME('M177.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-coolant-operation-through-tool-on-solid-shank',")
    lines.append("  (#52,#54,#60));")
    lines.append("/* DEFECT: MILLING_CUTTING_TOOL 'solid_endmill' — no internal_cooling channels declared */")
    lines.append("/* All cooling-channel fields are null — this is a solid-shank endmill */")
    lines.append("#54=MILLING_CUTTING_TOOL('solid_endmill',$,$,$,$,$,$,$,$);")
    lines.append("/* Byte assertion: contains(b'COOLANT_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'.THROUGH_TOOL.') */")
    lines.append("/* DEFECT: COOLANT_OPERATION with coolant_type .THROUGH_TOOL. on solid-shank tool */")
    lines.append("#53=COOLANT_OPERATION('thru_tool_coolant',.THROUGH_TOOL.,$);")
    lines.append("/* MILLING_OPERATION 'mill_with_thru_coolant' references both tool and coolant op */")
    lines.append("#52=MILLING_OPERATION('mill_with_thru_coolant',$,$,$,$,$,#53,#54,$,$,$,$,$);")
    lines.append("/* WORKPIECE 'coolant_workpiece' */")
    lines.append("#60=WORKPIECE('coolant_workpiece','Workpiece for through-tool coolant test',$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP links milling op to workpiece */")
    lines.append("#51=MACHINING_WORKINGSTEP('coolant_step','Through-tool coolant milling step',#52,#60,$);")
    lines.append("/* WORKPLAN: single milling step with through-tool coolant on solid-shank tool */")
    lines.append("#50=WORKPLAN('thru_tool_coolant_program','Through-tool coolant workplan',(),$,(#51));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M177','M177','M177',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m177(path) -> None:
    Path(path).write_text(_render_m177())


f.render = _render_m177  # type: ignore[method-assign]
f.write = _write_m177    # type: ignore[method-assign]
