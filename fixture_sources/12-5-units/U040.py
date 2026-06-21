"""U040 — Pressure unit `Pa` built from a derived-unit chain (`kg / (m * s^2)`).

Catalog claim: Pascal (Pa) is dimensionally kg*m^(-1)*s^(-2). A producer that emits pressure
as a DERIVED_UNIT composed of three DERIVED_UNIT_ELEMENT entries (mass at exponent +1, length
at exponent -1, time at exponent -2) stresses receivers that pattern-match on a single named
pressure unit. Variant: length unit is millimetre (MILLI METRE), making the composed unit
1000x off from Pa.

Reproducer recipe: DERIVED_UNIT_ELEMENT(#mass,1.0), DERIVED_UNIT_ELEMENT(#length,-1.0),
DERIVED_UNIT_ELEMENT(#time,-2.0), DERIVED_UNIT((#e1,#e2,#e3)).
Variant: length unit is millimetre so composed unit is kg*mm^-1*s^-2 = 1000 Pa.

Byte assertions:
  contains(b'DERIVED_UNIT_ELEMENT') and contains(b'DERIVED_UNIT(')
  count(b'DERIVED_UNIT_ELEMENT') >= 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U040",
    defect=(
        "Pressure unit Pa built from DERIVED_UNIT chain kg*mm^-1*s^-2 — 1000x off from SI Pa; "
        "input: STEP file where the pressure unit is emitted as a DERIVED_UNIT composed of "
        "three DERIVED_UNIT_ELEMENT entries: kilogram^+1, millimetre^-1, second^-2; "
        "the dimensional signature (mass^1 length^-1 time^-2) is correct for Pascal "
        "but the mixed SI prefix (mm instead of m) makes the scale 1000x off: "
        "kg*mm^-1*s^-2 = 1000 kg*m^-1*s^-2 = 1000 Pa; "
        "receivers that pattern-match on a named pressure unit do not recognise this DERIVED_UNIT chain; "
        "receivers that resolve the dimensional signature but ignore SI prefix yield 1000x scale error; "
        "kernel must heal: detect dimensional signature of pressure (mass^1 length^-1 time^-2), "
        "normalise SI prefix mismatches deterministically, and bind to a Pa context; "
        "warn when the composition does not reduce to a recognised SI unit without prefix coercion; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: STEP pressure Pa garbled, Pa unit not recognised from derived chain, "
        "DERIVED_UNIT pressure 1000x wrong, validation pressure derived unit, "
        "Pa from kg.m^-1.s^-2 not bound, pressure kg mm^-1 s^-2 mixed prefix"
    ),
)


def _render_u040() -> str:
    """Render a Part-21 with DERIVED_UNIT for Pa using kg, mm (not m), s — 1000x off."""
    return (
        "ISO-10303-21;\n"
        "/* U040: Pressure unit Pa as DERIVED_UNIT with mixed prefix: kg*mm^-1*s^-2 = 1000 Pa */\n"
        "/* DEFECT: length unit is MILLI METRE, not METRE — composed unit is 1000x off from Pa */\n"
        "/* Kernel must resolve dimensional signature and normalise SI prefix mismatch */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U040: Pa DERIVED_UNIT chain with mm length unit — 1000x SI prefix mismatch'),'2;1');\n"
        "FILE_NAME('U040.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: part with mm coordinates */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* Standard mm geometry context */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Base SI units for DERIVED_UNIT pressure chain */\n"
        "/* DEFECT: mass in kg (correct), but length is MILLI METRE not METRE */\n"
        "#20=(MASS_UNIT() NAMED_UNIT(*) SI_UNIT(.KILO.,.GRAM.));\n"
        "/* DEFECT: millimetre used for length in pressure chain — makes unit 1000x off from Pa */\n"
        "#21=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#22=(NAMED_UNIT(*) SI_UNIT($,.SECOND.) TIME_UNIT());\n"
        "/* DERIVED_UNIT for pressure: mass^+1, length^-1, time^-2 */\n"
        "/* With mm as length: kg*mm^-1*s^-2 = 1000*kg*m^-1*s^-2 = 1000 Pa */\n"
        "#30=DERIVED_UNIT_ELEMENT(#20,1.);\n"
        "#31=DERIVED_UNIT_ELEMENT(#21,-1.);\n"
        "#32=DERIVED_UNIT_ELEMENT(#22,-2.);\n"
        "/* DEFECT: this DERIVED_UNIT composes to 1000 Pa, not 1 Pa */\n"
        "#33=DERIVED_UNIT((#30,#31,#32));\n"
        "/* Pressure measure using the malformed DERIVED_UNIT */\n"
        "/* Author intends 101325 Pa (atmospheric) but the unit is 1000x off */\n"
        "#40=MEASURE_REPRESENTATION_ITEM('pressure_value',LENGTH_MEASURE(101325.),#33);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#50=GEOMETRIC_CURVE_SET('pressure-unit-pa-derived-chain',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u040(path) -> None:
    Path(path).write_text(_render_u040())


f.render = _render_u040  # type: ignore[method-assign]
f.write = _write_u040    # type: ignore[method-assign]
