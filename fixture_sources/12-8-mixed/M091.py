"""M091 — AP210 conductor trace exits the board outline.

Catalog claim: A CONDUCTOR_TRACK_PROFILE describes a copper segment
whose endpoints place part of the trace outside the board outline. The
trace is not fabricable.

Reproducer recipe: Board outline (0..30, 0..30); trace from (15,5) to
(40,5); the right half exits at x=30.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'CONDUCTOR_TRACK_PROFILE')
  contains(b'PLY_BOUNDARY_REPRESENTATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M091",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP210 CONDUCTOR_TRACK_PROFILE with copper trace "
        "endpoint outside the board outline; "
        "input: AP210 STEP file where LAMINATE_OR_PLY_DEFINITION 'core' has a "
        "PLY_BOUNDARY_REPRESENTATION with a POLYLINE board outline covering (0..30, 0..30) mm, "
        "and CONDUCTOR_TRACK_PROFILE 'trace_r1' describes a copper trace from CARTESIAN_POINT "
        "(15.0, 5.0, 0.0) to CARTESIAN_POINT (40.0, 5.0, 0.0) via a POLYLINE; "
        "the trace extends from x=15 to x=40 but the board outline only extends to x=30; "
        "the right-hand portion of the trace (x=30..40) exits the board substrate and "
        "is not fabricable — the conductor floats in air beyond the board edge; "
        "per ISO 10303-210 §6 conductor_track_profile geometric containment rules all "
        "conductor segments must lie within the ply boundary of the layer they inhabit; "
        "downstream impedance and continuity checks fail because the trace exits the substrate; "
        "kernel must validate trace containment against board outline; clip to board, "
        "reject the trace, or warn; "
        "synonyms: PCB trace exits board, AP210 conductor outside outline, ECAD trace floats "
        "off board, PCB trace off-board, conductor exits outline, AP210 trace exits board, "
        "ECAD trace floats off board, copper segment outside substrate"
    ),
    schema="AP242",
)


def _render_m091() -> str:
    """Render AP210 file with CONDUCTOR_TRACK_PROFILE exiting the board outline.

    Uses ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #20-#24   CARTESIAN_POINTs for 30x30 mm board outline corners
      #25       POLYLINE for board outline (closed 30x30 rectangle)
      #100      LAMINATE_OR_PLY_DEFINITION for the board core
      #101      PLY_BOUNDARY_REPRESENTATION linking outline to ply
      #200      CARTESIAN_POINT trace start (15.0, 5.0, 0.0) — inside board
      #201      CARTESIAN_POINT trace end (40.0, 5.0, 0.0) — OUTSIDE board (x>30)
      #210      POLYLINE for the trace path
      #220      CONDUCTOR_TRACK_PROFILE — defect: trace exits board outline
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M091: AP210 conductor trace exits the board outline */")
    lines.append("/* DEFECT: CONDUCTOR_TRACK_PROFILE trace from (15,5) to (40,5) but board ends at x=30 */")
    lines.append("/* The trace exits the board at x=30 — right half (x=30..40) is not fabricable */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'CONDUCTOR_TRACK_PROFILE') */")
    lines.append("/* Byte assertion: contains(b'PLY_BOUNDARY_REPRESENTATION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M091: AP210 conductor trace exits board outline'),'2;1');")
    lines.append("FILE_NAME('M091.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* PCB board outline: 30 mm x 30 mm rectangle */")
    lines.append("#20=CARTESIAN_POINT('bl',(0.0,0.0,0.0));")
    lines.append("#21=CARTESIAN_POINT('br',(30.0,0.0,0.0));")
    lines.append("#22=CARTESIAN_POINT('tr',(30.0,30.0,0.0));")
    lines.append("#23=CARTESIAN_POINT('tl',(0.0,30.0,0.0));")
    lines.append("/* Closed POLYLINE outline (30x30 mm board) */")
    lines.append("#25=POLYLINE('outline',(#20,#21,#22,#23,#20));")
    lines.append("/* Byte assertion: contains(b'PLY_BOUNDARY_REPRESENTATION') */")
    lines.append("/* Board core ply definition */")
    lines.append("#100=LAMINATE_OR_PLY_DEFINITION('core',$,$,$,LENGTH_MEASURE(0.2));")
    lines.append("/* PLY_BOUNDARY_REPRESENTATION links the outline to the ply */")
    lines.append("#101=PLY_BOUNDARY_REPRESENTATION('core_outline',(#25),#14);")
    lines.append("/* Trace endpoints: from (15,5) inside board to (40,5) outside board */")
    lines.append("/* Board right edge is at x=30; trace exits at x=30, ends at x=40 */")
    lines.append("#200=CARTESIAN_POINT('trace_start',(15.0,5.0,0.0));")
    lines.append("#201=CARTESIAN_POINT('trace_end',(40.0,5.0,0.0));")
    lines.append("/* Byte assertion: contains(b'CONDUCTOR_TRACK_PROFILE') */")
    lines.append("/* DEFECT: CONDUCTOR_TRACK_PROFILE trace exits board outline at x=30 */")
    lines.append("/* Right endpoint (40,5) is 10mm outside the 30x30mm board */")
    lines.append("#210=POLYLINE('trace_path',(#200,#201));")
    lines.append("#220=CONDUCTOR_TRACK_PROFILE('trace_r1',(#210),#14);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-conductor-trace-exits-board-outline',")
    lines.append("  (#25,#100,#101,#200,#201,#210,#220));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M091','M091','M091',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m091(path) -> None:
    Path(path).write_text(_render_m091())


f.render = _render_m091  # type: ignore[method-assign]
f.write = _write_m091    # type: ignore[method-assign]
