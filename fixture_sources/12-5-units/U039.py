"""U039 — Plane-angle unit declared as DEGREE but values stored as radians (or vice-versa).

Catalog claim: A PLANE_ANGLE_UNIT context is declared as degrees via a
CONVERSION_BASED_UNIT('DEGREE',#x) complex entity. Numeric angle attributes in the file
are stored as radians (e.g. 1.5708 intended as 90 degrees). A receiver that honours the
unit declaration reads 1.5708 degrees (off by factor of pi/180 ~ 57.3).

Reproducer recipe: a PLANE_ANGLE_UNIT context declared as
CONVERSION_BASED_UNIT('DEGREE',#refRadianMeasure) (factor pi/180); a
MEASURE_REPRESENTATION_ITEM carrying PLANE_ANGLE_MEASURE(1.5708) whose author intended 90
degrees but emitted the radian value.

Byte assertions:
  contains(b"CONVERSION_BASED_UNIT('DEGREE'") or contains(b"CONVERSION_BASED_UNIT('DEG'")
  contains(b'PLANE_ANGLE_MEASURE(1.5708') or contains(b'PLANE_ANGLE_MEASURE(90.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U039",
    defect=(
        "Plane-angle unit declared as DEGREE but value stored as radians (deg/rad confusion); "
        "input: STEP file where PLANE_ANGLE_UNIT context is declared as degrees via "
        "( CONVERSION_BASED_UNIT('DEGREE',#refRadian) NAMED_UNIT(*) PLANE_ANGLE_UNIT() ) "
        "with reference factor PLANE_ANGLE_MEASURE(0.01745329) = pi/180 (correct factor for degrees); "
        "a MEASURE_REPRESENTATION_ITEM then stores PLANE_ANGLE_MEASURE(1.5708) — "
        "the author intended 90 degrees but stored the radian value 1.5708 (= pi/2); "
        "a receiver that honours the declared DEGREE unit reads 1.5708 degrees — "
        "off by a factor of pi/180 ≈ 57.3 from the intended rotation; "
        "a receiver that hard-assumes radians for any PLANE_ANGLE_MEASURE silently produces "
        "90 degrees by accident, hiding the producer-side defect; "
        "kernel must surface the disagreement: 1.5708 degrees is plausible but if the intent "
        "was a rotation the unit declaration is authoritative; "
        "reject or warn when the angle magnitude is implausible for the declared unit "
        "(e.g. 90 rad ≈ 5157 degrees is unphysical); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: STEP angle wrong by 57x, deg/rad confusion, rotation off by pi/180, "
        "PLANE_ANGLE_MEASURE 1.5708 declared DEGREE, PMI angle reads 1.57 not 90, "
        "angular twin of mm vs inch length defect"
    ),
)


def _render_u039() -> str:
    """Render a Part-21 with DEGREE unit declared but radian value 1.5708 stored."""
    return (
        "ISO-10303-21;\n"
        "/* U039: PLANE_ANGLE_UNIT declared DEGREE but value 1.5708 is in radians */\n"
        "/* DEFECT: producer emitted radian value; declared unit is DEGREE */\n"
        "/* Correct receiver: read 1.5708 as 1.5708 degrees (off by factor pi/180 from intent) */\n"
        "/* Buggy receiver (hard-codes radians): silently reads 1.5708 rad = 90 deg by accident */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U039: DEGREE unit declared but 1.5708 radian value stored'),'2;1');\n"
        "FILE_NAME('U039.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: part with mm coordinates */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* SI radian base — required as the conversion reference for DEGREE */\n"
        "#8=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "/* Correct DEGREE conversion factor: pi/180 = 0.01745329251994329 */\n"
        "#9=PLANE_ANGLE_MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(0.01745329251994329),#8);\n"
        "/* DEGREE plane-angle unit declared with correct pi/180 factor */\n"
        "#10=(CONVERSION_BASED_UNIT('DEGREE',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT());\n"
        "#11=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#11,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#11,#10,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* DEFECT: PLANE_ANGLE_MEASURE(1.5708) — author intended 90 deg but stored pi/2 radians */\n"
        "/* With DEGREE unit declared, a conformant receiver reads this as 1.5708 degrees */\n"
        "/* A receiver hard-coding radians silently gets 90 degrees — hiding the defect */\n"
        "#20=MEASURE_REPRESENTATION_ITEM('rotation_angle',PLANE_ANGLE_MEASURE(1.5708),#10);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#30=GEOMETRIC_CURVE_SET('deg-declared-radian-stored',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u039(path) -> None:
    Path(path).write_text(_render_u039())


f.render = _render_u039  # type: ignore[method-assign]
f.write = _write_u039    # type: ignore[method-assign]
