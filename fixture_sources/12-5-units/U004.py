"""U004 — Inventor STEP export switches angle unit from DEGREE to RADIAN, breaks doc preference on round-trip.

Catalog claim: Inventor changed STEP angle unit to .RADIAN. for cross-vendor consistency.
After import the document angle unit setting is overwritten. The producer's preference for
degrees does not round-trip via the STEP plane_angle_unit context.

Reproducer recipe: doc set to degrees; export STEP; file contains
(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.)); reopen — display now in radians.

Byte assertions:
  contains(b'.RADIAN.')
  count(b'.RADIAN.') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U004",
    defect=(
        "Inventor STEP export switches angle unit from DEGREE to RADIAN — doc preference broken; "
        "input: Autodesk Inventor 2018+ document set to degree display preference; "
        "STEP export emits (NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.)) for the "
        "plane_angle_unit context; on re-import the document angle unit setting is overwritten "
        "and the session preference switches from degrees to radians; "
        "the producer's preference for degrees does not round-trip via STEP plane_angle_unit context; "
        "kernel should normalize/separate the wire unit (RADIAN by spec) from the display unit; "
        "preserve session angular display preference, or coerce an explicit "
        "CONVERSION_BASED_UNIT('DEGREE',..) when the author prefers degrees; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: Inventor STEP forces RADIAN angles, angle unit changes from DEGREE to RADIAN, "
        "doc preference broken on STEP round-trip, Inventor switches plane_angle to radians, "
        "STEP angle unit overwritten on import"
    ),
)


def _render_u004() -> str:
    """Render a Part-21 with SI_UNIT($,.RADIAN.) as plane_angle_unit (Inventor 2018+ pattern)."""
    return (
        "ISO-10303-21;\n"
        "/* U004: Inventor STEP export switches angle unit from DEGREE to RADIAN */\n"
        "/* Autodesk Inventor 2018+ changed STEP angle unit to .RADIAN. for cross-vendor compat */\n"
        "/* Document set to degrees display; STEP export switches to RADIAN silently */\n"
        "/* On re-import the session angle preference is overwritten to radians */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U004: Inventor switches plane_angle_unit to RADIAN on export'),'2;1');\n"
        "FILE_NAME('U004.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: a simple 50x50 mm part with a 45-degree chamfer */\n"
        "/* Chamfer angle stored as radian value (PI/4 = 0.7854) in RADIAN unit context */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,20.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,20.0));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: PLANE_ANGLE_UNIT is SI_UNIT($,.RADIAN.) — document preference was DEGREE */\n"
        "/* Inventor emits RADIAN for cross-vendor consistency, overwriting doc preference */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Angle value: 45 degrees = 0.7854 radians; doc preference was DEGREE not RADIAN */\n"
        "#15=PLANE_ANGLE_MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(0.7853981634),#11);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('inventor-radian-angle-part',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u004(path) -> None:
    Path(path).write_text(_render_u004())


f.render = _render_u004  # type: ignore[method-assign]
f.write = _write_u004    # type: ignore[method-assign]
