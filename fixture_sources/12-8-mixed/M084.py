"""M084 — AP209 composite laminate has empty ply stack.

Catalog claim: A LAMINATE_TABLE (intended to describe a multi-ply
composite stack) has an empty plies list. Computed bending stiffness is
zero; thin-shell elements using the laminate as their material have no
effective material at all.

Reproducer recipe: LAMINATE_TABLE('skin', (), coord_sys) with empty ply list.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'LAMINATE_TABLE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M084",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 LAMINATE_TABLE with empty ply stack; "
        "input: AP209 STEP file where LAMINATE_TABLE('skin', (), coord_sys) declares "
        "a multi-ply composite stack but the plies attribute is an empty list (); "
        "per ISO 10303-209 §8 composite_layup invariants a LAMINATE_TABLE must have "
        "at least one ply entry to be physically meaningful; "
        "an empty ply stack means computed bending stiffness is zero — thin-shell "
        "elements using this laminate as their material have no effective material; "
        "the FEM model with this laminate is infinitely flexible in bending; "
        "kernel must reject as malformed, or warn and treat as a single isotropic "
        "effective ply rather than silently using zero stiffness; "
        "synonyms: composite has no plies, FEM laminate empty, AP209 carbon-fiber stack "
        "zero stiffness, AP209 laminate stack zero entries, LAMINATE_TABLE empty, "
        "composite stack has no layers"
    ),
    schema="AP242",
)


def _render_m084() -> str:
    """Render AP209 file with LAMINATE_TABLE declaring empty ply list.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      PROPERTY_DEFINITION (placeholder material reference)
      #110      LAYERED_2D_ELEMENT_COORDINATE_SYSTEM (coordinate system for the laminate)
      #120      LAMINATE_TABLE('skin', (), #110) — the defect: empty ply list
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M084: AP209 composite laminate has empty ply stack */")
    lines.append("/* DEFECT: LAMINATE_TABLE('skin', (), coord_sys) — empty plies list */")
    lines.append("/* Empty ply stack: zero bending stiffness; FEM elements have no material */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'LAMINATE_TABLE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M084: AP209 composite laminate with empty ply stack'),'2;1');")
    lines.append("FILE_NAME('M084.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("FILE_SCHEMA(('STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('structural_analysis_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'structural_analysis_design',2001,#1);")
    lines.append("/* Standard unit context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('composite','3D'));")
    lines.append("/* Placeholder material reference for context */")
    lines.append("#100=PROPERTY_DEFINITION('cfrp','carbon-epoxy ply',$);")
    lines.append("/* Laminate coordinate system */")
    lines.append("#110=LAYERED_2D_ELEMENT_COORDINATE_SYSTEM($);")
    lines.append("/* Byte assertion: contains(b'LAMINATE_TABLE') */")
    lines.append("/* DEFECT: LAMINATE_TABLE with empty plies list — no plies in the stack */")
    lines.append("/* plies=() means zero stiffness; any shell element using 'skin' has no material */")
    lines.append("#120=LAMINATE_TABLE('skin',(),#110);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap209-composite-laminate-empty-ply-stack',")
    lines.append("  (#100,#110,#120));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M084','M084','M084',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m084(path) -> None:
    Path(path).write_text(_render_m084())


f.render = _render_m084  # type: ignore[method-assign]
f.write = _write_m084    # type: ignore[method-assign]
