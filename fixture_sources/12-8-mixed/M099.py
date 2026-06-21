"""M099 — AP238 tool feedrate declared as zero.

Catalog claim: A MACHINING_TOOL_FEEDSPEED carries a zero feed-rate value
during a cutting move (not a dwell). The controller dwells indefinitely with
the spindle running, work-hardening the chip-contact zone or burning the tool.

Reproducer recipe: MACHINING_TOOL_FEEDSPEED($, MEASURE_WITH_UNIT(
POSITIVE_RATIO_MEASURE(0.0), mm_per_min_unit), $).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MACHINING_TOOL_FEEDSPEED')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M099",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 MACHINING_TOOL_FEEDSPEED with zero feedrate "
        "on a cutting move — POSITIVE_RATIO_MEASURE(0.0) mm/min violates ISO 10303-238 §5.8 "
        "feedspeed positivity invariant; "
        "input: AP238 STEP-NC file where MACHINING_TOOL_FEEDSPEED on a MACHINING_OPERATION "
        "('cut_face') declares its feedrate as MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(0.0), "
        "mm_per_min_unit) — a zero feed value on a cutting (non-dwell) operation; "
        "per ISO 10303-238 §5.8 the feedspeed positivity invariant requires feedrate > 0 "
        "for any cutting operation; POSITIVE_RATIO_MEASURE(0.0) additionally violates "
        "the POSITIVE_RATIO_MEASURE domain constraint which requires strictly positive values; "
        "this defect arises from a CAM exporter losing the feedrate value during template "
        "flattening — the feedrate field is present but initialized to 0.0 instead of the "
        "intended cutting feed; "
        "a CNC controller encountering zero feedrate on a cutting move dwells indefinitely "
        "with the spindle running, work-hardening the chip-contact zone or burning the tool "
        "and the workpiece surface; "
        "kernel must reject zero feedrate on cutting moves; warn that operation will dwell; "
        "synonyms: feedrate zero, STEP-NC dwell during cut, missing feed value, "
        "AP238 zero feedrate, tool stops mid-cut, STEP-NC feedrate missing during cut"
    ),
    schema="AP242",
)


def _render_m099() -> str:
    """Render AP238 file with MACHINING_TOOL_FEEDSPEED set to zero feedrate.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20       SI_UNIT for length (mm) — used as feedrate unit base
      #21       MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(0.0), mm_unit) — DEFECT: zero feed
      #22       MACHINING_TOOL_FEEDSPEED with the zero feedrate — DEFECT
      #50       MACHINED_FEATURE 'face_d'
      #60       MACHINING_TOOL 'facemill_50mm'
      #70       MACHINING_OPERATION referencing #22 (zero feedspeed) as its feed
      #80       MACHINING_WORKINGSTEP wrapping the operation
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M099: AP238 tool feedrate declared as zero on a cutting move */")
    lines.append("/* DEFECT: MACHINING_TOOL_FEEDSPEED carries POSITIVE_RATIO_MEASURE(0.0) */")
    lines.append("/* Zero feedrate on cutting move causes indefinite dwell — tool burns workpiece */")
    lines.append("/* Violates ISO 10303-238 §5.8 feedspeed positivity invariant */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_TOOL_FEEDSPEED') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M099: AP238 MACHINING_TOOL_FEEDSPEED with zero feedrate'),'2;1');")
    lines.append("FILE_NAME('M099.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Feed rate unit base: mm (per minute implied by usage context) */")
    lines.append("#20=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("/* Byte assertion: contains(b'MACHINING_TOOL_FEEDSPEED') */")
    lines.append("/* DEFECT: POSITIVE_RATIO_MEASURE(0.0) — zero feedrate on cutting move */")
    lines.append("/* POSITIVE_RATIO_MEASURE domain requires strictly positive values > 0 */")
    lines.append("/* Zero feed causes controller to dwell indefinitely during cut */")
    lines.append("#21=MEASURE_WITH_UNIT(POSITIVE_RATIO_MEASURE(0.0),#20);")
    lines.append("/* MACHINING_TOOL_FEEDSPEED wrapping the zero feed measure */")
    lines.append("#22=MACHINING_TOOL_FEEDSPEED($,#21,$);")
    lines.append("/* Target machined feature — a face milling pass */")
    lines.append("#50=MACHINED_FEATURE('face_d',$,$,$,$,$);")
    lines.append("/* 50mm face mill — will burn if feedrate is zero */")
    lines.append("#60=MACHINING_TOOL('facemill_50mm',$,$,$);")
    lines.append("/* MACHINING_OPERATION references zero feedspeed #22 — DEFECT propagation */")
    lines.append("/* Controller dwells at each point in the toolpath with spindle running */")
    lines.append("#70=MACHINING_OPERATION('cut_face',#60,#22,$,$,$,$,$,#50,$,$);")
    lines.append("#80=MACHINING_WORKINGSTEP('face_step',#50,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-tool-feedrate-zero-on-cutting-move',")
    lines.append("  (#21,#22,#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M099','M099','M099',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m099(path) -> None:
    Path(path).write_text(_render_m099())


f.render = _render_m099  # type: ignore[method-assign]
f.write = _write_m099    # type: ignore[method-assign]
