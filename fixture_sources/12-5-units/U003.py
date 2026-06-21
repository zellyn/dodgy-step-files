"""U003 — Onshape inch workspace exports metric STEP (inch-shaped coordinates in mm LENGTH_UNIT context).

Catalog claim: A part modelled in Onshape with inch units exports to STEP whose LENGTH_UNIT
is metric (millimetres); but coordinates are exact inch-to-mm conversions like 25.4 (1 in)
and 63.5 (2.5 in). Geometry is preserved but the display-unit choice is lost.

Reproducer recipe: Onshape workspace=inch; export STEP; result file declares metric SI unit
although authoring was in inches — coordinates like 25.4 and 63.5.

Byte assertions:
  contains(b'SI_UNIT(.MILLI.,.METRE.)') or contains(b'SI_UNIT(.MILLI., .METRE.)')
  matches(rb'25\\.4|63\\.5')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U003",
    defect=(
        "Onshape inch workspace exports metric STEP — inch coordinates in mm LENGTH_UNIT context; "
        "input: part modelled in Onshape with inch workspace units (1 inch x 2.5 inch extents); "
        "Onshape export coerces LENGTH_UNIT to metric SI_UNIT(.MILLI.,.METRE.) but does NOT "
        "scale the coordinates — values 25.4 and 63.5 are the exact inch-to-mm conversions "
        "(1 in = 25.4 mm, 2.5 in = 63.5 mm); "
        "geometry is preserved but the display-unit choice is lost: the file looks like an "
        "inch part rewritten as mm without any further rescaling; "
        "receivers display in mm with mm display tolerances rather than the authored inch values; "
        "kernel should round-trip authored display unit through CONVERSION_BASED_UNIT for inch; "
        "do not coerce to base SI on export; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: Onshape inch workspace exports mm STEP, STEP coordinates 25.4 instead of 1, "
        "inch workspace lost in metric STEP, display unit lost on Onshape export, "
        "inch model with mm declaration"
    ),
)


def _render_u003() -> str:
    """Render a Part-21: inch workspace coordinates (25.4, 63.5) in a mm LENGTH_UNIT context."""
    return (
        "ISO-10303-21;\n"
        "/* U003: Onshape inch workspace exports mm STEP — display unit dropped */\n"
        "/* Authored as 1 in x 2.5 in part; Onshape forces LENGTH_UNIT to mm on export */\n"
        "/* Coordinates are inch-to-mm conversions: 1 in = 25.4, 2.5 in = 63.5 */\n"
        "/* The file looks like a mm part but the authoring intent was in inches */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U003: Onshape inch workspace export with mm LENGTH_UNIT context'),'2;1');\n"
        "FILE_NAME('U003.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 1 in x 2.5 in part; coordinates are inch-to-mm conversions */\n"
        "/* 1 inch = 25.4 mm, 2.5 inches = 63.5 mm */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(25.4,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,63.5,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.4));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(25.4,63.5,25.4));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: SI_UNIT(.MILLI.,.METRE.) but coordinates are inch-valued (25.4, 63.5) */\n"
        "/* Kernel should have preserved CONVERSION_BASED_UNIT for inch round-trip */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('onshape-inch-in-mm-context',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u003(path) -> None:
    Path(path).write_text(_render_u003())


f.render = _render_u003  # type: ignore[method-assign]
f.write = _write_u003    # type: ignore[method-assign]
