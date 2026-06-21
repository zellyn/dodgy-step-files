"""U005 — Plant 3D exports STEP whose LENGTH_UNIT context disagrees with authored drawing units.

Catalog claim: Models authored in Plant 3D export to STEP with a LENGTH_UNIT context whose
declared unit does not match drawing units. Typical signature: LENGTH_UNIT declared as
millimetres with UNCERTAINTY_MEASURE_WITH_UNIT 0.001 mm, but coordinates of 1.0 and 2.5;
a sub-millimetre or unscaled inch fragment sitting in a mm context.

Reproducer recipe: LENGTH_UNIT declared as millimetres; coordinates of 1.0, 2.5 that
represent unscaled inch values (1 inch, 2.5 inches) or sub-mm fragments in mm context.

Byte assertions:
  contains(b'SI_UNIT(.MILLI.,.METRE.)') or contains(b'SI_UNIT(.MILLI., .METRE.)')
  matches(rb'CARTESIAN_POINT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U005",
    defect=(
        "Plant 3D STEP LENGTH_UNIT context disagrees with authored drawing units; "
        "input: models authored in AutoCAD Plant 3D with drawing units that do not match "
        "the LENGTH_UNIT emitted in the STEP export; "
        "typical signature: LENGTH_UNIT declared as SI_UNIT(.MILLI.,.METRE.) with uncertainty "
        "0.001 mm (classic mm context), but CARTESIAN_POINT coordinates are 1.0 and 2.5 — "
        "raw inch values (1 in, 2.5 in) that should be 25.4 and 63.5 in mm; "
        "a sub-millimetre or unscaled inch fragment sitting in an mm context; "
        "the STEP serialisation pipeline silently changes the unit context between authoring "
        "and serialization without rescaling the coordinate values; "
        "kernel writer must emit unit context tied to authored model unit; "
        "producer pipeline must not silently change unit context; "
        "kernel reader must surface a unit-vs-coordinate-magnitude inconsistency; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: Plant 3D STEP unit context disagrees with drawing, sub-mm coords in mm STEP context, "
        "Plant 3D unit mismatch, AutoCAD Plant 3D wrong STEP units, drawing units differ from STEP unit"
    ),
)


def _render_u005() -> str:
    """Render a Part-21 with SI_UNIT(.MILLI.,.METRE.) but inch-scale coordinates."""
    return (
        "ISO-10303-21;\n"
        "/* U005: Plant 3D STEP LENGTH_UNIT context disagrees with authored drawing units */\n"
        "/* AutoCAD Plant 3D serializes LENGTH_UNIT as mm but model drawing units are inches */\n"
        "/* Coordinates 1.0 and 2.5 are raw inch values; a mm context implies 25.4 and 63.5 */\n"
        "/* Receivers see mismatched scale — a sub-mm part or an unscaled inch fragment */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U005: Plant 3D LENGTH_UNIT mm context with inch-scale coordinates'),'2;1');\n"
        "FILE_NAME('U005.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: coordinates 1.0 and 2.5 are raw inch values sitting in an mm context */\n"
        "/* If mm, these are sub-millimetre fragments; authored intent was 1 in and 2.5 in */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(1.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,2.5,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,1.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(1.0,2.5,1.0));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: SI_UNIT(.MILLI.,.METRE.) declared but coordinates 1.0/2.5 are inch values */\n"
        "/* Plant 3D serializer changed unit context without rescaling the coordinate values */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('plant3d-mm-context-inch-coords',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u005(path) -> None:
    Path(path).write_text(_render_u005())


f.render = _render_u005  # type: ignore[method-assign]
f.write = _write_u005    # type: ignore[method-assign]
