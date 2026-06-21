"""U034 — Mile-to-millimetre conversion factor mis-applied on export.

Catalog claim: An exporter is asked to write a part whose internal unit is "mile".
The STEP CONVERSION_BASED_UNIT factor for miles-to-millimetres is 1609344.0; exporter
writes 1609.344 (the metres-to-millimetres prefix accidentally applied), under-scaling
the resulting part by 1000x.

Reproducer recipe: Part 1 mile long internally; export with CONVERSION_BASED_UNIT('MILE', factor).
Factor written is wrong by 1000x.

Byte assertions:
  contains(b'1609.344')
  contains(b"CONVERSION_BASED_UNIT('MILE'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U034",
    defect=(
        "Mile-to-millimetre conversion factor mis-applied on export; "
        "input: STEP file with CONVERSION_BASED_UNIT('MILE',#lmwu) where #lmwu references "
        "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(1609.344),#mm); "
        "correct factor for 1 mile to mm is 1609344.0 mm; "
        "exporter accidentally applied metres-to-mm prefix (×1000) in the wrong direction, "
        "writing 1609.344 (km per mile) instead of 1609344.0 (mm per mile); "
        "part exported as 1 mile is under-scaled by 1000x on re-import; "
        "kernel must verify CONVERSION_BASED_UNIT('MILE') factor against schema-mandated constant "
        "1609344.0 mm/mile; never recompute — always use lookup table; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: mile-to-mm factor wrong by 1000, MILE conversion 1609.344 instead of 1609344, "
        "metres-to-mm prefix applied to miles, STEP mile under-scaled 1000x, "
        "wrong mile conversion factor on export"
    ),
)


def _render_u034() -> str:
    """Render a Part-21 with CONVERSION_BASED_UNIT MILE using wrong factor 1609.344."""
    return (
        "ISO-10303-21;\n"
        "/* U034: CONVERSION_BASED_UNIT('MILE') factor is 1609.344 instead of 1609344.0 */\n"
        "/* Exporter applied metres-to-mm prefix in wrong direction: 1609.344 km != 1 mile in mm */\n"
        "/* Correct: 1 mile = 1609344.0 mm exactly (1609.344 km) */\n"
        "/* DEFECT: factor 1609.344 under-scales geometry by 1000x on re-import */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U034: MILE conversion factor wrong: 1609.344 not 1609344.0'),'2;1');\n"
        "FILE_NAME('U034.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: 1x0.5x0.25 mile part (values in miles) */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(1.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,0.5,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,0.25));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(1.0,0.5,0.25));\n"
        "/* SI mm basis for conversion reference */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* DEFECT: factor 1609.344 — metres-to-mm prefix accidentally applied to miles */\n"
        "/* Correct factor: 1609344.0 mm per mile */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(1609.344),#8);\n"
        "/* CONVERSION_BASED_UNIT references the wrong-factor measure */\n"
        "#10=(CONVERSION_BASED_UNIT('MILE',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(6.21371E-7),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('mile-wrong-factor',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u034(path) -> None:
    Path(path).write_text(_render_u034())


f.render = _render_u034  # type: ignore[method-assign]
f.write = _write_u034    # type: ignore[method-assign]
