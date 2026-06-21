"""U024 — `dimensional_exponents` inconsistent with declared unit.

Catalog claim: A CONVERSION_BASED_UNIT declares dimensional_exponents that don't match the
physical quantity it claims to represent; e.g. mass-exponent 0 on a mass unit; length-exponent
!= -3 for density.

Reproducer recipe: CONVERSION_BASED_UNIT named 'POUND' with
DIMENSIONAL_EXPONENTS(0,0,0,0,0,0,0) (all zero) referenced from a mass measure.

Byte assertions:
  contains(b'DIMENSIONAL_EXPONENTS(0.0,0.0,0.0,0.0,0.0,0.0,0.0)') or
    matches(rb'DIMENSIONAL_EXPONENTS\\(0(?:\\.0)?(?:,\\s*0(?:\\.0)?){6}\\)')
  contains(b"'POUND'") or contains(b'DIMENSIONAL_EXPONENTS')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U024",
    defect=(
        "dimensional_exponents inconsistent with declared unit: POUND has all-zero exponents; "
        "input: STEP file with CONVERSION_BASED_UNIT named 'POUND' whose NAMED_UNIT references "
        "DIMENSIONAL_EXPONENTS(0.0,0.0,0.0,0.0,0.0,0.0,0.0) — all seven exponents are zero; "
        "the POUND is a mass unit; mass units must carry exponent (0.,1.,0.,0.,0.,0.,0.) "
        "per ISO 31: (length, mass, time, electric-current, temperature, luminous-intensity, "
        "amount-of-substance); all-zero exponents represent a dimensionless quantity, "
        "not a mass unit; referencing this from a mass measure makes the measure dimensionless; "
        "a kernel must cross-validate dimensional_exponents against the quantity used "
        "at the reference site: a MEASURE_REPRESENTATION_ITEM('mass',...) referencing a unit "
        "with all-zero exponents is invalid; kernel must reject or fall back to base SI; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: dimensional_exponents wrong for unit, POUND with all-zero exponents, "
        "DIMENSIONAL_EXPONENTS inconsistent with name, STEP unit exponents mass-zero, "
        "exponents don't match unit type"
    ),
)


def _render_u024() -> str:
    """Render a Part-21 with POUND CONVERSION_BASED_UNIT with all-zero DIMENSIONAL_EXPONENTS."""
    return (
        "ISO-10303-21;\n"
        "/* U024: CONVERSION_BASED_UNIT 'POUND' with DIMENSIONAL_EXPONENTS(0,0,0,0,0,0,0) */\n"
        "/* Mass unit must have exponent (0,1,0,0,0,0,0) per ISO 31 */\n"
        "/* All-zero exponents => dimensionless: inconsistent with mass unit claim */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U024: POUND unit with all-zero dimensional_exponents'),'2;1');\n"
        "FILE_NAME('U024.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: simple part */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* Standard geometry context: mm */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* DEFECT: POUND unit with all-zero DIMENSIONAL_EXPONENTS */\n"
        "/* Correct for mass: DIMENSIONAL_EXPONENTS(0.0,1.0,0.0,0.0,0.0,0.0,0.0) */\n"
        "#20=DIMENSIONAL_EXPONENTS(0.0,0.0,0.0,0.0,0.0,0.0,0.0);\n"
        "/* SI mm basis for pound conversion: 1 pound = 453.592 grams */\n"
        "#21=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#22=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(453.592),#21);\n"
        "/* DEFECT: CONVERSION_BASED_UNIT 'POUND' references all-zero exponents */\n"
        "#23=(CONVERSION_BASED_UNIT('POUND',#22) MASS_UNIT() NAMED_UNIT(#20));\n"
        "/* Validation property using the defective POUND unit */\n"
        "#40=MEASURE_REPRESENTATION_ITEM('mass',LENGTH_MEASURE(2.5),#23);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#50=GEOMETRIC_CURVE_SET('pound-bad-exponents',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u024(path) -> None:
    Path(path).write_text(_render_u024())


f.render = _render_u024  # type: ignore[method-assign]
f.write = _write_u024    # type: ignore[method-assign]
