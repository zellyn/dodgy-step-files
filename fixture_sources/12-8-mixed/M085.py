"""M085 — AP210 ply with mismatched top/bottom material designations.

Catalog claim: A LAMINATE_OR_PLY_DEFINITION (one homogeneous layer in a
PCB stackup) is expected to have a single material across its thickness,
but its top and bottom material references point to different
MATERIAL_DESIGNATIONs (FR4 top, polyimide bottom).

Reproducer recipe: LAMINATE_OR_PLY_DEFINITION('core_ply', $, FR4_ref,
polyimide_ref, LENGTH_MEASURE(0.2)).

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'LAMINATE_OR_PLY_DEFINITION')
  count_entity_def(b'MATERIAL_DESIGNATION') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M085",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP210 LAMINATE_OR_PLY_DEFINITION with mismatched "
        "top and bottom MATERIAL_DESIGNATION references; "
        "input: AP210 STEP file where LAMINATE_OR_PLY_DEFINITION('core_ply') has its "
        "top material referencing MATERIAL_DESIGNATION('FR4','glass-epoxy laminate') and "
        "its bottom material referencing MATERIAL_DESIGNATION('polyimide','polyimide film'); "
        "per ISO 10303-210 §5 laminate_or_ply_definition invariants a single ply must be "
        "homogeneous — one material across its entire thickness; "
        "a ply with FR4 on top and polyimide on bottom is physically a transition film "
        "that should be modeled as two adjacent plies; "
        "kernel must detect the mismatch and either split the ply into two plies, "
        "reject, or honor only one of the two materials and warn; "
        "synonyms: PCB layer with split material, stackup ply inconsistent, "
        "AP210 ply has mismatched top/bottom material, transition film mislabeled as ply, "
        "ply has two different MATERIAL_DESIGNATIONs, PCB ply has two materials, "
        "AP210 stackup inconsistent, laminate top/bottom mismatch"
    ),
    schema="AP242",
)


def _render_m085() -> str:
    """Render AP210 file with LAMINATE_OR_PLY_DEFINITION having mismatched top/bottom materials.

    Uses ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      MATERIAL_DESIGNATION('FR4') — top material
      #101      MATERIAL_DESIGNATION('polyimide') — bottom material
      #110      LAMINATE_OR_PLY_DEFINITION with FR4 top, polyimide bottom — defect
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M085: AP210 ply with mismatched top/bottom material designations */")
    lines.append("/* DEFECT: LAMINATE_OR_PLY_DEFINITION('core_ply') has FR4 top and polyimide bottom */")
    lines.append("/* A single ply must be homogeneous; different top/bottom = transition film */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'LAMINATE_OR_PLY_DEFINITION') */")
    lines.append("/* Byte assertion: count_entity_def(b'MATERIAL_DESIGNATION') >= 2 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M085: AP210 laminate_or_ply mismatched top/bottom material'),'2;1');")
    lines.append("FILE_NAME('M085.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("FILE_SCHEMA(('ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN { 1 0 10303 210 3 1 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('electronic_assembly_interconnect_and_packaging_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'electronic_assembly_interconnect_and_packaging_design',2014,#1);")
    lines.append("/* Standard unit context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('pcb','3D'));")
    lines.append("/* Byte assertion: count_entity_def(b'MATERIAL_DESIGNATION') >= 2 */")
    lines.append("/* Two distinct MATERIAL_DESIGNATIONs — one for top, one for bottom of the ply */")
    lines.append("#100=MATERIAL_DESIGNATION('FR4','glass-epoxy laminate',(#1));")
    lines.append("#101=MATERIAL_DESIGNATION('polyimide','polyimide film',(#1));")
    lines.append("/* Byte assertion: contains(b'LAMINATE_OR_PLY_DEFINITION') */")
    lines.append("/* DEFECT: top_material=#100 (FR4), bottom_material=#101 (polyimide) */")
    lines.append("/* A single ply must be homogeneous (one material); this is a transition film */")
    lines.append("#110=LAMINATE_OR_PLY_DEFINITION('core_ply',$,#100,#101,")
    lines.append("  LENGTH_MEASURE(0.2));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-laminate-ply-mismatched-top-bottom-material',")
    lines.append("  (#100,#101,#110));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M085','M085','M085',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m085(path) -> None:
    Path(path).write_text(_render_m085())


f.render = _render_m085  # type: ignore[method-assign]
f.write = _write_m085    # type: ignore[method-assign]
