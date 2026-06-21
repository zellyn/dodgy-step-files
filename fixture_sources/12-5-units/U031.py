"""U031 — `CONVERSION_BASED_UNIT('DEG',#9)` / DEG vs RADIAN encoding via complex entity.

Catalog claim: Plane-angle units are typically encoded as a complex entity combining
CONVERSION_BASED_UNIT('DEG',#refToRadianMeasure), NAMED_UNIT(*), and PLANE_ANGLE_UNIT().
Defects: members in non-alphabetical order; conversion factor wrong (not pi/180);
name spelled 'DEGREES' / 'deg'; missing PLANE_ANGLE_UNIT() member entirely so kernel
mistakes it for length.

Reproducer recipe: #10=( CONVERSION_BASED_UNIT('DEG',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT() );
with #9 = PLANE_ANGLE_MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(0.0174533),#radian) — and a
variant with factor 1.0 (treats degrees as radians).

Byte assertions:
  contains(b"CONVERSION_BASED_UNIT('DEG'") or contains(b'PLANE_ANGLE_UNIT')
  matches(rb"CONVERSION_BASED_UNIT\\('DEG'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U031",
    defect=(
        "CONVERSION_BASED_UNIT('DEG') with wrong factor 1.0 instead of pi/180 (0.01745329); "
        "input: STEP file with complex plane-angle entity "
        "( CONVERSION_BASED_UNIT('DEG',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT() ) "
        "where #9=PLANE_ANGLE_MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(1.0),#radian) — "
        "factor 1.0 means kernel treats degree values as radian values (57.3x error); "
        "correct factor is pi/180 ≈ 0.01745329; "
        "kernel must verify CONVERSION_BASED_UNIT('DEG') factor ≈ pi/180 within tolerance; "
        "resolve via PLANE_ANGLE_UNIT() membership rather than the name string; "
        "normalize the space-separated complex record members to alphabetical order; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: DEG vs RADIAN complex entity, CONVERSION_BASED_UNIT('DEG') wrong factor, "
        "PLANE_ANGLE_UNIT missing from complex, STEP degree unit factor not pi/180, "
        "complex angle unit malformed"
    ),
)


def _render_u031() -> str:
    """Render a Part-21 with CONVERSION_BASED_UNIT('DEG') using wrong factor 1.0."""
    return (
        "ISO-10303-21;\n"
        "/* U031: CONVERSION_BASED_UNIT('DEG') factor is 1.0 instead of pi/180 */\n"
        "/* Complex plane-angle entity: ( CONVERSION_BASED_UNIT('DEG',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT() ) */\n"
        "/* DEFECT: PLANE_ANGLE_MEASURE(1.0) — treats degrees as radians (57.3x error) */\n"
        "/* Correct factor: PLANE_ANGLE_MEASURE(0.01745329251994329) = pi/180 */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U031: DEG complex entity with wrong conversion factor 1.0'),'2;1');\n"
        "FILE_NAME('U031.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: part with coordinates in mm */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* Radian SI base for angle */\n"
        "#8=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "/* DEFECT: factor is 1.0 — kernel will interpret degree-values as radians */\n"
        "/* Correct: PLANE_ANGLE_MEASURE(0.01745329251994329) */\n"
        "#9=PLANE_ANGLE_MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(1.0),#8);\n"
        "/* Complex plane-angle entity with wrong factor reference */\n"
        "#10=( CONVERSION_BASED_UNIT('DEG',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT() );\n"
        "#11=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#11,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#11,#10,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('deg-wrong-factor',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u031(path) -> None:
    Path(path).write_text(_render_u031())


f.render = _render_u031  # type: ignore[method-assign]
f.write = _write_u031    # type: ignore[method-assign]
