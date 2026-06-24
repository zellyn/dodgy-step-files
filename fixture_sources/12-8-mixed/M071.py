"""M071 — AP238 machining_operation references nonexistent process_aspect.

Catalog claim: A STEP-NC file's MACHINING_OPERATION cites a PROCESS_ASPECT
by id, but the referenced entity is missing or is a different schema type
(e.g. a CARTESIAN_POINT instead). Bug-reporter language: "STEP-NC dangling
reference", "AP238 process_aspect not found", "machining operation has no
feature to act on".

Reproducer recipe: MACHINING_OPERATION('drill_hole_a',$,$,$,$,#200)
where #200 is declared as CARTESIAN_POINT(..), not a PROCESS_ASPECT subtype.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'MACHINING_OPERATION')
  contains(b'WORKPLAN')

Tier-3: shape_null == False, n_vertices_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M071",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where MACHINING_OPERATION references "
        "CARTESIAN_POINT (#200) instead of a PROCESS_ASPECT subtype — dangling type mismatch; "
        "input: AP238 STEP-NC file where MACHINING_OPERATION('drill_hole_a',$,$,$,$,#200) "
        "cites entity #200 as its process_aspect reference, but #200 is declared as a "
        "CARTESIAN_POINT, not a PROCESS_ASPECT subtype; "
        "AP238 §4.5 process_aspect referencing rules require the referenced entity to be "
        "a PROCESS_ASPECT subtype; a CARTESIAN_POINT is not valid there; "
        "kernel must detect the type mismatch / unresolved reference and reject the operation "
        "as malformed, or warn and continue with the operation treated as having no feature; "
        "synonyms: AP238 broken reference, STEP-NC missing process aspect, "
        "machining_operation has no feature, STEP-NC dangling reference"
    ),
    schema="AP242",
)


def _render_m071() -> str:
    """Render AP238 STEP-NC file with MACHINING_OPERATION referencing wrong type.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #10-#14   Unit context
      #20       GEOMETRIC_CURVE_SET model entity (anchor for OCC empty result)
      #50       WORKPLAN (AP238)
      #51       MACHINING_WORKINGSTEP (AP238)
      #52       MACHINING_OPERATION — references #200 (CARTESIAN_POINT, not PROCESS_ASPECT)
      #100      Product chain
      #200      CARTESIAN_POINT (wrongly referenced as process_aspect by #52)
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M071: AP238 MACHINING_OPERATION references CARTESIAN_POINT instead of PROCESS_ASPECT */")
    lines.append("/* DEFECT: type mismatch — #200 is CARTESIAN_POINT, not a PROCESS_ASPECT subtype */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'MACHINING_OPERATION') */")
    lines.append("/* Byte assertion: contains(b'WORKPLAN') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M071: AP238 machining_operation references nonexistent process_aspect'),'2;1');")
    lines.append("FILE_NAME('M071.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 3 1 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
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
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#20=GEOMETRIC_CURVE_SET('ap238-machining-op-dangling-process-aspect',");
    lines.append("  (#200));")
    lines.append("/* Byte assertion: contains(b'WORKPLAN') */")
    lines.append("/* AP238 WORKPLAN — top-level program structure */")
    lines.append("#50=WORKPLAN('main_program','AP238 STEP-NC workplan',(),$,(#51));")
    lines.append("/* AP238 MACHINING_WORKINGSTEP — references the operation */")
    lines.append("#51=MACHINING_WORKINGSTEP('drill_step','drilling workingstep',#52,$,$);")
    lines.append("/* Byte assertion: contains(b'MACHINING_OPERATION') */")
    lines.append("/* MACHINING_OPERATION — last attribute is process_aspect reference: #200 */")
    lines.append("/* #200 is a CARTESIAN_POINT, not a PROCESS_ASPECT subtype — the defect */")
    lines.append("#52=MACHINING_OPERATION('drill_hole_a',$,$,$,$,#200);")
    lines.append("/* Product chain */")
    lines.append("#100=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#101=PRODUCT_CONTEXT('',#100,'mechanical');")
    lines.append("#102=PRODUCT('M071','M071','M071',(#101));")
    lines.append("#103=PRODUCT_DEFINITION_FORMATION('','',#102);")
    lines.append("#104=PRODUCT_DEFINITION_CONTEXT(#100,'design');")
    lines.append("#105=PRODUCT_DEFINITION('','',#103,#104);")
    lines.append("#106=PRODUCT_DEFINITION_SHAPE('','',#105);")
    lines.append("#107=SHAPE_REPRESENTATION('',(#20),#14);")
    lines.append("#108=SHAPE_DEFINITION_REPRESENTATION(#106,#107);")
    lines.append("/* #200 = CARTESIAN_POINT wrongly referenced as process_aspect by MACHINING_OPERATION */")
    lines.append("#200=CARTESIAN_POINT('drill_center',(25.,25.,0.));")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m071(path) -> None:
    Path(path).write_text(_render_m071())


f.render = _render_m071  # type: ignore[method-assign]
f.write = _write_m071    # type: ignore[method-assign]
