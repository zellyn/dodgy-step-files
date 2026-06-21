"""U023 — Conversion factor for `'INCH'` is wrong / omitted.

Catalog claim: A CONVERSION_BASED_UNIT('INCH',..) must reference a
LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4), <millimeter>). Writers that emit a wrong
factor (e.g. 2.54E1 against a model whose values are mm; or 25.4 against a metre-based
reference) or omit the conversion entirely break unit interpretation.

Reproducer recipe: LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.54E1), #mm);
CONVERSION_BASED_UNIT('INCH', #lmwu) paired with a model whose values are actually in mm.

Byte assertions:
  matches(rb'LENGTH_MEASURE\\(2\\.54[Ee]?\\d*\\)') or matches(rb'LENGTH_MEASURE\\(2\\.54\\)')
  contains(b'2.54') or contains(b'2.54E1')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U023",
    defect=(
        "Conversion factor for 'INCH' is wrong: 2.54E1 (cm-based) instead of 25.4 (mm-based); "
        "input: STEP file with CONVERSION_BASED_UNIT('INCH',#lmwu) where #lmwu references "
        "LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.54E1),#mm); "
        "the correct inch-to-mm conversion factor is 25.4 — one inch equals exactly 25.4 mm; "
        "a factor of 2.54E1 is numerically identical to 25.4 in decimal, BUT the exponent "
        "notation 2.54E1 signals the writer computed the factor as 2.54 cm (wrong basis); "
        "this fixture pairs the wrong-notation factor with coordinates in plain mm, "
        "so a kernel that interprets 2.54E1 as 25.4 mm/inch will appear to work "
        "but one that interprets 2.54 (before E1) as cm will apply wrong scale; "
        "kernel must verify conversion-based-unit factors against known SI conversions: "
        "INCH must be 25.4 mm exactly; reject or warn if name and numeric factor are inconsistent; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: wrong inch conversion factor in STEP, INCH factor not 25.4, "
        "missing LENGTH_MEASURE_WITH_UNIT for inch, STEP inch factor 2.54 instead of 25.4, "
        "inch conversion factor mismatched"
    ),
)


def _render_u023() -> str:
    """Render a Part-21 with CONVERSION_BASED_UNIT INCH using wrong factor 2.54E1."""
    return (
        "ISO-10303-21;\n"
        "/* U023: INCH conversion factor expressed as 2.54E1 (cm-based notation) */\n"
        "/* Correct factor for INCH-to-mm is 25.4; using 2.54E1 signals wrong basis */\n"
        "/* Kernel must verify inch conversion against known SI: 1 inch = 25.4 mm exactly */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U023: INCH conversion factor wrong: 2.54E1 not 25.4'),'2;1');\n"
        "FILE_NAME('U023.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: part with mm-valued coordinates */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* SI mm basis */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "/* DEFECT: factor is 2.54E1 — cm-based notation rather than 25.4 */\n"
        "/* Correct would be: LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(25.4),#8) */\n"
        "#9=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(2.54E1),#8);\n"
        "/* CONVERSION_BASED_UNIT references the wrong-factor measure */\n"
        "#10=(CONVERSION_BASED_UNIT('INCH',#9) LENGTH_UNIT() NAMED_UNIT(*));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.0254),#8,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#20=GEOMETRIC_CURVE_SET('inch-wrong-factor',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u023(path) -> None:
    Path(path).write_text(_render_u023())


f.render = _render_u023  # type: ignore[method-assign]
f.write = _write_u023    # type: ignore[method-assign]
