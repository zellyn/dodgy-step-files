"""U022 — `'INCH'` spelled as `'inch'` / `'IN'` / `'inches'` on `CONVERSION_BASED_UNIT`.

Catalog claim: The conventional name is `'INCH'`; producers sometimes write `'inch'`,
`'IN'`, or `'inches'` on the `name` attribute of `CONVERSION_BASED_UNIT`, breaking
case-sensitive lookup tables.

Reproducer recipe: CONVERSION_BASED_UNIT('inches', #lmwu).

Byte assertions:
  contains(b"'inch'") or contains(b"'IN'") or contains(b"'inches'")
  count(b"CONVERSION_BASED_UNIT(") >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U022",
    defect=(
        "'INCH' spelled as 'inch' / 'IN' / 'inches' on CONVERSION_BASED_UNIT breaks case-sensitive lookup; "
        "input: STEP file with CONVERSION_BASED_UNIT where the name attribute uses lowercase or "
        "abbreviated forms: 'inch', 'IN', or 'inches' instead of the canonical 'INCH'; "
        "the conventional name per ISO 10303 is 'INCH' in uppercase; "
        "case-sensitive unit lookup tables used by receivers fail to match 'inch', 'IN', or 'inches'; "
        "kernels must normalize case-insensitively against the canonical set "
        "{INCH, FOOT, MILLIMETRE, MILLIMETER, METER, METRE, MIL, MICROINCH}; "
        "if name is unrecognized the kernel must fall back to resolving via dimensional_exponents "
        "rather than failing silently or applying identity scale; "
        "this fixture carries three CONVERSION_BASED_UNIT instances: 'inches', 'inch', and 'IN'; "
        "only the correct canonical 'INCH' is absent — all three are misspellings; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: INCH lowercase in CONVERSION_BASED_UNIT, STEP inch spelled as 'inch' or 'IN', "
        "case-sensitive inch lookup fails, 'inches' in CONVERSION_BASED_UNIT name, "
        "STEP unit name wrong case"
    ),
)


def _render_u022() -> str:
    """Render a Part-21 with CONVERSION_BASED_UNIT using misspelled inch names."""
    return (
        "ISO-10303-21;\n"
        "/* U022: INCH name misspelled as 'inches', 'inch', 'IN' on CONVERSION_BASED_UNIT */\n"
        "/* Canonical name is 'INCH' (uppercase); these variants break case-sensitive lookup */\n"
        "/* Kernel must normalize case-insensitively or resolve via dimensional_exponents */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U022: INCH spelled as inch/IN/inches in CONVERSION_BASED_UNIT'),'2;1');\n"
        "FILE_NAME('U022.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: simple part with 1-inch coordinates (values in mm = 25.4) */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(25.4,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,25.4,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,12.7));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(25.4,25.4,12.7));\n"
        "/* SI mm basis */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* Three misspelled inch CONVERSION_BASED_UNIT instances */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* DEFECT: 'inches' — wrong name, should be 'INCH' */\n"
        "#10=(CONVERSION_BASED_UNIT('inches',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#30=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* DEFECT: 'inch' — lowercase, should be 'INCH' */\n"
        "#31=(CONVERSION_BASED_UNIT('inch',#30) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#32=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8);\n"
        "/* DEFECT: 'IN' — abbreviated, should be 'INCH' */\n"
        "#33=(CONVERSION_BASED_UNIT('IN',#32) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0254),#8,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "/* GRC uses 'inches' (the first misspelled unit) */\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('inch-unit-name-misspelled',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u022(path) -> None:
    Path(path).write_text(_render_u022())


f.render = _render_u022  # type: ignore[method-assign]
f.write = _write_u022    # type: ignore[method-assign]
