"""M088 — AP210 etherometric vs metric measurement context confusion.

Catalog claim: A PCB stackup has ply outline coordinates that look like
etherometric (sheet-normalized 0..1) values, but the file's
representation_context is the global Cartesian one with mm LENGTH_UNIT.
Consumed as mm, the ply outline collapses from a 100mm board to a 1mm speck.

Reproducer recipe: A POLYLINE with corner coordinates (0,0)(1,0)(1,1)(0,1)
used as a PLY_BOUNDARY_REPRESENTATION in a context whose LENGTH_UNIT is mm.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'PLY_BOUNDARY_REPRESENTATION')
  contains(b'LAMINATE_OR_PLY_DEFINITION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M088",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP210 PLY_BOUNDARY_REPRESENTATION with etherometric "
        "sheet-normalized (0..1) coordinates declared in a mm LENGTH_UNIT context; "
        "input: AP210 STEP file where LAMINATE_OR_PLY_DEFINITION 'stackup_ply' has a "
        "PLY_BOUNDARY_REPRESENTATION with a POLYLINE outline using corner coordinates "
        "(0,0)(1,0)(1,1)(0,1) — the canonical etherometric sheet-normalized unit square — "
        "but the file's REPRESENTATION_CONTEXT declares LENGTH_UNIT as SI_UNIT MILLI METRE; "
        "consumed as mm the ply outline is a 1mm x 1mm square instead of the 100mm x 100mm "
        "board it represents in etherometric space; the PCB outline collapses by factor 100; "
        "per AP210 §4.3 measurement contexts etherometric and metric contexts must not be "
        "mixed without explicit unit conversion; receiver consuming etherometric coords as mm "
        "gets a 100x-shrunken board — downstream impedance and EMC computations are all wrong; "
        "kernel must warn and accept: validate coordinate magnitudes against declared unit, "
        "warn on suspiciously small footprints, or reject when crossing context kinds; "
        "synonyms: PCB outline tiny on import, AP210 board shrunk to 1mm, etherometric vs "
        "metric confusion, stackup coordinates 0.1 but unit is mm, PCB outline collapses to speck, "
        "PCB units wrong, outline scale 100x off, AP210 etherometric vs metric mismatch"
    ),
    schema="AP242",
)


def _render_m088() -> str:
    """Render AP210 file with etherometric (0..1) ply outline coords in a mm context.

    Uses ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm LENGTH_UNIT — the key mismatch)
      #20-#24   CARTESIAN_POINTs with unit-square etherometric coords (0..1)
      #25       POLYLINE for ply outline (etherometric unit square)
      #100      LAMINATE_OR_PLY_DEFINITION for the stackup ply
      #101      PLY_BOUNDARY_REPRESENTATION — defect: etherometric coords in mm context
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M088: AP210 etherometric vs metric measurement context confusion */")
    lines.append("/* DEFECT: PLY_BOUNDARY_REPRESENTATION has etherometric (0..1) coords in mm context */")
    lines.append("/* Consumed as mm, the 100mm PCB board collapses to a 1mm speck */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'PLY_BOUNDARY_REPRESENTATION') */")
    lines.append("/* Byte assertion: contains(b'LAMINATE_OR_PLY_DEFINITION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M088: AP210 etherometric vs metric context confusion'),'2;1');")
    lines.append("FILE_NAME('M088.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("FILE_SCHEMA(('ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN { 1 0 10303 210 3 1 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('electronic_assembly_interconnect_and_packaging_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'electronic_assembly_interconnect_and_packaging_design',2014,#1);")
    lines.append("/* Unit context declares mm — but coordinates below are etherometric (0..1) */")
    lines.append("/* This context mismatch is the defect: etherometric in metric context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('pcb','3D'));")
    lines.append("/* DEFECT: ply outline uses etherometric (sheet-normalized) unit-square coords */")
    lines.append("/* In etherometric space these represent a 100mm x 100mm board corner locations */")
    lines.append("/* Parsed as mm, the outline is only 1mm x 1mm — 100x too small */")
    lines.append("/* Etherometric unit square corners: (0,0), (1,0), (1,1), (0,1) */")
    lines.append("#20=CARTESIAN_POINT('bl',(0.0,0.0,0.0));")
    lines.append("#21=CARTESIAN_POINT('br',(1.0,0.0,0.0));")
    lines.append("#22=CARTESIAN_POINT('tr',(1.0,1.0,0.0));")
    lines.append("#23=CARTESIAN_POINT('tl',(0.0,1.0,0.0));")
    lines.append("/* Closed POLYLINE outline (etherometric unit square — wrong in mm context) */")
    lines.append("#25=POLYLINE('ply_outline',(#20,#21,#22,#23,#20));")
    lines.append("/* Byte assertion: contains(b'LAMINATE_OR_PLY_DEFINITION') */")
    lines.append("/* Stackup ply definition — references the mismatched boundary representation */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('stackup_ply',$,$,$,LENGTH_MEASURE(0.2));")
    lines.append("/* Byte assertion: contains(b'PLY_BOUNDARY_REPRESENTATION') */")
    lines.append("/* DEFECT: PLY_BOUNDARY_REPRESENTATION uses etherometric coords (0..1) in mm context */")
    lines.append("/* Receiver parsing this file treats coords as mm: 1mm board instead of 100mm */")
    lines.append("#101=PLY_BOUNDARY_REPRESENTATION('ply_boundary',(#25),#14);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-etherometric-vs-metric-context-confusion',")
    lines.append("  (#25,#100,#101,#20,#21,#22,#23));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M088','M088','M088',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m088(path) -> None:
    Path(path).write_text(_render_m088())


f.render = _render_m088  # type: ignore[method-assign]
f.write = _write_m088    # type: ignore[method-assign]
