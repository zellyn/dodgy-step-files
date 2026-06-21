"""U021 — KILO prefix REQUIRED on mass_unit referenced from a derived SI unit (Newton).

Catalog claim: Newton is [kg*m*s^-2]. Each si_unit referenced by derived_unit_element for
a derived SI unit must NOT carry a prefix, except when the referenced si_unit is a mass_unit,
which MUST carry .KILO.. Forgetting the prefix makes Newton numerically equivalent to
gram*m*s^-2, off by 1000.

Reproducer recipe: define a force_unit (Newton) whose derived_unit_element references a
mass_unit with no prefix; or a free-standing mass unit with prefix other than .KILO..

Byte assertions:
  contains(b'DERIVED_UNIT_ELEMENT')
  contains(b'force_unit') or contains(b'FORCE_UNIT') or contains(b'mass_unit') or contains(b'MASS_UNIT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U021",
    defect=(
        "KILO prefix REQUIRED on mass_unit referenced from a derived SI unit (Newton); "
        "input: STEP file defining a FORCE_UNIT (Newton) as a DERIVED_UNIT whose "
        "DERIVED_UNIT_ELEMENT references a MASS_UNIT (gram SI_UNIT) with NO prefix; "
        "per IEC/ISO 80000: Newton is kg*m*s^-2 — the mass_unit in any derived SI unit "
        "MUST carry .KILO. prefix (kilogram, not gram); "
        "omitting the .KILO. prefix makes Newton numerically equivalent to gram*m*s^-2 "
        "which is 1/1000 of a Newton — forces computed in this unit are off by 1000; "
        "a standalone mass_unit with a prefix other than .KILO. is likewise illegal "
        "(e.g. .MEGA. gram would be 1 tonne, not a valid SI mass quantity); "
        "kernel must validate that mass_unit in derived_unit_element carries .KILO. prefix; "
        "reject or auto-convert otherwise; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: KILO prefix missing on mass_unit, Newton built without kilo prefix, "
        "force_unit derived from gram instead of kg, STEP Newton off by 1000, "
        "mass_unit prefix wrong in derived SI"
    ),
)


def _render_u021() -> str:
    """Render a Part-21 with FORCE_UNIT (Newton) whose mass_unit has no .KILO. prefix."""
    return (
        "ISO-10303-21;\n"
        "/* U021: KILO prefix missing on mass_unit in FORCE_UNIT (Newton) derived unit */\n"
        "/* Newton = kg*m*s^-2; mass_unit MUST carry .KILO. prefix per ISO spec */\n"
        "/* DEFECT: mass_unit references SI_UNIT($,.GRAM.) -- no prefix => gram not kilogram */\n"
        "/* Force values will be 1000x wrong: unit is gram*m*s^-2, not Newton */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U021: FORCE_UNIT (Newton) with mass_unit missing .KILO. prefix'),'2;1');\n"
        "FILE_NAME('U021.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: a simple part */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* Standard length/angle/solid-angle units (correct) */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* DEFECT: mass_unit defined as SI_UNIT($,.GRAM.) -- NO .KILO. prefix */\n"
        "/* Should be SI_UNIT(.KILO.,.GRAM.) to represent kilograms */\n"
        "#20=(MASS_UNIT() NAMED_UNIT(*) SI_UNIT($,.GRAM.));\n"
        "/* SI time unit (seconds) — correct, no prefix */\n"
        "#21=(NAMED_UNIT(*) SI_UNIT($,.SECOND.) TIME_UNIT());\n"
        "/* SI length unit in metres for the Newton definition — correct, no prefix here */\n"
        "#22=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "/* DEFECT: Newton built from gram (no kilo) => off by 1000 */\n"
        "/* Correct: DERIVED_UNIT_ELEMENT(#kg_unit, 1.) but we use #20 (gram) */\n"
        "#23=DERIVED_UNIT_ELEMENT(#20,1.);\n"
        "#24=DERIVED_UNIT_ELEMENT(#22,1.);\n"
        "#25=DERIVED_UNIT_ELEMENT(#21,-2.);\n"
        "#26=(FORCE_UNIT() NAMED_UNIT(*) DERIVED_UNIT((#23,#24,#25)));\n"
        "/* Force validation property: 9.81 'N' but actually gram*m*s^-2 (1000x too small) */\n"
        "#40=MEASURE_REPRESENTATION_ITEM('applied_force',LENGTH_MEASURE(9.81),#26);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#50=GEOMETRIC_CURVE_SET('part-with-bad-newton-unit',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u021(path) -> None:
    Path(path).write_text(_render_u021())


f.render = _render_u021  # type: ignore[method-assign]
f.write = _write_u021    # type: ignore[method-assign]
