"""U015 — FreeCAD/OCCT 7.8.1: model in mm but file labelled as inches (re-import 25.4x too large).

Catalog claim: User picks "inch" as export unit; OCCT 7.8.1 still writes coordinates in mm
but writes LENGTH_UNIT as inch. Re-import scales 25.4x too large.

Reproducer recipe: file declares (CONVERSION_BASED_UNIT('INCH',..) NAMED_UNIT(..) LENGTH_UNIT())
but CARTESIAN_POINT coordinates are mm-valued.

Byte assertions:
  contains(b"CONVERSION_BASED_UNIT('INCH'")
  matches(rb"'INCH'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U015",
    defect=(
        "FreeCAD/OCCT 7.8.1: model in mm but file labelled as inches — re-import 25.4x too large; "
        "input: FreeCAD 1.0.x on OCCT 7.8.1 with user picking inch as export unit; "
        "OCCT 7.8.1 still writes coordinates in mm but writes LENGTH_UNIT as "
        "CONVERSION_BASED_UNIT('INCH',..) — the unit declaration says inch but the numeric "
        "values are mm magnitudes (e.g. 100.0, 50.0, 25.4 mm); "
        "on re-import a receiver honouring the declared inch unit applies the 25.4 mm/in factor "
        "and the body loads 25.4x too large — a 100 mm part appears as 2540 mm; "
        "kernel must detect the suspicious factor-of-25.4 magnitude mismatch between declared "
        "inch unit and observed coordinate sizes and emit a warning; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: FreeCAD STEP labelled inch but values mm, model in mm but file says inches, "
        "re-import 25.4x too large from FreeCAD STEP, mm coords with INCH declaration, "
        "OCCT 7.8.1 mislabels STEP as inches"
    ),
)


def _render_u015() -> str:
    """Render a Part-21 declaring INCH unit but with mm-scale coordinates (FreeCAD OCCT 7.8.1)."""
    return (
        "ISO-10303-21;\n"
        "/* U015: FreeCAD/OCCT 7.8.1 — model in mm but file labelled as INCH */\n"
        "/* User picks inch as export unit; OCCT 7.8.1 still writes mm coordinates */\n"
        "/* LENGTH_UNIT declared as INCH but coordinate values are mm magnitudes */\n"
        "/* Re-import: receiver multiplies by 25.4 => body is 25.4x too large */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U015: INCH unit declared but coordinates are mm-scale (FreeCAD OCCT 7.8.1)'),'2;1');\n"
        "FILE_NAME('U015.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 100x50x25.4 mm part; OCCT 7.8.1 writes mm coords despite INCH declaration */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(100.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.4));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(100.0,50.0,25.4));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* SI mm basis for the inch conversion factor */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* Standard inch conversion: 1 inch = 25.4 mm */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* DEFECT: INCH unit declared but coordinates are mm-valued — OCCT 7.8.1 regression */\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#8,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('freecad-inch-label-mm-coords',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u015(path) -> None:
    Path(path).write_text(_render_u015())


f.render = _render_u015  # type: ignore[method-assign]
f.write = _write_u015    # type: ignore[method-assign]
