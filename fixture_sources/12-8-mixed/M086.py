"""M086 — AP210 via drilled outside the conductor / board outline.

Catalog claim: A VIA_DEFINITION's drill location places the via center
at a point outside the board outline / LAMINATE_OR_PLY_DEFINITION's
boundary. The drill physically misses the substrate.

Reproducer recipe: Board outline (0.30, 0.30) mm; VIA_DEFINITION
with axis center (50, 50, 0).

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'VIA_DEFINITION')
  contains(b'LAMINATE_OR_PLY_DEFINITION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M086",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP210 VIA_DEFINITION with drill location outside "
        "the board outline / LAMINATE_OR_PLY_DEFINITION boundary; "
        "input: AP210 STEP file where LAMINATE_OR_PLY_DEFINITION 'core' has a "
        "PLY_BOUNDARY_REPRESENTATION with a POLYLINE outline covering (0..30, 0..30) mm, "
        "but VIA_DEFINITION 'via_a' places its drill axis center at CARTESIAN_POINT(50.0, 50.0, 0.0) "
        "— well outside the 30x30 mm board outline; "
        "the via drill physically misses the substrate; it does not pierce any copper layer; "
        "per ISO 10303-210 §6 via_definition geometric containment the via location must "
        "lie within the ply boundary; downstream impedance and continuity checks fail "
        "because the via path does not intersect any conductor; "
        "kernel must validate via location against ply outlines; "
        "reject, clamp into the board, or warn; "
        "synonyms: via outside board, drill misses substrate, AP210 via off-board, "
        "drill location outside outline, PCB via doesn't pierce copper, "
        "PCB via off-board, AP210 via outside outline, ECAD via drilled into air"
    ),
    schema="AP242",
)


def _render_m086() -> str:
    """Render AP210 file with VIA_DEFINITION center outside board outline.

    Uses ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20-#24   CARTESIAN_POINTs for 30x30 mm board outline corners
      #25       POLYLINE for board outline (closed rectangle)
      #100      LAMINATE_OR_PLY_DEFINITION for the board core
      #101      PLY_BOUNDARY_REPRESENTATION linking outline to ply
      #200      CARTESIAN_POINT for via center at (50, 50, 0) — outside board
      #201      AXIS2_PLACEMENT_3D for via drill axis
      #210      VIA_DEFINITION with drill outside board outline — the defect
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M086: AP210 via drilled outside the conductor / board outline */")
    lines.append("/* DEFECT: VIA_DEFINITION drill at (50,50,0) but board outline is (0..30, 0..30) mm */")
    lines.append("/* Via drills through air — doesn't pierce any copper layer */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* Byte assertion: contains(b'LAMINATE_OR_PLY_DEFINITION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M086: AP210 via outside board outline'),'2;1');")
    lines.append("FILE_NAME('M086.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* PCB board outline: 30 mm x 30 mm rectangle */")
    lines.append("#20=CARTESIAN_POINT('bl',(0.0,0.0,0.0));")
    lines.append("#21=CARTESIAN_POINT('br',(30.0,0.0,0.0));")
    lines.append("#22=CARTESIAN_POINT('tr',(30.0,30.0,0.0));")
    lines.append("#23=CARTESIAN_POINT('tl',(0.0,30.0,0.0));")
    lines.append("/* Closed POLYLINE outline (30x30 mm board) */")
    lines.append("#25=POLYLINE('outline',(#20,#21,#22,#23,#20));")
    lines.append("/* Byte assertion: contains(b'LAMINATE_OR_PLY_DEFINITION') */")
    lines.append("/* Board core ply definition */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('core',$,$,$,LENGTH_MEASURE(0.2));")
    lines.append("/* PLY_BOUNDARY_REPRESENTATION links the outline to the ply */")
    lines.append("#101=PLY_BOUNDARY_REPRESENTATION('core_outline',(#25),#14);")
    lines.append("/* Byte assertion: contains(b'VIA_DEFINITION') */")
    lines.append("/* DEFECT: via center at (50,50,0) is outside (0..30, 0..30) board outline */")
    lines.append("/* The via drill physically misses the substrate — drills into air */")
    lines.append("#200=CARTESIAN_POINT('via_loc',(50.0,50.0,0.0));")
    lines.append("#201=AXIS2_PLACEMENT_3D('via_axis',#200,$,$);")
    lines.append("#210=VIA_DEFINITION('via_a',$,#201,LENGTH_MEASURE(0.3));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-via-drilled-outside-board-outline',")
    lines.append("  (#25,#100,#101,#200,#201,#210));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M086','M086','M086',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m086(path) -> None:
    Path(path).write_text(_render_m086())


f.render = _render_m086  # type: ignore[method-assign]
f.write = _write_m086    # type: ignore[method-assign]
