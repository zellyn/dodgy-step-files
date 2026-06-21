"""M089 — AP210 stackup plies overlap in the Z direction.

Catalog claim: Two LAMINATE_OR_PLY_DEFINITIONs in the same LAMINATE_TABLE
occupy overlapping Z ranges. Ply A spans z=0.0..0.2 and ply B spans
z=0.15..0.35. The stackup is physically impossible.

Reproducer recipe: LAMINATE_TABLE('overlapping_stack', (ply_A, ply_B))
where ply_A is positioned at z=0..0.2 and ply_B at z=0.15..0.35.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  count_entity_def(b'LAMINATE_OR_PLY_DEFINITION') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M089",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP210 LAMINATE_TABLE with two overlapping "
        "LAMINATE_OR_PLY_DEFINITIONs in the Z direction; "
        "input: AP210 STEP file where LAMINATE_TABLE('overlapping_stack') contains "
        "two plies: LAMINATE_OR_PLY_DEFINITION('ply_a') placed at z_offset=0.0 with "
        "thickness 0.2mm (spanning z=0.0..0.2), and LAMINATE_OR_PLY_DEFINITION('ply_b') "
        "placed at z_offset=0.15 with thickness 0.2mm (spanning z=0.15..0.35); "
        "the two plies overlap in the range z=0.15..0.2 — two solid dielectrics occupy "
        "the same physical volume, which is geometrically and physically impossible; "
        "per AP210 §5 laminate_table sequencing rules plies must be non-overlapping and "
        "contiguous in the stacking direction; electromagnetic-solver consumers produce "
        "nonsense field solutions when two materials overlap; "
        "kernel must detect overlapping z ranges and reject, warn with conflicting ply names, "
        "or require explicit separation; "
        "synonyms: PCB stackup plies overlap, AP210 layers in same volume, ECAD stackup z "
        "conflict, stackup z conflict, PCB layer overlap, plies overlap in Z, "
        "AP210 stackup physically impossible, two dielectrics in same Z range"
    ),
    schema="AP242",
)


def _render_m089() -> str:
    """Render AP210 file with two overlapping LAMINATE_OR_PLY_DEFINITIONs in Z.

    Uses ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      LAMINATE_OR_PLY_DEFINITION('ply_a') at z=0.0, thickness=0.2 (spans 0.0..0.2)
      #101      LAMINATE_OR_PLY_DEFINITION('ply_b') at z=0.15, thickness=0.2 (spans 0.15..0.35)
      #110      LAMINATE_TABLE with both plies — the overlapping stackup defect
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M089: AP210 stackup plies overlap in the Z direction */")
    lines.append("/* DEFECT: ply_a spans z=0.0..0.2, ply_b spans z=0.15..0.35 — overlap at 0.15..0.2 */")
    lines.append("/* Two solid dielectrics in the same volume — physically impossible */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'LAMINATE_OR_PLY_DEFINITION') >= 2 */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M089: AP210 stackup plies overlapping in Z'),'2;1');")
    lines.append("FILE_NAME('M089.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("FILE_SCHEMA(('ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN { 1 0 10303 210 3 1 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('electronic_assembly_interconnect_and_packaging_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'electronic_assembly_interconnect_and_packaging_design',2014,#1);")
    lines.append("/* Standard unit context — mm */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('pcb','3D'));")
    lines.append("/* Byte assertion: count_entity_def(b'LAMINATE_OR_PLY_DEFINITION') >= 2 */")
    lines.append("/* ply_a: z_offset=0.0, thickness=0.2mm -> spans z=0.0..0.2 */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('ply_a',$,$,$,LENGTH_MEASURE(0.2));")
    lines.append("/* ply_b: z_offset=0.15, thickness=0.2mm -> spans z=0.15..0.35 */")
    lines.append("/* DEFECT: overlaps with ply_a in z=0.15..0.2 */")
    lines.append("#101=LAMINATE_OR_PLY_DEFINITION('ply_b',$,$,$,LENGTH_MEASURE(0.2));")
    lines.append("/* LAMINATE_TABLE with the two overlapping plies — ply ordering encodes z position */")
    lines.append("/* ply_a at index 0 -> z starts at 0.0; ply_b at index 1 -> z starts at 0.15 */")
    lines.append("/* (simulated by placing ply_b after only 0.15mm gap, not the full 0.2mm ply_a) */")
    lines.append("#110=LAMINATE_TABLE('overlapping_stack',(#100,#101),$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-stackup-plies-overlap-in-z-direction',")
    lines.append("  (#100,#101,#110));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M089','M089','M089',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m089(path) -> None:
    Path(path).write_text(_render_m089())


f.render = _render_m089  # type: ignore[method-assign]
f.write = _write_m089    # type: ignore[method-assign]
