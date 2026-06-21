"""M189 — AP238 boring tool diameter declared as negative

Catalog claim: A BORING_TOOL's diameter MEASURE_WITH_UNIT carries a negative
value (-12.0 mm). The controller either rejects the file or computes a
negative-radius offset toolpath, sending the boring bar in the wrong direction.

Reproducer recipe: BORING_TOOL whose diameter is
MEASURE_WITH_UNIT(LENGTH_MEASURE(-12.0), mm_unit).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'BORING_TOOL')
  contains(b'-12.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M189",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where BORING_TOOL "
        "declares a negative diameter via MEASURE_WITH_UNIT(LENGTH_MEASURE(-12.0), mm_unit); "
        "input: AP238 STEP-NC file containing a WORKPLAN with a boring operation; "
        "the BORING_TOOL 'boring_bar_12mm' declares diameter LENGTH_MEASURE(-12.0) mm; "
        "a negative tool diameter is physically meaningless — tool dimensions must be positive; "
        "the controller either rejects the file outright at load time; "
        "or computes a negative-radius offset toolpath, sending the boring bar in the wrong direction; "
        "negative-radius offset causes the tool to move away from the bore center instead of towards it; "
        "per ISO 10303-238 §5.7 boring_tool diameter-positivity invariant: "
        "tool diameter must be a positive value; "
        "kernel must reject negative tool diameters as malformed; "
        "synonyms: AP238 boring bar negative diameter, STEP-NC bore tool size below zero, "
        "negative tool dimension, AP238 boring tool negative diameter, "
        "STEP-NC tool dimension below zero, boring bar negative size, "
        "AP238 boring tool negative size, STEP-NC bore-bar diameter < 0, "
        "negative boring tool dimension, tool size below zero on boring op"
    ),
    schema="AP242",
)


def _render_m189() -> str:
    """Render AP238 STEP-NC file with BORING_TOOL declaring negative diameter -12.0 mm.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #30       BORING_TOOL 'boring_bar_12mm' — DEFECT: diameter = -12.0 mm
      #31       MEASURE_WITH_UNIT for diameter = LENGTH_MEASURE(-12.0) — DEFECT: negative
      #40       BORING_OPERATION 'bore_op' — uses boring_bar_12mm
      #50       MACHINING_WORKINGSTEP 'bore_step'
      #60       WORKPIECE 'bore_workpiece'
      #70       WORKPLAN 'negative_diameter_boring_program'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M189: AP238 BORING_TOOL diameter declared as negative (-12.0 mm) */")
    lines.append("/* DEFECT: BORING_TOOL 'boring_bar_12mm' diameter = LENGTH_MEASURE(-12.0) */")
    lines.append("/* Negative tool diameter is physically meaningless — must be positive */")
    lines.append("/* Controller rejects file or computes negative-radius offset toolpath */")
    lines.append("/* Negative-radius offset: boring bar moves away from bore center — wrong direction */")
    lines.append("/* Per ISO 10303-238 §5.7 boring_tool diameter-positivity invariant */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'BORING_TOOL') */")
    lines.append("/* Byte assertion: contains(b'-12.0') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M189: AP238 BORING_TOOL diameter LENGTH_MEASURE(-12.0) negative value'),'2;1');")
    lines.append("FILE_NAME('M189.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-boring-tool-negative-diameter',")
    lines.append("  (#30,#40,#50,#60));")
    lines.append("/* Byte assertion: contains(b'BORING_TOOL') */")
    lines.append("/* Byte assertion: contains(b'-12.0') */")
    lines.append("/* DEFECT: BORING_TOOL 'boring_bar_12mm' with diameter LENGTH_MEASURE(-12.0) mm */")
    lines.append("/* Negative diameter is physically meaningless — positivity invariant violated */")
    lines.append("#31=MEASURE_WITH_UNIT(LENGTH_MEASURE(-12.0),#15);")
    lines.append("#30=BORING_TOOL('boring_bar_12mm',$,#31,$,$,$,$,$,$);")
    lines.append("/* BORING_OPERATION 'bore_op': uses boring_bar_12mm with negative diameter */")
    lines.append("#40=BORING_OPERATION('bore_op',$,$,$,$,$,#30,$,$,$,$,$,$);")
    lines.append("/* WORKPIECE 'bore_workpiece' */")
    lines.append("#60=WORKPIECE('bore_workpiece','Workpiece for negative diameter boring test',$,$,$,$,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'bore_step' */")
    lines.append("#50=MACHINING_WORKINGSTEP('bore_step','Boring with negative diameter tool',#40,#60,$);")
    lines.append("/* WORKPLAN: boring operation with negative tool diameter — malformed */")
    lines.append("#70=WORKPLAN('negative_diameter_boring_program','Negative diameter boring workplan',(),$,(#50));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M189','M189','M189',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m189(path) -> None:
    Path(path).write_text(_render_m189())


f.render = _render_m189  # type: ignore[method-assign]
f.write = _write_m189    # type: ignore[method-assign]
