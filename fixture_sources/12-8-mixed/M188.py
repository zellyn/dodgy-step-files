"""M188 — AP238 deburring_operation references edge not present in workpiece

Catalog claim: A DEBURRING_OPERATION references an edge feature that isn't
part of the WORKPIECE's geometry. The deburring path is computed against a
phantom edge; the tool either swings into empty space or contacts the workpiece
in an unintended location.

Reproducer recipe: a WORKPIECE whose declared edges are #500 and #501; a
DEBURRING_OPERATION whose target edge is #510 (declared in file but not part
of the workpiece's edge list).

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'DEBURRING_OPERATION')
  contains(b'phantom_edge_NOT_ON_PART')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M188",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where DEBURRING_OPERATION "
        "references an edge feature that is not part of the workpiece geometry; "
        "input: AP238 STEP-NC file containing a WORKPLAN with a deburring operation; "
        "the WORKPIECE 'machined_block' declares edge list referencing #500 and #501 only; "
        "EDGE_FEATURE 'workpiece_edge_A' (#500) and 'workpiece_edge_B' (#501) are on the part; "
        "EDGE_FEATURE 'phantom_edge_NOT_ON_PART' (#510) is declared in the file but NOT in workpiece edge list; "
        "the DEBURRING_OPERATION 'deburr_phantom_op' targets edge #510 — the phantom edge; "
        "the deburring path is computed against a phantom edge not belonging to the workpiece; "
        "the tool either swings into empty space or contacts the workpiece in an unintended location; "
        "per ISO 10303-238 §5.8 deburring_operation edge-presence invariant: "
        "the target edge of a deburring operation must be present in the workpiece's geometry; "
        "kernel must validate deburring-op edge reference against workpiece geometry; "
        "kernel must reject as malformed when target edge is not on workpiece; "
        "synonyms: AP238 deburring of phantom edge, STEP-NC deburr edge missing from part, "
        "phantom edge in deburring op, AP238 deburring edge not on part, "
        "STEP-NC phantom edge in deburring, deburr op references missing edge, "
        "AP238 deburring phantom edge, STEP-NC deburr edge missing from workpiece, "
        "deburring op references foreign edge, phantom edge in deburring sequence"
    ),
    schema="AP242",
)


def _render_m188() -> str:
    """Render AP238 STEP-NC file with DEBURRING_OPERATION targeting phantom edge not on workpiece.

    Entity layout:
      #10-#14   Unit context (mm)
      #15       mm length unit reference for MEASURE_WITH_UNIT
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #500      EDGE_FEATURE 'workpiece_edge_A' — valid edge on workpiece
      #501      EDGE_FEATURE 'workpiece_edge_B' — valid edge on workpiece
      #510      EDGE_FEATURE 'phantom_edge_NOT_ON_PART' — DEFECT: declared but not in workpiece edge list
      #40       WORKPIECE 'machined_block' — edge list only contains #500, #501 (not #510)
      #50       DEBURRING_OPERATION 'deburr_phantom_op' — DEFECT: targets #510 (phantom edge)
      #60       MACHINING_WORKINGSTEP 'deburr_step'
      #70       WORKPLAN 'phantom_edge_deburr_program'
      #100+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M188: AP238 DEBURRING_OPERATION references edge #510 not present in workpiece */")
    lines.append("/* DEFECT: workpiece edge list = {#500, #501}; deburring target = #510 (phantom) */")
    lines.append("/* Phantom edge #510 is declared in file but NOT part of workpiece geometry */")
    lines.append("/* Tool swings into empty space or contacts workpiece in unintended location */")
    lines.append("/* Per ISO 10303-238 §5.8 deburring_operation edge-presence invariant */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'DEBURRING_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'phantom_edge_NOT_ON_PART') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M188: AP238 DEBURRING_OPERATION targets phantom edge not on workpiece'),'2;1');")
    lines.append("FILE_NAME('M188.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-deburring-operation-phantom-edge-not-on-workpiece',")
    lines.append("  (#500,#501,#510,#40,#50,#60));")
    lines.append("/* EDGE_FEATURE 'workpiece_edge_A' (#500): valid edge on machined_block workpiece */")
    lines.append("#500=EDGE_FEATURE('workpiece_edge_A','Valid edge A on machined block',$,$);")
    lines.append("/* EDGE_FEATURE 'workpiece_edge_B' (#501): valid edge on machined_block workpiece */")
    lines.append("#501=EDGE_FEATURE('workpiece_edge_B','Valid edge B on machined block',$,$);")
    lines.append("/* Byte assertion: contains(b'phantom_edge_NOT_ON_PART') */")
    lines.append("/* DEFECT: EDGE_FEATURE 'phantom_edge_NOT_ON_PART' (#510): declared in file */")
    lines.append("/* but NOT listed in machined_block workpiece edge list — phantom edge */")
    lines.append("#510=EDGE_FEATURE('phantom_edge_NOT_ON_PART','Phantom edge not belonging to workpiece',$,$);")
    lines.append("/* WORKPIECE 'machined_block': edge list = {#500, #501} only — #510 is NOT included */")
    lines.append("#40=WORKPIECE('machined_block','Machined block with two valid edges',$,$,(#500,#501),$,$);")
    lines.append("/* Byte assertion: contains(b'DEBURRING_OPERATION') */")
    lines.append("/* DEFECT: DEBURRING_OPERATION 'deburr_phantom_op' targets #510 — phantom edge */")
    lines.append("/* #510 is not in workpiece edge list; deburring path against non-existent edge */")
    lines.append("#50=DEBURRING_OPERATION('deburr_phantom_op',$,$,$,$,$,$,$,$,$,$,#510,$);")
    lines.append("/* MACHINING_WORKINGSTEP 'deburr_step' */")
    lines.append("#60=MACHINING_WORKINGSTEP('deburr_step','Deburring phantom edge step',#50,#40,$);")
    lines.append("/* WORKPLAN: deburring operation on phantom edge not part of workpiece */")
    lines.append("#70=WORKPLAN('phantom_edge_deburr_program','Phantom edge deburring workplan',(),$,(#60));")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M188','M188','M188',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m188(path) -> None:
    Path(path).write_text(_render_m188())


f.render = _render_m188  # type: ignore[method-assign]
f.write = _write_m188    # type: ignore[method-assign]
