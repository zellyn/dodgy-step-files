"""U014 — SI_UNIT(METRE) without MILLI prefix but mm-sized coordinates (OCCT 7.8 regression).

Catalog claim: After OCCT 7.8 the write.units / DESTEP_Parameters write-unit setting is no
longer applied: output coordinates are not scaled to the requested unit. Common signature:
LENGTH_UNIT declared as bare SI_UNIT(METRE) (no .MILLI. prefix) but coordinate values are
sized as if mm (e.g. 100, 50, 25.4), so a literal interpretation produces a 100 m x 50 m
oversized part.

Reproducer recipe: xstep.cascade.unit MM and write.step.unit M, write a 1-unit vertex;
file is still in mm. Result: LENGTH_UNIT is SI_UNIT($,.METRE.) but coordinates are 100, 50, 25.

Byte assertions:
  matches(rb'SI_UNIT\\(\\s*\\$\\s*,\\s*\\.METRE\\.\\)') or contains(b'SI_UNIT($,.METRE.)')
  contains(b'.METRE.')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U014",
    defect=(
        "OCCT 7.8 regression: write.units ignored — SI_UNIT(METRE) declared but coordinates are mm-sized; "
        "input: STEP file produced by OCCT STEPControl_Writer with xstep.cascade.unit MM and "
        "write.step.unit M; after OCCT 7.8 the write-unit setting is no longer applied so "
        "coordinates are not scaled to the requested unit; "
        "LENGTH_UNIT is bare SI_UNIT($,.METRE.) (no .MILLI. prefix) but coordinate values are "
        "mm-sized (100.0, 50.0, 25.4) — a literal interpretation produces a 100 m x 50 m x 25.4 m "
        "oversized part; "
        "receivers enforcing the spec see a 1000x scale discrepancy between declared unit and "
        "actual coordinate magnitudes; "
        "kernel must heal by applying 1/1000 scale or reject with a diagnostic; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: OCCT 7.8 ignores write.units setting, STEP exports as METRE despite mm setting, "
        "write.step.unit silently ignored, OCCT regression on STEP write unit, "
        "100m oversized part from STEP write"
    ),
)


def _render_u014() -> str:
    """Render a Part-21 with SI_UNIT($,.METRE.) but mm-scale coordinates (OCCT 7.8 regression)."""
    return (
        "ISO-10303-21;\n"
        "/* U014: OCCT 7.8 regression — write.units ignored */\n"
        "/* LENGTH_UNIT declared as bare SI_UNIT($,.METRE.) but coordinates are mm-sized */\n"
        "/* OCCT STEPControl_Writer with write.step.unit M still emits mm coordinates */\n"
        "/* Literal interpretation: 100.0 metres x 50.0 metres — 1000x too large */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U014: SI_UNIT(METRE) with mm-scale coordinates (OCCT 7.8 regression)'),'2;1');\n"
        "FILE_NAME('U014.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 100x50x25.4 mm part; coordinates remain mm despite METRE unit declaration */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(100.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.4));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(100.0,50.0,25.4));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: SI_UNIT($,.METRE.) — bare METRE, no .MILLI. prefix */\n"
        "/* OCCT 7.8 regression: write.step.unit M was requested but coordinates are mm-scale */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-07),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('occt-78-metre-with-mm-coords',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u014(path) -> None:
    Path(path).write_text(_render_u014())


f.render = _render_u014  # type: ignore[method-assign]
f.write = _write_u014    # type: ignore[method-assign]
